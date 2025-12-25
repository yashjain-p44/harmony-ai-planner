"""Approval node - handles approval flow for selected slots before creating events."""

from datetime import datetime
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
    
    # Generate summary of selected slots for approval
    habit_name = habit_definition.get("habit_name", "Scheduled Habit")
    frequency = habit_definition.get("frequency", "unknown")
    duration_minutes = habit_definition.get("duration_minutes", 30)
    
    # Format slots summary
    slots_summary = []
    for i, slot in enumerate(selected_slots, 1):
        try:
            start_time = datetime.fromisoformat(slot["start"])
            end_time = datetime.fromisoformat(slot["end"])
            slots_summary.append({
                "slot_number": i,
                "date": start_time.strftime("%Y-%m-%d"),
                "time": start_time.strftime("%H:%M"),
                "duration_minutes": slot.get("duration_minutes", duration_minutes)
            })
        except (ValueError, KeyError):
            continue
    
    summary_message = f"Ready to schedule '{habit_name}' ({frequency}, {duration_minutes} min) in {len(selected_slots)} time slot(s):\n"
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
    
    prompt = f"""{system_prompt}

I found {len(selected_slots)} time slot(s) for '{habit_name}' ({frequency}, {duration_minutes} minutes):
{slots_text}

Your friendly message asking for approval:"""
    
    response = llm.invoke(prompt)
    approval_message = AIMessage(content=response.content)
    
    # Set to PENDING to require human approval
    # The approval state will be updated by the frontend when user responds
    approval_state = "PENDING"
    print("[approval_node] Setting approval state to PENDING - waiting for user approval")
    
    return {
        "messages": messages + [approval_message],
        "approval_state": approval_state,
        "explanation_payload": {
            "summary": summary_message,
            "selected_slots": selected_slots,
            "habit_name": habit_name,
            "frequency": frequency,
            "duration_minutes": duration_minutes,
            "slots_summary": slots_summary  # Include formatted slots for UI display
        }
    }

