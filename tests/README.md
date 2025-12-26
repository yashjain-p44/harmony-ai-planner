# Tests

This directory contains all test files for the project, organized by module.

## Directory Structure

- `ai_agent/` - Tests for the AI agent functionality
  - `test_comprehensive.py` - Comprehensive test suite for AI agent with tools
  - `test_new_tools.py` - Tests for new tool functionality
  - `test_tool.py` - Basic tool tests

- `src/` - Tests for repository and source modules
  - `test_calendar_repository.py` - Tests for Google Calendar Repository
  - `test_firestore_repository.py` - Tests for Firestore Repository
  - `test_tasks_repository.py` - Tests for Google Tasks Repository

## Running Tests

You can run individual test files:

```bash
# Run AI agent tests
python tests/ai_agent/test_comprehensive.py
python tests/ai_agent/test_new_tools.py
python tests/ai_agent/test_tool.py

# Run repository tests
python tests/src/test_calendar_repository.py
python tests/src/test_firestore_repository.py
python tests/src/test_tasks_repository.py
```

Some tests may require additional setup:
- Calendar and Tasks repository tests require valid OAuth tokens
- Firestore tests require Firebase credentials
- AI agent tests may require environment variables (check individual test files)

