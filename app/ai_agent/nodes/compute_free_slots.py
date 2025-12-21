"""Compute free slots node - calculates available time windows."""

from datetime import datetime, timedelta, timezone
from typing import List, Dict

from app.ai_agent.state import AgentState


def compute_free_slots(state: AgentState) -> AgentState:
    """
    Compute free time slots from normalized calendar events.
    
    Reads: calendar_events_normalized, time_range (from planning_horizon)
    Writes: free_time_slots
    """
    normalized_events = state.get("calendar_events_normalized", [])
    planning_horizon = state.get("planning_horizon", {})
    
    # Get time range
    start_date = planning_horizon.get("start_date")
    end_date = planning_horizon.get("end_date")
    
    if not start_date:
        # Use UTC timezone for timezone-aware datetime
        start_date = datetime.now(timezone.utc)
    else:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        # Ensure timezone-aware
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
    
    if not end_date:
        end_date = start_date + timedelta(days=30)
    else:
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        # Ensure timezone-aware
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)
    
    # Convert events to datetime ranges
    busy_periods = []
    for event in normalized_events:
        try:
            event_start = datetime.fromisoformat(event["start"].replace("Z", "+00:00"))
            event_end = datetime.fromisoformat(event["end"].replace("Z", "+00:00"))
            busy_periods.append((event_start, event_end))
        except (ValueError, KeyError):
            continue
    
    # Sort busy periods by start time
    busy_periods.sort(key=lambda x: x[0])
    
    # Compute free slots
    free_slots: List[Dict] = []
    current_time = start_date
    
    # Round current_time to the nearest hour for cleaner slots
    current_time = current_time.replace(minute=0, second=0, microsecond=0)
    
    for busy_start, busy_end in busy_periods:
        # If there's a gap before this busy period, it's a free slot
        if current_time < busy_start:
            free_slots.append({
                "start": current_time.isoformat(),
                "end": busy_start.isoformat(),
                "duration_minutes": int((busy_start - current_time).total_seconds() / 60)
            })
        
        # Move current_time to after this busy period
        if busy_end > current_time:
            current_time = busy_end
    
    # Add final free slot if there's time remaining
    if current_time < end_date:
        free_slots.append({
            "start": current_time.isoformat(),
            "end": end_date.isoformat(),
            "duration_minutes": int((end_date - current_time).total_seconds() / 60)
        })
    
    # If no events, the entire range is free
    if not busy_periods:
        free_slots.append({
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "duration_minutes": int((end_date - start_date).total_seconds() / 60)
        })
    
    return {"free_time_slots": free_slots}