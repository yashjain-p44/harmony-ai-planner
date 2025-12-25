# AI Agent Module

This directory contains a sophisticated AI agent implementation using LangGraph for intelligent task and habit scheduling.

## Overview

The AI agent is a state machine that processes natural language requests to:
- **Classify user intent** (habit scheduling, task scheduling, calendar analysis)
- **Plan schedules** by extracting constraints and preferences
- **Find optimal time slots** by analyzing existing calendar events
- **Request human approval** before creating calendar events
- **Create calendar events** when approved

## Architecture

The agent uses LangGraph's `StateGraph` with a multi-stage workflow:

### State Management
- **AgentState**: TypedDict containing conversation history, planning artifacts, execution artifacts, and approval state
- See `state.py` for complete state schema

### Node Types

1. **Control Nodes** (`nodes/control_nodes/`):
   - `intent_classifier`: Determines user intent (HABIT_SCHEDULE, TASK_SCHEDULE, CALENDAR_ANALYSIS, UNKNOWN)
   - `habit_planner`: Extracts habit details and constraints from natural language
   - `execution_decider`: Decides whether to execute, dry-run, or cancel
   - `clarification_agent`: Asks for clarification when intent is unclear
   - `explanation_agent`: Provides explanations for infeasible plans

2. **Execution Nodes** (`nodes/`):
   - `fetch_calendar_events`: Retrieves existing calendar events
   - `normalize_calendar_events`: Normalizes timezones and formats
   - `compute_free_slots`: Finds available time windows
   - `filter_slots`: Applies constraints to filter slots
   - `select_slots`: Selects optimal slots for scheduling
   - `approval_node`: Prepares approval request for human review
   - `create_calendar_events`: Creates events in Google Calendar
   - `post_schedule_summary`: Generates completion summary

3. **Routing** (`router.py`):
   - Pure functions that route based on state (intent, plan_status, execution_decision, approval_state)

### Graph Flow

```
Entry → intent_classifier
  ├─→ HABIT_SCHEDULE → habit_planner → execution_decider
  │     ├─→ EXECUTE → fetch_calendar_events → normalize → compute_free_slots
  │     │     → filter_slots → select_slots → approval_node
  │     │       ├─→ APPROVED → create_calendar_events → post_schedule_summary → END
  │     │       ├─→ REJECTED → execution_decider
  │     │       └─→ CHANGES_REQUESTED → filter_slots (retry)
  │     ├─→ DRY_RUN → explanation_agent → END
  │     └─→ CANCEL → END
  ├─→ TASK_SCHEDULE → END (placeholder)
  ├─→ CALENDAR_ANALYSIS → END (placeholder)
  └─→ UNKNOWN → clarification_agent → END
```

See `graph.py` for the complete graph definition.

## Usage

### Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```env
OPENAI_API_KEY=your-api-key-here
```

3. Set up Google Calendar authentication (see main README)

### Running the Agent

#### Direct Execution

```python
from app.ai_agent.run_agent import run_agent

response = run_agent("Schedule daily exercise for 30 minutes")
print(response)
```

#### Command Line

```bash
python app/ai_agent/run_agent.py
```

Or as a module:
```bash
python -m app.ai_agent.run_agent
```

#### Via API

The agent is integrated into the Flask API at `/chat` endpoint. See `app/api/app.py` for details.

### Testing

Run comprehensive tests:
```bash
python app/ai_agent/test_comprehensive.py
python app/ai_agent/test_tool.py
```

## Tools

The agent has access to calendar tools (`tools/calendar_tools.py`):
- `get_calendar_events_tool`: Fetch calendar events
- `create_calendar_event_tool`: Create new calendar events
- `find_available_slots_tool`: Find available time slots

## Visualization

Generate a visual representation of the agent graph:
```bash
python app/ai_agent/visualize_agent_graph.py
```

This creates `agent_graph.png` showing the complete workflow.

## State Schema

The `AgentState` includes:
- **Messages**: Conversation history (HumanMessage, AIMessage, ToolMessage)
- **Intent & Routing**: intent_type, plan_status, execution_decision, approval_state
- **Planning Artifacts**: habit_definition, time_constraints, planning_horizon
- **Execution Artifacts**: calendar_events_raw, free_time_slots, selected_slots, created_events
- **Approval**: approval_state, approval_feedback, needs_approval_from_human

See `state.py` for complete schema with type annotations.

## Extending the Agent

To add new functionality:

1. **New Node**: Create in `nodes/` and register in `graph.py`
2. **New Tool**: Add to `tools/calendar_tools.py` and bind to LLM
3. **New Intent**: Add to `intent_classifier` and create corresponding flow
4. **New State Field**: Add to `AgentState` in `state.py`

## Files

- `graph.py`: Graph construction and compilation
- `state.py`: State schema definition
- `router.py`: Routing logic functions
- `run_agent.py`: Simple entry point for testing
- `nodes/`: All agent nodes (control and execution)
- `tools/`: LangChain tools for calendar operations
- `util/`: Utility functions (graph visualization)
