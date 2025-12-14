# AI Agent Module

This directory contains AI agent implementations using LangGraph.

## Simple Agent

The `run_agent.py` file contains a basic single-node LangGraph agent that:
- Takes user input as a message
- Processes it through an LLM (OpenAI GPT-4o-mini)
- Returns the AI response

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

### Running the Agent

```python
from app.ai_agent.run_agent import run_agent

response = run_agent("Hello! How are you?")
print(response)
```

Or run directly:
```bash
python app/ai_agent/run_agent.py
```

Or as a module:
```bash
python -m app.ai_agent.run_agent
```

## Architecture

The agent uses LangGraph's `StateGraph` with:
- **State**: `AgentState` containing a list of messages
- **Node**: Single `agent_node` that processes messages and generates responses
- **Flow**: Entry point → agent node → END

This is the simplest possible LangGraph agent - a single node that processes input and returns output.
