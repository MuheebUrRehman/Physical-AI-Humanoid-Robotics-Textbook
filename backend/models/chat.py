from pydantic import BaseModel, Field
from typing import List, Optional


class ChatRequest(BaseModel):
    """Request model for chat interactions."""

    query: str = Field(..., description="The user's query or question", min_length=1, max_length=2000)
    user_id: Optional[str] = Field(None, description="Optional user identifier")
    session_id: Optional[str] = Field(None, description="Optional session identifier")


class ChatResponse(BaseModel):
    """Response model for chat interactions."""

    response: str = Field(..., description="The AI-generated response to the query")
    source_chunks: List[str] = Field(default_factory=list, description="List of source chunks used to generate the response")
    confidence: float = Field(ge=0.0, le=1.0, default=0.0, description="Confidence score of the response")
    query_id: Optional[str] = Field(None, description="Identifier for the query")


class ErrorResponse(BaseModel):
    """Error response model for chat interactions."""

    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    query_id: Optional[str] = Field(None, description="Identifier for the query that caused the error")


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Timestamp of the health check")


class ChatKitSessionRequest(BaseModel):
    """Request model for ChatKit session creation."""
    pass


class ChatKitSessionResponse(BaseModel):
    """Response model for ChatKit session creation."""
    client_secret: str = Field(..., description="Client secret for ChatKit session")
    thread_id: Optional[str] = Field(None, description="Thread ID for the conversation")