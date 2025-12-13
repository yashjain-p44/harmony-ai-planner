"""
Calendar API

RESTful API for direct calendar operations using GoogleCalendarRepository.
Provides endpoints for managing calendars and events.
"""

import sys
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from googleapiclient.errors import HttpError

# Add src directory to path to import modules
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from calendar_repository import GoogleCalendarRepository


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize calendar repository
calendar_repo = GoogleCalendarRepository()


def parse_datetime(dt_str: str) -> datetime:
    """Parse ISO format datetime string to datetime object."""
    try:
        # Try parsing with timezone
        if 'Z' in dt_str:
            dt_str = dt_str.replace('Z', '+00:00')
        return datetime.fromisoformat(dt_str)
    except ValueError:
        # Try parsing without timezone (assume UTC)
        try:
            dt = datetime.fromisoformat(dt_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt
        except ValueError:
            raise ValueError(f"Invalid datetime format: {dt_str}")


@app.route('/calendar/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "calendar-api"
    }), 200


@app.route('/calendar/calendars', methods=['GET'])
def list_calendars():
    """
    List all calendars accessible by the user.
    
    Returns:
        JSON response with list of calendars
    """
    try:
        calendars = calendar_repo.list_calendars()
        return jsonify({
            "success": True,
            "calendars": calendars,
            "count": len(calendars)
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list calendars: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/calendar/calendars/<calendar_id>', methods=['GET'])
def get_calendar(calendar_id: str):
    """
    Get a specific calendar by ID.
    
    Args:
        calendar_id: The ID of the calendar to retrieve
    
    Returns:
        JSON response with calendar details
    """
    try:
        calendar = calendar_repo.get_calendar(calendar_id)
        return jsonify({
            "success": True,
            "calendar": calendar
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get calendar: {str(e)}"
        }), 404 if e.resp.status == 404 else 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/calendar/events', methods=['GET'])
def list_events():
    """
    List events from a calendar.
    
    Query parameters:
        calendar_id: Calendar identifier (default: "primary")
        time_min: Lower bound for event start time (ISO format, optional)
        time_max: Upper bound for event end time (ISO format, optional)
        max_results: Maximum number of events (default: 10)
        single_events: Whether to expand recurring events (default: true)
        order_by: Order of events (default: "startTime")
    
    Returns:
        JSON response with list of events
    """
    try:
        calendar_id = request.args.get('calendar_id', 'primary')
        max_results = int(request.args.get('max_results', 10))
        single_events = request.args.get('single_events', 'true').lower() == 'true'
        order_by = request.args.get('order_by', 'startTime')
        
        time_min = None
        time_max = None
        
        if request.args.get('time_min'):
            time_min = parse_datetime(request.args.get('time_min'))
        if request.args.get('time_max'):
            time_max = parse_datetime(request.args.get('time_max'))
        
        events = calendar_repo.list_events(
            calendar_id=calendar_id,
            time_min=time_min,
            time_max=time_max,
            max_results=max_results,
            single_events=single_events,
            order_by=order_by
        )
        
        return jsonify({
            "success": True,
            "events": events,
            "count": len(events)
        }), 200
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Invalid parameter: {str(e)}"
        }), 400
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list events: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/calendar/events/<event_id>', methods=['GET'])
def get_event(event_id: str):
    """
    Get a specific event by ID.
    
    Query parameters:
        calendar_id: Calendar identifier (default: "primary")
    
    Args:
        event_id: The ID of the event to retrieve
    
    Returns:
        JSON response with event details
    """
    try:
        calendar_id = request.args.get('calendar_id', 'primary')
        event = calendar_repo.get_event(event_id, calendar_id)
        return jsonify({
            "success": True,
            "event": event
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get event: {str(e)}"
        }), 404 if e.resp.status == 404 else 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/calendar/events', methods=['POST'])
