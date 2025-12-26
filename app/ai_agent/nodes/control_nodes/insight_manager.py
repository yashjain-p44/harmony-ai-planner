"""Insight manager node - extracts and structures analysis request details from user input."""

from langchain_openai import ChatOpenAI
import json
from datetime import datetime, timedelta, timezone

from app.ai_agent.state import AgentState


def insight_manager(state: AgentState) -> AgentState:
    """
    Extract and structure analysis request details from user input.
    
    This node processes the user's calendar analysis request and extracts:
    - User's prompt/query
    - Intent type
    - Time window for analysis
    - Any specific analysis requirements
    
    Reads: messages, intent_type
    Writes: insight_request (structured analysis request), planning_horizon (time window)
    """
    print("=" * 50)
    print("Insight Manager: Starting insight request analysis")
    print("=" * 50)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    messages = state.get("messages", [])
    intent_type = state.get("intent_type", "UNKNOWN")
    
    print(f"Insight Manager: Intent type = {intent_type}")
    
    if intent_type != "CALENDAR_ANALYSIS":
        print(f"Insight Manager: Intent mismatch. Expected CALENDAR_ANALYSIS, got {intent_type}")
        print("=" * 50)
        return {
            "insight_request": {},
            "planning_horizon": {}
        }
    
    # Extract user message
    user_message = ""
    for msg in reversed(messages):
        if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls'):
            user_message = msg.content
            break
    
    print(f"Insight Manager: User message = {user_message}")
    
    # Get current date and time for context
    today = datetime.now(timezone.utc)
    today_str = today.strftime("%Y-%m-%d")
    today_day_name = today.strftime("%A")
    today_time = today.strftime("%H:%M:%S")
    today_datetime = today.strftime("%Y-%m-%d %H:%M:%S")
    tomorrow = today + timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    tomorrow_day_name = tomorrow.strftime("%A")
    
    print(f"Insight Manager: Today is {today_day_name}, {today_str} at {today_time}")
    print(f"Insight Manager: Tomorrow is {tomorrow_day_name}, {tomorrow_str}")
    
    # Create prompt for extracting insight request details
    system_prompt = f"""You are an insight request analyzer. Extract structured information from the user's calendar analysis request.

CURRENT DATE AND TIME CONTEXT:
- Current date and time: {today_datetime} ({today_day_name})
- Today is {today_day_name}, {today_str}
- Current time: {today_time}
- Tomorrow is {tomorrow_day_name}, {tomorrow_str}

Use this date and time context to understand temporal references in the user's request (e.g., "this week", "next month", "last 7 days", "upcoming events").

Respond with a JSON object containing:
{{
    "insight_request": {{
        "user_prompt": "string (the original user query/prompt)",
        "intent": "CALENDAR_ANALYSIS",
        "analysis_type": "string (e.g., 'busy_periods', 'free_time', 'event_summary', 'schedule_overview', 'conflicts', 'general')",
        "focus_areas": ["area1", "area2"] (optional, specific aspects to analyze like 'meetings', 'work hours', 'personal time'),
        "time_window_description": "string (human-readable description of the time window, e.g., 'next 7 days', 'this month')"
    }},
    "planning_horizon": {{
        "start_date": "ISO 8601 datetime string (UTC, e.g., '{today.isoformat()}')",
        "end_date": "ISO 8601 datetime string (UTC, e.g., '{(today + timedelta(days=30)).isoformat()}')"
    }}
}}

For planning_horizon:
- Extract time window from phrases like "this week", "next month", "last 7 days", "upcoming events", "today", "tomorrow"
- If no time window is specified, default to next 30 days from today
- start_date should be today (or the specified start) in UTC
- end_date should be calculated based on the time window mentioned
- Use ISO 8601 format with timezone (e.g., "2024-01-15T10:30:00+00:00")

For analysis_type:
- "busy_periods": User wants to know when they're busy
- "free_time": User wants to know available/free time
- "event_summary": User wants a summary of events
- "schedule_overview": User wants an overview of their schedule
- "conflicts": User wants to identify scheduling conflicts
- "general": General calendar analysis or insights

Examples:
- "Show me my schedule this week" → analysis_type: "schedule_overview", time_window: this week
- "When am I free next week?" → analysis_type: "free_time", time_window: next week
- "What meetings do I have?" → analysis_type: "event_summary", focus_areas: ["meetings"]
- "Analyze my calendar" → analysis_type: "general", time_window: default (30 days)"""
    
    prompt = f"{system_prompt}\n\nUser request: {user_message}\n\nResponse (JSON only):"
    
    print("Insight Manager: Invoking LLM for insight request analysis...")
    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
    except Exception as e:
        # Handle LLM invocation errors
        print(f"Insight Manager: Error invoking LLM - {type(e).__name__}: {e}")
        print("Insight Manager: Using defaults")
        print("=" * 50)
        # Default to next 30 days
        default_end = today + timedelta(days=30)
        return {
            "insight_request": {
                "user_prompt": user_message,
                "intent": "CALENDAR_ANALYSIS",
                "analysis_type": "general",
                "time_window_description": "next 30 days"
            },
            "planning_horizon": {
                "start_date": today.isoformat(),
                "end_date": default_end.isoformat()
            }
        }
    
    print(f"Insight Manager: LLM response = {response_text}")
    
    # Try to extract JSON from response
    try:
        # Remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(response_text)
        print(f"Insight Manager: Parsed data = {data}")
        
        insight_request = data.get("insight_request", {})
        planning_horizon = data.get("planning_horizon", {})
        
        # Validate and set defaults
        if not insight_request.get("user_prompt"):
            insight_request["user_prompt"] = user_message
        
        if not insight_request.get("intent"):
            insight_request["intent"] = "CALENDAR_ANALYSIS"
        
        if not insight_request.get("analysis_type"):
            insight_request["analysis_type"] = "general"
        
        # Ensure planning_horizon has valid dates
        if not planning_horizon.get("start_date"):
            planning_horizon["start_date"] = today.isoformat()
        
        if not planning_horizon.get("end_date"):
            default_end = today + timedelta(days=30)
            planning_horizon["end_date"] = default_end.isoformat()
        
        print(f"Insight Manager: Insight request = {insight_request}")
        print(f"Insight Manager: Planning horizon = {planning_horizon}")
        print("Insight Manager: Insight request analysis complete")
        print("=" * 50)
        
        return {
            "insight_request": insight_request,
            "planning_horizon": planning_horizon
        }
    except (json.JSONDecodeError, KeyError) as e:
        # If parsing fails, use defaults
        print(f"Insight Manager: Error parsing JSON response - {type(e).__name__}: {e}")
        print(f"Insight Manager: Raw response text = {response_text}")
        print("Insight Manager: Using defaults")
        print("=" * 50)
        default_end = today + timedelta(days=30)
        return {
            "insight_request": {
                "user_prompt": user_message,
                "intent": "CALENDAR_ANALYSIS",
                "analysis_type": "general",
                "time_window_description": "next 30 days"
            },
            "planning_horizon": {
                "start_date": today.isoformat(),
                "end_date": default_end.isoformat()
            }
        }

