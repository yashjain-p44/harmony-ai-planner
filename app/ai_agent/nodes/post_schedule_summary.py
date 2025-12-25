"""Post schedule summary node - creates summary message after scheduling."""

from datetime import datetime
from langchain_core.messages import AIMessage
from typing import List, Dict

from app.ai_agent.state import AgentState


def post_schedule_summary(state: AgentState) -> AgentState:
    """
    Create a summary message after scheduling events.
    
    Reads: created_events, habit_definition, task_definition
    Writes: messages (append assistant summary)
    """
    messages = state.get("messages", [])
    created_events = state.get("created_events", [])
    habit_definition = state.get("habit_definition", {})
    task_definition = state.get("task_definition", {})
    
    # Check if this is a task or habit
    is_task = bool(task_definition)
    
    if is_task:
        item_name = task_definition.get("task_name", "task")
    else:
        item_name = habit_definition.get("habit_name", "habit")
    
    if not created_events:
        summary_text = f"I wasn't able to schedule any events for {item_name}. Please check your calendar availability."
    else:
        num_events = len(created_events)
        summary_text = f"Successfully scheduled {num_events} event(s) for {item_name}:\n\n"
        
        for idx, event in enumerate(created_events, 1):
            start_time = event.get("start", "Unknown time")
            end_time = event.get("end", "")
            # Format the time nicely
            try:
                if isinstance(start_time, str):
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    if end_time:
                        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        summary_text += f"{idx}. {event.get('summary', item_name)} - {start_dt.strftime('%Y-%m-%d %H:%M')} to {end_dt.strftime('%H:%M')}\n"
                    else:
                        summary_text += f"{idx}. {event.get('summary', item_name)} - {start_dt.strftime('%Y-%m-%d %H:%M')}\n"
                else:
                    summary_text += f"{idx}. {event.get('summary', item_name)} - {start_time}\n"
            except:
                summary_text += f"{idx}. {event.get('summary', item_name)} - {start_time}\n"
    
    summary_message = AIMessage(content=summary_text)
    
    return {"messages": messages + [summary_message]}