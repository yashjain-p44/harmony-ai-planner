"""
Flask API Application

RESTful API for AI agent chat interface and calendar operations.
Combines chat/AI agent endpoints with direct calendar management endpoints.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flasgger import Swagger
from googleapiclient.errors import HttpError

# Add project root to path for ai_agent imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
project_root = os.path.abspath(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add src directory to path for calendar repository
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Load environment variables from .env file
env_path = Path(project_root) / ".env"
load_dotenv(dotenv_path=env_path)

from app.ai_agent.graph import create_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from app.api.models import ChatRequest, ChatResponse
from pydantic import ValidationError
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
        "title": "Scheduler AI Agent API",
        "description": "RESTful API for AI agent chat interface with calendar integration and direct calendar operations",
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
            "name": "Chat",
            "description": "AI agent chat endpoints"
        },
        {
            "name": "Calendars",
            "description": "Calendar management endpoints"
        },
        {
            "name": "Events",
            "description": "Event management endpoints"
        }
    ],
    "definitions": {
        "AgentState": {
            "type": "object",
            "description": "Complete agent state containing conversation history and approval status",
            "required": ["messages", "needs_approval_from_human"],
            "properties": {
                "messages": {
                    "type": "array",
                    "description": "List of all messages in the conversation (HumanMessage, AIMessage, ToolMessage)",
                    "items": {
                        "$ref": "#/definitions/Message"
                    }
                },
                "needs_approval_from_human": {
                    "type": "boolean",
                    "description": "Whether the agent needs human approval before executing actions",
                    "example": False
                }
            }
        },
        "Message": {
            "type": "object",
            "description": "A message in the conversation. Can be HumanMessage, AIMessage, or ToolMessage",
            "required": ["type", "content"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["HumanMessage", "AIMessage", "ToolMessage"],
                    "description": "Type of message",
                    "example": "AIMessage"
                },
                "content": {
                    "type": "string",
                    "description": "Message content",
                    "example": "I've scheduled a meeting with John tomorrow at 2pm."
                },
                "tool_calls": {
                    "type": "array",
                    "description": "Tool calls made by the AI (only for AIMessage)",
                    "items": {
                        "$ref": "#/definitions/ToolCall"
                    }
                },
                "tool_call_id": {
                    "type": "string",
                    "description": "ID of the tool call this message responds to (only for ToolMessage)",
                    "example": "call_abc123"
                }
            }
        },
        "ToolCall": {
            "type": "object",
            "description": "A tool call made by the AI agent",
            "required": ["name", "args", "id"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the tool being called",
                    "example": "create_calendar_event"
                },
                "args": {
                    "type": "object",
                    "description": "Arguments passed to the tool",
                    "additionalProperties": True,
                    "example": {
                        "summary": "Team Meeting",
                        "start_time": "2024-01-15T14:00:00Z"
                    }
                },
                "id": {
                    "type": "string",
                    "description": "Unique identifier for this tool call",
                    "example": "call_abc123"
                }
            }
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Initialize calendar repository (handle auth errors gracefully)
try:
    calendar_repo = GoogleCalendarRepository()
except Exception as e:
    print(f"Warning: Could not initialize calendar repository: {e}")
    print("Calendar endpoints will not be available. Chat endpoints should still work.")
    calendar_repo = None


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


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health Check Endpoint
    ---
    tags:
      - Health
    summary: Check API health status
    description: Returns the health status of the API service
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
              example: scheduler-api
    """
    return jsonify({
        "status": "healthy",
        "service": "scheduler-api"
    }), 200


