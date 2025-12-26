"""
Pure routing logic for LangGraph agents.

This module contains routing functions that decide the next node to execute
based on the current state. These functions contain no LLM calls, API calls,
or node logic - only pure conditional routing decisions.

All routing functions follow the pattern:
- Input: AgentState
- Output: String (node name or "END")
"""

from app.ai_agent.state import AgentState


def should_continue(state: AgentState) -> str:
    """
    Determine if we should execute tools or end.
    
    Checks if the last message in the conversation has tool calls that need
    to be executed. This is used for tool-calling workflows.
    
    Args:
        state: Current agent state containing messages
        
    Returns:
        "tools" if there are tool calls to execute, "end" otherwise
    """
    messages = state.get("messages", [])
    
    if not messages:
        return "end"
    
    last_message = messages[-1]
    
    # Check if the last message has tool calls
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    
    return "end"


def route_by_intent(state: AgentState) -> str:
    """
    Route based on the classified user intent.
    
    Args:
        state: Current agent state with intent_type field
        
    Returns:
        Intent type string: "HABIT_SCHEDULE", "TASK_SCHEDULE", 
        "CALENDAR_ANALYSIS", or "UNKNOWN"
    """
    return state["intent_type"]


def route_by_plan_status(state: AgentState) -> str:
    """
    Route based on planning completion status.
    
    Args:
        state: Current agent state with plan_status field
        
    Returns:
        Plan status string: "PLAN_READY", "NEEDS_CLARIFICATION", or "PLAN_INFEASIBLE"
    """
    return state["plan_status"]


def route_by_execution_decision(state: AgentState) -> str:
    """
    Route based on execution decision.
    
    Args:
        state: Current agent state with execution_decision field
        
    Returns:
        Execution decision string: "EXECUTE", "DRY_RUN", or "CANCEL"
    """
    return state["execution_decision"]


def route_by_approval_state(state: AgentState) -> str:
    """
    Route based on human approval state.
    
    For CHANGES_REQUESTED, routes based on intent type:
    - Tasks: go directly to select_slots (skip filter_slots)
    - Habits: go to filter_slots first
    
    Args:
        state: Current agent state with approval_state and intent_type fields
        
    Returns:
        Node name or approval state string: "APPROVED", "REJECTED", 
        "select_slots" (for tasks with CHANGES_REQUESTED), 
        "filter_slots" (for habits with CHANGES_REQUESTED),
        or "PENDING" (default)
    """
    approval_state = state.get("approval_state", "PENDING")
    
    # For CHANGES_REQUESTED, route based on intent type
    # Tasks skip filter_slots, habits go through filter_slots
    if approval_state == "CHANGES_REQUESTED":
        intent_type = state.get("intent_type", "UNKNOWN")
        if intent_type == "TASK_SCHEDULE":
            return "select_slots"  # Tasks go directly to select_slots
        else:
            return "filter_slots"  # Habits go through filter_slots
    
    return approval_state


def route_by_intent_after_slots(state: AgentState) -> str:
    """
    Route based on intent type after computing free slots.
    Tasks skip filter_slots and go directly to select_slots.
    Habits go through filter_slots first.
    
    Args:
        state: Current agent state with intent_type field
        
    Returns:
        "select_slots" for tasks, "filter_slots" for habits
    """
    intent_type = state.get("intent_type", "UNKNOWN")
    if intent_type == "TASK_SCHEDULE":
        return "select_slots"
    else:
        return "filter_slots"
