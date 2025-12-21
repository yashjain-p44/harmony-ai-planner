"""Execution decision node - decides whether to execute, dry-run, or cancel."""

from langchain_openai import ChatOpenAI
import json

from app.ai_agent.state import AgentState


def execution_decider(state: AgentState) -> AgentState:
    """
    Decide whether to execute, dry-run, or cancel the plan.
    
    Reads: plan (from habit_definition)
    Writes: execution_decision
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    habit_definition = state.get("habit_definition", {})
    plan_status = state.get("plan_status", "PLAN_INFEASIBLE")
    
    if plan_status != "PLAN_READY":
        return {"execution_decision": "CANCEL"}
    
    if not habit_definition:
        return {"execution_decision": "CANCEL"}
    
    # Create decision prompt
    system_prompt = """You are an execution decision maker. Based on the plan, decide whether to:
- EXECUTE: Proceed with creating calendar events
- DRY_RUN: Show what would be scheduled without actually creating events
- CANCEL: Do not proceed with scheduling

Respond with ONLY one word: EXECUTE, DRY_RUN, or CANCEL"""
    
    plan_str = json.dumps(habit_definition, indent=2)
    prompt = f"{system_prompt}\n\nPlan:\n{plan_str}\n\nDecision:"
    
    response = llm.invoke(prompt)
    decision_text = response.content.strip().upper()
    
    # Map response to valid decision
    valid_decisions = ["EXECUTE", "DRY_RUN", "CANCEL"]
    execution_decision = "CANCEL"
    for valid_decision in valid_decisions:
        if valid_decision in decision_text:
            execution_decision = valid_decision
            break
    
    return {"execution_decision": execution_decision}