# Scheduler API

Flask REST API for the scheduler application.

This directory contains two API files:
- `app.py` - Scheduler API for planning and scheduling events
- `calendar_api.py` - Calendar API for direct calendar operations

## Scheduler API Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "scheduler-api"
}
```

### POST /schedule
Schedule events based on plan requirements.

**Request Body:**
```json
{
  "plan_description": "Reading books",
  "total_minutes_per_week": 120,
  "min_event_duration": 30,
  "max_event_duration": 60,
  "min_break": 15,
  "scheduling_window_days": 7,
  "preferred_time_windows": [
    {
      "start_hour": 9,
      "start_minute": 0,
      "end_hour": 17,
      "end_minute": 0
    }
  ],
  "calendar_id": "primary"
}
```

**Response:**
```json
{
  "success": true,
  "events_created": [...],
  "event_ids": [...],
  "total_minutes_scheduled": 120,
  "remaining_minutes": 0,
  "decision_log": [...],
  "warnings": [],
  "errors": []
}
```

### POST /schedule/preview
Preview scheduling without creating calendar events (not yet implemented).

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

## Running the APIs

### Scheduler API
```bash
# From the app/api directory
python app.py

# Or from the project root
cd app/api && python app.py
```
The Scheduler API runs on `http://localhost:5000` by default.

### Calendar API
```bash
# From the app/api directory
python calendar_api.py

# Or from the project root
cd app/api && python calendar_api.py
```
The Calendar API runs on `http://localhost:5001` by default.

## CORS

CORS is enabled on both APIs to allow frontend integration.
