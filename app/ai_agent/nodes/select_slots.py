"""Select slots node - chooses final slots for scheduling."""

from datetime import datetime, timedelta
from typing import List, Dict

from app.ai_agent.state import AgentState


def select_slots(state: AgentState) -> AgentState:
    """
    Select final slots from candidate slots for scheduling.
    
    Reads: filtered_slots (candidate_slots)
    Writes: selected_slots
    """
    print("[select_slots] Starting to select final slots...")
    candidate_slots = state.get("filtered_slots", [])
    habit_definition = state.get("habit_definition", {})
    
    print(f"[select_slots] Number of candidate slots: {len(candidate_slots)}")
    
    if not candidate_slots:
        print("[select_slots] No candidate slots available, returning empty selection")
        return {"selected_slots": []}
    
    # Extract scheduling preferences
    frequency = habit_definition.get("frequency", "daily")
    required_duration_minutes = habit_definition.get("duration_minutes", 30)
    buffer_minutes = habit_definition.get("buffer_minutes", 15)
    
    print(f"[select_slots] Selection criteria:")
    print(f"  - Frequency: {frequency}")
    print(f"  - Required duration: {required_duration_minutes} minutes")
    print(f"  - Buffer between events: {buffer_minutes} minutes")
    
    # Determine how many slots to select based on frequency
    # This is a simple heuristic - could be more sophisticated
    num_slots_to_select = 1
    if frequency == "daily":
        # Select slots for the next week (7 days)
        num_slots_to_select = 7
    elif frequency == "weekly":
        num_slots_to_select = 1
    elif frequency == "twice_weekly":
        num_slots_to_select = 2
    
    print(f"[select_slots] Target number of slots to select: {num_slots_to_select}")
    
    # Sort slots by start time (earliest first)
    sorted_slots = sorted(
        candidate_slots,
        key=lambda s: datetime.fromisoformat(s["start"])
    )
    
    # Select slots with spacing based on frequency
    # Buffer ensures minimum gap between consecutive events (end of one to start of next)
    selected_slots: List[Dict] = []
    last_selected_end_time = None
    
    for slot in sorted_slots:
        if len(selected_slots) >= num_slots_to_select:
            break
        
        slot_start = datetime.fromisoformat(slot["start"])
        slot_end = datetime.fromisoformat(slot["end"])
        
        # Check buffer requirement: if we have a previous event, ensure gap >= buffer_minutes
        if last_selected_end_time:
            gap_minutes = (slot_start - last_selected_end_time).total_seconds() / 60
            if gap_minutes < buffer_minutes:
                print(f"[select_slots] Skipping slot: gap {gap_minutes:.1f} min < required buffer {buffer_minutes} min")
                continue
        
        # For daily frequency, ensure slots are at least 20 hours apart (for different days)
        if frequency == "daily" and last_selected_end_time:
            time_diff_hours = (slot_start - last_selected_end_time).total_seconds() / 3600
            if time_diff_hours < 20:
                continue
        
        # Ensure slot is long enough
        if slot.get("duration_minutes", 0) >= required_duration_minutes:
            selected_slots.append(slot)
            last_selected_end_time = slot_end  # Track end time for buffer calculation
            print(f"[select_slots] Selected slot {len(selected_slots)}: {slot_start} (duration: {slot.get('duration_minutes', 0)} min)")
    
    print(f"[select_slots] Selected {len(selected_slots)} slots out of {len(candidate_slots)} candidates")
    return {"selected_slots": selected_slots}