def create_event():
    """
    Create a new calendar event.
    
    Request body should be a JSON object with:
    - summary: str (required) - Title of the event
    - start_time: str (required) - Start time in ISO format
    - end_time: str (optional) - End time in ISO format (defaults to 1 hour after start)
    - description: str (optional) - Description of the event
    - location: str (optional) - Location of the event
    - attendees: list[str] (optional) - List of attendee email addresses
    - calendar_id: str (optional) - Calendar ID (default: "primary")
    - Additional event properties can be passed as extra fields
    
    Returns:
        JSON response with created event
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        if 'summary' not in data:
            return jsonify({
                "success": False,
                "error": "summary is required"
            }), 400
        
        if 'start_time' not in data:
            return jsonify({
                "success": False,
                "error": "start_time is required"
            }), 400
        
        # Parse datetime strings
        start_time = parse_datetime(data['start_time'])
        end_time = None
        if 'end_time' in data:
            end_time = parse_datetime(data['end_time'])
        
        # Extract additional kwargs (any fields not in the standard parameters)
        standard_fields = {'summary', 'start_time', 'end_time', 'description', 
                          'location', 'attendees', 'calendar_id'}
        kwargs = {k: v for k, v in data.items() if k not in standard_fields}
        
        event = calendar_repo.create_event(
            summary=data['summary'],
            start_time=start_time,
            end_time=end_time,
            description=data.get('description'),
            location=data.get('location'),
            attendees=data.get('attendees'),
            calendar_id=data.get('calendar_id', 'primary'),
            **kwargs
        )
        
        return jsonify({
            "success": True,
            "event": event
        }), 201
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Invalid datetime format: {str(e)}"
        }), 400
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to create event: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/calendar/events/<event_id>', methods=['PUT', 'PATCH'])
def update_event(event_id: str):
    """
    Update an existing calendar event.
    
    Query parameters:
        calendar_id: Calendar identifier (default: "primary")
    
    Request body should be a JSON object with any of:
    - summary: str - New title of the event
    - start_time: str - New start time in ISO format
    - end_time: str - New end time in ISO format
    - description: str - New description
    - location: str - New location
    - attendees: list[str] - New list of attendee email addresses
    - Additional event properties can be passed as extra fields
    
    Returns:
        JSON response with updated event
    """
    try:
        data = request.get_json()
        calendar_id = request.args.get('calendar_id', data.get('calendar_id', 'primary'))
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Parse datetime strings if provided
        start_time = None
        end_time = None
        if 'start_time' in data:
            start_time = parse_datetime(data['start_time'])
        if 'end_time' in data:
            end_time = parse_datetime(data['end_time'])
        
        # Extract additional kwargs
        standard_fields = {'summary', 'start_time', 'end_time', 'description', 
                          'location', 'attendees', 'calendar_id'}
        kwargs = {k: v for k, v in data.items() if k not in standard_fields}
        
        event = calendar_repo.update_event(
            event_id=event_id,
            calendar_id=calendar_id,
            summary=data.get('summary'),
            start_time=start_time,
            end_time=end_time,
            description=data.get('description'),
            location=data.get('location'),
            attendees=data.get('attendees'),
            **kwargs
        )
        
        return jsonify({
            "success": True,
            "event": event
        }), 200
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Invalid datetime format: {str(e)}"
        }), 400
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to update event: {str(e)}"
        }), 404 if e.resp.status == 404 else 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/calendar/events/<event_id>', methods=['DELETE'])
def delete_event(event_id: str):
    """
    Delete a calendar event.
    
    Query parameters:
        calendar_id: Calendar identifier (default: "primary")
    
    Args:
        event_id: The ID of the event to delete
    
    Returns:
        JSON response confirming deletion
    """
    try:
        calendar_id = request.args.get('calendar_id', 'primary')
        calendar_repo.delete_event(event_id, calendar_id)
        return jsonify({
            "success": True,
            "message": f"Event {event_id} deleted successfully"
        }), 200
    except HttpError as e:
        return jsonify({
            "success": False,
            "error": f"Failed to delete event: {str(e)}"
        }), 404 if e.resp.status == 404 else 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
