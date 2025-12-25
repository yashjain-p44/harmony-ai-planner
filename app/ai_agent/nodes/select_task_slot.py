"""Select task slot node - chooses final slot for task scheduling."""

from datetime import datetime, timedelta
from typing import List, Dict
import json

from langchain_openai import ChatOpenAI

from app.ai_agent.state import AgentState


def select_task_slot(state: AgentState) -> AgentState:
    """
    Select final slot from candidate slots for task scheduling using LLM intelligence.
    
    Reads: filtered_slots (candidate_slots), task_definition
    Writes: selected_slots (single slot for task)
    """
    print("[select_task_slot] ===== SELECT TASK SLOT START =====")
    candidate_slots = state.get("filtered_slots", [])
    task_definition = state.get("task_definition", {})
    
    print(f"[select_task_slot] Input: {len(candidate_slots)} candidate slots")
    print(f"[select_task_slot] Task definition: task_name={task_definition.get('task_name', 'N/A')}, priority={task_definition.get('priority', 'N/A')}")
    
    if not candidate_slots:
        print("[select_task_slot] ===== ERROR: NO CANDIDATE SLOTS =====")
        print("[select_task_slot] Cannot select slot - no candidates available")
        print("[select_task_slot] ===== SELECT TASK SLOT END (EMPTY) =====")
        return {"selected_slots": []}
    
    # Extract task information
    required_duration_minutes = task_definition.get("estimated_duration_minutes", 60)
    task_name = task_definition.get("task_name", "task")
    priority = task_definition.get("priority", "MEDIUM")
    task_due = task_definition.get("due")
    
    print(f"[select_task_slot] Selection criteria:")
    print(f"  - Task: {task_name}")
    print(f"  - Priority: {priority}")
    print(f"  - Required duration: {required_duration_minutes} minutes")
    if task_due:
        print(f"  - Due date: {task_due}")
    
    # Use LLM to intelligently select the best slot
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    # Prepare candidate slots data for LLM (limit to reasonable number)
    sorted_candidates = sorted(
        candidate_slots[:50],  # Limit to 50 to avoid token limits
        key=lambda s: datetime.fromisoformat(s["start"])
    )
    
    print(f"[select_task_slot] Processing {len(sorted_candidates)} slots (limited from {len(candidate_slots)})")
    if sorted_candidates:
        first_slot = sorted_candidates[0]
        last_slot = sorted_candidates[-1]
        print(f"[select_task_slot] Slot range: {first_slot.get('start', 'N/A')} to {last_slot.get('start', 'N/A')}")
    
    # Format slots for LLM
    slots_data = []
    now = datetime.now(datetime.now().astimezone().tzinfo)
    print(f"[select_task_slot] Current time: {now}")
    
    for i, slot in enumerate(sorted_candidates, 1):
        slot_start = datetime.fromisoformat(slot["start"])
        time_until_slot = (slot_start - now).total_seconds() / 3600  # hours
        
        slots_data.append({
            "index": i,
            "start": slot["start"],
            "end": slot["end"],
            "duration_minutes": slot.get("duration_minutes", 0),
            "date": slot_start.strftime("%Y-%m-%d"),
            "time": slot_start.strftime("%H:%M"),
            "day_of_week": slot_start.strftime("%A"),
            "hours_from_now": round(time_until_slot, 1)
        })
    
    # Build context about due date if available
    due_date_context = ""
    if task_due:
        try:
            due_dt = datetime.fromisoformat(task_due.replace('Z', '+00:00'))
            due_date_context = f"\n- Task is due: {due_dt.strftime('%Y-%m-%d %H:%M')}"
        except:
            pass
    
    system_prompt = f"""You are a smart scheduling assistant. Select the best time slot for scheduling a task.

Task Requirements:
- Name: {task_name}
- Priority: {priority}
- Estimated duration: {required_duration_minutes} minutes
- Due date: {task_due or "Not specified"}{due_date_context}

Selection Guidelines:
1. Select exactly ONE slot from the candidate slots
2. For HIGH priority tasks: prefer earlier slots, ideally within 24-48 hours
3. For MEDIUM priority tasks: prefer slots within the next 3-5 days
4. For LOW priority tasks: any suitable slot is fine
5. If task has a due date, ensure the selected slot is before the due date
6. Prefer slots during typical work hours (9 AM - 5 PM) when possible
7. Ensure the slot duration meets or exceeds the required duration ({required_duration_minutes} minutes)
8. Consider the time until the slot (hours_from_now) - balance urgency with availability

Respond with a JSON object containing:
{{
    "selected_index": <index from the candidate slots, e.g., 5>,
    "reasoning": "Brief explanation of why this slot was selected"
}}

Only return the index of the slot that should be selected. The index corresponds to the "index" field in each candidate slot."""
    
    prompt = f"""{system_prompt}

Candidate Slots (sorted by start time):
{json.dumps(slots_data, indent=2)}

Response (JSON only):"""
    
    print(f"[select_task_slot] ===== CALLING LLM FOR SELECTION =====")
    print(f"[select_task_slot] Sending {len(slots_data)} slots to LLM for intelligent selection")
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        print(f"[select_task_slot] LLM raw response (first 200 chars): {response_text[:200]}...")
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result_data = json.loads(response_text)
        selected_index = result_data.get("selected_index")
        reasoning = result_data.get("reasoning", "")
        
        print(f"[select_task_slot] ===== LLM SELECTION RESULT =====")
        print(f"[select_task_slot] LLM reasoning: {reasoning}")
        print(f"[select_task_slot] LLM selected index: {selected_index} (1-based, will convert to 0-based)")
        
        # Map index back to actual slot
        selected_slots = []
        if selected_index:
            # Find slot with matching index (1-based from LLM, 0-based in list)
            slot_idx = selected_index - 1
            print(f"[select_task_slot] Converting index: {selected_index} (1-based) -> {slot_idx} (0-based)")
            if 0 <= slot_idx < len(sorted_candidates):
                selected_slot = sorted_candidates[slot_idx]
                selected_slots.append(selected_slot)
                slot_start = datetime.fromisoformat(selected_slot["start"])
                slot_end = datetime.fromisoformat(selected_slot["end"])
                print(f"[select_task_slot] ===== SELECTED SLOT =====")
                print(f"[select_task_slot] Start: {slot_start}")
                print(f"[select_task_slot] End: {slot_end}")
                print(f"[select_task_slot] Duration: {selected_slot.get('duration_minutes', 0)} minutes")
            else:
                print(f"[select_task_slot] ERROR: Index {slot_idx} out of range (0-{len(sorted_candidates)-1})")
        
        # If LLM didn't select a slot, fall back to simple selection
        if not selected_slots:
            print(f"[select_task_slot] LLM selection failed or invalid. Falling back to simple selection...")
            # Fallback: select the first slot that meets duration requirement
            for slot in sorted_candidates:
                if slot.get("duration_minutes", 0) >= required_duration_minutes:
                    selected_slots.append(slot)
                    slot_start = datetime.fromisoformat(slot["start"])
                    print(f"[select_task_slot] Fallback selected slot: {slot_start}")
                    break
        
        print(f"[select_task_slot] ===== SELECTION COMPLETE =====")
        print(f"[select_task_slot] Final result: {len(selected_slots)} slot(s) selected from {len(candidate_slots)} candidates")
        print(f"[select_task_slot] ===== SELECT TASK SLOT END =====")
        return {"selected_slots": selected_slots}
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"[select_task_slot] ===== ERROR: LLM SELECTION FAILED =====")
        print(f"[select_task_slot] Error type: {type(e).__name__}")
        print(f"[select_task_slot] Error message: {str(e)}")
        if 'response_text' in locals():
            print(f"[select_task_slot] Response text: {response_text[:500]}")
        print(f"[select_task_slot] Falling back to simple selection logic...")
        # Fallback to simple selection logic
        selected_slots = []
        
        sorted_slots = sorted(
            candidate_slots,
            key=lambda s: datetime.fromisoformat(s["start"])
        )
        
        for slot in sorted_slots:
            if slot.get("duration_minutes", 0) >= required_duration_minutes:
                selected_slots.append(slot)
                break
        
        print(f"[select_task_slot] ===== FALLBACK SELECTION COMPLETE =====")
        if selected_slots:
            fallback_slot = selected_slots[0]
            slot_start = datetime.fromisoformat(fallback_slot["start"])
            print(f"[select_task_slot] Fallback selected: {slot_start} ({fallback_slot.get('duration_minutes', 0)}min)")
        print(f"[select_task_slot] Final result: {len(selected_slots)} slot(s) selected")
        print(f"[select_task_slot] ===== SELECT TASK SLOT END (FALLBACK) =====")
        return {"selected_slots": selected_slots}

