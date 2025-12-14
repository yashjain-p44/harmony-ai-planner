"""
Flask API Application

RESTful API for scheduling events based on plan requirements.
"""

import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add src directory to path to import modules
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Add project root to path for ai_agent imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
project_root = os.path.abspath(project_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables from .env file
env_path = Path(project_root) / ".env"
load_dotenv(dotenv_path=env_path)

from scheduler_app import schedule_plan
from models.plan_requirement import PlanRequirement
from scheduler_engine import SchedulingResult
from app.ai_agent.run_agent import run_agent
from app.api.models import ChatRequest, ChatResponse
from pydantic import ValidationError


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration


def scheduling_result_to_dict(result: SchedulingResult) -> dict:
    """Convert SchedulingResult to dictionary for JSON response."""
    return {
        "success": result.success,
        "events_created": result.events_created,
        "event_ids": result.event_ids,
        "total_minutes_scheduled": result.total_minutes_scheduled,
        "remaining_minutes": result.remaining_minutes,
        "decision_log": [
            {
                "step": decision.step,
                "message": decision.message,
                "details": decision.details
            }
            for decision in result.decision_log
        ],
        "warnings": result.warnings,
        "errors": result.errors
    }


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "scheduler-api"
    }), 200


@app.route('/schedule', methods=['POST'])
def schedule():
    """
    Schedule events based on plan requirements.
    
    Request body should be a JSON object with:
    - plan_description: str
    - total_minutes_per_week: int
    - min_event_duration: int
    - max_event_duration: int
    - min_break: int
    - scheduling_window_days: int (optional, default: 7)
    - preferred_time_windows: list (optional)
    - calendar_id: str (optional, default: "primary")
    
    Returns:
        JSON response with scheduling result
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Validate and create PlanRequirement
        try:
            requirement = PlanRequirement(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Invalid plan requirement: {str(e)}"
            }), 400
        
        # Schedule the plan
        result = schedule_plan(requirement)
        
        # Convert result to dictionary
        response_data = scheduling_result_to_dict(result)
        
        # Return appropriate status code
        status_code = 200 if result.success else 500
        
        return jsonify(response_data), status_code
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/schedule/preview', methods=['POST'])
def schedule_preview():
    """
    Preview scheduling without creating calendar events.
    
    Same request body as /schedule, but returns what would be scheduled
    without actually creating events in the calendar.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        try:
            requirement = PlanRequirement(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Invalid plan requirement: {str(e)}"
            }), 400
        
        # TODO: Implement preview mode that doesn't create events
        # For now, this endpoint returns the same as /schedule
        # In the future, we could modify scheduler_engine to support preview mode
        
        return jsonify({
            "success": False,
            "error": "Preview mode not yet implemented"
        }), 501
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


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
                error=f"Validation error: {'; '.join(errors)}"
            ).model_dump()), 400
        
        # Run the agent with the validated prompt
        agent_response = run_agent(chat_request.prompt)
        
        # Create and return response using Pydantic model
        chat_response = ChatResponse(
            success=True,
            response=agent_response,
            prompt=chat_request.prompt
        )
        
        return jsonify(chat_response.model_dump()), 200
        
    except Exception as e:
        return jsonify(ChatResponse(
            success=False,
            response="",
            prompt="",
            error=f"Internal server error: {str(e)}"
        ).model_dump()), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
