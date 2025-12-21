"""State definitions for LangGraph agents."""

from typing import TypedDict, Annotated
from typing import Literal, Optional, List

class AgentState(TypedDict):
    """State for the agent graph."""
    # Conversation history
    messages: Annotated[list, "List of messages in the conversation"]

    # Routing & control
    intent_type: Annotated[Literal[
        "HABIT_SCHEDULE",
        "TASK_SCHEDULE",
        "CALENDAR_ANALYSIS",
        "UNKNOWN",
    ], "Determines high-level flow (habit, task, analysis)"]

    plan_status: Annotated[Literal[
        "PLAN_READY",
        "NEEDS_CLARIFICATION",
        "PLAN_INFEASIBLE",
    ], "Indicates whether planning is complete, infeasible, or needs clarification"]

    execution_decision: Annotated[Literal[
        "EXECUTE",
        "DRY_RUN",
        "CANCEL",
    ], "Determines whether scheduling executes, dry-runs, or cancels"]

     # Planning artifacts
    habit_definition: Annotated[dict, "Structured definition of habit (what, frequency, duration)"]
    time_constraints: Annotated[dict, "Time-of-day, days-of-week, buffers, exclusions"]
    planning_horizon: Annotated[dict, "Time window for analysis (e.g., next 30 days)"]
    estimated_commitment: Annotated[dict, "Expected time per session / per week"]

    # Execution artifacts
    calendar_events_raw: Annotated[List[dict], "Raw calendar events fetched from provider"] 
    calendar_events_normalized: Annotated[List[dict], "Timezone-aligned, conflict-free events"]
    free_time_slots: Annotated[List[dict], "All available time windows"]
    filtered_slots: Annotated[List[dict], "Slots that satisfy constraints"]
    selected_slots: Annotated[List[dict], "Final chosen slots for scheduling"]
    created_events: Annotated[List[dict], "Provider event IDs and metadata"]
    
     # Failure / explanation
    failure_reason: Annotated[Optional[str], "Machine-readable reason for failure"]
    explanation_payload: Annotated[Optional[dict], "Structured data for human-readable explanation"]
    needs_approval_from_human: Annotated[Optional[bool], "Whether the agent needs human approval before continuing"]
    # Tool calls and results are handled through messages (AIMessage with tool_calls, ToolMessage responses)
