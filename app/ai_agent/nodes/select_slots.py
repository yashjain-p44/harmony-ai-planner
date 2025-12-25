"""Select slots node - chooses final slots for scheduling."""

from datetime import datetime, timedelta
from typing import List, Dict
import json

from langchain_openai import ChatOpenAI

from app.ai_agent.state import AgentState


def select_slots(state: AgentState) -> AgentState:
    """
    Select final slots from candidate slots for scheduling using LLM intelligence.
    
    Reads: filtered_slots (candidate_slots), habit_definition
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
    num_occurrences = habit_definition.get("num_occurrences")
    habit_name = habit_definition.get("habit_name", "habit")
    
    print(f"[select_slots] Selection criteria:")
    print(f"  - Habit: {habit_name}")
    print(f"  - Frequency: {frequency}")
    print(f"  - Required duration: {required_duration_minutes} minutes")
    print(f"  - Buffer between events: {buffer_minutes} minutes")
    print(f"  - Number of occurrences: {num_occurrences}")
    
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
    
    print(f"[select_slots] Target number of slots to select: {num_slots_to_select}")
    
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
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result_data = json.loads(response_text)
        selected_indices = result_data.get("selected_indices", [])
        reasoning = result_data.get("reasoning", "")
        
        print(f"[select_slots] LLM reasoning: {reasoning}")
        print(f"[select_slots] LLM selected indices: {selected_indices}")
        
        # Map indices back to actual slots
        selected_slots = []
        for idx in selected_indices:
            # Find slot with matching index (1-based from LLM, 0-based in list)
            slot_idx = idx - 1
            if 0 <= slot_idx < len(sorted_candidates):
                selected_slots.append(sorted_candidates[slot_idx])
                slot_start = datetime.fromisoformat(sorted_candidates[slot_idx]["start"])
                print(f"[select_slots] Selected slot {len(selected_slots)}: {slot_start} (duration: {sorted_candidates[slot_idx].get('duration_minutes', 0)} min)")
        
        # If LLM didn't select enough, fall back to simple selection
        if len(selected_slots) < num_slots_to_select and len(selected_slots) < len(sorted_candidates):
            print(f"[select_slots] LLM selected {len(selected_slots)} slots, but need {num_slots_to_select}. Adding more slots...")
            # Add remaining slots in order, ensuring buffer requirement
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
        
        print(f"[select_slots] Selected {len(selected_slots)} slots out of {len(candidate_slots)} candidates")
        return {"selected_slots": selected_slots}
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"[select_slots] LLM selection failed: {str(e)}. Falling back to simple selection...")
        # Fallback to simple selection logic
        selected_slots = []
        last_selected_end_time = None
        
        sorted_slots = sorted(
            candidate_slots,
            key=lambda s: datetime.fromisoformat(s["start"])
        )
        
        for slot in sorted_slots:
            if len(selected_slots) >= num_slots_to_select:
                break
            
            slot_start = datetime.fromisoformat(slot["start"])
            slot_end = datetime.fromisoformat(slot["end"])
            
            # Check buffer requirement
            if last_selected_end_time:
                gap_minutes = (slot_start - last_selected_end_time).total_seconds() / 60
                if gap_minutes < buffer_minutes:
                    continue
            
            # Check duration requirement
            if slot.get("duration_minutes", 0) >= required_duration_minutes:
                selected_slots.append(slot)
                last_selected_end_time = slot_end
        
        print(f"[select_slots] Fallback: Selected {len(selected_slots)} slots")
        return {"selected_slots": selected_slots}