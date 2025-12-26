"""Calendar insights node - provides analysis and insights about the user's calendar."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai_agent.state import AgentState


def calendar_insights(state: AgentState) -> AgentState:
    """
    Generate insights and analysis about the user's calendar.
    
    This node analyzes calendar events to provide insights to the user.
    It does NOT modify any calendar events - it is read-only.
    
    Reads: messages, calendar_events_raw (optional), calendar_events_normalized (optional)
    Writes: messages (append assistant insights)
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    messages = state.get("messages", [])
    calendar_events_raw = state.get("calendar_events_raw", [])
    calendar_events_normalized = state.get("calendar_events_normalized", [])
    insight_request = state.get("insight_request", {})
    
    # Use normalized events if available, otherwise use raw events
    events_to_analyze = calendar_events_normalized if calendar_events_normalized else calendar_events_raw
    
    # Get the user prompt from insight_request if available, otherwise from messages
    user_prompt = insight_request.get("user_prompt") if insight_request else None
    if not user_prompt:
        # Fallback to last user message
        for msg in reversed(messages):
            if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls'):
                user_prompt = msg.content
                break
    
    # Prepare calendar data summary for the LLM
    events_summary = ""
    if events_to_analyze:
        events_summary = f"Found {len(events_to_analyze)} calendar events to analyze."
        # Include a sample of events for context
        sample_events = events_to_analyze[:10]  # First 10 events
        events_summary += f"\n\nSample events:\n"
        for i, event in enumerate(sample_events, 1):
            summary = event.get("summary", "No title")
            start = event.get("start", {})
            end = event.get("end", {})
            events_summary += f"{i}. {summary} ({start} - {end})\n"
    else:
        events_summary = "No calendar events found in the current state."
    
    # Create prompt for insights generation
    # TODO: This prompt will be refined in more detail later
    system_prompt = """You are a helpful calendar assistant that provides insights and analysis about the user's calendar.
You should analyze the calendar events and provide meaningful insights based on the user's query.
Do NOT suggest modifying or creating calendar events - this is a read-only analysis.
Be clear, concise, and helpful."""
    
    user_query_context = f"User query: {user_prompt}" if user_prompt else "User wants calendar analysis."
    
    # Include insight request details if available
    analysis_context = ""
    if insight_request:
        analysis_type = insight_request.get("analysis_type", "general")
        time_window = insight_request.get("time_window_description", "")
        focus_areas = insight_request.get("focus_areas", [])
        analysis_context = f"\n\nAnalysis request details:\n- Analysis type: {analysis_type}"
        if time_window:
            analysis_context += f"\n- Time window: {time_window}"
        if focus_areas:
            analysis_context += f"\n- Focus areas: {', '.join(focus_areas)}"
    
    prompt = f"""{system_prompt}

{user_query_context}{analysis_context}

Calendar data:
{events_summary}

Provide your insights and analysis:"""
    
    response = llm.invoke(prompt)
    insights_message = AIMessage(content=response.content)
    
    return {"messages": messages + [insights_message]}

