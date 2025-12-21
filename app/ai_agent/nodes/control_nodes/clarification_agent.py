"""Clarification agent node - asks user for clarification."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai_agent.state import AgentState


def clarification_agent(state: AgentState) -> AgentState:
    """
    Generate clarification questions for the user.
    
    Reads: clarification_questions (from explanation_payload)
    Writes: messages (append assistant clarification message)
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    messages = state.get("messages", [])
    explanation_payload = state.get("explanation_payload", {})
    clarification_questions = explanation_payload.get("clarification_questions", [])
    
    if not clarification_questions:
        # Generate generic clarification
        clarification_text = "I need more information to help you schedule this. Could you provide more details?"
    else:
        # Format questions nicely
        if len(clarification_questions) == 1:
            clarification_text = f"I need to clarify: {clarification_questions[0]}"
        else:
            questions_list = "\n".join(f"- {q}" for q in clarification_questions)
            clarification_text = f"I need some clarification:\n{questions_list}"
    
    # Use LLM to make the clarification message more natural
    system_prompt = """You are a helpful assistant asking for clarification. Make your message friendly and conversational."""
    prompt = f"{system_prompt}\n\nQuestions to ask: {clarification_text}\n\nYour message:"
    
    response = llm.invoke(prompt)
    clarification_message = AIMessage(content=response.content)
    
    return {"messages": messages + [clarification_message]}