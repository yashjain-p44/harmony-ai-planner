"""Response model for chat endpoint."""

from typing import Optional, List, Dict, Any, Literal
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
    needs_approval_from_human: bool = Field(
        default=False,
        description="Whether the agent needs human approval before continuing"
    )
    approval_state: Optional[Literal["PENDING", "APPROVED", "REJECTED", "CHANGES_REQUESTED"]] = Field(
        default=None,
        description="Current approval state (PENDING means approval is needed)"
    )
    approval_summary: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Summary of what needs approval (slots, habit info, etc.)"
    )
    state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Full agent state (returned when needs_approval_from_human is True)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if success is False"
    )
