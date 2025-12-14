"""Agent node implementation for processing conversation state."""

from langchain_openai import ChatOpenAI

from app.ai_agent.state import AgentState
from app.ai_agent.tools import (
    get_calendar_events_tool,
    create_calendar_event_tool,
    find_available_slots_tool
)


def agent_node(state: AgentState) -> AgentState:
    """
    Single node that processes the conversation state.
    
    Args:
        state: Current state containing messages
        
    Returns:
        Updated state with AI response (may include tool calls)
    """
    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # Bind tools to the LLM
    tools = [
        get_calendar_events_tool,
        create_calendar_event_tool,
        find_available_slots_tool
    ]
    llm_with_tools = llm.bind_tools(tools)
    
    # Get messages from state
    messages = state["messages"]
    
    # Generate response using the LLM (may include tool calls)
    response = llm_with_tools.invoke(messages)
    
    # Add the AI response to the messages
    return {"messages": messages + [response]}
