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


def route_by_task_or_habit(state: AgentState) -> str:
    """
    Route based on whether this is a task or habit scheduling flow.
    
    Args:
        state: Current agent state
        
    Returns:
        "filter_task_slots" if task_definition exists, "filter_slots" otherwise
    """
    task_definition = state.get("task_definition")
    if task_definition:
        return "filter_task_slots"
    else:
        return "filter_slots"


def route_by_approval_state(state: AgentState) -> str:
    """
    Route based on human approval state.
    
    For CHANGES_REQUESTED, routes to task-specific or habit-specific filter nodes
    based on whether task_definition or habit_definition exists in state.
    
    Args:
        state: Current agent state with approval_state field
        
    Returns:
        Approval state string: "APPROVED", "REJECTED", "CHANGES_REQUESTED", 
        or "PENDING" (default)
    """
    approval_state = state.get("approval_state", "PENDING")
    
    # For CHANGES_REQUESTED, route to appropriate filter node based on task vs habit
    if approval_state == "CHANGES_REQUESTED":
        # Check if this is a task or habit
        task_definition = state.get("task_definition")
        if task_definition:
            # Task scheduling: route back to filter_task_slots
            return "CHANGES_REQUESTED_TASK"
        else:
            # Habit scheduling: route back to filter_slots
            return "CHANGES_REQUESTED_HABIT"
    
    # For REJECTED, check if it's a task (tasks should just END, habits go to execution_decider)
    if approval_state == "REJECTED":
        task_definition = state.get("task_definition")
        if task_definition:
            # Task scheduling: just end
            return "REJECTED_TASK"
        else:
            # Habit scheduling: go back to execution_decider
            return "REJECTED"
    
    return approval_state
