# Frontend-Backend Integration Guide

This guide explains how the frontend is integrated with the backend APIs for calendar events and chatbot functionality.

## Overview

The frontend now communicates with the backend Flask API to:
1. **Fetch calendar events** from Google Calendar
2. **Chat with the AI agent** for task scheduling and management
3. **Create and manage tasks** through natural language

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐
│                     │         │                     │
│  React Frontend     │◄───────►│  Flask Backend      │
│  (Port 5173)        │         │  (Port 5000)        │
│                     │         │                     │
└─────────────────────┘         └─────────────────────┘
         │                               │
         │                               │
         ▼                               ▼
  - AIPanel.tsx                 - /chat endpoint
  - CalendarView.tsx            - /calendar/events endpoint
  - Dashboard.tsx               - Google Calendar API
```

## Setup Instructions

### 1. Backend Setup

First, ensure the backend is running:

```bash
# Navigate to project root
cd /Users/yashjainp44/task-ai-poc

# Install Python dependencies (if not already done)
pip install -r requirements.txt

# Set up Google Calendar credentials
# Follow the README in app/api/ for OAuth setup

# Start the backend server
python -m app.api.app
# OR
python app/api/app.py
```

The backend should start on `http://localhost:5000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd figma-frontend

# Install dependencies (if not already done)
npm install

# The .env file is already created with:
# VITE_API_BASE_URL=http://localhost:5000

# Start the development server
npm run dev
```

The frontend should start on `http://localhost:5173`

## Features Integrated

### 1. AI Chatbot Integration

**File**: `src/components/AIPanel.tsx`

The chatbot now communicates with the backend AI agent:

- **Endpoint**: `POST /chat`
- **Features**:
  - Natural language task creation
  - Calendar event queries
  - Conversational context maintained via agent state
  - Real-time responses from the AI

**Example interactions**:
- "Schedule a meeting tomorrow at 2pm for 1 hour"
- "What events do I have today?"
- "Create a focus time block for coding"

### 2. Calendar Events Display

**Files**: 
- `src/App.tsx` - Main integration logic
- `src/components/Dashboard.tsx` - UI updates
- `src/components/CalendarView.tsx` - Event rendering

**Features**:
- Automatic fetching of Google Calendar events
- Events displayed alongside user-created tasks
- Calendar events marked with 📅 icon
- Refresh button to manually sync calendar
- 30-day event window

**Endpoint**: `GET /calendar/events`

**Query Parameters**:
- `calendar_id`: Default is "primary"
- `time_min`: ISO datetime string
- `time_max`: ISO datetime string
- `max_results`: Maximum events to fetch
- `single_events`: Expand recurring events
- `order_by`: Sort order (startTime/updated)

### 3. API Health Monitoring

The frontend checks if the backend is available and displays a warning if it's offline.

**Endpoint**: `GET /health`

## API Service Layer

**File**: `src/services/api.ts`

This file contains all API communication functions:

### Functions

1. **`sendChatMessage(request: ChatRequest): Promise<ChatResponse>`**
   - Sends a message to the AI agent
   - Maintains conversation state
   - Returns AI response and updated state

2. **`fetchCalendarEvents(params): Promise<{...}>`**
   - Fetches calendar events from backend
   - Supports filtering by time range
   - Returns array of CalendarEvent objects

3. **`createCalendarEvent(params): Promise<{...}>`**
   - Creates a new calendar event
   - Supports attendees, location, description
   - Returns created event

4. **`checkAPIHealth(): Promise<{...}>`**
   - Checks if backend API is responsive
   - Returns health status

## Data Models

### Task Interface

```typescript
interface Task {
  id: string;
  title: string;
  category: 'work' | 'personal' | 'focus';
  duration: number; // in hours
  deadline?: Date;
  scheduledStart?: Date;
  scheduledEnd?: Date;
  notes?: string;
  constraints?: {
    location?: string;
    timeOfDay?: string;
    energyLevel?: string;
  };
  isFromGoogleCalendar?: boolean; // Marks Google Calendar events
}
```

