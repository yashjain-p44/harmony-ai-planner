"""Graph construction and configuration for LangGraph agents."""

from langgraph.graph import StateGraph, END

from app.ai_agent.state import AgentState
from app.ai_agent.nodes import agent_node


def create_agent():
    """
    Create and compile a simple single-node LangGraph agent.
    
    Returns:
        Compiled StateGraph ready to use
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add the single agent node
    workflow.add_node("agent", agent_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Connect agent to END
    workflow.add_edge("agent", END)
    
    # Compile the graph
    return workflow.compile()
