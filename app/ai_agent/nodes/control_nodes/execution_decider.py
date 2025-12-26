"""Execution decision node - decides whether to execute, dry-run, or cancel."""

from langchain_openai import ChatOpenAI
import json

from app.ai_agent.state import AgentState


def execution_decider(state: AgentState) -> AgentState:
    """
    Decide whether to execute, dry-run, or cancel the plan.
    
    Reads: plan (from habit_definition or task_definition)
    Writes: execution_decision
    """
    print("=" * 50)
    print("Execution Decider: Starting execution decision")
    print("=" * 50)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    habit_definition = state.get("habit_definition", {})
    task_definition = state.get("task_definition", {})
    plan_status = state.get("plan_status", "PLAN_INFEASIBLE")
    
    print(f"Execution Decider: Plan status = {plan_status}")
    print(f"Execution Decider: Has habit_definition = {bool(habit_definition)}")
    print(f"Execution Decider: Has task_definition = {bool(task_definition)}")
    
    if plan_status != "PLAN_READY":
        print(f"Execution Decider: Plan status is not PLAN_READY, returning CANCEL")
        print("=" * 50)
        return {"execution_decision": "CANCEL"}
    
    # Determine which definition to use (habit or task)
    plan_definition = habit_definition if habit_definition else task_definition
    plan_type = "habit" if habit_definition else "task"
    
    if not plan_definition:
        print("Execution Decider: No plan definition found, returning CANCEL")
        print("=" * 50)
        return {"execution_decision": "CANCEL"}
    
    print(f"Execution Decider: Using {plan_type} definition")
    print(f"Execution Decider: Plan definition = {plan_definition}")
    
    # Create decision prompt
    system_prompt = """You are an execution decision maker. Based on the plan, decide whether to:
- EXECUTE: Proceed with creating calendar events
- DRY_RUN: Show what would be scheduled without actually creating events
- CANCEL: Do not proceed with scheduling

Respond with ONLY one word: EXECUTE, DRY_RUN, or CANCEL"""
    
    plan_str = json.dumps(plan_definition, indent=2)
    prompt = f"{system_prompt}\n\nPlan ({plan_type}):\n{plan_str}\n\nDecision:"
    
    print(f"Execution Decider: Invoking LLM for execution decision...")
    response = llm.invoke(prompt)
    decision_text = response.content.strip().upper()
    
    print(f"Execution Decider: LLM response = {response.content}")
    print(f"Execution Decider: Decision text = {decision_text}")
    
    # Map response to valid decision
    valid_decisions = ["EXECUTE", "DRY_RUN", "CANCEL"]
    execution_decision = "CANCEL"
    for valid_decision in valid_decisions:
        if valid_decision in decision_text:
            execution_decision = valid_decision
            break
    
    print(f"Execution Decider: Final execution decision = {execution_decision}")
    print("=" * 50)
    
    return {"execution_decision": execution_decision}