"""Intent classification node for determining user intent from input."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from app.ai_agent.state import AgentState


def intent_node(state: AgentState) -> AgentState:
    """
    Classify user intent from the conversation.
    
    This node analyzes the user's message to determine their intent:
    - schedule_meeting: User wants to create/schedule a calendar event
    - query_events: User wants to see/list existing calendar events
    - find_slots: User wants to find available time slots
    - general_chat: General conversation or unclear intent
    
    Args:
        state: Current state containing messages
        
    Returns:
        Updated state with intent field set
    """
    # Use a lightweight, fast model for intent classification
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Get the last user message
    messages = state.get("messages", [])
    if not messages:
        return {"intent": "general_chat"}
    
    # Find the last human message
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break
    
    if not last_user_message:
        return {"intent": "general_chat"}
    
    # Create intent classification prompt
    intent_prompt = f"""You are an intent classifier for a calendar scheduling assistant.

Analyze the user's message and classify their intent into one of these categories:

1. schedule_meeting - User wants to create, schedule, or book a calendar event/meeting
   Examples: "Schedule a meeting", "Book a call", "Create an event", "Set up a meeting with John"

2. query_events - User wants to see, list, or check existing calendar events
   Examples: "What meetings do I have?", "Show my calendar", "What's on my schedule today?"

3. find_slots - User wants to find available time slots or check availability
   Examples: "When am I free?", "Find available slots", "What times work for me?"

4. general_chat - General conversation, greetings, or unclear intent
   Examples: "Hello", "How are you?", "What can you do?"

User message: "{last_user_message}"

Respond with ONLY the intent category name (schedule_meeting, query_events, find_slots, or general_chat).
Do not include any explanation or additional text."""

    # Classify intent
    response = llm.invoke(intent_prompt)
    intent = response.content.strip().lower()
    
    # Validate and normalize intent
    valid_intents = ["schedule_meeting", "query_events", "find_slots", "general_chat"]
    if intent not in valid_intents:
        # Fallback to general_chat if invalid response
        intent = "general_chat"
    
    print(f"🎯 Intent classified: {intent}")
    
    # Update state with intent
    return {"intent": intent}
