# task-ai-poc
A POC for AI driven task manager scheduler

## Frontend

The frontend is built with React and Vite. It's located in the `frontend` directory.

### Prerequisites
- Node.js (v16 or higher)
- npm (comes with Node.js)

### Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

### Running the Frontend

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173` and will automatically open in your browser.

### Stopping the Server

- If running in a terminal: Press `Ctrl+C`
- If running in the background: 
  ```bash
  lsof -ti:5173 | xargs kill -9
  ```

## Backend

Backend API documentation coming soon...

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
