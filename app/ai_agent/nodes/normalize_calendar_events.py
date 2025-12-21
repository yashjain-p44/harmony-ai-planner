"""Normalize calendar events node - standardizes event format and timezone."""

from datetime import datetime
from typing import List, Dict

from app.ai_agent.state import AgentState


def normalize_calendar_events(state: AgentState) -> AgentState:
    """
    Normalize calendar events to a standard format with timezone alignment.
    
    Reads: calendar_events_raw
    Writes: calendar_events_normalized
    """
    print("[normalize_calendar_events] Starting to normalize calendar events...")
    raw_events = state.get("calendar_events_raw", [])
    print(f"[normalize_calendar_events] Number of raw events to normalize: {len(raw_events)}")
    
    normalized_events: List[Dict] = []
    skipped_count = 0
    
    for event in raw_events:
        # Extract and normalize event data
        event_id = event.get("id", "")
        summary = event.get("summary", "Untitled Event")
        
        # Normalize start time
        start_data = event.get("start", {})
        if "dateTime" in start_data:
            start_time = start_data["dateTime"]
        elif "date" in start_data:
            # All-day event
            start_time = f"{start_data['date']}T00:00:00Z"
        else:
            skipped_count += 1
            continue  # Skip invalid events
        
        # Normalize end time
        end_data = event.get("end", {})
        if "dateTime" in end_data:
            end_time = end_data["dateTime"]
        elif "date" in end_data:
            end_time = f"{end_data['date']}T23:59:59Z"
        else:
            skipped_count += 1
            continue  # Skip invalid events
        
        # Create normalized event
        normalized_event = {
            "id": event_id,
            "summary": summary,
            "start": start_time,
            "end": end_time,
            "timezone": start_data.get("timeZone", "UTC")
        }
        
        normalized_events.append(normalized_event)
    
    print(f"[normalize_calendar_events] Normalized {len(normalized_events)} events (skipped {skipped_count} invalid events)")
    return {"calendar_events_normalized": normalized_events}