"""Post schedule summary node - creates summary message after scheduling."""

from langchain_core.messages import AIMessage
from typing import List, Dict

from app.ai_agent.state import AgentState


def post_schedule_summary(state: AgentState) -> AgentState:
    """
    Create a summary message after scheduling events.
    
    Reads: created_events
    Writes: messages (append assistant summary)
    """
    messages = state.get("messages", [])
    created_events = state.get("created_events", [])
    habit_definition = state.get("habit_definition", {})
    
    habit_name = habit_definition.get("habit_name", "habit")
    
    if not created_events:
        summary_text = f"I wasn't able to schedule any events for {habit_name}. Please check your calendar availability."
    else:
        num_events = len(created_events)
        summary_text = f"Successfully scheduled {num_events} event(s) for {habit_name}:\n\n"
        
        for idx, event in enumerate(created_events, 1):
            start_time = event.get("start", "Unknown time")
            summary_text += f"{idx}. {event.get('summary', habit_name)} - {start_time}\n"
    
    summary_message = AIMessage(content=summary_text)
    
    return {"messages": messages + [summary_message]}