@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat with the AI Agent
    ---
    tags:
      - Chat
    summary: Send a message to the AI agent
    description: |
      Chat with the AI agent. The agent can help with calendar management,
      scheduling, and other tasks. Supports conversation state management
      for human-in-the-loop scenarios.
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Chat request payload
        required: true
        schema:
          type: object
          required:
            - prompt
          properties:
            prompt:
              type: string
              minLength: 1
              maxLength: 10000
              description: The user's message/prompt to send to the AI agent
              example: "Schedule a meeting with John tomorrow at 2pm"
            state:
              type: object
              description: Previous agent state to resume from (for human-in-the-loop scenarios)
              properties:
                messages:
                  type: array
                  description: List of messages in the conversation
                  items:
                    $ref: '#/definitions/Message'
                needs_approval_from_human:
                  type: boolean
                  description: Whether human approval is needed
                  example: false
              example:
                messages:
                  - type: "HumanMessage"
                    content: "Schedule a meeting"
                  - type: "AIMessage"
                    content: "I can help you schedule a meeting."
                needs_approval_from_human: false
    responses:
      200:
        description: Successful response from the AI agent
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            response:
              type: string
              description: The AI agent's response
              example: "I've scheduled a meeting with John tomorrow at 2pm."
            prompt:
              type: string
              description: The original user prompt
              example: "Schedule a meeting with John tomorrow at 2pm"
            messages:
              type: array
              description: Complete list of messages from the agent state
              items:
                $ref: '#/definitions/Message'
            needs_approval_from_human:
              type: boolean
              description: Whether the agent needs human approval before continuing
              example: false
            state:
              $ref: '#/definitions/AgentState'
              description: Full agent state (returned when needs_approval_from_human is True or always for conversation continuity)
              nullable: true
            error:
              type: string
              nullable: true
              description: Error message if success is False
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
              example: "Validation error: prompt: Field required"
            response:
              type: string
              example: ""
            prompt:
              type: string
              example: ""
            messages:
              type: array
              items:
                $ref: '#/definitions/Message'
            needs_approval_from_human:
              type: boolean
              example: false
            state:
              $ref: '#/definitions/AgentState'
              nullable: true
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            error:
              type: string
              example: "Internal server error: An unexpected error occurred"
            response:
              type: string
              example: ""
            prompt:
              type: string
              example: ""
            messages:
              type: array
              items:
                $ref: '#/definitions/Message'
            needs_approval_from_human:
              type: boolean
              example: false
            state:
              $ref: '#/definitions/AgentState'
              nullable: true
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify(ChatResponse(
                success=False,
                response="",
                prompt="",
                messages=[],
                needs_approval_from_human=False,
                state=None,
                error="No JSON data provided"
            ).model_dump()), 400
        
        # Validate request using Pydantic model
        try:
            chat_request = ChatRequest(**data)
        except ValidationError as e:
            # Return validation errors in a user-friendly format
            errors = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                errors.append(f"{field}: {message}")
            
            return jsonify(ChatResponse(
                success=False,
                response="",
                prompt=data.get("prompt", ""),
                messages=[],
                needs_approval_from_human=False,
                state=None,
                error=f"Validation error: {'; '.join(errors)}"
            ).model_dump()), 400
        
        # Run the agent and get full state
        app = create_agent()
        
        # Prepare initial state - either resume from provided state or create new
        if chat_request.state:
            # Resume from previous state
            # The frontend already appends the new user message to the state,
            # so we use the state as-is
            # Reconstruct messages from state dict
            messages = []
            for msg_dict in chat_request.state.get("messages", []):
                msg_type = msg_dict.get("type", "")
                content = msg_dict.get("content", "")
                
                if msg_type == "HumanMessage":
                    messages.append(HumanMessage(content=content))
                elif msg_type == "AIMessage":
                    msg = AIMessage(content=content)
                    # Restore tool calls if present
                    if "tool_calls" in msg_dict:
                        msg.tool_calls = msg_dict["tool_calls"]
                    messages.append(msg)
                elif msg_type == "ToolMessage":
                    tool_call_id = msg_dict.get("tool_call_id", "")
                    messages.append(ToolMessage(content=content, tool_call_id=tool_call_id))
            
            # Check if the last message is already the user's prompt (frontend appended it)
            # If not, append it for backward compatibility
            if not messages or not isinstance(messages[-1], HumanMessage) or messages[-1].content != chat_request.prompt:
                messages.append(HumanMessage(content=chat_request.prompt))
            
            initial_state = {
                "messages": messages,
                "needs_approval_from_human": chat_request.state.get("needs_approval_from_human", False)
            }
            # Merge any existing state fields
            for key, value in chat_request.state.items():
                if key not in ["messages", "needs_approval_from_human"]:
                    initial_state[key] = value
        else:
            # New conversation
            initial_state = {
                "messages": [HumanMessage(content=chat_request.prompt)],
                "needs_approval_from_human": False
            }
        
        # Merge approval fields from request into state (if provided)
        if chat_request.approval_state is not None:
            initial_state["approval_state"] = chat_request.approval_state
        if chat_request.approval_feedback is not None:
            initial_state["approval_feedback"] = chat_request.approval_feedback
        
        result = app.invoke(initial_state)
        
        # Check approval state
        approval_state = result.get("approval_state")
        approval_summary = result.get("explanation_payload") if approval_state == "PENDING" else None
        needs_approval = result.get("needs_approval_from_human", False) or approval_state == "PENDING"
        
        if needs_approval:
            # Format state for response
            formatted_messages = []
            for msg in result["messages"]:
                msg_dict = {
                    "type": type(msg).__name__,
                    "content": getattr(msg, 'content', ''),
                }
                
                # Add tool calls if present
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "name": tc.get("name"),
                            "args": tc.get("args", {}),
                            "id": tc.get("id")
                        }
                        for tc in msg.tool_calls
                    ]
                
                # Add tool call ID for ToolMessage
                if hasattr(msg, 'tool_call_id'):
                    msg_dict["tool_call_id"] = msg.tool_call_id
                
                formatted_messages.append(msg_dict)
            
            # Format state dict for response
            state_dict = {
                "messages": formatted_messages,
                "needs_approval_from_human": result.get("needs_approval_from_human", False)
            }
            # Include approval state in state dict
            if approval_state:
                state_dict["approval_state"] = approval_state
            if approval_feedback := result.get("approval_feedback"):
                state_dict["approval_feedback"] = approval_feedback
            
            # Extract the last response for display
            agent_response = ""
            if result["messages"]:
                last_message = result["messages"][-1]
                if isinstance(last_message, AIMessage):
                    agent_response = last_message.content or ""
            
            # If no response from messages, generate one based on approval state
            if not agent_response:
                if approval_state == "PENDING":
                    agent_response = "I've found some time slots for your schedule. Please review and approve below."
                elif approval_state == "APPROVED":
                    agent_response = "Great! I'm creating the calendar events now."
                elif approval_state == "REJECTED":
                    agent_response = "I understand. The scheduling has been cancelled."
                elif approval_state == "CHANGES_REQUESTED":
                    agent_response = "I'll adjust the schedule based on your feedback."
                else:
                    # Try to get response from explanation_payload if available
                    explanation = result.get("explanation_payload", {})
                    if isinstance(explanation, dict):
                        agent_response = explanation.get("message") or explanation.get("summary") or "Request processed."
                    else:
                        agent_response = "Request processed."
            
            # Return early with state
            chat_response = ChatResponse(
                success=True,
                response=agent_response,
                prompt=chat_request.prompt,
                messages=formatted_messages,
                needs_approval_from_human=True,
                approval_state=approval_state,
                approval_summary=approval_summary,
                state=state_dict
            )
            
            return jsonify(chat_response.model_dump()), 200
        
        # Extract the final response
        agent_response = ""
        if result["messages"]:
            last_message = result["messages"][-1]
            if isinstance(last_message, AIMessage):
                agent_response = last_message.content or ""
        
        # If no response from messages, generate one based on state
        if not agent_response:
            approval_state = result.get("approval_state")
            if approval_state == "PENDING":
                agent_response = "I've found some time slots for your schedule. Please review and approve below."
            elif approval_state == "APPROVED":
                agent_response = "Great! I'm creating the calendar events now."
            elif approval_state == "REJECTED":
                agent_response = "I understand. The scheduling has been cancelled."
            elif approval_state == "CHANGES_REQUESTED":
                agent_response = "I'll adjust the schedule based on your feedback."
            else:
                # Try to get response from explanation_payload if available
                explanation = result.get("explanation_payload", {})
                if isinstance(explanation, dict):
                    agent_response = explanation.get("message") or explanation.get("summary") or "Request processed."
                else:
                    agent_response = "Request processed."
        
        # Format messages for response
        formatted_messages = []
        for msg in result["messages"]:
            msg_dict = {
                "type": type(msg).__name__,
                "content": getattr(msg, 'content', ''),
            }
            
            # Add tool calls if present
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                msg_dict["tool_calls"] = [
                    {
                        "name": tc.get("name"),
                        "args": tc.get("args", {}),
                        "id": tc.get("id")
                    }
                    for tc in msg.tool_calls
                ]
            
            # Add tool call ID for ToolMessage
            if hasattr(msg, 'tool_call_id'):
                msg_dict["tool_call_id"] = msg.tool_call_id
            
            formatted_messages.append(msg_dict)
        
        # Format state dict for response (always return state for frontend to maintain conversation)
        state_dict = {
            "messages": formatted_messages,
            "needs_approval_from_human": result.get("needs_approval_from_human", False)
        }
        # Include approval state in state dict if present
        if approval_state:
            state_dict["approval_state"] = approval_state
        if approval_feedback := result.get("approval_feedback"):
            state_dict["approval_feedback"] = approval_feedback
        
        # Create and return response using Pydantic model
        chat_response = ChatResponse(
            success=True,
            response=agent_response,
            prompt=chat_request.prompt,
            messages=formatted_messages,
            needs_approval_from_human=result.get("needs_approval_from_human", False),
            approval_state=approval_state,
            approval_summary=approval_summary,
            state=state_dict  # Always return state so frontend can maintain full conversation
        )
        
        return jsonify(chat_response.model_dump()), 200
        
    except Exception as e:
        return jsonify(ChatResponse(
            success=False,
            response="",
            prompt="",
            messages=[],
            needs_approval_from_human=False,
            state=None,
            error=f"Internal server error: {str(e)}"
        ).model_dump()), 500


# ============================================================================
# CALENDAR API ENDPOINTS
# ============================================================================

@app.route('/calendar/health', methods=['GET'])
def calendar_health_check():
    """
    Calendar Health Check Endpoint
    ---
    tags:
      - Health
    summary: Check Calendar API health status
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
    if calendar_repo is None:
        return jsonify({
            "success": False,
            "error": "Calendar repository not initialized. Please check Google Calendar authentication."
        }), 503
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
    if calendar_repo is None:
        return jsonify({
            "success": False,
            "error": "Calendar repository not initialized. Please check Google Calendar authentication."
        }), 503
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
    app.run(debug=True, host='0.0.0.0', port=5002)
