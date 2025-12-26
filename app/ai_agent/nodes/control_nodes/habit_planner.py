"""Habit planning node - creates a plan for scheduling habits."""

from langchain_openai import ChatOpenAI
import json
from datetime import datetime, timedelta

from app.ai_agent.state import AgentState


def habit_planner(state: AgentState) -> AgentState:
    """
    Create a plan for habit scheduling.
    
    Reads: messages, intent_type
    Writes: plan (stored in habit_definition), plan_status, clarification_questions (stored in explanation_payload)
    """
    print("=" * 50)
    print("Habit Planner: Starting habit planning")
    print("=" * 50)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    
    messages = state.get("messages", [])
    intent_type = state.get("intent_type", "UNKNOWN")
    
    print(f"Habit Planner: Intent type = {intent_type}")
    
    if intent_type != "HABIT_SCHEDULE":
        print(f"Habit Planner: Intent mismatch. Expected HABIT_SCHEDULE, got {intent_type}")
        print("=" * 50)
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
    
    print(f"Habit Planner: User message = {user_message}")
    
    # Get current date and time for context
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_day_name = today.strftime("%A")
    today_time = today.strftime("%H:%M:%S")
    today_datetime = today.strftime("%Y-%m-%d %H:%M:%S")
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    tomorrow_day_name = tomorrow.strftime("%A")
    
    print(f"Habit Planner: Today is {today_day_name}, {today_str} at {today_time}")
    print(f"Habit Planner: Tomorrow is {tomorrow_day_name}, {tomorrow_str}")
    
    # Create planning prompt
    system_prompt = f"""You are a habit planning assistant. Analyze the user's request and create a structured plan.

CURRENT DATE AND TIME CONTEXT:
- Current date and time: {today_datetime} ({today_day_name})
- Today is {today_day_name}, {today_str}
- Current time: {today_time}
- Tomorrow is {tomorrow_day_name}, {tomorrow_str}

Use this date and time context to understand temporal references in the user's request (e.g., "starting today", "for 2 weeks", "every Monday").

Respond with a JSON object containing:
{{
    "plan": {{
        "habit_name": "string",
        "frequency": "daily/weekly/etc",
        "duration_minutes": number,
        "max_duration_minutes": number (optional, maximum duration for the habit session, default to 60 if not specified),
        "buffer_minutes": number (optional, minimum gap between consecutive events for this habit, default to 15 if not specified),
        "num_occurrences": number (optional, total number of events to schedule. For example: "2 weeks" with daily frequency = 14, "1 month" with weekly frequency = 4. If not specified, defaults based on frequency: daily=7, weekly=1, twice_weekly=2),
        "description": "string"
    }},
    "plan_status": "PLAN_READY" | "NEEDS_CLARIFICATION" | "PLAN_INFEASIBLE",
    "clarification_questions": ["question1", "question2"] (only if plan_status is NEEDS_CLARIFICATION)
}}

If information is missing or unclear, set plan_status to NEEDS_CLARIFICATION and provide clarification_questions.
If the request is impossible or contradictory, set plan_status to PLAN_INFEASIBLE.
If max_duration_minutes is not specified by the user, set it to 60.
If buffer_minutes is not specified by the user, set it to 15.
Extract num_occurrences from user requests like "for 2 weeks", "for 1 month", "for 10 days", etc. If the user says "schedule daily for 2 weeks", set num_occurrences to 14 (2 weeks × 7 days)."""
    
    prompt = f"{system_prompt}\n\nUser request: {user_message}\n\nResponse (JSON only):"
    
    print(f"Habit Planner: Prompt created (length: {len(prompt)} characters)")
    print("Habit Planner: Invoking LLM for habit planning...")
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
    except Exception as e:
        # Handle LLM invocation errors (network, API, timeout, etc.)
        print(f"Habit Planner: Error invoking LLM - {type(e).__name__}: {e}")
        print("Habit Planner: Returning NEEDS_CLARIFICATION status due to LLM error")
        print("=" * 50)
        return {
            "plan_status": "NEEDS_CLARIFICATION",
            "habit_definition": {},
            "explanation_payload": {
                "clarification_questions": ["I encountered an error processing your request. Could you please try again or rephrase your request?"]
            }
        }
    
    print(f"Habit Planner: LLM response = {response_text}")
    
    # Try to extract JSON from response
    try:
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        plan_data = json.loads(response_text)
        print(f"Habit Planner: Parsed plan data = {plan_data}")
        
        plan = plan_data.get("plan", {})
        plan_status = plan_data.get("plan_status", "PLAN_INFEASIBLE")
        clarification_questions = plan_data.get("clarification_questions", [])
        
        print(f"Habit Planner: Plan status = {plan_status}")
        print(f"Habit Planner: Habit name = {plan.get('habit_name', 'N/A')}")
        print(f"Habit Planner: Frequency = {plan.get('frequency', 'N/A')}")
        print(f"Habit Planner: Duration (minutes) = {plan.get('duration_minutes', 'N/A')}")
        
        # Set default max_duration_minutes to 60 if not provided
        if "max_duration_minutes" not in plan:
            plan["max_duration_minutes"] = 60
            print("Habit Planner: max_duration_minutes not specified, set to default 60")
        else:
            print(f"Habit Planner: max_duration_minutes = {plan.get('max_duration_minutes')}")
        
        # Set default buffer_minutes to 15 if not provided
        if "buffer_minutes" not in plan:
            plan["buffer_minutes"] = 15
            print("Habit Planner: buffer_minutes not specified, set to default 15")
        else:
            print(f"Habit Planner: buffer_minutes = {plan.get('buffer_minutes')}")
        
        # Set default num_occurrences based on frequency if not provided
        if "num_occurrences" not in plan:
            frequency = plan.get("frequency", "daily")
            if frequency == "daily":
                plan["num_occurrences"] = 7  # Default to 1 week
            elif frequency == "weekly":
                plan["num_occurrences"] = 1  # Default to 1 occurrence
            elif frequency == "twice_weekly":
                plan["num_occurrences"] = 2  # Default to 2 occurrences
            else:
                plan["num_occurrences"] = 1  # Default fallback
            print(f"Habit Planner: num_occurrences not specified, set to default {plan['num_occurrences']} based on frequency '{frequency}'")
        else:
            print(f"Habit Planner: num_occurrences = {plan.get('num_occurrences')}")
        
        result = {
            "habit_definition": plan,  # Store plan in habit_definition
            "plan_status": plan_status
        }
        
        if clarification_questions:
            print(f"Habit Planner: Clarification questions = {clarification_questions}")
            result["explanation_payload"] = {"clarification_questions": clarification_questions}
        
        print(f"Habit Planner: Final habit definition = {plan}")
        print("Habit Planner: Habit planning complete")
        print("=" * 50)
        
        return result
    except (json.JSONDecodeError, KeyError) as e:
        # If parsing fails, mark as needing clarification
        print(f"Habit Planner: Error parsing JSON response - {type(e).__name__}: {e}")
        print(f"Habit Planner: Raw response text = {response_text}")
        print("Habit Planner: Returning NEEDS_CLARIFICATION status")
        print("=" * 50)
        return {
            "plan_status": "NEEDS_CLARIFICATION",
            "habit_definition": {},
            "explanation_payload": {
                "clarification_questions": ["Could you provide more details about the habit you'd like to schedule?"]
            }
        }