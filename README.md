# task-ai-poc
A POC for AI driven task manager scheduler

## Frontends

This project has two frontend implementations:

### 1. Original Frontend (`frontend/`)
The initial prototype frontend with basic chat and planning interfaces.

### 2. Figma Frontend (`figma-frontend/`)
A complete, production-ready UI exported from Figma with:
- Beautiful glassmorphism design
- Multi-step onboarding flow
- AI chat interface with natural language parsing
- Calendar views (Day/Week/Month)
- Advanced task management (List/Kanban views)
- Google Calendar integration
- Full accessibility support

The Figma frontend is built with React and Vite. See [figma-frontend/README.md](figma-frontend/README.md) for detailed documentation.

### Prerequisites
- Node.js (v18 or higher)
- npm (comes with Node.js)

### Running the Original Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The app will be available at `http://localhost:5173`.

### Running the Figma Frontend

1. Navigate to the figma-frontend directory:
   ```bash
   cd figma-frontend
   ```

2. Install dependencies (already done if following setup):
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The app will be available at `http://localhost:5173` (or next available port if 5173 is in use).

### Stopping the Servers

- If running in a terminal: Press `Ctrl+C`
- If running in the background: 
  ```bash
  lsof -ti:5173 | xargs kill -9
  ```

## Backend

The backend is a unified Flask API located in `app/api/app.py` that provides:

- **AI Agent Chat Interface** - Natural language planning and scheduling with LangGraph
- **Calendar Operations** - Direct CRUD operations for calendars and events
- **Health Check Endpoints** - Monitoring for both services

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (see AI Agent section)

### Running the API

Start the unified API server (port 5002):
```bash
python3 app/api/app.py
```

This single command starts the server with all endpoints available:
- Chat/AI endpoints at `/health` and `/chat`
- Calendar endpoints at `/calendar/*`

### API Documentation

Interactive Swagger/OpenAPI documentation is available when the API is running:

- **Unified API Docs**: http://localhost:5002/api-docs

The documentation includes all endpoints organized by tags:
- Health - Health check endpoints
- Chat - AI agent chat endpoints
- Calendars - Calendar management endpoints
- Events - Event management endpoints

For detailed endpoint documentation, see [app/api/README.md](app/api/README.md).

## AI Agent

The AI agent is built with LangGraph and located in `app/ai_agent`.

### Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

### Running the Agent

```bash
source venv/bin/activate
python3 app/ai_agent/run_agent.py
```

Or as a module:
```bash
python3 -m app.ai_agent.run_agent
```
