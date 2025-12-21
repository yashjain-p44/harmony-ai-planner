"""Graph construction and configuration for LangGraph agents."""

from langgraph.graph import StateGraph, END

from app.ai_agent.state import AgentState
from app.ai_agent.nodes import fetch_calendar_events, normalize_calendar_events, compute_free_slots, filter_slots, select_slots, create_calendar_events, post_schedule_summary
from app.ai_agent.nodes.control_nodes import intent_classifier, habit_planner, execution_decider, clarification_agent, explanation_agent
from app.ai_agent.router import route_by_intent, route_by_plan_status, route_by_execution_decision


def create_agent():
    """
    Create and compile a LangGraph agent with tool support.
    
    Returns:
        Compiled StateGraph ready to use
    """
    # Create the graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    # Register nodes
    graph.add_node("intent_classifier", intent_classifier.intent_classifier)
    graph.add_node("habit_planner", habit_planner.habit_planner)
    graph.add_node("execution_decider", execution_decider.execution_decider)
    graph.add_node("clarification_agent", clarification_agent.clarification_agent)
    graph.add_node("explanation_agent", explanation_agent.explanation_agent)

    graph.add_node("fetch_calendar_events", fetch_calendar_events.fetch_calendar_events)
    graph.add_node("normalize_calendar_events", normalize_calendar_events.normalize_calendar_events)
    graph.add_node("compute_free_slots", compute_free_slots.compute_free_slots)
    graph.add_node("filter_slots", filter_slots.filter_slots)
    graph.add_node("select_slots", select_slots.select_slots)
    graph.add_node("create_calendar_events", create_calendar_events.create_calendar_events)
    graph.add_node("post_schedule_summary", post_schedule_summary.post_schedule_summary)
    
    # Entry point
    graph.set_entry_point("intent_classifier")
    
    # Conditional routing — intent
    graph.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "HABIT_SCHEDULE": "habit_planner",
            "TASK_SCHEDULE": END,            # placeholder
            "CALENDAR_ANALYSIS": END,         # placeholder
            "UNKNOWN": "clarification_agent",
        },
    )

    # Conditional routing — planning
    graph.add_conditional_edges(
        "habit_planner",
        route_by_plan_status,
        {
            "PLAN_READY": "execution_decider",
            "NEEDS_CLARIFICATION": "clarification_agent",
            "PLAN_INFEASIBLE": "explanation_agent",
        },
    )

    # Conditional routing — execution
    graph.add_conditional_edges(
        "execution_decider",
        route_by_execution_decision,
        {
            "EXECUTE": "fetch_calendar_events",
            "DRY_RUN": "explanation_agent",
            "CANCEL": END,
        },
    )

    # Static execution pipeline
    graph.add_edge("fetch_calendar_events", "normalize_calendar_events")
    graph.add_edge("normalize_calendar_events", "compute_free_slots")
    graph.add_edge("compute_free_slots", "filter_slots")
    graph.add_edge("filter_slots", "select_slots")
    graph.add_edge("select_slots", "create_calendar_events")
    graph.add_edge("create_calendar_events", "post_schedule_summary")
    
    # Terminal edges
    graph.add_edge("post_schedule_summary", END)
    graph.add_edge("clarification_agent", END)
    graph.add_edge("explanation_agent", END)
    
    # Compile the graph
    return graph.compile()

# if __name__ == "__main__":
#     graph = create_agent()
#     print("Graph created")
#     # graph.get_graph().draw_mermaid_png()
