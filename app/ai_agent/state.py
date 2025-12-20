"""State definitions for LangGraph agents."""

from typing import TypedDict, Annotated, Optional


class AgentState(TypedDict):
    """State for the agent graph."""
    messages: Annotated[list, "List of messages in the conversation"]
    needs_approval_from_human: Annotated[bool, "Whether the agent needs human approval before continuing"]
    intent: Annotated[Optional[str], "User intent classification (e.g., 'schedule_meeting', 'query_events', 'find_slots', 'general_chat')"]
    # Tool calls and results are handled through messages (AIMessage with tool_calls, ToolMessage responses)
