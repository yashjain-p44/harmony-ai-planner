"""State definitions for LangGraph agents."""

from typing import TypedDict, Annotated


class AgentState(TypedDict):
    """State for the agent graph."""
    messages: Annotated[list, "List of messages in the conversation"]
