# AI Task Scheduler & Calendar Assistant

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.3.1-61dafb.svg)](https://reactjs.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent AI-powered task scheduling and calendar management system that uses natural language to help users organize their time, schedule habits, and manage calendar events through Google Calendar integration.

## 🎯 Overview

This project combines a sophisticated LangGraph-based AI agent with a modern React frontend to provide an intuitive interface for:
- **Natural Language Task Scheduling**: Describe tasks in plain English and let the AI schedule them
- **Habit Planning**: Automatically schedule recurring habits based on your preferences
- **Calendar Analysis**: Get AI-powered insights about your schedule, busy periods, and free time
- **Calendar Integration**: Seamless Google Calendar sync with conflict detection
- **Human-in-the-Loop**: Approval workflow for scheduling decisions
- **Smart Time Slot Finding**: AI-powered free time detection and optimization

## ✨ Key Features

### AI Agent Capabilities
- **Intent Classification**: Automatically understands user intent (habit scheduling, task scheduling, calendar analysis)
- **Intelligent Planning**: Extracts task details, constraints, and preferences from natural language
- **Calendar Analysis**: Provides insights about schedule patterns, busy periods, free time, and event summaries
- **Insight Management**: Structures analysis requests with time windows and focus areas
- **Conflict Detection**: Analyzes existing calendar events to find optimal time slots
- **Approval Workflow**: Requests user confirmation before creating calendar events
- **Error Handling**: Graceful handling of infeasible plans with clear explanations

### Frontend Features
- **Modern UI**: Beautiful glassmorphism design with smooth animations
- **Multi-View Calendar**: Day, Week, and Month views
- **Task Management**: List and Kanban board views with filtering
- **Onboarding Flow**: Guided setup for new users
- **Real-time Updates**: Live calendar sync and status indicators
- **Accessibility**: WCAG 2.0 compliant with full keyboard navigation

### Backend API
- **RESTful API**: Comprehensive Flask API with Swagger documentation
- **Calendar Operations**: Full CRUD operations for calendars and events
- **Task Management**: Google Tasks integration
- **Streaming Support**: Real-time chat responses via Server-Sent Events
- **Health Monitoring**: Built-in health check endpoints

## 💡 Usage Examples

### Calendar Analysis
Ask the AI agent questions about your calendar:

```
"Show me my schedule this week"
"When am I free next week?"
"What meetings do I have this month?"
"Analyze my calendar for the next 7 days"
"Show me my busy periods"
```

The AI will:
- Extract the time window from your query
- Fetch relevant calendar events
- Generate insights about your schedule patterns
- Provide analysis without modifying any events

### Task Scheduling
```
"Schedule a meeting with John tomorrow at 2pm"
"Add a 1-hour workout session every Monday morning"
"Block 2 hours for deep work this Friday"
```

### Habit Planning
```
"Schedule daily exercise for 30 minutes"
"Add weekly team standup every Monday at 9am"
"Plan 1-hour reading time every evening"
```

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐
│  React Frontend │  (frontend/)
│  (TypeScript)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   Flask API     │  (app/api/app.py)
│   (Python)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph AI   │  (app/ai_agent/)
│     Agent       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Google Calendar │
│  & Tasks APIs   │
└─────────────────┘
```

### AI Agent Flow

The AI agent uses a state machine pattern with LangGraph to orchestrate complex scheduling workflows. The following diagram illustrates the complete agent graph with all nodes and routing paths:

![AI Agent Graph Nodes and Routing](/ai_agent_graph_nodes_routing.png)

#### Flow Overview

The agent graph consists of several node types that work together to process user requests:

- **Entry Point (Purple)**: Marks the beginning of a process
- **Control/Decision (Green)**: Decision points and control actions
- **Calendar Pipeline (Light Green/Teal)**: Steps involved in calendar interactions
- **Analysis (Purple)**: Analytical processes
- **Approval/Create (Orange)**: Human approval or event creation steps
- **Terminal (Red)**: End points of a flow (success, error, or cancellation)

**Note**: Tasks skip `filter_slots`, while Habits use it. This is a key distinction in the routing logic.

#### Main Flow Paths

**1. Intent Classification**
- The process begins at `START` and proceeds to `intent_classifier`, which classifies user intent into:
  - **UNKNOWN** → Leads to `clarification` (terminal)
  - **HABIT_SCHEDULE** → Routes to `habit_planner`
  - **TASK_SCHEDULE** → Routes to `task_analyzer`
  - **CALENDAR_ANALYSIS** → Routes to `insight_manager`

**2. Habit Scheduling Path**
- **`habit_planner`**: Plans recurring events
  - `NEEDS_CLARIFICATION` → `clarification` (terminal)
  - `PLAN_INFEASIBLE` → `explanation` (terminal)
  - `PLAN_READY` → `filter_slots` (habits-specific step)
- **`filter_slots`**: Filters available slots for habits
  - `CHANGES_REQUESTED` → Loops back to `habit_planner`
  - Primary flow → `select_slots`
- **`select_slots`**: Final slot selection
  - Routes to `approval`

**3. Task Scheduling Path**
- **`task_analyzer`**: Plans one-time events
  - `NEEDS_CLARIFICATION` → `clarification` (terminal)
  - `PLAN_INFEASIBLE` → `explanation` (terminal)
  - `PLAN_READY` → `execution_decider`
- **`execution_decider`**: Determines execution mode
  - `DRY_RUN` → `explanation` (terminal)
  - `PLAN_INFEASIBLE` → `explanation` (terminal)
  - `CANCEL` → `END (Cancel)` (terminal)
  - `EXECUTE` → `fetch_events`
- **Calendar Pipeline** (for tasks):
  - **`fetch_events`**: Fetches raw calendar events
  - **`normalize`**: Performs timezone alignment
  - **`compute_slots`**: Finds available time slots
    - `CALENDAR_ANALYSIS` → `calendar_insights` (terminal)
    - `TASK_SCHEDULE` → `select_slots`
- **`select_slots`**: Final slot selection
  - Routes to `approval`

**4. Calendar Analysis Path**
- **`insight_manager`**: Extracts analysis request details
  - Directly routes to `calendar_insights` (terminal)
  - Provides calendar insights without modifying events

**5. Common Approval & Creation Path** (for both Habits and Tasks)
- **`select_slots`** → **`approval`**: Human review step
  - `PENDING` → `END (Pending)` (terminal)
  - `APPROVED` → `create_events`
- **`create_events`**: Writes events to calendar
  - → `summary` (terminal, indicates completion)

#### Terminal Nodes

The flow can terminate at several points:
- **`clarification`**: User needs to provide more information
- **`explanation`**: Provides explanation for infeasible plans or dry-run results
- **`END (Cancel)`**: User explicitly cancelled the operation
- **`calendar_insights`**: Calendar analysis completed
- **`END (Pending)`**: Awaiting human approval
- **`summary`**: Successfully completed with events created

#### Flow Characteristics

- **Solid lines**: Represent primary flow paths
- **Dashed lines**: Represent error or alternative paths (clarifications, cancellations, infeasible plans)
- **Looping**: Habits can loop back from `filter_slots` to `habit_planner` if changes are requested
- **Parallel Processing**: Different intent types follow distinct paths but converge at common nodes like `select_slots` and `approval`

### Technical Implementation Details

#### LangGraph Architecture

The agent is built using **LangGraph 0.2+**, which provides a state machine framework for building complex AI agent workflows. The implementation follows these key patterns:

**1. StateGraph Construction**
- Uses `StateGraph(AgentState)` to create a typed state machine
- All nodes receive and return `AgentState` (TypedDict) for type safety
- State is immutable - nodes return partial state updates that are merged

**2. Node Registration**
```python
graph = StateGraph(AgentState)
graph.add_node("intent_classifier", intent_classifier.intent_classifier)
graph.add_node("habit_planner", habit_planner.habit_planner)
# ... more nodes
graph.set_entry_point("intent_classifier")
return graph.compile()
```

**3. Conditional Routing**
The graph uses conditional edges for dynamic routing based on state:

- **`add_conditional_edges(source, route_function, mapping)`**: Routes to different nodes based on route function output
- **Route Functions**: Pure functions in `router.py` that inspect state and return node names
- **Mapping**: Dictionary mapping route function outputs to target nodes

Example:
```python
graph.add_conditional_edges(
    "intent_classifier",
    route_by_intent,  # Pure function: AgentState -> str
    {
        "HABIT_SCHEDULE": "habit_planner",
        "TASK_SCHEDULE": "task_analyzer",
        "CALENDAR_ANALYSIS": "insight_manager",
        "UNKNOWN": "clarification_agent",
    },
)
```

**4. Static Edges**
For linear pipelines, static edges connect nodes sequentially:
```python
graph.add_edge("fetch_calendar_events", "normalize_calendar_events")
graph.add_edge("normalize_calendar_events", "compute_free_slots")
```

#### State Management

**AgentState Schema** (`app/ai_agent/state.py`):
- **TypedDict**: Provides type hints and validation
- **Annotated Fields**: Use `Annotated[type, "description"]` for documentation
- **Immutable Updates**: Nodes return partial state dictionaries that are merged

Key State Fields:
- `messages`: Conversation history (LangChain message objects)
- `intent_type`: Routing control (`HABIT_SCHEDULE`, `TASK_SCHEDULE`, `CALENDAR_ANALYSIS`, `UNKNOWN`)
- `plan_status`: Planning state (`PLAN_READY`, `NEEDS_CLARIFICATION`, `PLAN_INFEASIBLE`)
- `execution_decision`: Execution mode (`EXECUTE`, `DRY_RUN`, `CANCEL`)
- `approval_state`: Human approval status (`PENDING`, `APPROVED`, `REJECTED`, `CHANGES_REQUESTED`)
- Planning artifacts: `habit_definition`, `task_definition`, `time_constraints`, `planning_horizon`
- Execution artifacts: `calendar_events_raw`, `calendar_events_normalized`, `free_time_slots`, `filtered_slots`, `selected_slots`, `created_events`

**State Updates Pattern**:
```python
def node_function(state: AgentState) -> AgentState:
    # Read from state
    messages = state.get("messages", [])
    intent = state.get("intent_type", "UNKNOWN")
    
    # Process and compute new values
    result = process(messages)
    
    # Return partial state update (merged automatically)
    return {
        "plan_status": "PLAN_READY",
        "task_definition": result
    }
```

#### Routing Mechanism

**Pure Routing Functions** (`app/ai_agent/router.py`):
- No side effects (no LLM calls, API calls, or mutations)
- Inspect state and return node name or `END`
- Used in conditional edges for dynamic flow control

Key Routing Functions:
- `route_by_intent(state)`: Routes based on `intent_type`
- `route_by_plan_status(state)`: Routes based on `plan_status`
- `route_by_execution_decision(state)`: Routes based on `execution_decision`
- `route_by_approval_state(state)`: Routes based on `approval_state` (with intent-aware logic for `CHANGES_REQUESTED`)
- `route_by_intent_after_slots(state)`: Routes tasks to `select_slots`, habits to `filter_slots`
- `route_by_intent_after_normalize(state)`: Routes analysis to `calendar_insights`, scheduling to `compute_free_slots`

**Intent-Aware Routing Example**:
```python
def route_by_approval_state(state: AgentState) -> str:
    approval_state = state.get("approval_state", "PENDING")
    
    # For CHANGES_REQUESTED, route based on intent type
    if approval_state == "CHANGES_REQUESTED":
        intent_type = state.get("intent_type", "UNKNOWN")
        if intent_type == "TASK_SCHEDULE":
            return "select_slots"  # Tasks skip filter_slots
        else:
            return "filter_slots"  # Habits go through filter_slots
    
    return approval_state
```

#### Node Architecture

**Node Types**:

1. **Control Nodes** (`app/ai_agent/nodes/control_nodes/`):
   - Use LLMs (OpenAI GPT-4o-mini) for intelligent decision-making
   - Extract structured data from natural language
   - Return state updates with routing control fields
   - Examples: `intent_classifier`, `habit_planner`, `task_analyzer`, `execution_decider`

2. **Execution Nodes** (`app/ai_agent/nodes/`):
   - Perform concrete operations (API calls, data processing)
   - No LLM calls (pure computation)
   - Examples: `fetch_calendar_events`, `normalize_calendar_events`, `compute_free_slots`, `create_calendar_events`

3. **Hybrid Nodes**:
   - Combine LLM reasoning with execution
   - Examples: `select_slots` (uses LLM to select optimal slots), `calendar_insights` (uses LLM to generate insights)

**Node Implementation Pattern**:
```python
def node_function(state: AgentState) -> AgentState:
    """
    Node function that processes state and returns updates.
    
    Reads: messages, intent_type, ...
    Writes: plan_status, task_definition, ...
    """
    # Initialize LLM (if needed)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    
    # Extract relevant state
    messages = state.get("messages", [])
    
    # Process (LLM call, API call, computation)
    result = process(messages)
    
    # Return state update
    return {
        "plan_status": "PLAN_READY",
        "task_definition": result
    }
```

#### LLM Integration

**Model Configuration**:
- **Primary Model**: `gpt-4o-mini` (cost-effective, fast)
- **Temperature**: Varies by node (0.5 for planning, 0.7 for conversational)
- **Structured Outputs**: JSON parsing for structured data extraction

**LLM Usage Patterns**:

1. **Structured Extraction** (Planning Nodes):
   ```python
   system_prompt = """Extract JSON with task_name, estimated_time_minutes, ..."""
   response = llm.invoke(prompt)
   # Parse JSON from response
   task_data = json.loads(extract_json(response.content))
   ```

2. **Classification** (Intent/Routing):
   ```python
   prompt = f"Classify intent: {user_message}"
   response = llm.invoke(prompt)
   intent = parse_intent(response.content)
   ```

3. **Natural Language Generation** (Summaries, Explanations):
   ```python
   prompt = f"Generate summary: {context}"
   response = llm.invoke(prompt)
   summary = response.content
   ```

**Error Handling**:
- Try-catch blocks around LLM invocations
- Fallback to `NEEDS_CLARIFICATION` on errors
- JSON parsing with fallbacks (markdown code block extraction)

#### Conditional Flow Control

**Multi-Level Routing**:
1. **Intent Level**: Routes to different planners (habit vs task)
2. **Planning Level**: Routes based on plan feasibility
3. **Execution Level**: Routes based on execution decision (execute/dry-run/cancel)
4. **Approval Level**: Routes based on human approval state
5. **Intent-Aware Routing**: Different paths for habits vs tasks (filter_slots skipping)

**Looping Support**:
- Habits can loop: `filter_slots` → `approval` → `CHANGES_REQUESTED` → `filter_slots`
- Tasks can loop: `select_slots` → `approval` → `CHANGES_REQUESTED` → `select_slots`
- Prevents infinite loops through approval state management

#### Graph Compilation & Execution

**Compilation**:
```python
agent = create_agent()  # Returns compiled StateGraph
```

**Execution**:
```python
initial_state = {
    "messages": [HumanMessage(content="Schedule daily exercise")],
    "intent_type": "UNKNOWN",  # Will be set by intent_classifier
    # ... other initial state
}

result = agent.invoke(initial_state)
final_state = result  # Contains all state updates
```

**State Persistence**:
- State is passed through the graph automatically
- Each node receives full state, returns partial updates
- LangGraph merges updates automatically
- No manual state management needed

#### Error Handling & Edge Cases

**Error Handling Patterns**:
1. **LLM Errors**: Catch exceptions, return `NEEDS_CLARIFICATION` with helpful message
2. **JSON Parsing Errors**: Try multiple extraction strategies (markdown blocks, direct JSON)
3. **API Errors**: Handle in execution nodes, propagate through state
4. **Infeasible Plans**: Set `plan_status: PLAN_INFEASIBLE`, route to `explanation_agent`

**Terminal Nodes**:
- `clarification_agent`: Ends flow, requests user input
- `explanation_agent`: Ends flow, explains why plan failed
- `calendar_insights`: Ends flow, returns analysis results
- `post_schedule_summary`: Ends flow, returns completion summary
- `END`: Explicit termination point

#### Performance Considerations

**Optimization Strategies**:
- **Lazy Evaluation**: Nodes only execute when routed to
- **State Merging**: Efficient partial state updates
- **Model Selection**: `gpt-4o-mini` for cost/performance balance
- **Caching**: Calendar events cached in state (avoid redundant API calls)

**Scalability**:
- Stateless nodes (pure functions) enable horizontal scaling
- State can be serialized for distributed execution
- Graph structure supports async execution (LangGraph supports async nodes)

### Project Structure

```
task-ai-poc/
├── app/
│   ├── ai_agent/          # LangGraph AI agent implementation
│   │   ├── graph.py       # Agent graph definition
│   │   ├── state.py       # State schema
│   │   ├── router.py      # Routing logic
│   │   ├── nodes/         # Agent nodes (intent, planning, execution, insights)
│   │   │   └── control_nodes/  # Control nodes (insight_manager, calendar_insights)
│   │   └── tools/         # Calendar tools
│   ├── api/               # Flask REST API
│   │   ├── app.py         # Main API server
│   │   └── models/        # Pydantic request/response models
│   ├── src/               # Core repositories
│   │   ├── calendar_repository.py
│   │   ├── tasks_repository.py
│   │   └── google_auth_provider.py
│   └── creds/             # Credentials (gitignored)
├── frontend/              # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   └── styles/        # CSS/Tailwind styles
│   └── package.json
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 18+** with npm
- **Google Cloud Project** with Calendar and Tasks APIs enabled
- **OpenAI API Key** for the AI agent

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd task-ai-poc
   ```

2. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env file in project root
   cp .env.example .env  # If example exists
   
   # Add your API keys
   OPENAI_API_KEY=your-openai-api-key
   ```

4. **Set up Google Calendar authentication:**
   ```bash
   # Place your Google service account credentials in:
   # app/creds/ai-task-master-7dc79-firebase-adminsdk-fbsvc-9d2fe1e4e1.json
   # (See app/creds/*.json.example for format)
   
   # Or use OAuth flow (see app/src/AUTH_ARCHITECTURE.md)
   ```

5. **Set up frontend:**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the backend API:**
   ```bash
   # From project root
   python3 app/api/app.py
   ```
   The API will be available at `http://localhost:5002`
   - API Documentation: `http://localhost:5002/api-docs`

2. **Start the frontend (in a new terminal):**
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

3. **Test the AI agent directly (optional):**
   ```bash
   python3 app/ai_agent/run_agent.py
   ```

## 🧪 Testing

### Backend Tests

```bash
# Run AI agent tests
python3 tests/ai_agent/test_comprehensive.py
python3 tests/ai_agent/test_tool.py

# Run repository tests
python3 tests/src/test_calendar_repository.py
python3 tests/src/test_tasks_repository.py
python3 tests/src/test_firestore_repository.py
```

### API Testing

Use the Swagger UI at `http://localhost:5002/api-docs` to test endpoints interactively.

### Frontend Testing

```bash
cd frontend
npm test  # If test suite is configured
```

## 📚 Documentation

### API Documentation

- **Interactive Swagger UI**: `http://localhost:5002/api-docs`
- **API README**: [app/api/README.md](app/api/README.md)

### AI Agent Documentation

- **Agent README**: [app/ai_agent/README.md](app/ai_agent/README.md)
- **Architecture**: See Architecture section above

### Frontend Documentation

- **Frontend README**: [frontend/README.md](frontend/README.md)
- **Integration Guide**: [frontend/INTEGRATION_GUIDE.md](frontend/INTEGRATION_GUIDE.md)

### Authentication

- **Auth Architecture**: [app/src/AUTH_ARCHITECTURE.md](app/src/AUTH_ARCHITECTURE.md)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI API
OPENAI_API_KEY=your-key-here

# Google Calendar (if using OAuth)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5002/auth/callback

# API Configuration
API_PORT=5002
API_HOST=0.0.0.0
```

### Frontend Configuration

Edit `frontend/.env` (or create it):

```env
VITE_API_BASE_URL=http://localhost:5002
```

## 🛠️ Development

### Code Style

- **Python**: Follow PEP 8 style guide
- **TypeScript/React**: Use ESLint and Prettier configurations
- **Documentation**: Add docstrings to all functions and classes

### Adding New Features

1. **New AI Agent Node**: Add to `app/ai_agent/nodes/` and register in `graph.py`
2. **New API Endpoint**: Add route in `app/api/app.py` with Swagger documentation
3. **New Frontend Component**: Add to `frontend/src/components/`

### Debugging

- **Backend**: Use Python debugger or print statements (check console output)
- **Frontend**: Use browser DevTools and React DevTools
- **AI Agent**: Check state transitions in `app/ai_agent/state.py`

## 📦 Dependencies

### Backend (Python)
- **LangGraph**: Agent orchestration framework
- **LangChain**: LLM integration
- **Flask**: Web framework
- **Google API Client**: Calendar and Tasks integration
- **Pydantic**: Data validation

See [requirements.txt](requirements.txt) for complete list.

### Frontend (Node.js)
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Framer Motion**: Animations

See [frontend/package.json](frontend/package.json) for complete list.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---
