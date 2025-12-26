"""Task analyzer node - extracts minimal task information from user request."""

from langchain_openai import ChatOpenAI
import json
from datetime import datetime, timedelta

from app.ai_agent.state import AgentState


def task_analyzer(state: AgentState) -> AgentState:
    """
    Analyze task request to extract minimal task information.
    
    Reads: messages, intent_type
    Writes: task_definition (with task_name, estimated_time_minutes, description), plan_status
    """
    print("=" * 50)
    print("Task Analyzer: Starting task analysis")
    print("=" * 50)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    
    messages = state.get("messages", [])
    intent_type = state.get("intent_type", "UNKNOWN")
    
    print(f"Task Analyzer: Intent type = {intent_type}")
    
    if intent_type != "TASK_SCHEDULE":
        print(f"Task Analyzer: Intent mismatch. Expected TASK_SCHEDULE, got {intent_type}")
        return {
            "plan_status": "PLAN_INFEASIBLE",
            "task_definition": {},
            "explanation_payload": {"reason": "Intent is not TASK_SCHEDULE"}
        }
    
    # Extract user message
    user_message = ""
    for msg in reversed(messages):
        if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls'):
            user_message = msg.content
            break
    
    print(f"Task Analyzer: User message = {user_message}")
    
    # Get current date for context
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_day_name = today.strftime("%A")
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    tomorrow_day_name = tomorrow.strftime("%A")
    
    print(f"Task Analyzer: Today is {today_day_name}, {today_str}")
    print(f"Task Analyzer: Tomorrow is {tomorrow_day_name}, {tomorrow_str}")
    
    # Create simplified task analysis prompt - only extract essentials
    system_prompt = f"""You are a task analysis assistant. Analyze the user's task request and extract only the essential information needed for scheduling.

CURRENT DATE CONTEXT:
- Today is {today_day_name}, {today_str}
- Tomorrow is {tomorrow_day_name}, {tomorrow_str}

Use this date context to understand temporal references in the user's request (e.g., "tonight" means today's evening, "tomorrow" means {tomorrow_str}).

Respond with a JSON object containing:
{{
    "task": {{
        "task_name": "string (brief description of the task, e.g., 'Dinner', 'Team meeting', 'Review documents')",
        "estimated_time_minutes": number (estimated time required to complete the task in minutes),
        "description": "string (optional - detailed description if helpful, otherwise can be empty string)"
    }},
    "plan_status": "PLAN_READY" | "NEEDS_CLARIFICATION" | "PLAN_INFEASIBLE",
    "clarification_questions": ["question1", "question2"] (only if plan_status is NEEDS_CLARIFICATION)
}}

For estimated_time_minutes:
- Extract time estimates from phrases like "30 minutes", "1 hour", "2 hours", "half an hour", "1hr", etc.
- If no time is mentioned, make a reasonable estimate based on the task type:
  * Quick tasks (emails, calls): 15-30 minutes
  * Standard tasks (meetings, reviews): 30-60 minutes
  * Complex tasks (deep work, projects): 1-3 hours
  * Events (dinner, activities): 1-2 hours
- Be reasonable - if user says "1hr for dinner", extract 60 minutes

For task_name:
- Create a brief, descriptive name (2-5 words)
- Use the task type or activity mentioned
- Examples: "Dinner", "Team meeting", "Review documents", "Exercise", "Doctor appointment"

For description:
- Only include if it adds meaningful context
- Can be empty string if task_name is self-explanatory
- Keep it concise (1-2 sentences max)

If information is missing or unclear (especially estimated_time_minutes), set plan_status to NEEDS_CLARIFICATION and provide clarification_questions.
If the request is impossible or contradictory, set plan_status to PLAN_INFEASIBLE.

IMPORTANT: Do NOT extract scheduling preferences (when, what time, which days) - those will be understood directly from the user's original message during slot selection."""
    
    prompt = f"{system_prompt}\n\nUser request: {user_message}\n\nResponse (JSON only):"
    
    print("Task Analyzer: Invoking LLM for task analysis...")
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
    except Exception as e:
        # Handle LLM invocation errors (network, API, timeout, etc.)
        print(f"Task Analyzer: Error invoking LLM - {type(e).__name__}: {e}")
        print("Task Analyzer: Returning NEEDS_CLARIFICATION status due to LLM error")
        print("=" * 50)
        return {
            "plan_status": "NEEDS_CLARIFICATION",
            "task_definition": {},
            "explanation_payload": {
                "clarification_questions": ["I encountered an error processing your request. Could you please try again or rephrase your request?"]
            }
        }
    
    print(f"Task Analyzer: LLM response = {response_text}")
    
    # Try to extract JSON from response
    try:
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        task_data = json.loads(response_text)
        print(f"Task Analyzer: Parsed task data = {task_data}")
        
        task = task_data.get("task", {})
        plan_status = task_data.get("plan_status", "PLAN_INFEASIBLE")
        clarification_questions = task_data.get("clarification_questions", [])
        
        print(f"Task Analyzer: Plan status = {plan_status}")
        print(f"Task Analyzer: Task name = {task.get('task_name', 'N/A')}")
        print(f"Task Analyzer: Estimated time (minutes) = {task.get('estimated_time_minutes', 'N/A')}")
        print(f"Task Analyzer: Description = {task.get('description', 'N/A')}")
        
        # Validate and set defaults
        if "estimated_time_minutes" not in task or task["estimated_time_minutes"] <= 0:
            print(f"Task Analyzer: Estimated time invalid or missing ({task.get('estimated_time_minutes', 'N/A')}), setting default to 30 minutes")
            task["estimated_time_minutes"] = 30  # Default to 30 minutes if not specified or invalid
        
        # Set default description to empty string if not present
        if "description" not in task:
            task["description"] = ""
            print("Task Analyzer: Description not specified, set to empty string")
        
        result = {
            "task_definition": task,
            "plan_status": plan_status
        }
        
        if clarification_questions:
            print(f"Task Analyzer: Clarification questions = {clarification_questions}")
            result["explanation_payload"] = {"clarification_questions": clarification_questions}
        
        print(f"Task Analyzer: Final task definition = {task}")
        print("Task Analyzer: Task analysis complete")
        print("=" * 50)
        
        return result
    except (json.JSONDecodeError, KeyError) as e:
        # If parsing fails, mark as needing clarification
        print(f"Task Analyzer: Error parsing JSON response - {type(e).__name__}: {e}")
        print(f"Task Analyzer: Raw response text = {response_text}")
        print("Task Analyzer: Returning NEEDS_CLARIFICATION status")
        print("=" * 50)
        return {
            "plan_status": "NEEDS_CLARIFICATION",
            "task_definition": {},
            "explanation_payload": {
                "clarification_questions": ["Could you provide more details about the task you'd like to schedule? Please include the task name and estimated time required."]
            }
        }

