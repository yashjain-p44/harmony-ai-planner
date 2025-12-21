"""Explanation agent node - provides explanations to the user."""

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.ai_agent.state import AgentState


def explanation_agent(state: AgentState) -> AgentState:
    """
    Generate explanations for the user.
    
    Reads: plan (from habit_definition) OR failure_reason
    Writes: messages (append assistant explanation)
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    messages = state.get("messages", [])
    habit_definition = state.get("habit_definition", {})
    failure_reason = state.get("failure_reason")
    plan_status = state.get("plan_status", "PLAN_INFEASIBLE")
    execution_decision = state.get("execution_decision")
    created_events = state.get("created_events", [])
    
    # Determine what to explain
    if failure_reason:
        explanation_context = f"Failure reason: {failure_reason}"
    elif plan_status == "PLAN_INFEASIBLE":
        explanation_context = "The requested plan is not feasible."
    elif execution_decision == "DRY_RUN":
        # Explain what would be scheduled
        explanation_context = f"Dry run mode. Plan: {habit_definition}. Would create {len(created_events)} events."
    elif created_events:
        # Explain what was scheduled
        explanation_context = f"Successfully scheduled {len(created_events)} events based on plan: {habit_definition}"
    else:
        explanation_context = f"Plan status: {plan_status}"
    
    # Generate explanation
    system_prompt = """You are a helpful assistant explaining scheduling results to the user. Be clear and concise."""
    prompt = f"{system_prompt}\n\nContext: {explanation_context}\n\nYour explanation:"
    
    response = llm.invoke(prompt)
    explanation_message = AIMessage(content=response.content)
    
    return {"messages": messages + [explanation_message]}