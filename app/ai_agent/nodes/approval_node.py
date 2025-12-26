"""Approval node - handles approval flow for selected slots before creating events."""

from datetime import datetime, timedelta
from typing import List, Dict

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai_agent.state import AgentState


def approval_node(state: AgentState) -> AgentState:
    """
    Handle approval flow for selected slots.
    
    Reads: selected_slots, habit_definition or task_definition, approval_state, approval_feedback, messages, intent_type
    Writes: messages (append AIMessage when approval needed), approval_state, explanation_payload
    """
    print("=" * 50)
    print("Approval Node: Starting approval flow")
    print("=" * 50)
    
    selected_slots = state.get("selected_slots", [])
    habit_definition = state.get("habit_definition", {})
    task_definition = state.get("task_definition", {})
    intent_type = state.get("intent_type", "UNKNOWN")
    current_approval_state = state.get("approval_state")
    approval_feedback = state.get("approval_feedback")
    
    # Determine if this is a task or habit
    is_task = bool(task_definition) or intent_type == "TASK_SCHEDULE"
    
    print(f"Approval Node: Number of selected slots = {len(selected_slots)}")
    print(f"Approval Node: Current approval state = {current_approval_state}")
    print(f"Approval Node: Intent type = {intent_type}")
    print(f"Approval Node: Processing as {'TASK' if is_task else 'HABIT'}")
    
    # If approval state is already set (from external input), use it
    if current_approval_state in ["APPROVED", "REJECTED", "CHANGES_REQUESTED"]:
        print(f"Approval Node: Approval state already set to {current_approval_state}")
        
        if current_approval_state == "REJECTED":
            # Generate explanation for rejection
            feedback = approval_feedback or "Scheduling was rejected by user"
            print("Approval Node: Returning REJECTED state")
            print("=" * 50)
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
            print("Approval Node: Returning CHANGES_REQUESTED state")
            print("=" * 50)
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
            print("Approval Node: Returning APPROVED state")
            print("=" * 50)
            return {
                "approval_state": "APPROVED"
            }
    
    # If no approval state set yet, set to PENDING and generate summary
    if not selected_slots:
        print("Approval Node: No slots selected, setting approval to REJECTED")
        print("=" * 50)
        return {
            "approval_state": "REJECTED",
            "approval_feedback": "No slots were selected for scheduling",
            "explanation_payload": {
                "reason": "No slots available",
                "message": "No suitable time slots were found for scheduling."
            }
        }
    
    # Generate summary of selected slots for approval
    if is_task:
        # Task-specific information
        item_name = task_definition.get("task_name", "Scheduled Task")
        priority = task_definition.get("priority", "MEDIUM")
        duration_minutes = task_definition.get("estimated_time_minutes", 30)
        description = task_definition.get("description", "")
        print(f"Approval Node: Task name = {item_name}")
        print(f"Approval Node: Priority = {priority}")
        print(f"Approval Node: Estimated duration = {duration_minutes} minutes")
    else:
        # Habit-specific information
        item_name = habit_definition.get("habit_name", "Scheduled Habit")
        frequency = habit_definition.get("frequency", "unknown")
        duration_minutes = habit_definition.get("duration_minutes", 30)
        print(f"Approval Node: Habit name = {item_name}")
        print(f"Approval Node: Frequency = {frequency}")
        print(f"Approval Node: Duration = {duration_minutes} minutes")
    
    # Format slots summary
    # Always calculate duration_minutes from end_time - start_time
    # Do not modify start/end times - just pass through the actual slot info
    slots_summary = []
    for i, slot in enumerate(selected_slots, 1):
        try:
            start_time = datetime.fromisoformat(slot["start"])
            end_time = datetime.fromisoformat(slot["end"])
            
            # Always calculate duration_minutes from actual start and end times
            slot_duration_minutes = int((end_time - start_time).total_seconds() / 60)
            
            slots_summary.append({
                "slot_number": i,
                "date": start_time.strftime("%Y-%m-%d"),
                "time": start_time.strftime("%H:%M"),
                "duration_minutes": slot_duration_minutes,  # Always calculated from end_time - start_time
                "start": slot["start"],  # Pass through original start time
                "end": slot["end"]  # Pass through original end time
            })
        except (ValueError, KeyError) as e:
            print(f"Approval Node: Skipping invalid slot - {type(e).__name__}: {e}")
            continue
    
    # Generate summary message based on task or habit
    if is_task:
        summary_message = f"Ready to schedule task '{item_name}' (Priority: {priority}, {duration_minutes} min) in {len(selected_slots)} time slot(s):\n"
    else:
        summary_message = f"Ready to schedule '{item_name}' ({frequency}, {duration_minutes} min) in {len(selected_slots)} time slot(s):\n"
    
    for slot_info in slots_summary:
        summary_message += f"  - {slot_info['date']} at {slot_info['time']} ({slot_info['duration_minutes']} min)\n"
    
    print(f"Approval Node: Generated approval summary:\n{summary_message}")
    
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
    
    # Create different prompts for tasks vs habits
    if is_task:
        prompt = f"""{system_prompt}

I found {len(selected_slots)} time slot(s) for task '{item_name}' (Priority: {priority}, {duration_minutes} minutes):
{slots_text}

Your friendly message asking for approval:"""
    else:
        prompt = f"""{system_prompt}

I found {len(selected_slots)} time slot(s) for '{item_name}' ({frequency}, {duration_minutes} minutes):
{slots_text}

Your friendly message asking for approval:"""
    
    print(f"Approval Node: Invoking LLM to generate approval message...")
    response = llm.invoke(prompt)
    approval_message = AIMessage(content=response.content)
    
    print(f"Approval Node: LLM generated approval message: {response.content[:100]}...")
    
    # Set to PENDING to require human approval
    # The approval state will be updated by the frontend when user responds
    approval_state = "PENDING"
    print("Approval Node: Setting approval state to PENDING - waiting for user approval")
    
    # Build explanation payload based on task or habit
    explanation_payload = {
        "summary": summary_message,
        "selected_slots": selected_slots,
        "slots_summary": slots_summary  # Include formatted slots for UI display
    }
    
    if is_task:
        explanation_payload.update({
            "task_name": item_name,
            "priority": priority,
            "estimated_time_minutes": duration_minutes,
            "description": description
        })
    else:
        explanation_payload.update({
            "habit_name": item_name,
            "frequency": frequency,
            "duration_minutes": duration_minutes
        })
    
    print("Approval Node: Approval flow complete")
    print("=" * 50)
    
    return {
        "messages": messages + [approval_message],
        "approval_state": approval_state,
        "explanation_payload": explanation_payload
    }

