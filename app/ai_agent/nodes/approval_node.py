"""Approval node - handles approval flow for selected slots before creating events."""

from datetime import datetime, timedelta
from typing import List, Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai_agent.state import AgentState


def approval_node(state: AgentState) -> AgentState:
    """
    Handle approval flow for selected slots.
    
    Reads: selected_slots, habit_definition, approval_state, approval_feedback, messages
    Writes: messages (append AIMessage when approval needed), approval_state, explanation_payload
    """
    print("[approval_node] Starting approval flow...")
    selected_slots = state.get("selected_slots", [])
    habit_definition = state.get("habit_definition", {})
    current_approval_state = state.get("approval_state")
    approval_feedback = state.get("approval_feedback")
    
    print(f"[approval_node] Number of selected slots: {len(selected_slots)}")
    print(f"[approval_node] Current approval state: {current_approval_state}")
    
    # If approval state is already set (from external input), use it
    if current_approval_state in ["APPROVED", "REJECTED", "CHANGES_REQUESTED"]:
        print(f"[approval_node] Approval state already set to: {current_approval_state}")
        
        if current_approval_state == "REJECTED":
            # Generate explanation for rejection
            feedback = approval_feedback or "Scheduling was rejected by user"
            return {
                "approval_state": "REJECTED",
                "approval_feedback": feedback,
                "explanation_payload": {
                    "reason": "Scheduling rejected",
                    "message": feedback,
                    "selected_slots": selected_slots
                }
            }
        elif current_approval_state == "CHANGES_REQUESTED":
            # Generate explanation for changes requested
            feedback = approval_feedback or "Changes requested by user"
            return {
                "approval_state": "CHANGES_REQUESTED",
                "approval_feedback": feedback,
                "explanation_payload": {
                    "reason": "Changes requested",
                    "message": feedback,
                    "selected_slots": selected_slots,
                    "suggested_changes": feedback
                }
            }
        elif current_approval_state == "APPROVED":
            # Approved, can proceed
            return {
                "approval_state": "APPROVED"
            }
    
    # If no approval state set yet, set to PENDING and generate summary
    if not selected_slots:
        print("[approval_node] No slots selected, setting approval to REJECTED")
        return {
            "approval_state": "REJECTED",
            "approval_feedback": "No slots were selected for scheduling",
            "explanation_payload": {
                "reason": "No slots available",
                "message": "No suitable time slots were found for scheduling."
            }
        }
    
    # Check if this is a task or habit
    task_definition = state.get("task_definition", {})
    is_task = bool(task_definition)
    
    print(f"[approval_node] ===== APPROVAL NODE (TASK MODE) =====" if is_task else f"[approval_node] ===== APPROVAL NODE (HABIT MODE) =====")
    print(f"[approval_node] Item type: {'TASK' if is_task else 'HABIT'}")
    
    if is_task:
        # Task scheduling
        task_name = task_definition.get("task_name", "Task")
        duration_minutes = task_definition.get("estimated_duration_minutes", 60)
        priority = task_definition.get("priority", "MEDIUM")
        task_due = task_definition.get("due")
        item_name = task_name
        item_type = "task"
        item_description = f"Priority: {priority}, Duration: {duration_minutes} min"
        print(f"[approval_node] Task details:")
        print(f"[approval_node]   - Name: {task_name}")
        print(f"[approval_node]   - Priority: {priority}")
        print(f"[approval_node]   - Duration: {duration_minutes} minutes")
        print(f"[approval_node]   - Due date: {task_due or 'Not specified'}")
    else:
        # Habit scheduling
        habit_name = habit_definition.get("habit_name", "Scheduled Habit")
        frequency = habit_definition.get("frequency", "unknown")
        duration_minutes = habit_definition.get("duration_minutes", 30)
        item_name = habit_name
        item_type = "habit"
        item_description = f"{frequency}, {duration_minutes} min"
    
    # Format slots summary
    # Always calculate habit_duration_minutes from end_time - start_time
    # Do not modify start/end times - just pass through the actual slot info
    slots_summary = []
    for i, slot in enumerate(selected_slots, 1):
        try:
            start_time = datetime.fromisoformat(slot["start"])
            end_time = datetime.fromisoformat(slot["end"])
            
            # Always calculate habit_duration_minutes from actual start and end times
            habit_duration_minutes = int((end_time - start_time).total_seconds() / 60)
            
            slots_summary.append({
                "slot_number": i,
                "date": start_time.strftime("%Y-%m-%d"),
                "time": start_time.strftime("%H:%M"),
                "duration_minutes": habit_duration_minutes,  # Always calculated from end_time - start_time
                "start": slot["start"],  # Pass through original start time
                "end": slot["end"]  # Pass through original end time
            })
        except (ValueError, KeyError):
            continue
    
    if is_task:
        summary_message = f"Ready to schedule task '{item_name}' ({item_description}) in {len(selected_slots)} time slot(s):\n"
    else:
        summary_message = f"Ready to schedule '{item_name}' ({item_description}) in {len(selected_slots)} time slot(s):\n"
    
    for slot_info in slots_summary:
        summary_message += f"  - {slot_info['date']} at {slot_info['time']} ({slot_info['duration_minutes']} min)\n"
    
    print(f"[approval_node] Generated approval summary:\n{summary_message}")
    
    # Generate a friendly, conversational message asking for approval
    messages = state.get("messages", [])
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    # Format slots for the LLM prompt
    slots_text = "\n".join([
        f"- {slot_info['date']} at {slot_info['time']} ({slot_info['duration_minutes']} minutes)"
        for slot_info in slots_summary
    ])
    
    system_prompt = """You are a helpful assistant asking the user to approve a schedule. Be friendly, conversational, and concise. 
Briefly mention what you found and ask them to review and approve. Don't repeat all the details - they'll see them in the approval box."""
    
    if is_task:
        prompt = f"""{system_prompt}

I found {len(selected_slots)} time slot(s) for task '{item_name}' ({item_description}):
{slots_text}

Your friendly message asking for approval:"""
    else:
        prompt = f"""{system_prompt}

I found {len(selected_slots)} time slot(s) for '{item_name}' ({item_description}):
{slots_text}

Your friendly message asking for approval:"""
    
    response = llm.invoke(prompt)
    approval_message = AIMessage(content=response.content)
    
    # Set to PENDING to require human approval
    # The approval state will be updated by the frontend when user responds
    approval_state = "PENDING"
    print("[approval_node] ===== SETTING APPROVAL STATE TO PENDING =====")
    print(f"[approval_node] Waiting for user approval for {len(selected_slots)} slot(s)")
    
    # Build explanation payload
    explanation_payload = {
        "summary": summary_message,
        "selected_slots": selected_slots,
        "slots_summary": slots_summary  # Include formatted slots for UI display
    }
    
    if is_task:
        explanation_payload.update({
            "task_name": item_name,
            "priority": priority,
            "duration_minutes": duration_minutes
        })
        print(f"[approval_node] Approval payload includes task info:")
        print(f"[approval_node]   - Task name: {item_name}")
        print(f"[approval_node]   - Priority: {priority}")
        print(f"[approval_node]   - Duration: {duration_minutes} min")
    else:
        explanation_payload.update({
            "habit_name": item_name,
            "frequency": frequency,
            "duration_minutes": duration_minutes
        })
        print(f"[approval_node] Approval payload includes habit info:")
        print(f"[approval_node]   - Habit name: {item_name}")
        print(f"[approval_node]   - Frequency: {frequency}")
        print(f"[approval_node]   - Duration: {duration_minutes} min")
    
    print(f"[approval_node] Explanation payload summary: {summary_message[:100]}...")
    print(f"[approval_node] Number of slots in payload: {len(selected_slots)}")
    print(f"[approval_node] Number of formatted slots: {len(slots_summary)}")
    print(f"[approval_node] ===== APPROVAL NODE END (PENDING) =====")
    
    return {
        "messages": messages + [approval_message],
        "approval_state": approval_state,
        "explanation_payload": explanation_payload
    }

