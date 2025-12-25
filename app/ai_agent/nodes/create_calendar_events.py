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
    
    # Check if this is a task or habit
    is_task = bool(task_definition)
    
    print(f"[create_calendar_events] ===== CREATE CALENDAR EVENTS START =====")
    print(f"[create_calendar_events] Event type: {'TASK' if is_task else 'HABIT'}")
    
    if is_task:
        event_name = task_definition.get("task_name", "Scheduled Task")
        description = task_definition.get("notes", "")
        priority = task_definition.get("priority", "MEDIUM")
        duration = task_definition.get("estimated_duration_minutes", 60)
        print(f"[create_calendar_events] Task details:")
        print(f"[create_calendar_events]   - Name: {event_name}")
        print(f"[create_calendar_events]   - Priority: {priority}")
        print(f"[create_calendar_events]   - Duration: {duration} minutes")
        print(f"[create_calendar_events]   - Description: {description[:100] if description else 'None'}...")
    else:
        event_name = habit_definition.get("habit_name", "Scheduled Habit")
        description = habit_definition.get("description", "")
        print(f"[create_calendar_events] Habit: {event_name}")
    
    print(f"[create_calendar_events] Number of slots to create events for: {len(selected_slots)}")
    if selected_slots:
        print(f"[create_calendar_events] First slot: {selected_slots[0].get('start', 'N/A')} to {selected_slots[0].get('end', 'N/A')}")
    
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
                print(f"[create_calendar_events] ✅ Successfully created event {i+1}/{len(selected_slots)}")
                print(f"[create_calendar_events]   - Event ID: {event_data.get('id', 'N/A')}")
                print(f"[create_calendar_events]   - Time: {event_data.get('start', 'N/A')} to {event_data.get('end', 'N/A')}")
                print(f"[create_calendar_events]   - Link: {event_data.get('htmlLink', 'N/A')}")
            else:
                # Tool returned an error, log it but continue with other slots
                error_msg = result.get("error", "Unknown error")
                print(f"[create_calendar_events] ❌ Failed to create event {i+1}/{len(selected_slots)}: {error_msg}")
                # In production, you might want to log this error
                continue
                
        except Exception as e:
            # If tool invocation fails, skip this slot and continue
            print(f"[create_calendar_events] ❌ Exception while creating event {i+1}/{len(selected_slots)}: {type(e).__name__}: {str(e)}")
            # In production, you might want to log this error
            continue
    
    print(f"[create_calendar_events] ===== CREATION SUMMARY =====")
    print(f"[create_calendar_events] Successfully created: {len(created_events)} out of {len(selected_slots)} events")
    if len(created_events) < len(selected_slots):
        print(f"[create_calendar_events] ⚠️  {len(selected_slots) - len(created_events)} event(s) failed to create")
    print(f"[create_calendar_events] ===== CREATE CALENDAR EVENTS END =====")
    return {"created_events": created_events}