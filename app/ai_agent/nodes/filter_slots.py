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
    
    print(f"[filter_slots] ===== INPUT STATE FIELDS =====")
    print(f"[filter_slots] free_time_slots count: {len(free_slots)}")
    if free_slots:
        print(f"[filter_slots] Sample free slot (first): {free_slots[0]}")
    print(f"[filter_slots] habit_definition (full): {habit_definition}")
    print(f"[filter_slots] time_constraints (full): {time_constraints}")
    
    # Extract constraints from plan
    required_duration_minutes = habit_definition.get("duration_minutes", 30)
    max_duration_minutes = habit_definition.get("max_duration_minutes", 60)
    frequency = habit_definition.get("frequency", "daily")
    buffer_minutes = habit_definition.get("buffer_minutes", 15)
    
    # Extract time constraints
    preferred_times = time_constraints.get("preferred_times", [])  # e.g., ["09:00", "14:00"]
    days_of_week = time_constraints.get("days_of_week", [])  # e.g., [0, 1, 2, 3, 4] for weekdays
    
    print(f"[filter_slots] ===== EXTRACTED FILTERING CRITERIA =====")
    print(f"[filter_slots] Required duration: {required_duration_minutes} minutes")
    print(f"[filter_slots] Max duration: {max_duration_minutes} minutes")
    print(f"[filter_slots] Frequency: {frequency}")
    print(f"[filter_slots] Buffer: {buffer_minutes} minutes")
    print(f"[filter_slots] Preferred times: {preferred_times}")
    print(f"[filter_slots] Days of week: {days_of_week}")
    
    candidate_slots: List[Dict] = []
    
    # Minimum slot size needed: just the required duration (buffer is gap between events, not part of event)
    min_slot_size_minutes = required_duration_minutes
    
    for slot in free_slots:
        slot_duration = slot.get("duration_minutes", 0)
        
        # Check if slot is long enough for at least one event
        if slot_duration < min_slot_size_minutes:
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
        
        # Break large slots into multiple smaller slots
        # Buffer is a gap BETWEEN events, not part of the event duration
        # Each event is: required_duration_minutes to max_duration_minutes
        # Between consecutive events, there should be at least buffer_minutes gap
        
        current_time = slot_start
        remaining_duration = slot_duration
        
        while remaining_duration >= min_slot_size_minutes:
            # Calculate how much time we can use for this event (up to max_duration_minutes)
            available_for_habit = min(max_duration_minutes, remaining_duration)
            
            # Ensure we have at least required_duration_minutes
            if available_for_habit < required_duration_minutes:
                break
            
            # Create an event slot: just the habit duration (no buffer included)
            event_start = current_time
            event_end = event_start + timedelta(minutes=available_for_habit)
            
            # Make sure we don't exceed the original slot end time
            if event_end > slot_end:
                event_end = slot_end
                available_for_habit = int((event_end - event_start).total_seconds() / 60)
                
                # If the remaining time is less than minimum, break
                if available_for_habit < required_duration_minutes:
                    break
            
            # Create the candidate slot (event only, no buffer)
            candidate_slots.append({
                "start": event_start.isoformat(),
                "end": event_end.isoformat(),
                "duration_minutes": available_for_habit,  # Just the event duration
                "habit_duration_minutes": available_for_habit,
                "meets_constraints": True
            })
            
            # Move to next potential slot: event end + buffer (gap between events)
            current_time = event_end + timedelta(minutes=buffer_minutes)
            remaining_duration = int((slot_end - current_time).total_seconds() / 60)
            
            # If remaining duration is less than minimum, stop
            if remaining_duration < min_slot_size_minutes:
                break
    
    print(f"[filter_slots] Generated {len(candidate_slots)} candidate slots from {len(free_slots)} free slots")
    return {"filtered_slots": candidate_slots}