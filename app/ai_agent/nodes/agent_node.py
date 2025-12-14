"""Agent node implementation for processing conversation state."""

from langchain_openai import ChatOpenAI

from app.ai_agent.state import AgentState


def agent_node(state: AgentState) -> AgentState:
    """
    Single node that processes the conversation state.
    
    Args:
        state: Current state containing messages
        
    Returns:
        Updated state with AI response
    """
    # Initialize the LLM (you'll need to set OPENAI_API_KEY environment variable)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # Get the last human message
    messages = state["messages"]
    
    # Generate response using the LLM
    response = llm.invoke(messages)
    
    # Add the AI response to the messages
    return {"messages": messages + [response]}
