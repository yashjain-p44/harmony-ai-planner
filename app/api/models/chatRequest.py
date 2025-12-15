"""Request model for chat endpoint."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    prompt: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The user's message/prompt to send to the AI agent"
    )
    state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Previous agent state to resume from (for human-in-the-loop scenarios)"
    )
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate that prompt is not just whitespace."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty or only whitespace")
        return v.strip()
