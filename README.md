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

The AI agent uses a state machine pattern with LangGraph with three main flows:

#### Scheduling Flow (Habits & Tasks)
1. **Intent Classification** → Determines user intent (habit, task, analysis)
2. **Planning Phase** → Extracts requirements and constraints
3. **Execution Decision** → Decides whether to execute, dry-run, or cancel
4. **Calendar Fetching** → Retrieves existing events from Google Calendar
5. **Slot Computation** → Finds free time slots
6. **Filtering & Selection** → Applies constraints and selects optimal slots
7. **Approval** → Requests user confirmation
8. **Event Creation** → Creates calendar events if approved
9. **Summary** → Provides completion summary

#### Calendar Analysis Flow
1. **Intent Classification** → Identifies calendar analysis intent
2. **Insight Management** → Extracts analysis request details (time window, focus areas, analysis type)
3. **Calendar Fetching** → Retrieves events for the specified time window
4. **Event Normalization** → Normalizes and timezone-aligns events
5. **Insights Generation** → Generates AI-powered insights about the calendar

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
python3 app/ai_agent/test_comprehensive.py
python3 app/ai_agent/test_tool.py

# Run repository tests
python3 app/src/test_calendar_repository.py
python3 app/src/test_tasks_repository.py
python3 app/src/test_firestore_repository.py
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
