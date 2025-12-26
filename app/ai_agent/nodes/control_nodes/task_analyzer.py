"""Task analyzer node - extracts task priority and estimated time from user request."""

from langchain_openai import ChatOpenAI
import json

from app.ai_agent.state import AgentState


def task_analyzer(state: AgentState) -> AgentState:
    """
    Analyze task request to extract priority and estimated time.
    
    Reads: messages, intent_type
    Writes: task_definition (with priority and estimated_time_minutes), plan_status
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
    
    # Create task analysis prompt
    system_prompt = """You are a task analysis assistant. Analyze the user's task request and extract key information.

Respond with a JSON object containing:
{
    "task": {
        "task_name": "string (brief description of the task)",
        "priority": "HIGH" | "MEDIUM" | "LOW" (based on urgency and importance),
        "estimated_time_minutes": number (estimated time required to complete the task in minutes),
        "description": "string (detailed description of the task)"
    },
    "plan_status": "PLAN_READY" | "NEEDS_CLARIFICATION" | "PLAN_INFEASIBLE",
    "clarification_questions": ["question1", "question2"] (only if plan_status is NEEDS_CLARIFICATION)
}

Priority guidelines:
- HIGH: Urgent tasks, deadlines, important meetings, critical work
- MEDIUM: Regular tasks, moderate importance, flexible deadlines
- LOW: Nice-to-have tasks, low urgency, can be deferred

For estimated_time_minutes:
- Extract time estimates from phrases like "30 minutes", "1 hour", "2 hours", "half an hour", etc.
- If no time is mentioned, make a reasonable estimate based on the task type
- Common task durations: quick tasks (15-30 min), standard tasks (30-60 min), complex tasks (1-3 hours), projects (3+ hours)

If information is missing or unclear, set plan_status to NEEDS_CLARIFICATION and provide clarification_questions.
If the request is impossible or contradictory, set plan_status to PLAN_INFEASIBLE."""
    
    prompt = f"{system_prompt}\n\nUser request: {user_message}\n\nResponse (JSON only):"
    
    print("Task Analyzer: Invoking LLM for task analysis...")
    response = llm.invoke(prompt)
    response_text = response.content.strip()
    
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
        print(f"Task Analyzer: Priority = {task.get('priority', 'N/A')}")
        print(f"Task Analyzer: Estimated time (minutes) = {task.get('estimated_time_minutes', 'N/A')}")
        
        # Validate and set defaults
        if "priority" not in task:
            print("Task Analyzer: Priority not found, setting default to MEDIUM")
            task["priority"] = "MEDIUM"  # Default priority
        
        if "estimated_time_minutes" not in task or task["estimated_time_minutes"] <= 0:
            print(f"Task Analyzer: Estimated time invalid or missing ({task.get('estimated_time_minutes', 'N/A')}), setting default to 30 minutes")
            task["estimated_time_minutes"] = 30  # Default to 30 minutes if not specified or invalid
        
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
                "clarification_questions": ["Could you provide more details about the task you'd like to schedule? Please include the task name, priority (if any), and estimated time required."]
            }
        }

