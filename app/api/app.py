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


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "scheduler-api"
    }), 200


@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat with the AI agent.
    
    Request body should be a JSON object with:
    - prompt: str (the user's message/prompt, 1-10000 characters)
    
    Returns:
        JSON response with the agent's response following ChatResponse model
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
