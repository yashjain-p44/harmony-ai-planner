"""Test script to verify tool access in the AI agent."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from langchain_core.messages import HumanMessage
from app.ai_agent.graph import create_agent


def test_tool_access():
    """Test if the agent can access calendar tools."""
    print("Testing AI Agent Tool Access")
    print("=" * 60)
    
    # Create the agent
    app = create_agent()
    
    # Test prompt that should trigger tool usage
    test_prompt = "Can you show me my calendar events for today?"
    
    print(f"\nUser: {test_prompt}")
    print("\nProcessing...")
    
    try:
        # Initialize state
        initial_state = {
            "messages": [HumanMessage(content=test_prompt)]
        }
        
        # Run the agent
        result = app.invoke(initial_state)
        
        # Display all messages to see tool calls and responses
        print("\n" + "=" * 60)
        print("Agent Execution Trace:")
        print("=" * 60)
        
        for i, msg in enumerate(result["messages"]):
            msg_type = type(msg).__name__
            print(f"\n[{i+1}] {msg_type}:")
            
            if msg_type == "HumanMessage":
                print(f"  Content: {msg.content}")
            elif msg_type == "AIMessage":
                print(f"  Content: {msg.content}")
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    print(f"  Tool Calls: {len(msg.tool_calls)}")
                    for tool_call in msg.tool_calls:
                        print(f"    - {tool_call.get('name')} with args: {tool_call.get('args')}")
            elif msg_type == "ToolMessage":
                print(f"  Tool: {msg.name if hasattr(msg, 'name') else 'Unknown'}")
                print(f"  Result: {msg.content[:200]}..." if len(msg.content) > 200 else f"  Result: {msg.content}")
        
        # Get final response
        final_message = result["messages"][-1]
        if hasattr(final_message, 'content'):
            print("\n" + "=" * 60)
            print("Final Response:")
            print("=" * 60)
            print(final_message.content)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_tool_access()
