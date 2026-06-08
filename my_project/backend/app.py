import logging
import os
import sys
import time
import json
import asyncio
from datetime import datetime
from typing import Optional, AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from config import Config
from models.chat import ChatRequest, ChatResponse, ErrorResponse, HealthCheckResponse, SSEMessage, AgentResponse
from pydantic import BaseModel
import secrets
from retrieval import get_relevant_chunks
from agent import book_knowledge_agent, Runner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Build CORS origins from environment so deployments can be configured
# without code changes. We normalize by removing trailing slashes because
# FastAPI compares origins as exact strings.
allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://physical-ai-humanoid-robotics-textb-three-alpha.vercel.app",
)
allowed_origins = [
    origin.strip().rstrip("/")
    for origin in allowed_origins_env.split(",")
    if origin.strip()
]

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot Backend",
    description="A Retrieval-Augmented Generation chatbot for technical book content",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Validate configuration on startup
try:
    Config.validate()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration validation failed: {e}")
    sys.exit(1)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Middleware to add process time to response headers."""
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def root():
    """Root endpoint for the application."""
    return {"message": "Welcome to the Physical AI & Humanoid Robotics Textbook RAG Chatbot API",
            "version": "0.1.0",
            "endpoints": {
                "/health": "Health check endpoint",
                "/chat": "Chat endpoint (POST)"
            }}


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint to verify service status."""
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )


async def chat_stream_generator(request: ChatRequest, relevant_chunks: list[str]) -> AsyncGenerator[str, None]:
    """Generator for SSE events from the agent stream."""
    tokens_yielded = 0
    try:
        logger.info(f"Starting agent stream for query: {request.query[:50]}...")
        
        # Start streaming from the agent
        stream = Runner.run_streamed(
            book_knowledge_agent,
            request.query,
            context={
                "book_chunks": relevant_chunks,
                "user_id": request.user_id,
                "session_id": request.session_id
            }
        )

        async for event in stream.stream_events():
            # Handle token deltas from the raw response
            if event.type == "raw_response_event":
                data = event.data
                
                # IMPORTANT: Filter out tokens that might come from the judge agent
                # The BookKnowledgeAgent uses gemini-3.5-flash
                # The JudgeAgent uses gemini-3.1-flash-lite
                model = getattr(getattr(data, "response", None), "model", "")
                if "3.1" in str(model):
                    continue

                delta = getattr(data, "delta", None)
                if delta:
                    tokens_yielded += 1
                    message = SSEMessage(type="token", content=delta)
                    yield f"data: {message.model_dump_json()}\n\n"

            # Handle the final completion of the agent run
            elif event.type == "run_item_stream_event":
                result = getattr(event, "result", None)
                if result and hasattr(result, "final_output"):
                    final_output = result.final_output
                    if final_output:
                        logger.info(f"Final output received: {str(final_output)[:50]}...")
                        # If it's a structured response (AgentResponse), use it
                        # Otherwise wrap it in an AgentResponse
                        if isinstance(final_output, AgentResponse):
                            message = SSEMessage(type="final", content=final_output)
                        else:
                            message = SSEMessage(type="final", content=AgentResponse(
                                answer=str(final_output),
                                confidence=0.85,
                                citations=[]
                            ))
                        yield f"data: {message.model_dump_json()}\n\n"
                        tokens_yielded += 1

        if tokens_yielded == 0:
            logger.warning("Stream finished but no tokens or final result were yielded.")
            error_message = SSEMessage(type="error", content="The AI generated an empty response. Please try a different question.")
            yield f"data: {error_message.model_dump_json()}\n\n"

    except Exception as e:
        from agents import InputGuardrailTripwireTriggered
        if "InputGuardrailTripwireTriggered" in str(type(e)):
            logger.info("Guardrail triggered (InputGuardrailTripwireTriggered)")
            error_message = SSEMessage(type="error", content="Off-topic query detected. I can only answer questions related to Physical AI and Robotics.")
            yield f"data: {error_message.model_dump_json()}\n\n"
        else:
            logger.error(f"Error in chat stream: {e}", exc_info=True)
            error_message = SSEMessage(type="error", content=f"Streaming error: {str(e)}")
            yield f"data: {error_message.model_dump_json()}\n\n"


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint for the RAG system with SSE streaming.
    """
    try:
        # Validate the request
        from utils.validation import validate_query, validate_user_id, validate_session_id

        is_valid, error_msg, sanitized_query = validate_query(request.query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Retrieve relevant chunks from vector store using the sanitized query
        logger.info(f"Retrieving relevant chunks for query: {sanitized_query[:50]}...")
        relevant_chunks = await get_relevant_chunks(sanitized_query)

        # Create a new request object with the sanitized query for the stream generator
        sanitized_request = request.model_copy(update={"query": sanitized_query})

        # Return the streaming response
        return StreamingResponse(
            chat_stream_generator(sanitized_request, relevant_chunks),
            media_type="text/event-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint setup: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while setting up the stream: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )