"""Tool execution node for processing tool calls."""

import json
from langchain_core.messages import ToolMessage

from app.ai_agent.state import AgentState
from app.ai_agent.tools import (
    get_calendar_events_tool,
    create_calendar_event_tool,
    find_available_slots_tool
)


def tool_node(state: AgentState) -> AgentState:
    """
    Execute tool calls from the last AI message.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with tool results
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Get tool calls from the last message
    tool_calls = last_message.tool_calls if hasattr(last_message, 'tool_calls') else []
    
    tool_messages = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_call_id = tool_call.get("id")
        
        # Execute the appropriate tool
        print(f"Executing tool: {tool_name}")
        if tool_name == "get_calendar_events_tool":
            result = get_calendar_events_tool.invoke(tool_args)
        elif tool_name == "create_calendar_event_tool":
            result = create_calendar_event_tool.invoke(tool_args)
        elif tool_name == "find_available_slots_tool":
            result = find_available_slots_tool.invoke(tool_args)
        else:
            result = f"Unknown tool: {tool_name}"
        
        # Create tool message with result
        tool_message = ToolMessage(
            content=str(result),
            tool_call_id=tool_call_id
        )
        tool_messages.append(tool_message)
    
    return {"messages": messages + tool_messages}
