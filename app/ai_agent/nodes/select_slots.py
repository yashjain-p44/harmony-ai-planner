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
    
    habit_definition = state.get("habit_definition", {})
    task_definition = state.get("task_definition", {})
    intent_type = state.get("intent_type", "UNKNOWN")
    
    # Determine if this is a task or habit
    is_task = bool(task_definition) or intent_type == "TASK_SCHEDULE"
    
    # For tasks: use free_time_slots directly (skip filter_slots)
    # For habits: use filtered_slots (from filter_slots node)
    if is_task:
        candidate_slots = state.get("free_time_slots", [])
        print(f"Select Slots: Using free_time_slots (TASK mode) - {len(candidate_slots)} slots")
    else:
        candidate_slots = state.get("filtered_slots", [])
        print(f"Select Slots: Using filtered_slots (HABIT mode) - {len(candidate_slots)} slots")
    
    print(f"Select Slots: Intent type = {intent_type}")
    print(f"Select Slots: Has habit_definition = {bool(habit_definition)}")
    print(f"Select Slots: Has task_definition = {bool(task_definition)}")
    
    if not candidate_slots:
        print("Select Slots: No candidate slots available, returning empty selection")
        print("=" * 50)
        return {"selected_slots": []}
    
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
        # Task-specific prompt - comprehensive and high quality
        system_prompt = f"""You are an intelligent scheduling assistant specializing in task scheduling. Your goal is to select the optimal time slot for a single task based on all available information.

=== TASK INFORMATION ===
Task Name: {task_name}
Priority Level: {priority}
Estimated Duration: {estimated_time_minutes} minutes
Description: {task_description if task_description else 'No additional description provided'}

=== AVAILABLE FREE TIME SLOTS ===
You have access to {len(sorted_candidates)} candidate time slots. These are PERIODS when the user's calendar is free and available for scheduling. Each slot represents a continuous block of free time.

IMPORTANT: Free slots can be much longer than the task duration. For example, a free slot might be 4 hours long (9:00 AM - 1:00 PM), but the task only needs {estimated_time_minutes} minutes. Your job is to:
1. Identify which free slot to use
2. Select a SPECIFIC START TIME within that free slot
3. The task will run from your selected start time for {estimated_time_minutes} minutes

Each slot includes:
- index: Unique identifier (use this to reference the slot)
- start: Start of the free period (ISO format) - earliest you can schedule
- end: End of the free period (ISO format) - latest you can schedule
- duration_minutes: Total available time in this free slot (can be much longer than task duration)
- date: Date in YYYY-MM-DD format
- time: Start time of free period in HH:MM format
- day_of_week: Day name (Monday, Tuesday, etc.)

Example: If a free slot is from 9:00 AM to 1:00 PM (4 hours), and the task needs 30 minutes, you could schedule it at 10:00 AM (within that free period), making it run from 10:00 AM to 10:30 AM.

=== SELECTION CRITERIA ===

1. DURATION REQUIREMENT (MANDATORY):
   - The selected free slot MUST have duration_minutes >= {required_duration_minutes} minutes (enough time to fit the task)
   - The task requires {estimated_time_minutes} minutes to complete
   - Your selected start time must allow the task to complete before the free slot ends
   - Formula: selected_start_time + {estimated_time_minutes} minutes <= free_slot_end_time
   - Prefer slots with some buffer time if available (allows for slight overruns and natural breaks)

2. PRIORITY-BASED SCHEDULING:
   - HIGH priority tasks:
     * Prioritize EARLIEST available slots
     * Urgency is the primary concern
     * Prefer slots today or tomorrow if available
     * Time of day is secondary to urgency
   
   - MEDIUM priority tasks:
     * Balance urgency with convenience
     * Consider optimal time of day for productivity
     * Prefer slots within the next few days
     * Avoid scheduling too far in advance unless necessary
   
   - LOW priority tasks:
     * Flexibility is key - convenience over urgency
     * Can be scheduled further out
     * Prioritize optimal time of day for the task type
     * Consider user's typical schedule patterns

3. TIME OF DAY CONSIDERATIONS:
   - Analyze the task description to determine optimal time:
     * Deep work / Focus tasks: Prefer morning hours (9 AM - 12 PM) when focus is highest
     * Creative tasks: Consider when user is most creative (often mid-morning or afternoon)
     * Administrative tasks: Can be scheduled during lower-energy periods
     * Meetings/Calls: Consider business hours and time zones
     * Physical tasks: Consider energy levels and availability
   - Avoid scheduling during typical meal times unless task is brief
   - Consider work-life balance (avoid late evening for work tasks if possible)

4. DAY OF WEEK CONSIDERATIONS:
   - Weekdays (Monday-Friday): Better for work-related tasks
   - Weekends: Better for personal tasks, hobbies, or non-urgent work
   - Consider the task description to match appropriate day type

5. START TIME SELECTION WITHIN FREE SLOT:
   - Once you've chosen a free slot, select the optimal START TIME within it
   - Consider the task type when choosing start time:
     * Morning tasks (9-11 AM): Best for high-focus work
     * Mid-day tasks (11 AM-2 PM): Good for meetings, calls, collaborative work
     * Afternoon tasks (2-5 PM): Suitable for creative or administrative work
     * Evening tasks (5-8 PM): For personal tasks or low-energy work
   - Leave buffer time before/after if the free slot allows (e.g., if slot is 2 hours and task is 30 min, don't schedule at the very start or end)
   - Consider natural break points (e.g., on the hour, half-hour, or after typical meal times)
   
6. SLOT QUALITY ASSESSMENT:
   - Free slots can be any length - focus on finding the right time, not the right slot size
   - Consider slots that provide natural breaks before/after the task
   - Avoid scheduling too close to the end of a free slot (leave some buffer)
   - If multiple suitable free slots exist, choose the one that best matches the task's nature and optimal time

=== SELECTION PROCESS ===

1. Review ALL available free time slots below
2. Filter free slots that have enough time to fit the task (duration_minutes >= {required_duration_minutes} minutes)
3. Apply priority-based filtering (HIGH = earliest free slot, MEDIUM = balanced, LOW = convenient)
4. Consider time of day and day of week appropriateness for this specific task
5. Select ONE free slot that optimizes all criteria
6. Within that free slot, choose the OPTIMAL START TIME for the task
7. Ensure: selected_start_time + {estimated_time_minutes} minutes <= free_slot_end_time
8. Provide clear reasoning for both the free slot choice and the specific start time

=== OUTPUT FORMAT ===

Respond with a JSON object containing:
{{
    "selected_slot_index": integer (the index of the free slot you chose, e.g., 5),
    "task_start_time": "ISO format datetime string (e.g., '2024-01-15T10:00:00Z')",
    "reasoning": "Detailed explanation of: (1) why this free slot was chosen, (2) why this specific start time within the slot is optimal, considering the task name, priority, description, and how it aligns with the selection criteria"
}}

IMPORTANT:
- Select exactly 1 free slot (by index)
- Choose a SPECIFIC START TIME within that free slot (in ISO format)
- The task_start_time must be >= free_slot_start and task_start_time + {estimated_time_minutes} minutes <= free_slot_end
- Your reasoning should demonstrate you considered all task information, available free slots, and the optimal time within the chosen slot
- Be specific about why this free slot and start time combination is optimal for this particular task"""
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
    
    # Create prompt with slots data
    if is_task:
        # For tasks: Create a summary and detailed presentation
        if slots_data:
            slots_summary = f"""
Total Available Slots: {len(slots_data)}
Time Range: {slots_data[0]['date']} {slots_data[0]['time']} to {slots_data[-1]['date']} {slots_data[-1]['time']}
Slots Meeting Duration Requirement ({required_duration_minutes} min): {sum(1 for s in slots_data if s['duration_minutes'] >= required_duration_minutes)}
"""
        else:
            slots_summary = "\nNo slots available.\n"
        
        prompt = f"""{system_prompt}

=== AVAILABLE FREE TIME SLOTS ===
{slots_summary}

Detailed Slot Information (sorted chronologically):
{json.dumps(slots_data, indent=2)}

=== YOUR TASK ===
Carefully analyze all the information above:
1. Review the task details (name: "{task_name}", priority: {priority}, duration: {estimated_time_minutes} min, description: "{task_description if task_description else 'N/A'}")
2. Examine all {len(slots_data)} available FREE TIME SLOTS (these are periods of free time, not task slots)
3. Apply the selection criteria based on priority ({priority}) and task characteristics
4. Choose ONE free slot that can accommodate the task
5. Select a SPECIFIC START TIME within that free slot for the {estimated_time_minutes}-minute task
6. Ensure your selected start time allows the task to complete within the free slot boundaries

NOTE: The task_start_time in your response should be in ISO format (e.g., "2024-01-15T10:00:00Z" or "2024-01-15T10:00:00+00:00"). Use the date and time from the free slot you selected, but choose the optimal hour and minute within that free period.

Response (JSON only):"""
    else:
        # For habits: Simpler presentation
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
        reasoning = result_data.get("reasoning", "")
        
        print(f"Select Slots: LLM reasoning = {reasoning}")
        
        # Handle task vs habit response format
        if is_task:
            # For tasks: LLM returns selected_slot_index and task_start_time
            selected_slot_index = result_data.get("selected_slot_index")
            task_start_time_str = result_data.get("task_start_time")
            
            print(f"Select Slots: LLM selected slot index = {selected_slot_index}")
            print(f"Select Slots: LLM selected task start time = {task_start_time_str}")
            
            if selected_slot_index is None or task_start_time_str is None:
                raise ValueError("LLM response missing selected_slot_index or task_start_time")
            
            # Find the free slot (1-based index from LLM, 0-based in list)
            slot_idx = selected_slot_index - 1
            if not (0 <= slot_idx < len(sorted_candidates)):
                raise ValueError(f"Selected slot index {selected_slot_index} is out of range")
            
            free_slot = sorted_candidates[slot_idx]
            free_slot_start = datetime.fromisoformat(free_slot["start"])
            free_slot_end = datetime.fromisoformat(free_slot["end"])
            
            # Parse the task start time
            task_start_time = datetime.fromisoformat(task_start_time_str.replace('Z', '+00:00'))
            if task_start_time.tzinfo is None:
                task_start_time = task_start_time.replace(tzinfo=free_slot_start.tzinfo)
            
            # Calculate task end time
            task_end_time = task_start_time + timedelta(minutes=estimated_time_minutes)
            
            # Validate that task fits within free slot
            if task_start_time < free_slot_start:
                print(f"Select Slots: WARNING - Task start time {task_start_time} is before free slot start {free_slot_start}. Adjusting to free slot start.")
                task_start_time = free_slot_start
                task_end_time = task_start_time + timedelta(minutes=estimated_time_minutes)
            
            if task_end_time > free_slot_end:
                print(f"Select Slots: WARNING - Task end time {task_end_time} exceeds free slot end {free_slot_end}. Adjusting to fit within slot.")
                task_end_time = free_slot_end
                task_start_time = task_end_time - timedelta(minutes=estimated_time_minutes)
                if task_start_time < free_slot_start:
                    raise ValueError(f"Task duration {estimated_time_minutes} minutes is too long for free slot")
            
            # Create the selected slot with specific start/end times
            selected_slot = {
                "start": task_start_time.isoformat(),
                "end": task_end_time.isoformat(),
                "duration_minutes": estimated_time_minutes,
                "original_free_slot_index": selected_slot_index
            }
            selected_slots = [selected_slot]
            
            print(f"Select Slots: Created task slot: {task_start_time} to {task_end_time} ({estimated_time_minutes} min)")
            print(f"Select Slots: Within free slot: {free_slot_start} to {free_slot_end} ({free_slot.get('duration_minutes', 0)} min)")
        else:
            # For habits: Use the old format with selected_indices
            selected_indices = result_data.get("selected_indices", [])
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
                if is_task:
                    # For tasks: create a slot with specific start/end times within the free slot
                    # Use the start of the free slot as the task start time
                    task_start_time = slot_start
                    task_end_time = task_start_time + timedelta(minutes=estimated_time_minutes)
                    
                    # Ensure it fits within the free slot
                    if task_end_time > slot_end:
                        task_end_time = slot_end
                        task_start_time = task_end_time - timedelta(minutes=estimated_time_minutes)
                        if task_start_time < slot_start:
                            # This slot is too small, skip it
                            continue
                    
                    selected_slot = {
                        "start": task_start_time.isoformat(),
                        "end": task_end_time.isoformat(),
                        "duration_minutes": estimated_time_minutes,
                        "original_free_slot_index": None  # Fallback, no index available
                    }
                    selected_slots.append(selected_slot)
                    print(f"Select Slots: Fallback - Created task slot: {task_start_time} to {task_end_time} ({estimated_time_minutes} min)")
                    break  # For tasks, we only need one slot
                else:
                    # For habits: use the slot as-is
                    selected_slots.append(slot)
                    last_selected_end_time = slot_end
        
        print(f"Select Slots: Fallback: Selected {len(selected_slots)} slot(s)")
        print("Select Slots: Slot selection complete")
        print("=" * 50)
        return {"selected_slots": selected_slots}