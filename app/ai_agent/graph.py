"""Graph construction and configuration for LangGraph agents."""

from langgraph.graph import StateGraph, END

from app.ai_agent.state import AgentState
from app.ai_agent.nodes import agent_node, tool_node, intent_node
from app.ai_agent.router import should_continue, route_after_intent


def create_agent():
    """
    Create and compile a LangGraph agent with tool support.
    
    Returns:
        Compiled StateGraph ready to use
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("intent", intent_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Set entry point to intent classification
    workflow.set_entry_point("intent")
    
    # After intent classification, route to agent
    workflow.add_conditional_edges(
        "intent",
        route_after_intent,
        {
            "agent": "agent",
            "end": END
        }
    )
    
    # Add conditional edge: after agent, check if tools need to be executed
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # After tools execute, return to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    return workflow.compile()
