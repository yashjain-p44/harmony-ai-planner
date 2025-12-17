# Scheduler AI Agent API

Unified Flask REST API for the scheduler application with AI agent chat and calendar operations.

This directory contains:
- `app.py` - Unified API with AI chat interface and calendar operations
- `models.py` - Pydantic models for request/response validation

## Interactive API Documentation

Swagger/OpenAPI documentation is available when the API is running:
- **Unified API**: http://localhost:5002/api-docs

The Swagger UI provides interactive documentation with request/response schemas and the ability to test endpoints directly. All endpoints are organized by tags:
- **Health** - Health check endpoints
- **Chat** - AI agent chat endpoints  
- **Calendars** - Calendar management endpoints
- **Events** - Event management endpoints

## Chat & AI Agent Endpoints

### GET /health
Health check endpoint for the main API.

**Response:**
```json
{
  "status": "healthy",
  "service": "scheduler-api"
}
```

### POST /chat
Chat with the AI agent for natural language planning and scheduling.

**Request Body:**
```json
{
  "prompt": "Schedule a meeting with John tomorrow at 2pm",
  "state": {
    "messages": [...],
    "needs_approval_from_human": false
  }
}
```

The `state` field is optional and used for conversation continuity and human-in-the-loop scenarios.

**Response:**
```json
{
  "success": true,
  "response": "I've scheduled a meeting with John tomorrow at 2pm.",
  "prompt": "Schedule a meeting with John tomorrow at 2pm",
  "messages": [...],
  "needs_approval_from_human": false,
  "state": {
    "messages": [...],
    "needs_approval_from_human": false
  },
  "error": null
}
```

When `needs_approval_from_human` is true, the agent is awaiting confirmation before executing actions. Return the state in the next request to continue the conversation.

## Calendar API Endpoints

### GET /calendar/health
Health check endpoint for calendar API.

### GET /calendar/calendars
List all calendars accessible by the user.

**Response:**
```json
{
  "success": true,
  "calendars": [...],
  "count": 5
}
```

### GET /calendar/calendars/<calendar_id>
Get a specific calendar by ID.

**Response:**
```json
{
  "success": true,
  "calendar": {...}
}
```

### GET /calendar/events
List events from a calendar.

**Query Parameters:**
- `calendar_id` (optional, default: "primary")
- `time_min` (optional) - ISO format datetime
- `time_max` (optional) - ISO format datetime
- `max_results` (optional, default: 10)
- `single_events` (optional, default: true)
- `order_by` (optional, default: "startTime")

**Response:**
```json
{
  "success": true,
  "events": [...],
  "count": 10
}
```

### GET /calendar/events/<event_id>
Get a specific event by ID.

**Query Parameters:**
- `calendar_id` (optional, default: "primary")

**Response:**
```json
{
  "success": true,
  "event": {...}
}
```

### POST /calendar/events
Create a new calendar event.

**Request Body:**
```json
{
  "summary": "Meeting",
  "start_time": "2024-01-15T10:00:00Z",
  "end_time": "2024-01-15T11:00:00Z",
  "description": "Team meeting",
  "location": "Conference Room A",
  "attendees": ["user@example.com"],
  "calendar_id": "primary"
}
```

**Response:**
```json
{
  "success": true,
  "event": {...}
}
```

### PUT /calendar/events/<event_id>
Update an existing calendar event.

**Query Parameters:**
- `calendar_id` (optional, default: "primary")

**Request Body:** (same as POST, all fields optional)

**Response:**
```json
{
  "success": true,
  "event": {...}
}
```

### DELETE /calendar/events/<event_id>
Delete a calendar event.

**Query Parameters:**
- `calendar_id` (optional, default: "primary")

**Response:**
```json
{
  "success": true,
  "message": "Event <event_id> deleted successfully"
}
```

## Running the API

Start the unified API server:

```bash
# From the app/api directory
python app.py

# Or from the project root
python3 app/api/app.py
```

The unified API runs on `http://localhost:5002` and exposes all endpoints:
- Chat/AI endpoints: `/health`, `/chat`
- Calendar endpoints: `/calendar/health`, `/calendar/calendars`, `/calendar/events`

## CORS

CORS is enabled on the API to allow frontend integration from any origin.
