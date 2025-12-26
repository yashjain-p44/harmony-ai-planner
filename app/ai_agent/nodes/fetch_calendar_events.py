"""Fetch calendar events node - retrieves events from calendar provider."""

import json
from datetime import datetime, timedelta, timezone
from typing import List, Dict

from app.ai_agent.state import AgentState
from app.ai_agent.tools import get_calendar_events_tool


def fetch_calendar_events(state: AgentState) -> AgentState:
    """
    Fetch calendar events from the calendar provider.
    
    Reads: time_range (from planning_horizon)
    Writes: calendar_events_raw
    """
    print("=" * 50)
    print("Fetch Calendar Events: Starting to fetch calendar events")
    print("=" * 50)
    
    planning_horizon = state.get("planning_horizon", {})
    print(f"Fetch Calendar Events: Planning horizon = {planning_horizon}")
    
    # Extract time range from planning_horizon
    # Default to next 30 days if not specified
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
    
    print(f"Fetch Calendar Events: Start date = {start_date}")
    print(f"Fetch Calendar Events: End date = {end_date}")
    print(f"Fetch Calendar Events: Time range = {end_date - start_date}")
    
    # Use the calendar tool to fetch events
    try:
        # Format dates as ISO strings for the tool
        time_min = start_date.isoformat()
        time_max = end_date.isoformat()
        
        print(f"Fetch Calendar Events: Invoking calendar tool...")
        print(f"Fetch Calendar Events: time_min = {time_min}")
        print(f"Fetch Calendar Events: time_max = {time_max}")
        
        # Invoke the tool directly
        result_json = get_calendar_events_tool.invoke({
            "calendar_id": "primary",
            "max_results": 250,  # Get all events in range
            "time_min": time_min,
            "time_max": time_max
        })
        
        # Parse the JSON response
        result = json.loads(result_json)
        
        if result.get("success", False):
            # Convert tool response format to raw events format
            tool_events = result.get("events", [])
            print(f"Fetch Calendar Events: Successfully fetched {len(tool_events)} events from calendar")
            raw_events: List[Dict] = []
            
            for event in tool_events:
                # The tool returns start/end as strings (ISO format)
                # Convert to the format expected by normalize_calendar_events
                start_str = event.get("start", "")
                end_str = event.get("end", "")
                
                # Determine if it's a dateTime or date (all-day event)
                start_dict = {}
                end_dict = {}
                
                if start_str:
                    if "T" in start_str:
                        # Has time component - it's a dateTime
                        start_dict["dateTime"] = start_str
                    else:
                        # No time component - it's an all-day event
                        start_dict["date"] = start_str
                
                if end_str:
                    if "T" in end_str:
                        # Has time component - it's a dateTime
                        end_dict["dateTime"] = end_str
                    else:
                        # No time component - it's an all-day event
                        end_dict["date"] = end_str
                
                raw_event = {
                    "id": event.get("id"),
                    "summary": event.get("summary", "No title"),
                    "start": start_dict,
                    "end": end_dict,
                    "description": event.get("description", ""),
                    "location": event.get("location", "")
                }
                raw_events.append(raw_event)
            
            print(f"Fetch Calendar Events: Converted {len(raw_events)} events to raw format")
            print(f"Fetch Calendar Events: Sample events (first 3):")
            for i, event in enumerate(raw_events[:3]):
                print(f"  Event {i+1}: {event.get('summary', 'No title')} from {event.get('start', {})} to {event.get('end', {})}")
            print("Fetch Calendar Events: Calendar fetch complete")
            print("=" * 50)
            return {"calendar_events_raw": raw_events}
        else:
            # Tool returned an error, return empty list
            error_msg = result.get("error", "Unknown error")
            print(f"Fetch Calendar Events: Tool returned error: {error_msg}")
            print("Fetch Calendar Events: Returning empty events list")
            print("=" * 50)
            return {"calendar_events_raw": []}
            
    except Exception as e:
        # If tool invocation fails, return empty list
        # In production, you might want to log this error
        print(f"Fetch Calendar Events: Exception occurred - {type(e).__name__}: {str(e)}")
        import traceback
        print(f"Fetch Calendar Events: Traceback:\n{traceback.format_exc()}")
        print("Fetch Calendar Events: Returning empty events list")
        print("=" * 50)
        return {"calendar_events_raw": []}