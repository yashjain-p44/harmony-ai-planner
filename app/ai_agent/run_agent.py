"""Simple single node LangGraph agent implementation."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path to allow imports when running directly
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables from .env file
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from langchain_core.messages import HumanMessage, AIMessage

from app.ai_agent.graph import create_agent


def run_agent(user_input: str) -> str:
    """
    Run the agent with a user input.
    
    Args:
        user_input: The user's message
        
    Returns:
        The agent's response
    """
    # Create the agent
    app = create_agent()
    
    # Initialize state with user message
    initial_state = {
        "messages": [HumanMessage(content=user_input)]
    }
    
    # Run the agent
    result = app.invoke(initial_state)
    
    # Extract and return the last AI message
    if result["messages"]:
        last_message = result["messages"][-1]
        if isinstance(last_message, AIMessage):
            return last_message.content
    
    return "No response generated."


if __name__ == "__main__":
    # Example usage
    print("Simple LangGraph Agent")
    print("=" * 50)
    
    # Example: Run the agent with a simple query
    try:
        response = run_agent("Hello! Can you tell me a fun fact?")
        print(f"\nUser: Hello! Can you tell me a fun fact?")
        print(f"Agent: {response}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure you have set the OPENAI_API_KEY environment variable.")
