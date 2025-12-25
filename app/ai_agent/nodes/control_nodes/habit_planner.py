"""Habit planning node - creates a plan for scheduling habits."""

from langchain_openai import ChatOpenAI
import json

from app.ai_agent.state import AgentState


def habit_planner(state: AgentState) -> AgentState:
    """
    Create a plan for habit scheduling.
    
    Reads: messages, intent_type
    Writes: plan (stored in habit_definition), plan_status, clarification_questions (stored in explanation_payload)
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    
    messages = state.get("messages", [])
    intent_type = state.get("intent_type", "UNKNOWN")
    
    if intent_type != "HABIT_SCHEDULE":
        return {
            "plan_status": "PLAN_INFEASIBLE",
            "habit_definition": {},
            "explanation_payload": {"reason": "Intent is not HABIT_SCHEDULE"}
        }
    
    # Extract user message
    user_message = ""
    for msg in reversed(messages):
        if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls'):
            user_message = msg.content
            break
    
    # Create planning prompt
    system_prompt = """You are a habit planning assistant. Analyze the user's request and create a structured plan.

Respond with a JSON object containing:
{
    "plan": {
        "habit_name": "string",
        "frequency": "daily/weekly/etc",
        "duration_minutes": number,
        "max_duration_minutes": number (optional, maximum duration for the habit session, default to 60 if not specified),
        "buffer_minutes": number (optional, minimum gap between consecutive events for this habit, default to 15 if not specified),
        "description": "string"
    },
    "plan_status": "PLAN_READY" | "NEEDS_CLARIFICATION" | "PLAN_INFEASIBLE",
    "clarification_questions": ["question1", "question2"] (only if plan_status is NEEDS_CLARIFICATION)
}

If information is missing or unclear, set plan_status to NEEDS_CLARIFICATION and provide clarification_questions.
If the request is impossible or contradictory, set plan_status to PLAN_INFEASIBLE.
If max_duration_minutes is not specified by the user, set it to 60.
If buffer_minutes is not specified by the user, set it to 15."""
    
    prompt = f"{system_prompt}\n\nUser request: {user_message}\n\nResponse (JSON only):"
    
    response = llm.invoke(prompt)
    response_text = response.content.strip()
    
    # Try to extract JSON from response
    try:
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        plan_data = json.loads(response_text)
        
        plan = plan_data.get("plan", {})
        plan_status = plan_data.get("plan_status", "PLAN_INFEASIBLE")
        clarification_questions = plan_data.get("clarification_questions", [])
        
        # Set default max_duration_minutes to 60 if not provided
        if "max_duration_minutes" not in plan:
            plan["max_duration_minutes"] = 60
        
        # Set default buffer_minutes to 15 if not provided
        if "buffer_minutes" not in plan:
            plan["buffer_minutes"] = 15
        
        result = {
            "habit_definition": plan,  # Store plan in habit_definition
            "plan_status": plan_status
        }
        
        if clarification_questions:
            result["explanation_payload"] = {"clarification_questions": clarification_questions}
        
        return result
    except (json.JSONDecodeError, KeyError) as e:
        # If parsing fails, mark as needing clarification
        return {
            "plan_status": "NEEDS_CLARIFICATION",
            "habit_definition": {},
            "explanation_payload": {
                "clarification_questions": ["Could you provide more details about the habit you'd like to schedule?"]
            }
        }