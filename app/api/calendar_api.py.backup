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
from flasgger import Swagger

# Add src directory to path to import modules
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from calendar_repository import GoogleCalendarRepository


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api-docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Calendar API",
        "description": "RESTful API for direct calendar operations using Google Calendar",
        "version": "1.0.0",
        "contact": {
            "name": "API Support"
        }
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "tags": [
        {
            "name": "Health",
            "description": "Health check endpoints"
        },
        {
            "name": "Calendars",
            "description": "Calendar management endpoints"
        },
        {
            "name": "Events",
            "description": "Event management endpoints"
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

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
    """
    Health Check Endpoint
    ---
    tags:
      - Health
    summary: Check API health status
    description: Returns the health status of the Calendar API service
    responses:
      200:
        description: API is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            service:
              type: string
              example: calendar-api
    """
    return jsonify({
        "status": "healthy",
        "service": "calendar-api"
    }), 200


@app.route('/calendar/calendars', methods=['GET'])
def list_calendars():
    """
    List All Calendars
    ---
    tags:
      - Calendars
    summary: List all calendars accessible by the user
    description: Retrieves a list of all calendars that the authenticated user has access to
    responses:
      200:
        description: Successfully retrieved calendars
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            calendars:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: "primary"
                  summary:
                    type: string
                    example: "My Calendar"
                  description:
                    type: string
                    example: "My primary calendar"
            count:
              type: integer
              example: 1
      500:
        description: Server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to list calendars: ..."
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
    Get Calendar by ID
    ---
    tags:
      - Calendars
    summary: Get a specific calendar by ID
    description: Retrieves detailed information about a specific calendar
    parameters:
      - name: calendar_id
        in: path
        type: string
        required: true
        description: The ID of the calendar to retrieve
        example: "primary"
    responses:
      200:
        description: Successfully retrieved calendar
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            calendar:
              type: object
              properties:
                id:
                  type: string
                  example: "primary"
                summary:
                  type: string
                  example: "My Calendar"
      404:
        description: Calendar not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to get calendar: ..."
      500:
        description: Server error
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
    List Events
    ---
    tags:
      - Events
    summary: List events from a calendar
    description: Retrieves a list of events from the specified calendar with optional filtering
    parameters:
      - name: calendar_id
        in: query
        type: string
        required: false
        default: "primary"
        description: Calendar identifier
      - name: time_min
        in: query
        type: string
        required: false
        description: Lower bound for event start time (ISO format)
        example: "2024-01-01T00:00:00Z"
      - name: time_max
        in: query
        type: string
        required: false
        description: Upper bound for event end time (ISO format)
        example: "2024-12-31T23:59:59Z"
      - name: max_results
        in: query
        type: integer
        required: false
        default: 10
        description: Maximum number of events to return
      - name: single_events
        in: query
        type: boolean
        required: false
        default: true
        description: Whether to expand recurring events
      - name: order_by
        in: query
        type: string
        required: false
        default: "startTime"
        enum: ["startTime", "updated"]
        description: Order of events
    responses:
      200:
        description: Successfully retrieved events
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            events:
              type: array
              items:
                type: object
            count:
              type: integer
              example: 5
      400:
        description: Bad request - invalid parameters
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Invalid parameter: ..."
      500:
        description: Server error
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
    Get Event by ID
    ---
    tags:
      - Events
    summary: Get a specific event by ID
    description: Retrieves detailed information about a specific event
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
        description: The ID of the event to retrieve
        example: "abc123def456"
      - name: calendar_id
        in: query
        type: string
        required: false
        default: "primary"
        description: Calendar identifier
    responses:
      200:
        description: Successfully retrieved event
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            event:
              type: object
              properties:
                id:
                  type: string
                  example: "abc123def456"
                summary:
                  type: string
                  example: "Team Meeting"
      404:
        description: Event not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to get event: ..."
      500:
        description: Server error
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
    Create Event
    ---
    tags:
      - Events
    summary: Create a new calendar event
    description: Creates a new event in the specified calendar
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Event creation payload
        required: true
        schema:
          type: object
          required:
            - summary
            - start_time
          properties:
            summary:
              type: string
              description: Title of the event
              example: "Team Meeting"
            start_time:
              type: string
              format: date-time
              description: Start time in ISO format
              example: "2024-01-15T14:00:00Z"
            end_time:
              type: string
              format: date-time
              description: End time in ISO format (defaults to 1 hour after start)
              example: "2024-01-15T15:00:00Z"
            description:
              type: string
              description: Description of the event
              example: "Weekly team sync"
            location:
              type: string
              description: Location of the event
              example: "Conference Room A"
            attendees:
              type: array
              items:
                type: string
              description: List of attendee email addresses
              example: ["john@example.com", "jane@example.com"]
            calendar_id:
              type: string
              description: Calendar ID (default: "primary")
              example: "primary"
    responses:
      201:
        description: Event created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            event:
              type: object
              properties:
                id:
                  type: string
                  example: "abc123def456"
                summary:
                  type: string
                  example: "Team Meeting"
      400:
        description: Bad request - validation error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "summary is required"
      500:
        description: Server error
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
    Update Event
    ---
    tags:
      - Events
    summary: Update an existing calendar event
    description: Updates an existing event in the specified calendar. All fields are optional.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
        description: The ID of the event to update
        example: "abc123def456"
      - name: calendar_id
        in: query
        type: string
        required: false
        default: "primary"
        description: Calendar identifier
      - in: body
        name: body
        description: Event update payload
        required: true
        schema:
          type: object
          properties:
            summary:
              type: string
              description: New title of the event
              example: "Updated Team Meeting"
            start_time:
              type: string
              format: date-time
              description: New start time in ISO format
              example: "2024-01-15T15:00:00Z"
            end_time:
              type: string
              format: date-time
              description: New end time in ISO format
              example: "2024-01-15T16:00:00Z"
            description:
              type: string
              description: New description
              example: "Updated weekly team sync"
            location:
              type: string
              description: New location
              example: "Conference Room B"
            attendees:
              type: array
              items:
                type: string
              description: New list of attendee email addresses
              example: ["john@example.com"]
    responses:
      200:
        description: Event updated successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            event:
              type: object
              properties:
                id:
                  type: string
                  example: "abc123def456"
                summary:
                  type: string
                  example: "Updated Team Meeting"
      400:
        description: Bad request - validation error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Invalid datetime format: ..."
      404:
        description: Event not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to update event: ..."
      500:
        description: Server error
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
    Delete Event
    ---
    tags:
      - Events
    summary: Delete a calendar event
    description: Deletes an event from the specified calendar
    parameters:
      - name: event_id
        in: path
        type: string
        required: true
        description: The ID of the event to delete
        example: "abc123def456"
      - name: calendar_id
        in: query
        type: string
        required: false
        default: "primary"
        description: Calendar identifier
    responses:
      200:
        description: Event deleted successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Event abc123def456 deleted successfully"
      404:
        description: Event not found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Failed to delete event: ..."
      500:
        description: Server error
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
