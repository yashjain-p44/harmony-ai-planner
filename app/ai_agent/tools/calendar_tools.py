"""Calendar tools for the AI agent."""

import sys
import os
from pathlib import Path
from typing import Optional, List
from langchain_core.tools import tool

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add src to path
src_path = os.path.join(project_root, "app", "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from calendar_repository import GoogleCalendarRepository
from time_slot_finder import TimeSlotFinder

# Initialize calendar repository (singleton pattern)
_calendar_repo = None

def get_calendar_repository():
    """Get or create calendar repository instance."""
    global _calendar_repo
    if _calendar_repo is None:
        _calendar_repo = GoogleCalendarRepository()
    return _calendar_repo


@tool
def get_calendar_events_tool(
    calendar_id: str = "primary",
    max_results: int = 10,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None
) -> str:
    """
    Get calendar events from a specified calendar.
    
    Args:
        calendar_id: Calendar identifier (default: "primary")
        max_results: Maximum number of events to return (default: 10)
        time_min: Lower bound for event start time in ISO format (optional)
        time_max: Upper bound for event end time in ISO format (optional)
    
    Returns:
        JSON string containing list of events with their details
    """
    try:
        import json
        import datetime
        
        repo = get_calendar_repository()
        
        # Parse datetime strings if provided
        time_min_dt = None
        time_max_dt = None
        
        if time_min:
            time_min_dt = datetime.datetime.fromisoformat(time_min.replace('Z', '+00:00'))
        if time_max:
            time_max_dt = datetime.datetime.fromisoformat(time_max.replace('Z', '+00:00'))
        
        events = repo.list_events(
            calendar_id=calendar_id,
            time_min=time_min_dt,
            time_max=time_max_dt,
            max_results=max_results,
            single_events=True,
            order_by="startTime"
        )
        
        # Format events for response
        formatted_events = []
        for event in events:
            formatted_event = {
                "id": event.get("id"),
                "summary": event.get("summary", "No title"),
                "start": event.get("start", {}).get("dateTime") or event.get("start", {}).get("date"),
                "end": event.get("end", {}).get("dateTime") or event.get("end", {}).get("date"),
                "description": event.get("description", ""),
                "location": event.get("location", "")
            }
            formatted_events.append(formatted_event)
        
        return json.dumps({
            "success": True,
            "count": len(formatted_events),
            "events": formatted_events
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def create_calendar_event_tool(
    summary: str,
    start_time: str,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    calendar_id: str = "primary"
) -> str:
    """
    Create a new calendar event.
    
    Args:
        summary: Title/summary of the event (required)
        start_time: Start time of the event in ISO format (required, e.g., "2025-12-15T10:00:00+05:30")
        end_time: End time of the event in ISO format (optional, defaults to 1 hour after start_time)
        description: Description of the event (optional)
        location: Location of the event (optional)
        attendees: List of attendee email addresses (optional)
        calendar_id: Calendar identifier (default: "primary")
    
    Returns:
        JSON string containing the created event details
    """
    try:
        import json
        import datetime
        
        repo = get_calendar_repository()
        
        # Parse datetime strings
        start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = None
        if end_time:
            end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # Create the event
        created_event = repo.create_event(
            summary=summary,
            start_time=start_dt,
            end_time=end_dt,
            description=description,
            location=location,
            attendees=attendees,
            calendar_id=calendar_id
        )
        
        # Format response
        formatted_event = {
            "id": created_event.get("id"),
            "summary": created_event.get("summary"),
            "start": created_event.get("start", {}).get("dateTime") or created_event.get("start", {}).get("date"),
            "end": created_event.get("end", {}).get("dateTime") or created_event.get("end", {}).get("date"),
            "description": created_event.get("description", ""),
            "location": created_event.get("location", ""),
            "htmlLink": created_event.get("htmlLink", "")
        }
        
        return json.dumps({
            "success": True,
            "message": "Event created successfully",
            "event": formatted_event
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


@tool
def find_available_slots_tool(
    start_time: str,
    end_time: str,
    min_duration_minutes: int = 30,
    calendar_id: str = "primary"
) -> str:
    """
    Find available time slots in a calendar within a specified time range.
    
    Args:
        start_time: Start of the time window to search in ISO format (required, e.g., "2025-12-15T09:00:00+05:30")
        end_time: End of the time window to search in ISO format (required, e.g., "2025-12-15T17:00:00+05:30")
        min_duration_minutes: Minimum duration required for a slot in minutes (default: 30)
        calendar_id: Calendar identifier (default: "primary")
    
    Returns:
        JSON string containing list of available time slots
    """
    try:
        import json
        import datetime
        
        repo = get_calendar_repository()
        
        # Parse datetime strings
        start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        # Get existing events in the time range
        existing_events = repo.list_events(
            calendar_id=calendar_id,
            time_min=start_dt,
            time_max=end_dt,
            max_results=250,  # Get all events in range
            single_events=True,
            order_by="startTime"
        )
        
        # Use TimeSlotFinder to find free slots
        slot_finder = TimeSlotFinder(
            existing_events=existing_events,
            start_time=start_dt,
            end_time=end_dt
        )
        
        free_slots = slot_finder.find_free_slots(min_duration_minutes=min_duration_minutes)
        
        # Format slots for response
        formatted_slots = []
        for slot in free_slots:
            formatted_slots.append({
                "start": slot.start.isoformat(),
                "end": slot.end.isoformat(),
                "duration_minutes": slot.duration_minutes
            })
        
        return json.dumps({
            "success": True,
            "count": len(formatted_slots),
            "slots": formatted_slots,
            "time_range": {
                "start": start_time,
                "end": end_time
            },
            "min_duration_minutes": min_duration_minutes
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })
