"""Filter slots node - filters free slots based on plan constraints."""

from datetime import datetime, timedelta
from typing import List, Dict

from app.ai_agent.state import AgentState


def filter_slots(state: AgentState) -> AgentState:
    """
    Filter free slots based on plan constraints.
    
    Reads: free_time_slots, plan (from habit_definition)
    Writes: filtered_slots
    """
    print("[filter_slots] Starting to filter free time slots...")
    free_slots = state.get("free_time_slots", [])
    habit_definition = state.get("habit_definition", {})
    time_constraints = state.get("time_constraints", {})
    
    print(f"[filter_slots] Total free slots to filter: {len(free_slots)}")
    
    # Extract constraints from plan
    required_duration_minutes = habit_definition.get("duration_minutes", 30)
    frequency = habit_definition.get("frequency", "daily")
    
    # Extract time constraints
    preferred_times = time_constraints.get("preferred_times", [])  # e.g., ["09:00", "14:00"]
    days_of_week = time_constraints.get("days_of_week", [])  # e.g., [0, 1, 2, 3, 4] for weekdays
    buffer_minutes = time_constraints.get("buffer_minutes", 15)
    
    print(f"[filter_slots] Filtering criteria:")
    print(f"  - Required duration: {required_duration_minutes} minutes")
    print(f"  - Frequency: {frequency}")
    print(f"  - Buffer: {buffer_minutes} minutes")
    print(f"  - Preferred times: {preferred_times}")
    print(f"  - Days of week: {days_of_week}")
    
    candidate_slots: List[Dict] = []
    
    for slot in free_slots:
        slot_duration = slot.get("duration_minutes", 0)
        
        # Check if slot is long enough (with buffer)
        if slot_duration < (required_duration_minutes + buffer_minutes):
            continue
        
        # Parse slot times
        try:
            slot_start = datetime.fromisoformat(slot["start"])
            slot_end = datetime.fromisoformat(slot["end"])
        except (ValueError, KeyError):
            continue
        
        # Check day of week constraint
        if days_of_week:
            slot_weekday = slot_start.weekday()  # 0 = Monday, 6 = Sunday
            if slot_weekday not in days_of_week:
                continue
        
        # Check preferred time constraints
        if preferred_times:
            slot_time = slot_start.strftime("%H:%M")
            matches_preferred = False
            for preferred_time in preferred_times:
                # Simple time matching (could be more sophisticated)
                pref_hour, pref_min = map(int, preferred_time.split(":"))
                slot_hour = slot_start.hour
                slot_min = slot_start.minute
                
                # Allow ±1 hour window
                if abs(slot_hour - pref_hour) <= 1:
                    matches_preferred = True
                    break
            
            if not matches_preferred:
                continue
        
        # Slot passes all filters
        # Cap the slot duration to the required duration to prevent excessive durations
        slot_end_capped = slot_start + timedelta(minutes=required_duration_minutes)
        
        candidate_slot = {
            "start": slot_start.isoformat(),
            "end": slot_end_capped.isoformat(),
            "duration_minutes": required_duration_minutes,
            "meets_constraints": True
        }
        
        # Preserve any additional metadata from the original slot
        for key in slot:
            if key not in ["start", "end", "duration_minutes"]:
                candidate_slot[key] = slot[key]
        
        candidate_slots.append(candidate_slot)
    
    print(f"[filter_slots] Filtered {len(candidate_slots)} candidate slots from {len(free_slots)} free slots")
    return {"filtered_slots": candidate_slots}