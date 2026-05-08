import logging
import os
import sys
import time
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import Config
from models.chat import ChatRequest, ChatResponse, ErrorResponse, HealthCheckResponse, ChatKitSessionRequest, ChatKitSessionResponse
from pydantic import BaseModel
from typing import Optional
import secrets
from retrieval import get_relevant_chunks
from agent import get_agent_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot Backend",
    description="A Retrieval-Augmented Generation chatbot for technical book content",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://physical-ai-humanoid-robotics-textb-three-alpha.vercel.app/,http://localhost:3000"],  # In production, replace with specific origins
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


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for the application."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="An unexpected error occurred",
            error_code="INTERNAL_ERROR",
        ).model_dump()
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint to verify service status."""
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/api/chatkit/session", response_model=ChatKitSessionResponse)
async def create_chatkit_session(request: ChatKitSessionRequest):
    """
    Create a ChatKit session and return a client secret.
    This endpoint follows the pattern expected by ChatKit for session management.
    """
    # Generate a temporary client secret (in a real implementation, this would
    # integrate with OpenAI's ChatKit service to get a proper client secret)
    client_secret = f"chatkit_{secrets.token_urlsafe(32)}"

    # Return the client secret and an optional thread ID
    return ChatKitSessionResponse(
        client_secret=client_secret,
        thread_id=None  # Start with a new thread
    )


@app.post("/api/chatkit/refresh", response_model=ChatKitSessionResponse)
async def refresh_chatkit_session():
    """
    Refresh a ChatKit session.
    This endpoint follows the pattern expected by ChatKit for token refreshing.
    """
    # Generate a new client secret for refresh
    client_secret = f"chatkit_{secrets.token_urlsafe(32)}"

    return ChatKitSessionResponse(
        client_secret=client_secret,
        thread_id=None
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, response: Response):
    """
    Main chat endpoint for the RAG system.

    This endpoint receives a user query, retrieves relevant book chunks,
    processes the query with the agent, and returns a response grounded
    in the book content.
    """
    start_time = time.time()

    try:
        # Validate the request
        from utils.validation import validate_query, validate_user_id, validate_session_id

        is_valid, error_msg = validate_query(request.query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        user_valid, user_error = validate_user_id(request.user_id)
        if not user_valid:
            raise HTTPException(status_code=400, detail=user_error)

        session_valid, session_error = validate_session_id(request.session_id)
        if not session_valid:
            raise HTTPException(status_code=400, detail=session_error)

        # Retrieve relevant chunks from vector store
        retrieval_start = time.time()
        logger.info(f"Retrieving relevant chunks for query: {request.query[:50]}...")
        relevant_chunks = await get_relevant_chunks(request.query)
        retrieval_time = time.time() - retrieval_start

        # Generate response using the agent
        agent_start = time.time()
        logger.info("Generating response with agent...")
        response_text = await get_agent_response(request.query, relevant_chunks)
        agent_time = time.time() - agent_start

        # If the response indicates off-topic query, set confidence lower
        is_off_topic = "only answer questions related to the technical book content" in response_text.lower()
        confidence = 0.3 if is_off_topic else 0.8

        total_time = time.time() - start_time
        logger.info(f"Request completed in {total_time:.2f}s (retrieval: {retrieval_time:.2f}s, agent: {agent_time:.2f}s)")

        # Add performance metrics to response headers
        response.headers["X-Response-Time"] = f"{total_time:.3f}"
        response.headers["X-Retrieval-Time"] = f"{retrieval_time:.3f}"
        response.headers["X-Agent-Time"] = f"{agent_time:.3f}"
        response.headers["X-Total-Time"] = f"{total_time:.3f}"

        return ChatResponse(
            response=response_text,
            source_chunks=relevant_chunks if not is_off_topic else [],
            confidence=confidence
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"Error in chat endpoint after {total_time:.2f}s: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )