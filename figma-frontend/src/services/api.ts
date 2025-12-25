/**
 * API service for communicating with the backend
 */

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:5002';

export interface ChatRequest {
  prompt: string;
  state?: AgentState;
  approval_state?: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CHANGES_REQUESTED';
  approval_feedback?: string;
}

export interface ChatResponse {
  success: boolean;
  response: string;
  prompt: string;
  messages: ChatMessage[];
  needs_approval_from_human: boolean;
  approval_state?: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CHANGES_REQUESTED';
  approval_summary?: ApprovalSummary;
  state?: AgentState;
  error?: string;
}

export interface ChatMessage {
  type: string;
  content: string;
  tool_calls?: any[];
  tool_call_id?: string;
}

export interface AgentState {
  messages?: ChatMessage[];
  needs_approval_from_human?: boolean;
  approval_state?: 'PENDING' | 'APPROVED' | 'REJECTED' | 'CHANGES_REQUESTED';
  approval_feedback?: string;
  [key: string]: any;
}

export interface ApprovalSummary {
  summary?: string;
  selected_slots?: any[];
  habit_name?: string;
  frequency?: string;
  duration_minutes?: number;
  slots_summary?: Array<{
    slot_number: number;
    date: string;
    time: string;
    duration_minutes: number;
  }>;
}

export interface CalendarEvent {
  id: string;
  summary: string;
  description?: string;
  location?: string;
  start: {
    dateTime?: string;
    date?: string;
  };
  end: {
    dateTime?: string;
    date?: string;
  };
}

/**
 * Check if the API is healthy
 */
export async function checkAPIHealth(): Promise<{ status: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    });
    if (response.ok) {
      const data = await response.json();
      return data;
    }
    return { status: 'unhealthy' };
  } catch (error) {
    return { status: 'unhealthy' };
  }
}

/**
 * Fetch calendar events from the backend
 */
export async function fetchCalendarEvents(params?: {
  calendar_id?: string;
  time_min?: string;
  time_max?: string;
  max_results?: number;
  single_events?: boolean;
  order_by?: string;
}): Promise<{ success: boolean; events?: CalendarEvent[] }> {
  try {
    const queryParams = new URLSearchParams();
    if (params?.calendar_id) queryParams.append('calendar_id', params.calendar_id);
    if (params?.time_min) queryParams.append('time_min', params.time_min);
    if (params?.time_max) queryParams.append('time_max', params.time_max);
    if (params?.max_results) queryParams.append('max_results', params.max_results.toString());
    if (params?.single_events !== undefined) queryParams.append('single_events', params.single_events.toString());
    if (params?.order_by) queryParams.append('order_by', params.order_by);

    const response = await fetch(`${API_BASE_URL}/calendar/events?${queryParams.toString()}`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: data.success || false,
      events: data.events || [],
    };
  } catch (error) {
    console.error('Error fetching calendar events:', error);
    return { success: false, events: [] };
  }
}

/**
 * Send a chat message to the AI agent
 */
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  console.log('Sending chat request:', request);
  
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error('HTTP error response:', response.status, errorText);
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  console.log('Chat response data:', data);
  return data;
}

