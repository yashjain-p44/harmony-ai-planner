"""Select slots node - chooses final slots for scheduling."""

from datetime import datetime, timedelta
from typing import List, Dict
import json

from langchain_openai import ChatOpenAI

from app.ai_agent.state import AgentState


def select_slots(state: AgentState) -> AgentState:
    """
    Select final slots from candidate slots for scheduling using LLM intelligence.
    
    Reads: filtered_slots (candidate_slots), habit_definition or task_definition, intent_type
    Writes: selected_slots
    """
    print("=" * 50)
    print("Select Slots: Starting to select final slots")
    print("=" * 50)
    
    candidate_slots = state.get("filtered_slots", [])
    habit_definition = state.get("habit_definition", {})
    task_definition = state.get("task_definition", {})
    intent_type = state.get("intent_type", "UNKNOWN")
    
    print(f"Select Slots: Number of candidate slots = {len(candidate_slots)}")
    print(f"Select Slots: Intent type = {intent_type}")
    print(f"Select Slots: Has habit_definition = {bool(habit_definition)}")
    print(f"Select Slots: Has task_definition = {bool(task_definition)}")
    
    if not candidate_slots:
        print("Select Slots: No candidate slots available, returning empty selection")
        print("=" * 50)
        return {"selected_slots": []}
    
    # Determine if this is a task or habit
    is_task = bool(task_definition) or intent_type == "TASK_SCHEDULE"
    
    if is_task:
        # Task-specific logic: select only ONE slot
        print("Select Slots: Processing as TASK (single event)")
        
        # Extract task information
        task_name = task_definition.get("task_name", "task")
        priority = task_definition.get("priority", "MEDIUM")
        estimated_time_minutes = task_definition.get("estimated_time_minutes", 30)
        task_description = task_definition.get("description", "")
        
        print(f"Select Slots: Task name = {task_name}")
        print(f"Select Slots: Priority = {priority}")
        print(f"Select Slots: Estimated time = {estimated_time_minutes} minutes")
        
        # For tasks, we only need to select 1 slot
        num_slots_to_select = 1
        required_duration_minutes = estimated_time_minutes
        
    else:
        # Habit-specific logic: select multiple slots
        print("Select Slots: Processing as HABIT (multiple events)")
        
        # Extract scheduling preferences
        frequency = habit_definition.get("frequency", "daily")
        required_duration_minutes = habit_definition.get("duration_minutes", 30)
        buffer_minutes = habit_definition.get("buffer_minutes", 15)
        num_occurrences = habit_definition.get("num_occurrences")
        habit_name = habit_definition.get("habit_name", "habit")
        
        print(f"Select Slots: Habit name = {habit_name}")
        print(f"Select Slots: Frequency = {frequency}")
        print(f"Select Slots: Required duration = {required_duration_minutes} minutes")
        print(f"Select Slots: Buffer between events = {buffer_minutes} minutes")
        print(f"Select Slots: Number of occurrences = {num_occurrences}")
        
        # Determine how many slots to select
        if num_occurrences is not None:
            num_slots_to_select = num_occurrences
        else:
            # Fallback to frequency-based defaults
            if frequency == "daily":
                num_slots_to_select = 7
            elif frequency == "weekly":
                num_slots_to_select = 1
            elif frequency == "twice_weekly":
                num_slots_to_select = 2
            else:
                num_slots_to_select = 1
    
    print(f"Select Slots: Target number of slots to select = {num_slots_to_select}")
    
    # Use LLM to intelligently select slots
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    # Prepare candidate slots data for LLM (limit to reasonable number to avoid token limits)
    # Sort by start time and take up to 50 candidates
    sorted_candidates = sorted(
        candidate_slots[:50],  # Limit to 50 to avoid token limits
        key=lambda s: datetime.fromisoformat(s["start"])
    )
    
    # Format slots for LLM
    slots_data = []
    for i, slot in enumerate(sorted_candidates, 1):
        slot_start = datetime.fromisoformat(slot["start"])
        slots_data.append({
            "index": i,
            "start": slot["start"],
            "end": slot["end"],
            "duration_minutes": slot.get("duration_minutes", 0),
            "date": slot_start.strftime("%Y-%m-%d"),
            "time": slot_start.strftime("%H:%M"),
            "day_of_week": slot_start.strftime("%A")
        })
    
    # Create different prompts for tasks vs habits
    if is_task:
        # Task-specific prompt
        system_prompt = f"""You are a smart scheduling assistant. Select the best time slot for scheduling a task.

Task Requirements:
- Name: {task_name}
- Priority: {priority}
- Estimated duration: {estimated_time_minutes} minutes
- Description: {task_description if task_description else 'No description provided'}

Selection Guidelines:
1. Select exactly 1 slot from the candidate slots
2. Consider task priority:
   - HIGH priority: Prefer earlier slots, prioritize urgent scheduling
   - MEDIUM priority: Balance between urgency and convenience
   - LOW priority: Can be scheduled flexibly, prefer convenient times
3. Select a slot that meets the duration requirement ({required_duration_minutes} minutes minimum)
4. Consider the time of day that would be most productive for this task
5. Prefer slots that don't conflict with typical work hours or personal time preferences

Respond with a JSON object containing:
{{
    "selected_indices": [single index from the candidate slots, e.g., [5]],
    "reasoning": "Brief explanation of why this slot was selected"
}}

Only return the index of the single slot that should be selected. The index corresponds to the "index" field in the candidate slot."""
    else:
        # Habit-specific prompt
        frequency = habit_definition.get("frequency", "daily")
        buffer_minutes = habit_definition.get("buffer_minutes", 15)
        num_occurrences = habit_definition.get("num_occurrences")
        habit_name = habit_definition.get("habit_name", "habit")
        
        system_prompt = f"""You are a smart scheduling assistant. Select the best time slots for scheduling a habit.

Habit Requirements:
- Name: {habit_name}
- Frequency: {frequency}
- Duration per session: {required_duration_minutes} minutes
- Buffer between events: {buffer_minutes} minutes (minimum gap between end of one event and start of next)
- Number of events to schedule: {num_occurrences if num_occurrences else 'based on frequency'}

Selection Guidelines:
1. Select exactly {num_slots_to_select} slots from the candidate slots
2. Ensure proper spacing based on frequency:
   - For "weekly" frequency: events should be spread across different weeks when possible (approximately 7 days apart)
   - For "daily" frequency: events should be on different days (at least 20 hours apart)
   - For "twice_weekly": events should be approximately 3-4 days apart
3. Ensure buffer requirement: gap between end of previous event and start of next event >= {buffer_minutes} minutes
4. Prefer slots that are well-distributed across the time period
5. Consider day of week preferences if relevant
6. Select slots that meet the duration requirement ({required_duration_minutes} minutes minimum)

Respond with a JSON object containing:
{{
    "selected_indices": [list of indices from the candidate slots, e.g., [1, 5, 12]],
    "reasoning": "Brief explanation of why these slots were selected"
}}

Only return the indices of slots that should be selected. The indices correspond to the "index" field in each candidate slot."""
    
    prompt = f"""{system_prompt}

Candidate Slots (sorted by start time):
{json.dumps(slots_data, indent=2)}

Response (JSON only):"""
    
    print(f"Select Slots: Invoking LLM for slot selection ({'TASK' if is_task else 'HABIT'} mode)...")
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        print(f"Select Slots: LLM response = {response_text}")
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result_data = json.loads(response_text)
        selected_indices = result_data.get("selected_indices", [])
        reasoning = result_data.get("reasoning", "")
        
        print(f"Select Slots: LLM reasoning = {reasoning}")
        print(f"Select Slots: LLM selected indices = {selected_indices}")
        
        # Map indices back to actual slots
        selected_slots = []
        for idx in selected_indices:
            # Find slot with matching index (1-based from LLM, 0-based in list)
            slot_idx = idx - 1
            if 0 <= slot_idx < len(sorted_candidates):
                selected_slots.append(sorted_candidates[slot_idx])
                slot_start = datetime.fromisoformat(sorted_candidates[slot_idx]["start"])
                print(f"Select Slots: Selected slot {len(selected_slots)}: {slot_start} (duration: {sorted_candidates[slot_idx].get('duration_minutes', 0)} min)")
        
        # If LLM didn't select enough, fall back to simple selection (only for habits, tasks should always be 1)
        if not is_task and len(selected_slots) < num_slots_to_select and len(selected_slots) < len(sorted_candidates):
            print(f"Select Slots: LLM selected {len(selected_slots)} slots, but need {num_slots_to_select}. Adding more slots...")
            # Add remaining slots in order, ensuring buffer requirement
            buffer_minutes = habit_definition.get("buffer_minutes", 15)
            last_end_time = None
            if selected_slots:
                last_end_time = datetime.fromisoformat(selected_slots[-1]["end"])
            
            for slot in sorted_candidates:
                if len(selected_slots) >= num_slots_to_select:
                    break
                
                if slot in selected_slots:
                    continue
                
                slot_start = datetime.fromisoformat(slot["start"])
                slot_end = datetime.fromisoformat(slot["end"])
                
                # Check buffer requirement
                if last_end_time:
                    gap_minutes = (slot_start - last_end_time).total_seconds() / 60
                    if gap_minutes < buffer_minutes:
                        continue
                
                # Check duration requirement
                if slot.get("duration_minutes", 0) >= required_duration_minutes:
                    selected_slots.append(slot)
                    last_end_time = slot_end
        
        print(f"Select Slots: Selected {len(selected_slots)} slot(s) out of {len(candidate_slots)} candidates")
        print("Select Slots: Slot selection complete")
        print("=" * 50)
        return {"selected_slots": selected_slots}
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Select Slots: LLM selection failed - {type(e).__name__}: {str(e)}")
        print("Select Slots: Falling back to simple selection...")
        
        # Fallback to simple selection logic
        selected_slots = []
        last_selected_end_time = None
        
        sorted_slots = sorted(
            candidate_slots,
            key=lambda s: datetime.fromisoformat(s["start"])
        )
        
        # For tasks, only select 1 slot. For habits, use num_slots_to_select
        target_count = 1 if is_task else num_slots_to_select
        buffer_minutes = habit_definition.get("buffer_minutes", 15) if not is_task else 0
        
        for slot in sorted_slots:
            if len(selected_slots) >= target_count:
                break
            
            slot_start = datetime.fromisoformat(slot["start"])
            slot_end = datetime.fromisoformat(slot["end"])
            
            # Check buffer requirement (only for habits)
            if not is_task and last_selected_end_time:
                gap_minutes = (slot_start - last_selected_end_time).total_seconds() / 60
                if gap_minutes < buffer_minutes:
                    continue
            
            # Check duration requirement
            if slot.get("duration_minutes", 0) >= required_duration_minutes:
                selected_slots.append(slot)
                last_selected_end_time = slot_end
                if is_task:
                    # For tasks, we only need one slot
                    break
        
        print(f"Select Slots: Fallback: Selected {len(selected_slots)} slot(s)")
        print("Select Slots: Slot selection complete")
        print("=" * 50)
        return {"selected_slots": selected_slots}