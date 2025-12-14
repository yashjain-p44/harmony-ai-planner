"""Response model for chat endpoint."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    
    success: bool = Field(..., description="Whether the request was successful")
    response: str = Field(..., description="The AI agent's response")
    prompt: str = Field(..., description="The original user prompt")
    messages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Complete list of messages from the agent state (HumanMessage, AIMessage, ToolMessage, etc.)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if success is False"
    )
