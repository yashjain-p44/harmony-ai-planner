"""State definitions for LangGraph agents."""

from typing import TypedDict, Annotated


class AgentState(TypedDict):
    """State for the agent graph."""
    messages: Annotated[list, "List of messages in the conversation"]
    needs_approval_from_human: Annotated[bool, "Whether the agent needs human approval before continuing"]
    # Tool calls and results are handled through messages (AIMessage with tool_calls, ToolMessage responses)
