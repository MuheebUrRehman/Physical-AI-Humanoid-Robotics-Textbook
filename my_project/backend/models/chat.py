from pydantic import BaseModel, Field
from typing import List, Optional, Union


class ChatRequest(BaseModel):
    """Request model for chat interactions."""

    query: str = Field(..., description="The user's query or question", min_length=1, max_length=2000)
    user_id: str = Field(..., description="Unique user identifier")
    session_id: str = Field(..., description="Unique session identifier")


class AgentResponse(BaseModel):
    """Structured response from the AI Agent."""

    answer: str = Field(..., description="The grounded response based on book content")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score of the response")
    citations: List[str] = Field(default_factory=list, description="List of source file paths or chapter titles referenced")


class SSEMessage(BaseModel):
    """Schema for Server-Sent Events messages."""

    type: str = Field(..., description="Event type: 'token', 'final', or 'error'")
    content: Union[str, AgentResponse] = Field(..., description="Content of the event")


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


class PageContext(BaseModel):
    """Page context information from the frontend."""
    url: str
    title: str
    headings: List[str] = Field(default_factory=list)


class RequestContext(BaseModel):
    """Context for a ChatKit request with user isolation."""
    user_id: str
    page_context: Optional[PageContext] = None
    metadata: dict = Field(default_factory=dict)


class ChatKitSessionRequest(BaseModel):
    """Request model for ChatKit session creation."""
    user_id: str = Field(..., description="User ID for session initialization")


class ChatKitSessionResponse(BaseModel):
    """Response model for ChatKit session creation."""
    client_secret: str = Field(..., description="Client secret for ChatKit session")
    thread_id: Optional[str] = Field(None, description="Thread ID for the conversation")
    user_id: str = Field(..., description="User ID associated with the session")