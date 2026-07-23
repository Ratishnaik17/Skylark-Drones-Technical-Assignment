"""
Pydantic request schemas for the Founder Business Intelligence Agent.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Business question from the founder",
        examples=["What is our current pipeline value?"],
    )

    session_id: Optional[str] = Field(
        default=None,
        description="Conversation session ID",
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


class ErrorResponse(BaseModel):
    """Standard API error response."""

    success: bool = False
    error: str