"""Update task due date node - updates task due date if it's in the past."""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai_agent.state import AgentState


def update_task_due_date(state: AgentState) -> AgentState:
    """
    Update task due date if it's in the past, using LLM to determine best new due date.
    
    Reads: task_definition (with due date, priority, estimated_duration_minutes)
    Writes: task_definition (with updated due date), messages (append update message)
    
    If due date is in the future, passes through unchanged.
    """
    print("[update_task_due_date] ===== UPDATE TASK DUE DATE START =====")
    
    task_definition = state.get("task_definition", {})
    messages = state.get("messages", [])
    
    if not task_definition:
        print("[update_task_due_date] No task definition found, passing through")
        return {}
    
    task_name = task_definition.get("task_name", "")
    task_id = task_definition.get("task_id")
    current_due = task_definition.get("due")
    priority = task_definition.get("priority", "MEDIUM")
    estimated_duration = task_definition.get("estimated_duration_minutes", 60)
    task_notes = task_definition.get("notes", "")
    
    print(f"[update_task_due_date] Task: {task_name}")
    print(f"[update_task_due_date] Current due date: {current_due or 'Not set'}")
    print(f"[update_task_due_date] Priority: {priority}")
    print(f"[update_task_due_date] Estimated duration: {estimated_duration} minutes")
    
    # Check if due date exists and is in the past
    is_past_due = False
    original_due_date = None
    
    if current_due:
        try:
            # Parse the due date (handle both RFC3339 and ISO formats)
            due_str = current_due.replace('Z', '+00:00') if 'Z' in current_due else current_due
            original_due_date = datetime.fromisoformat(due_str)
            now = datetime.now(timezone.utc)
            # Compare dates (ignore time for date comparison)
            if original_due_date.date() < now.date():
                is_past_due = True
                print(f"[update_task_due_date] ⚠️  DUE DATE IS IN THE PAST: {original_due_date.date()} < {now.date()}")
            else:
                print(f"[update_task_due_date] ✅ Due date is in the future: {original_due_date.date()}")
        except (ValueError, AttributeError) as e:
            print(f"[update_task_due_date] Could not parse due date '{current_due}': {e}")
            is_past_due = False
    else:
        print("[update_task_due_date] No due date set, passing through")
    
    # If due date is in the future or not set, pass through unchanged
    if not is_past_due:
        print("[update_task_due_date] ===== UPDATE TASK DUE DATE END (PASS THROUGH) =====")
        return {}
    
    # Use LLM to determine the best new due date
    print("[update_task_due_date] Using LLM to determine best new due date...")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    # Build context for LLM
    task_context = f"Task: {task_name}"
    if task_notes:
        task_context += f"\nNotes: {task_notes}"
    task_context += f"\nPriority: {priority}"
    task_context += f"\nEstimated duration: {estimated_duration} minutes"
    task_context += f"\nOriginal due date (past): {original_due_date.date() if original_due_date else current_due}"
    
    system_prompt = """You are a task scheduling assistant. Given a task with a past due date, determine the best new due date based on:
1. Task priority (HIGH, MEDIUM, LOW)
2. Estimated time required to complete the task
3. Current date and reasonable scheduling expectations

Guidelines:
- HIGH priority tasks: Should be scheduled within 1-3 days from today
- MEDIUM priority tasks: Should be scheduled within 3-7 days from today
- LOW priority tasks: Should be scheduled within 7-14 days from today
- Consider the estimated duration - longer tasks may need more buffer time
- Be realistic about what can be accomplished

Respond with a JSON object containing:
{
    "new_due_date": "<ISO date string in YYYY-MM-DD format>",
    "reasoning": "Brief explanation of why this due date was chosen"
}"""
    
    prompt = f"""{system_prompt}

{task_context}

Current date: {datetime.now(timezone.utc).date()}

Determine the best new due date (JSON only):"""
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        new_due_date_str = result.get("new_due_date")
        reasoning = result.get("reasoning", "")
        
        if new_due_date_str:
            try:
                # Parse the new due date (expecting YYYY-MM-DD format)
                new_due_date = datetime.fromisoformat(new_due_date_str).replace(tzinfo=timezone.utc)
                # Convert to RFC3339 format for Google Tasks API
                new_due_date_rfc3339 = new_due_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                print(f"[update_task_due_date] ===== LLM DUE DATE SUGGESTION =====")
                print(f"[update_task_due_date] New due date: {new_due_date.date()}")
                print(f"[update_task_due_date] Reasoning: {reasoning}")
                
                # Update task definition with new due date
                updated_task_definition = task_definition.copy()
                updated_task_definition["due"] = new_due_date_rfc3339
                updated_task_definition["original_due"] = current_due  # Keep original for reference
                updated_task_definition["needs_due_date_update"] = True
                
                # Create a message about the update
                update_message = f"Updated due date for '{task_name}' from {original_due_date.date() if original_due_date else 'past'} to {new_due_date.date()}. {reasoning}"
                update_ai_message = AIMessage(content=update_message)
                
                print(f"[update_task_due_date] ===== UPDATE TASK DUE DATE END =====")
                
                return {
                    "task_definition": updated_task_definition,
                    "messages": messages + [update_ai_message]
                }
            except (ValueError, AttributeError) as e:
                print(f"[update_task_due_date] ⚠️  Could not parse new due date '{new_due_date_str}': {e}")
                # Fallback to priority-based calculation
                return _fallback_due_date_update(task_definition, original_due_date, priority, messages)
        else:
            print("[update_task_due_date] ⚠️  LLM didn't provide new_due_date, using fallback")
            return _fallback_due_date_update(task_definition, original_due_date, priority, messages)
            
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"[update_task_due_date] ===== ERROR: LLM DUE DATE UPDATE FAILED =====")
        print(f"[update_task_due_date] Error type: {type(e).__name__}")
        print(f"[update_task_due_date] Error message: {str(e)}")
        print(f"[update_task_due_date] Response text (first 500 chars): {response_text[:500] if 'response_text' in locals() else 'N/A'}")
        print(f"[update_task_due_date] Falling back to priority-based calculation...")
        return _fallback_due_date_update(task_definition, original_due_date, priority, messages)


