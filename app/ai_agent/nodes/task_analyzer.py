"""Task analyzer node - analyzes task, assigns priority, and estimates time."""

import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai_agent.state import AgentState


def task_analyzer(state: AgentState) -> AgentState:
    """
    Analyze a task: check/assign priority and estimate time required.
    
    Reads: task_data (from state), messages
    Writes: task_definition (with priority, estimated_duration_minutes), planning_horizon
    """
    print("[task_analyzer] Starting task analysis...")
    
    # Get task data from state
    task_data = state.get("task_data", {})
    messages = state.get("messages", [])
    
    if not task_data:
        print("[task_analyzer] No task data found, returning error")
        return {
            "failure_reason": "No task data provided",
            "explanation_payload": {
                "reason": "Missing task data",
                "message": "Task information is required for scheduling."
            }
        }
    
    task_title = task_data.get("title", "")
    task_notes = task_data.get("notes", "")
    task_due = task_data.get("due")
    existing_priority = task_data.get("priority")
    
    print(f"[task_analyzer] ===== TASK ANALYZER START =====")
    print(f"[task_analyzer] Analyzing task: '{task_title}'")
    print(f"[task_analyzer] Task ID: {task_data.get('id', 'N/A')}")
    print(f"[task_analyzer] Existing priority: {existing_priority or 'None (will be assigned)'}")
    print(f"[task_analyzer] Task notes: {task_notes[:100] if task_notes else 'None'}...")
    print(f"[task_analyzer] Task due date: {task_due or 'Not specified'}")
    print(f"[task_analyzer] Input state keys: {list(state.keys())}")
    
    # Use LLM to analyze task and determine priority/time estimate
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    # Build task description for LLM
    task_description = f"Title: {task_title}"
    if task_notes:
        task_description += f"\nNotes: {task_notes}"
    if task_due:
        task_description += f"\nDue date: {task_due}"
    
    system_prompt = """You are a task analysis assistant. Analyze the given task and provide:
1. Priority level (HIGH, MEDIUM, LOW) - consider urgency, importance, due dates
2. Estimated time to complete in minutes (be realistic based on task complexity)
3. Recommended time window for scheduling (e.g., "next 7 days", "next 3 days", "today")

Respond with a JSON object containing:
{
    "priority": "HIGH" | "MEDIUM" | "LOW",
    "estimated_duration_minutes": <number>,
    "scheduling_horizon_days": <number of days to look ahead>,
    "reasoning": "Brief explanation of your analysis"
}"""
    
    prompt = f"""{system_prompt}

Task to analyze:
{task_description}

Existing priority (if any): {existing_priority or "None"}

Analysis (JSON only):"""
    
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        analysis = json.loads(response_text)
        
        priority = analysis.get("priority", "MEDIUM")
        estimated_duration = analysis.get("estimated_duration_minutes", 60)
        horizon_days = analysis.get("scheduling_horizon_days", 7)
        reasoning = analysis.get("reasoning", "")
        
        # Use existing priority if it exists, otherwise use LLM-assigned priority
        final_priority = existing_priority if existing_priority else priority
        
        # Set up planning horizon
        now = datetime.now(timezone.utc)
        start_date = now
        end_date = now + timedelta(days=horizon_days)
        
        print(f"[task_analyzer] ===== LLM ANALYSIS RESULTS =====")
        print(f"[task_analyzer] Priority (from LLM): {priority}")
        print(f"[task_analyzer] Final priority (using existing if available): {final_priority}")
        print(f"[task_analyzer] Estimated duration: {estimated_duration} minutes")
        print(f"[task_analyzer] Scheduling horizon: {horizon_days} days")
        print(f"[task_analyzer] Planning window: {start_date.strftime('%Y-%m-%d %H:%M')} to {end_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"[task_analyzer] Reasoning: {reasoning}")
        
        # Create task definition (similar to habit_definition but for tasks)
        # Note: Due date update will be handled by update_task_due_date node
        task_definition = {
            "task_name": task_title,
            "task_id": task_data.get("id"),
            "priority": final_priority,
            "estimated_duration_minutes": estimated_duration,
            "notes": task_notes,
            "due": task_due  # Pass through original due date, update_task_due_date will handle if needed
        }
        
        planning_horizon = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "horizon_days": horizon_days
        }
        
        # Create a summary message
        summary_message = f"Analyzed task '{task_title}': Priority {final_priority}, estimated {estimated_duration} minutes. {reasoning}"
        analysis_message = AIMessage(content=summary_message)
        
        print(f"[task_analyzer] ===== TASK DEFINITION CREATED =====")
        print(f"[task_analyzer] Task definition: {json.dumps(task_definition, indent=2, default=str)}")
        print(f"[task_analyzer] Planning horizon: {json.dumps(planning_horizon, indent=2, default=str)}")
        print(f"[task_analyzer] ===== TASK ANALYZER END =====")
        
        return {
            "task_definition": task_definition,
            "planning_horizon": planning_horizon,
            "messages": messages + [analysis_message]
        }
        
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"[task_analyzer] ===== ERROR: LLM ANALYSIS FAILED =====")
        print(f"[task_analyzer] Error type: {type(e).__name__}")
        print(f"[task_analyzer] Error message: {str(e)}")
        print(f"[task_analyzer] Response text (first 500 chars): {response_text[:500] if 'response_text' in locals() else 'N/A'}")
        print(f"[task_analyzer] Falling back to default values...")
        # Fallback to defaults
        task_definition = {
            "task_name": task_title,
            "task_id": task_data.get("id"),
            "priority": existing_priority or "MEDIUM",
            "estimated_duration_minutes": 60,
            "notes": task_notes,
            "due": task_due
        }
        
        now = datetime.now(timezone.utc)
        planning_horizon = {
            "start_date": now.isoformat(),
            "end_date": (now + timedelta(days=7)).isoformat(),
            "horizon_days": 7
        }
        
        print(f"[task_analyzer] ===== FALLBACK TASK DEFINITION =====")
        print(f"[task_analyzer] Using default values: priority={task_definition['priority']}, duration=60min, horizon=7days")
        print(f"[task_analyzer] ===== TASK ANALYZER END (FALLBACK) =====")
        
        return {
            "task_definition": task_definition,
            "planning_horizon": planning_horizon
        }

