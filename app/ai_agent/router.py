"""Pure routing logic for LangGraph agents.

This module contains routing functions that decide the next node to execute
based on the current state. These functions contain no LLM calls, API calls,
or node logic - only pure conditional routing decisions.
"""

from app.ai_agent.state import AgentState


def should_continue(state: AgentState) -> str:
    """
    Determine if we should execute tools or end.
    
    Args:
        state: Current agent state
        
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
    return state["intent_type"]

def route_by_plan_status(state: AgentState) -> str:
    return state["plan_status"]

def route_by_execution_decision(state: AgentState) -> str:
    return state["execution_decision"]
