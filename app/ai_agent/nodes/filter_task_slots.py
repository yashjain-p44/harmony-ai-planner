"""Filter task slots node - filters free slots for task scheduling."""

from datetime import datetime
from typing import List, Dict

from app.ai_agent.state import AgentState


def filter_task_slots(state: AgentState) -> AgentState:
    """
    Filter free slots for task scheduling based on task requirements.
    
    Reads: free_time_slots, task_definition
    Writes: filtered_slots
    """
    print("[filter_task_slots] ===== FILTER TASK SLOTS START =====")
    free_slots = state.get("free_time_slots", [])
    task_definition = state.get("task_definition", {})
    
    print(f"[filter_task_slots] Input: {len(free_slots)} free time slots available")
    print(f"[filter_task_slots] Task definition keys: {list(task_definition.keys())}")
    if free_slots:
        print(f"[filter_task_slots] First free slot sample: start={free_slots[0].get('start', 'N/A')}, duration={free_slots[0].get('duration_minutes', 'N/A')}min")
    
    # Extract task requirements
    required_duration_minutes = task_definition.get("estimated_duration_minutes", 60)
    task_due = task_definition.get("due")
    priority = task_definition.get("priority", "MEDIUM")
    
    print(f"[filter_task_slots] Filtering criteria:")
    print(f"  - Required duration: {required_duration_minutes} minutes")
    print(f"  - Priority: {priority}")
    if task_due:
        print(f"  - Due date: {task_due}")
    
    candidate_slots: List[Dict] = []
    filtered_out_count = 0
    filtered_reasons = {"too_short": 0, "past_due": 0, "invalid_time": 0}
    
    # Parse due date if available
    due_datetime = None
    if task_due:
        try:
            due_datetime = datetime.fromisoformat(task_due.replace('Z', '+00:00'))
            print(f"[filter_task_slots] Parsed due date: {due_datetime}")
        except (ValueError, AttributeError) as e:
            print(f"[filter_task_slots] Failed to parse due date '{task_due}': {e}")
            pass
    
    print(f"[filter_task_slots] Processing {len(free_slots)} free slots...")
    for idx, slot in enumerate(free_slots):
        slot_duration = slot.get("duration_minutes", 0)
        
        # Check if slot is long enough
        if slot_duration < required_duration_minutes:
            filtered_out_count += 1
            filtered_reasons["too_short"] += 1
            if idx < 3:  # Log first few for debugging
                print(f"[filter_task_slots] Slot {idx+1} filtered: too short ({slot_duration}min < {required_duration_minutes}min)")
            continue
        
        # Parse slot times
        try:
            slot_start = datetime.fromisoformat(slot["start"])
            slot_end = datetime.fromisoformat(slot["end"])
        except (ValueError, KeyError) as e:
            filtered_out_count += 1
            filtered_reasons["invalid_time"] += 1
            if idx < 3:
                print(f"[filter_task_slots] Slot {idx+1} filtered: invalid time format - {e}")
            continue
        
        # If task has a due date, ensure slot is before due date
        if due_datetime and slot_start > due_datetime:
            filtered_out_count += 1
            filtered_reasons["past_due"] += 1
            if idx < 3:
                print(f"[filter_task_slots] Slot {idx+1} filtered: after due date ({slot_start} > {due_datetime})")
            continue
        
        # Create candidate slot with exact duration needed
        # Use the required duration, but don't exceed the slot duration
        from datetime import timedelta
        event_duration = min(required_duration_minutes, slot_duration)
        event_end = slot_start + timedelta(minutes=event_duration)
        
        # Ensure event_end doesn't exceed slot_end
        if event_end > slot_end:
            event_end = slot_end
            event_duration = int((event_end - slot_start).total_seconds() / 60)
        
        # Only add if it meets minimum duration
        if event_duration >= required_duration_minutes:
            candidate_slots.append({
                "start": slot_start.isoformat(),
                "end": event_end.isoformat(),
                "duration_minutes": event_duration,
                "meets_constraints": True
            })
    
    print(f"[filter_task_slots] ===== FILTERING RESULTS =====")
    print(f"[filter_task_slots] Input slots: {len(free_slots)}")
    print(f"[filter_task_slots] Filtered out: {filtered_out_count} slots")
    print(f"[filter_task_slots]   - Too short: {filtered_reasons['too_short']}")
    print(f"[filter_task_slots]   - Past due date: {filtered_reasons['past_due']}")
    print(f"[filter_task_slots]   - Invalid time: {filtered_reasons['invalid_time']}")
    print(f"[filter_task_slots] Candidate slots: {len(candidate_slots)}")
    if candidate_slots:
        print(f"[filter_task_slots] First candidate: {candidate_slots[0].get('start', 'N/A')} ({candidate_slots[0].get('duration_minutes', 'N/A')}min)")
    print(f"[filter_task_slots] ===== FILTER TASK SLOTS END =====")
    return {"filtered_slots": candidate_slots}

