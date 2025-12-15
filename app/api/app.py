"""
Flask API Application

RESTful API for AI agent chat interface.
"""

import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flasgger import Swagger

# Add project root to path for ai_agent imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
project_root = os.path.abspath(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables from .env file
env_path = Path(project_root) / ".env"
load_dotenv(dotenv_path=env_path)

from app.ai_agent.graph import create_agent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from app.api.models import ChatRequest, ChatResponse
from pydantic import ValidationError


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
        "description": "RESTful API for AI agent chat interface with calendar integration",
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
        else:
            # New conversation
            initial_state = {
                "messages": [HumanMessage(content=chat_request.prompt)],
                "needs_approval_from_human": False
            }
        
        result = app.invoke(initial_state)
        
        # Check if human approval is needed
        needs_approval = result.get("needs_approval_from_human", False)
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
            
            # Extract the last response for display
            agent_response = ""
            if result["messages"]:
                last_message = result["messages"][-1]
                if isinstance(last_message, AIMessage):
                    agent_response = last_message.content or ""
            
            # Return early with state
            chat_response = ChatResponse(
                success=True,
                response=agent_response,
                prompt=chat_request.prompt,
                messages=formatted_messages,
                needs_approval_from_human=True,
                state=state_dict
            )
            
            return jsonify(chat_response.model_dump()), 200
        
        # Extract the final response
        agent_response = ""
        if result["messages"]:
            last_message = result["messages"][-1]
            if isinstance(last_message, AIMessage):
                agent_response = last_message.content or ""
        
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
        
        # Create and return response using Pydantic model
        chat_response = ChatResponse(
            success=True,
            response=agent_response,
            prompt=chat_request.prompt,
            messages=formatted_messages,
            needs_approval_from_human=result.get("needs_approval_from_human", False),
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
