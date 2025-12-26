"""Comprehensive test suite for AI agent with tools."""

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


def test_scenario(prompt: str, description: str):
    """Test a specific scenario."""
    print(f"\n{'='*60}")
    print(f"Test: {description}")
    print(f"Prompt: {prompt}")
    print('='*60)
    
    app = create_agent()
    result = app.invoke({'messages': [HumanMessage(content=prompt)]})
    
    # Check if tool was called
    tool_called = False
    for msg in result['messages']:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            tool_called = True
            print(f"✓ Tool called: {msg.tool_calls[0].get('name')}")
            break
    
    # Get final response
    final_msg = result['messages'][-1]
    if hasattr(final_msg, 'content') and final_msg.content:
        print(f"✓ Response received: {final_msg.content[:150]}...")
    
    return tool_called, final_msg.content if hasattr(final_msg, 'content') else ""


def run_tests():
    """Run comprehensive tests."""
    print("\n" + "="*60)
    print("COMPREHENSIVE AI AGENT TEST SUITE")
    print("="*60)
    
    tests = [
        ("Show me my calendar events", "Basic calendar query"),
        ("What events do I have today?", "Today's events query"),
        ("List my upcoming calendar events", "Upcoming events query"),
        ("Can you check my calendar?", "Simple calendar check"),
        ("Hello, how are you?", "Non-calendar query (should not use tool)"),
    ]
    
    results = []
    for prompt, description in tests:
        tool_used, response = test_scenario(prompt, description)
        results.append({
            'prompt': prompt,
            'tool_used': tool_used,
            'has_response': bool(response)
        })
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    tool_tests = sum(1 for r in results if r['tool_used'])
    print(f"Total tests: {len(results)}")
    print(f"Tool usage detected: {tool_tests}/{len(results)}")
    print(f"All tests have responses: {all(r['has_response'] for r in results)}")
    print("="*60)


if __name__ == "__main__":
    run_tests()
