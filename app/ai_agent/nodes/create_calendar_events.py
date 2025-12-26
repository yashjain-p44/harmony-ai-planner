"""Create calendar events node - creates events in calendar provider."""

import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict

from app.ai_agent.state import AgentState
from app.ai_agent.tools import create_calendar_event_tool


def create_calendar_events(state: AgentState) -> AgentState:
    """
    Create calendar events from selected slots.
    
    Reads: selected_slots
    Writes: created_events
    """
    print("[create_calendar_events] Starting to create calendar events...")
    selected_slots = state.get("selected_slots", [])
    habit_definition = state.get("habit_definition", {})
    task_definition = state.get("task_definition", {})
    intent_type = state.get("intent_type", "UNKNOWN")
    
    # Determine if this is a task or habit
    is_task = bool(task_definition) or intent_type == "TASK_SCHEDULE"
    
    if is_task:
        # For tasks: use task_name from task_definition
        event_name = task_definition.get("task_name", "Scheduled Task")
        description = task_definition.get("description", "")
        print(f"[create_calendar_events] Creating event for task: {event_name}")
    else:
        # For habits: use habit_name from habit_definition
        event_name = habit_definition.get("habit_name", "Scheduled Habit")
        description = habit_definition.get("description", "")
        print(f"[create_calendar_events] Creating events for habit: {event_name}")
    
    print(f"[create_calendar_events] Number of slots to create events for: {len(selected_slots)}")
    
    created_events: List[Dict] = []
    
    for i, slot in enumerate(selected_slots):
        start_time = slot.get("start")
        end_time = slot.get("end")
        
        if not start_time or not end_time:
            continue  # Skip invalid slots
        
        # Buffer is now a gap BETWEEN events, not part of the event duration
        # So slot start/end times are already the event start/end times
        print(f"[create_calendar_events] Processing slot {i+1}/{len(selected_slots)}: {start_time} to {end_time}")
        
        try:
            # Use the calendar tool to create the event
            result_json = create_calendar_event_tool.invoke({
                "summary": event_name,
                "start_time": start_time,
                "end_time": end_time,
                "description": description,
                "calendar_id": "primary"
            })
            
            # Parse the JSON response
            result = json.loads(result_json)
            
            if result.get("success", False):
                event_data = result.get("event", {})
                created_event = {
                    "id": event_data.get("id"),
                    "summary": event_data.get("summary", event_name),
                    "description": event_data.get("description", description),
                    "start": event_data.get("start"),
                    "end": event_data.get("end"),
                    "location": event_data.get("location", ""),
                    "htmlLink": event_data.get("htmlLink", ""),
                    "status": "confirmed"
                }
                created_events.append(created_event)
                print(f"[create_calendar_events] Successfully created event: {event_data.get('id')}")
            else:
                # Tool returned an error, log it but continue with other slots
                error_msg = result.get("error", "Unknown error")
                print(f"[create_calendar_events] Failed to create event: {error_msg}")
                # In production, you might want to log this error
                continue
                
        except Exception as e:
            # If tool invocation fails, skip this slot and continue
            print(f"[create_calendar_events] Exception while creating event: {str(e)}")
            # In production, you might want to log this error
            continue
    
    print(f"[create_calendar_events] Successfully created {len(created_events)} out of {len(selected_slots)} events")
    return {"created_events": created_events}