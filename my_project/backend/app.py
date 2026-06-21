import logging
import os
import time
import json
import asyncio
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from config import Config
import secrets
from retrieval import get_relevant_chunks
from agent import book_knowledge_agent, Runner, InputGuardrailTripwireTriggered
from chatkit_server import initialize_chatkit_server
from models.chat import (
    ChatRequest, ErrorResponse, HealthCheckResponse,
    SSEMessage, AgentResponse, ChatKitSessionRequest, ChatKitSessionResponse,
    RequestContext, PageContext
)
from utils.validation import validate_query, validate_user_id, validate_session_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

allowed_origins = [
    origin.strip().rstrip("/")
    for origin in Config.ALLOWED_ORIGINS.split(",")
    if origin.strip()
]


class InMemoryRateLimiter:
    """Simple sliding-window rate limiter per IP."""
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_limited(self, ip: str) -> bool:
        now = time.time()
        window_start = now - self.window_seconds
        self.requests[ip] = [t for t in self.requests[ip] if t > window_start]
        if len(self.requests[ip]) >= self.max_requests:
            return True
        self.requests[ip].append(now)
        return False


rate_limiter = InMemoryRateLimiter(Config.RATE_LIMIT_REQUESTS, Config.RATE_LIMIT_WINDOW_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Config.validate()
    logger.info("Configuration validated successfully")

    app.state.chatkit_server = await initialize_chatkit_server()
    logger.info("ChatKitServer initialized successfully")
    yield


app = FastAPI(
    title="RAG Chatbot Backend",
    description="A Retrieval-Augmented Generation chatbot for technical book content",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    if rate_limiter.is_limited(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Too many requests", "error_code": "RATE_LIMITED"}
        )
    return await call_next(request)


@app.get("/")
async def root():
    return {"message": "Welcome to the Physical AI & Humanoid Robotics Textbook RAG Chatbot API",
            "version": "0.1.0",
            "endpoints": {
                "/health": "Health check endpoint",
                "/chat": "Chat endpoint (POST)"
            }}


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.now().isoformat()
    )


async def chat_stream_generator(request: ChatRequest) -> AsyncGenerator[str, None]:
    tokens_yielded = 0
    try:
        logger.info(f"Retrieving relevant chunks for query: {request.query[:50]}...")
        relevant_chunks = await get_relevant_chunks(request.query)

        logger.info(f"Starting agent stream for query: {request.query[:50]}...")

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
            if event.type == "raw_response_event":
                data = event.data
                agent_name = getattr(getattr(data, "response", None), "name", "")
                if agent_name == "Judge":
                    continue

                delta = getattr(data, "delta", None)
                if delta:
                    tokens_yielded += 1
                    message = SSEMessage(type="token", content=delta)
                    yield f"data: {message.model_dump_json()}\n\n"

            elif event.type == "run_item_stream_event":
                result = getattr(event, "result", None)
                if result and hasattr(result, "final_output"):
                    final_output = result.final_output
                    if final_output:
                        logger.info(f"Final output received: {str(final_output)[:50]}...")
                        if isinstance(final_output, AgentResponse):
                            message = SSEMessage(type="final", content=final_output)
                        else:
                            citations = [c["source"] for c in relevant_chunks if isinstance(c, dict) and c.get("source")]
                            message = SSEMessage(type="final", content=AgentResponse(
                                answer=str(final_output),
                                confidence=0.85,
                                citations=citations
                            ))
                        yield f"data: {message.model_dump_json()}\n\n"
                        tokens_yielded += 1

        if tokens_yielded == 0:
            logger.warning("Stream finished but no tokens or final result were yielded.")
            error_message = SSEMessage(type="error", content="The AI generated an empty response. Please try a different question.")
            yield f"data: {error_message.model_dump_json()}\n\n"

    except InputGuardrailTripwireTriggered:
        logger.info("Guardrail triggered (InputGuardrailTripwireTriggered)")
        error_message = SSEMessage(type="error", content="Off-topic query detected. I can only answer questions related to Physical AI and Robotics.")
        yield f"data: {error_message.model_dump_json()}\n\n"
    except Exception as e:
        logger.error(f"Error in chat stream: {e}", exc_info=True)
        error_message = SSEMessage(type="error", content=f"Streaming error: {str(e)}")
        yield f"data: {error_message.model_dump_json()}\n\n"


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        is_valid, error_msg, sanitized_query = validate_query(request.query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        is_valid, error_msg = validate_user_id(request.user_id)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        is_valid, error_msg = validate_session_id(request.session_id)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        sanitized_request = request.model_copy(update={"query": sanitized_query})

        return StreamingResponse(
            chat_stream_generator(sanitized_request),
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


@app.post("/api/chatkit/session", response_model=ChatKitSessionResponse)
async def chatkit_session(session_req: ChatKitSessionRequest, request: Request):
    try:
        cs = request.app.state.chatkit_server
        thread = await cs.store.create_thread(
            user_id=session_req.user_id,
            metadata={"source": "textbook_web"}
        )

        client_secret = f"sk_{secrets.token_urlsafe(32)}"

        return ChatKitSessionResponse(
            client_secret=client_secret,
            thread_id=thread.id,
            user_id=session_req.user_id
        )
    except Exception as e:
        logger.error(f"Error creating ChatKit session: {e}")
        raise HTTPException(status_code=500, detail="Could not initialize session")


@app.post("/api/chatkit/refresh")
async def chatkit_refresh(request: Request):
    user_id = request.headers.get("X-User-ID", "anonymous_student")
    new_secret = f"sk_{secrets.token_urlsafe(32)}"
    return ChatKitSessionResponse(
        client_secret=new_secret,
        thread_id=None,
        user_id=user_id
    )


@app.get("/api/chatkit/user")
async def chatkit_user(request: Request):
    user_id = request.headers.get("X-User-ID", "anonymous_student")
    return {"user_id": user_id, "name": "Physical AI Student"}


@app.post("/chatkit")
async def chatkit_protocol(request: Request):
    user_id = request.headers.get("X-User-ID", "anonymous_student")

    raw_body = await request.body()

    page_context = None
    try:
        body_json = json.loads(raw_body)
        if isinstance(body_json, dict):
            params = body_json.get("params", {})
            input_data = params.get("input", {})
            metadata = input_data.get("metadata", {})
            pc_data = metadata.get("pageContext")
            if pc_data and isinstance(pc_data, dict):
                headings = pc_data.get("headings", [])
                if isinstance(headings, str):
                    headings = [headings]
                page_context = PageContext(
                    url=pc_data.get("url", ""),
                    title=pc_data.get("title", ""),
                    headings=headings
                )
    except Exception as e:
        logger.warning(f"Could not parse pageContext from request body: {e}")

    ctx = RequestContext(user_id=user_id, page_context=page_context)

    try:
        from chatkit.server import StreamingResult, NonStreamingResult
        cs = request.app.state.chatkit_server
        result = await cs.process(raw_body, context=ctx)

        if isinstance(result, StreamingResult):
            return StreamingResponse(result, media_type="text/event-stream")
        elif isinstance(result, NonStreamingResult):
            return JSONResponse(content=json.loads(result.json))
        else:
            logger.error(f"Unexpected result type from ChatKitServer.process: {type(result)}")
            raise HTTPException(status_code=500, detail="Unexpected response from ChatKit server")
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.error(f"Error in ChatKit protocol handler: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="ChatKit processing error")


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
