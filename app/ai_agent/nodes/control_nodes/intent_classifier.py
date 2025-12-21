"""Intent classification node - determines user intent from messages."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai_agent.state import AgentState


def intent_classifier(state: AgentState) -> AgentState:
    """
    Classify user intent into one of: HABIT_SCHEDULE, TASK_SCHEDULE, CALENDAR_ANALYSIS, UNKNOWN.
    
    Reads: messages
    Writes: intent_type
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    messages = state.get("messages", [])
    if not messages:
        return {"intent_type": "UNKNOWN"}
    
    # Get the last user message
    last_user_message = None
    for msg in reversed(messages):
        if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls'):
            last_user_message = msg.content
            break
    
    if not last_user_message:
        return {"intent_type": "UNKNOWN"}
    
    # Create prompt for intent classification
    system_prompt = """You are an intent classifier. Classify the user's intent into one of these categories:
- HABIT_SCHEDULE: User wants to schedule a recurring habit or routine
- TASK_SCHEDULE: User wants to schedule a one-time task or event
- CALENDAR_ANALYSIS: User wants to analyze or view their calendar
- UNKNOWN: Intent is unclear or doesn't fit the above categories

Respond with ONLY the intent type, nothing else."""
    
    prompt = f"{system_prompt}\n\nUser message: {last_user_message}\n\nIntent:"
    
    response = llm.invoke(prompt)
    intent_text = response.content.strip().upper()
    
    # Map response to valid intent type
    valid_intents = ["HABIT_SCHEDULE", "TASK_SCHEDULE", "CALENDAR_ANALYSIS", "UNKNOWN"]
    intent_type = "UNKNOWN"
    for valid_intent in valid_intents:
        if valid_intent in intent_text:
            intent_type = valid_intent
            break
    
    print(f"Intent classifier response: {response.content}")
    print(f"Intent type: {intent_type}")
    
    return {"intent_type": intent_type}