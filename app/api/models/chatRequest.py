"""Request model for chat endpoint."""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    
    prompt: str = Field(
        default="",
        min_length=0,
        max_length=10000,
        description="The user's message/prompt to send to the AI agent. Can be empty if approval_state is provided."
    )
    state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Previous agent state to resume from (for human-in-the-loop scenarios)"
    )
    approval_state: Optional[Literal["PENDING", "APPROVED", "REJECTED", "CHANGES_REQUESTED"]] = Field(
        default=None,
        description="Approval state to update in agent state (for approval flow)"
    )
    approval_feedback: Optional[str] = Field(
        default=None,
        description="Feedback for approval (required if approval_state is REJECTED or CHANGES_REQUESTED)"
    )
    
    @field_validator('prompt')
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate that prompt is not just whitespace."""
        # Basic validation - will be checked again in model_validator
        return v.strip() if v else ""
    
    @model_validator(mode='after')
    def validate_prompt_with_approval(self):
        """Validate prompt based on whether approval_state is provided."""
        # Allow empty prompt if approval_state is provided (approval-only request)
        if self.approval_state:
            # For approval requests, empty prompt is allowed
            self.prompt = self.prompt.strip() if self.prompt else ""
        else:
            # For regular requests, prompt is required
            if not self.prompt or not self.prompt.strip():
                raise ValueError("Prompt cannot be empty or only whitespace")
            self.prompt = self.prompt.strip()
        return self
    
    @field_validator('approval_feedback')
    @classmethod
    def validate_approval_feedback(cls, v: Optional[str], info) -> Optional[str]:
        """Validate that feedback is provided when required."""
        approval_state = info.data.get('approval_state')
        if approval_state in ["REJECTED", "CHANGES_REQUESTED"] and not v:
            raise ValueError(f"approval_feedback is required when approval_state is {approval_state}")
        return v
