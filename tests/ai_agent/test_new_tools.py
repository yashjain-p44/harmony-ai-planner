"""Test the new calendar tools."""

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


def test_tool(prompt: str, description: str):
    """Test a specific tool scenario."""
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"Prompt: {prompt}")
    print('='*60)
    
    app = create_agent()
    result = app.invoke({'messages': [HumanMessage(content=prompt)]})
    
    # Check if tool was called
    tool_called = False
    tool_name = None
    for msg in result['messages']:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            tool_called = True
            tool_name = msg.tool_calls[0].get('name')
            print(f"✓ Tool called: {tool_name}")
            break
    
    # Get final response
    final_msg = result['messages'][-1]
    if hasattr(final_msg, 'content') and final_msg.content:
        response_preview = final_msg.content[:200] + "..." if len(final_msg.content) > 200 else final_msg.content
        print(f"✓ Response: {response_preview}")
    
    return tool_called, tool_name


def run_tests():
    """Run tests for new tools."""
    print("\n" + "="*60)
    print("TESTING NEW CALENDAR TOOLS")
    print("="*60)
    
    tests = [
        ("Find available time slots for tomorrow between 9 AM and 5 PM", "Find available slots"),
        ("What free time do I have on December 16th from 10 AM to 4 PM?", "Find available slots (specific date)"),
        ("Create a calendar event called 'Team Meeting' tomorrow at 2 PM for 1 hour", "Create event"),
        ("Schedule a meeting titled 'Project Review' on December 20th at 3 PM", "Create event (specific date)"),
    ]
    
    results = []
    for prompt, description in tests:
        tool_used, tool_name = test_tool(prompt, description)
        results.append({
            'description': description,
            'tool_used': tool_used,
            'tool_name': tool_name
        })
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for result in results:
        status = "✓" if result['tool_used'] else "✗"
        print(f"{status} {result['description']}: {result['tool_name'] or 'No tool called'}")
    print("="*60)


if __name__ == "__main__":
    run_tests()
