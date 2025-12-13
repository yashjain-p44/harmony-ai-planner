"""
Flask API Application

RESTful API for scheduling events based on plan requirements.
"""

import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add src directory to path to import modules
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from scheduler_app import schedule_plan
from models.plan_requirement import PlanRequirement
from scheduler_engine import SchedulingResult


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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