def _fallback_due_date_update(
    task_definition: Dict,
    original_due_date: Optional[datetime],
    priority: str,
    messages: list
) -> AgentState:
    """Fallback function to calculate due date based on priority."""
    now = datetime.now(timezone.utc)
    
    # Calculate based on priority
    if priority == "HIGH":
        new_due_date = now + timedelta(days=2)  # 2 days for HIGH
    elif priority == "MEDIUM":
        new_due_date = now + timedelta(days=5)  # 5 days for MEDIUM
    else:
        new_due_date = now + timedelta(days=10)  # 10 days for LOW
    
    new_due_date_rfc3339 = new_due_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    print(f"[update_task_due_date] ✅ Fallback new due date calculated: {new_due_date.date()} based on priority {priority}")
    
    # Update task definition
    updated_task_definition = task_definition.copy()
    updated_task_definition["due"] = new_due_date_rfc3339
    updated_task_definition["original_due"] = task_definition.get("due")
    updated_task_definition["needs_due_date_update"] = True
    
    # Create a message about the update
    task_name = task_definition.get("task_name", "Task")
    update_message = f"Updated due date for '{task_name}' from {original_due_date.date() if original_due_date else 'past'} to {new_due_date.date()} based on priority {priority}."
    update_ai_message = AIMessage(content=update_message)
    
    print(f"[update_task_due_date] ===== UPDATE TASK DUE DATE END (FALLBACK) =====")
    
    return {
        "task_definition": updated_task_definition,
        "messages": messages + [update_ai_message]
    }