### CalendarEvent Interface

```typescript
interface CalendarEvent {
  id: string;
  summary: string;
  description?: string;
  start: {
    dateTime?: string;
    date?: string;
    timeZone?: string;
  };
  end: {
    dateTime?: string;
    date?: string;
    timeZone?: string;
  };
  location?: string;
  attendees?: Array<{
    email: string;
    displayName?: string;
    responseStatus?: string;
  }>;
  status?: string;
  htmlLink?: string;
}
```

## Configuration

### Environment Variables

The frontend uses Vite's environment variable system:

- **`.env`** (local, not committed):
  ```
  VITE_API_BASE_URL=http://localhost:5000
  ```

- **`.env.example`** (template, committed):
  ```
  VITE_API_BASE_URL=http://localhost:5000
  ```

To change the backend URL, update `VITE_API_BASE_URL` in `.env` and restart the dev server.

## User Flow

### 1. Onboarding
- User completes onboarding
- Optionally connects Google Calendar
- Frontend attempts API health check

### 2. Dashboard View
- If calendar connected, automatically fetches events
- Events appear in calendar view with special styling
- AI chatbot panel available on the right

### 3. Chatbot Interaction
- User opens AI panel (floating button)
- Types natural language request
- Message sent to backend `/chat` endpoint
- AI response displayed in chat
- Tasks can be created from conversation

### 4. Calendar Sync
- Manual refresh button available
- Events auto-refresh when switching views
- Google Calendar events cannot be deleted from UI (read-only)

## Troubleshooting

### Backend Not Responding

**Symptom**: "API Offline" warning or chatbot errors

**Solutions**:
1. Check if backend is running: `curl http://localhost:5000/health`
2. Verify Google Calendar credentials are set up
3. Check backend terminal for errors
4. Ensure port 5000 is not blocked

### Calendar Events Not Showing

**Symptom**: Empty calendar despite having events

**Solutions**:
1. Verify Google Calendar OAuth is complete
2. Check browser console for API errors
3. Click the "Refresh" button manually
4. Verify events exist in the time range (next 30 days)

### Chatbot Not Responding

**Symptom**: Messages sent but no AI response

**Solutions**:
1. Check backend logs for AI agent errors
2. Verify LangChain/AI dependencies are installed
3. Check API keys (OpenAI, etc.) are configured
4. Try simple message: "Hello"

## CORS Configuration

The backend is configured with CORS enabled:

```python
from flask_cors import CORS
CORS(app)  # Allows all origins in development
```

For production, restrict CORS to specific origins:

```python
CORS(app, origins=['https://yourdomain.com'])
```

## Testing the Integration

### 1. Test API Health
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "API is running"
}
```

### 2. Test Calendar Events
```bash
curl "http://localhost:5000/calendar/events?max_results=5"
```

### 3. Test Chat Endpoint
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What events do I have today?"}'
```

### 4. Frontend Tests
1. Open `http://localhost:5173`
2. Complete onboarding with calendar connection
3. Verify events appear in calendar view
4. Open AI panel and send a message
5. Try creating a task through chat

## Next Steps

Potential enhancements:

1. **Real-time Updates**: WebSocket connection for live calendar sync
2. **Offline Support**: Cache events locally with service worker
3. **Error Retry**: Automatic retry logic for failed API calls
4. **Loading States**: More granular loading indicators
5. **Event Creation**: Allow creating calendar events from frontend
6. **Authentication**: Add user authentication and session management
7. **Multi-Calendar**: Support multiple Google Calendar calendars

## API Documentation

The backend provides Swagger documentation at:
- URL: `http://localhost:5000/api-docs`

This interactive documentation allows you to test all API endpoints directly.

## Security Notes

- **Never commit `.env`** files with real credentials
- Use environment variables for all sensitive data
- Implement authentication for production deployment
- Validate all user inputs on both frontend and backend
- Use HTTPS in production

## Support

For issues or questions:
1. Check the main README.md
2. Review backend API documentation: `app/api/README.md`
3. Check browser console for errors
4. Review backend terminal logs


