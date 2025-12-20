"""Pure routing logic for LangGraph agents.

This module contains routing functions that decide the next node to execute
based on the current state. These functions contain no LLM calls, API calls,
or node logic - only pure conditional routing decisions.
"""

from app.ai_agent.state import AgentState


def route_after_intent(state: AgentState) -> str:
    """
    Route after intent classification.
    
    Routes to the agent node to process the request based on the classified intent.
    In the future, this can be extended to route to specialized nodes based on intent.
    
    Args:
        state: Current agent state with intent field
        
    Returns:
        "agent" to continue processing, "end" if no valid intent
    """
    intent = state.get("intent")
    
    # If intent is not set or is general_chat, still route to agent
    # (agent can handle general conversation)
    if not intent:
        return "agent"
    
    # For now, all intents route to the agent node
    # Later, we can add specialized nodes and route based on intent:
    # if intent == "schedule_meeting":
    #     return "parameter_extractor"
    # elif intent == "query_events":
    #     return "query_handler"
    # etc.
    
    return "agent"


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
