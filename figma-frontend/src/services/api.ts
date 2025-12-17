/**
 * API Service Layer
 * 
 * Provides functions to interact with the backend API for calendar and chat operations.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

/**
 * Message type for chat conversations
 */
export interface ChatMessage {
  type: string;
  content: string;
  id?: string;
  name?: string;
  tool_call_id?: string;
}

/**
 * Agent state for maintaining conversation context
 */
export interface AgentState {
  messages: ChatMessage[];
  needs_approval_from_human: boolean;
}

/**
 * Chat request payload
 */
export interface ChatRequest {
  prompt: string;
  state?: AgentState;
}

/**
 * Chat response from the backend
 */
export interface ChatResponse {
  success: boolean;
  response: string;
  prompt: string;
  messages: ChatMessage[];
  needs_approval_from_human: boolean;
  state?: AgentState;
  error?: string;
}

/**
 * Calendar event from Google Calendar
 */
export interface CalendarEvent {
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

/**
 * Send a message to the AI agent chatbot
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
}

/**
 * Fetch calendar events from the backend
 */
export async function fetchCalendarEvents(params: {
  calendar_id?: string;
  time_min?: string;
  time_max?: string;
  max_results?: number;
  single_events?: boolean;
  order_by?: 'startTime' | 'updated';
}): Promise<{ success: boolean; events: CalendarEvent[]; count: number; error?: string }> {
  try {
    const queryParams = new URLSearchParams();
    
    if (params.calendar_id) queryParams.append('calendar_id', params.calendar_id);
    if (params.time_min) queryParams.append('time_min', params.time_min);
    if (params.time_max) queryParams.append('time_max', params.time_max);
    if (params.max_results) queryParams.append('max_results', params.max_results.toString());
    if (params.single_events !== undefined) queryParams.append('single_events', params.single_events.toString());
    if (params.order_by) queryParams.append('order_by', params.order_by);

    const response = await fetch(`${API_BASE_URL}/calendar/events?${queryParams.toString()}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching calendar events:', error);
    return {
      success: false,
      events: [],
      count: 0,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Create a new calendar event
 */
export async function createCalendarEvent(params: {
  calendar_id?: string;
  summary: string;
  description?: string;
  start: {
    dateTime: string;
    timeZone?: string;
  };
  end: {
    dateTime: string;
    timeZone?: string;
  };
  location?: string;
  attendees?: Array<{
    email: string;
  }>;
}): Promise<{ success: boolean; event?: CalendarEvent; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/calendar/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error creating calendar event:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Health check for the backend API
 */
export async function checkAPIHealth(): Promise<{ status: string; message: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error checking API health:', error);
    return {
      status: 'error',
      message: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}
