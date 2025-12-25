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
  created_events?: Array<{
    id: string;
    summary: string;
    start: string;
    end: string;
    description?: string;
    location?: string;
    htmlLink?: string;
  }>;
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
  task_name?: string;
  frequency?: string;
  priority?: string;
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

export interface GoogleTask {
  id: string;
  title: string;
  notes?: string;
  status?: 'needsAction' | 'completed';
  due?: string;
  updated?: string;
  position?: string;
  [key: string]: any;
}

export interface TaskList {
  id: string;
  title: string;
  updated?: string;
  [key: string]: any;
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

export interface StreamUpdate {
  type: 'progress' | 'complete' | 'error';
  node?: string;
  description?: string;
  response?: ChatResponse;
  error?: string;
}

/**
 * Send a chat message to the AI agent with streaming updates
 * @param request Chat request
 * @param onUpdate Callback for each stream update
 * @returns Promise that resolves with the final response
 */
export async function sendChatMessageStream(
  request: ChatRequest,
  onUpdate: (update: StreamUpdate) => void
): Promise<ChatResponse> {
  console.log('Sending streaming chat request:', request);
  
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
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

  if (!response.body) {
    throw new Error('Response body is null');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  let finalResponse: ChatResponse | null = null;

  try {
    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            onUpdate(data);
            
            if (data.type === 'complete' && data.response) {
              finalResponse = data.response;
            } else if (data.type === 'error') {
              throw new Error(data.error || 'Unknown error');
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e, line);
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  if (!finalResponse) {
    throw new Error('No final response received from stream');
  }

  return finalResponse;
}

/**
 * Fetch task lists from Google Tasks
 */
export async function fetchTaskLists(): Promise<{ success: boolean; task_lists?: TaskList[]; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks/lists`, {
      method: 'GET',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: data.success || false,
      task_lists: data.task_lists || [],
    };
  } catch (error) {
    console.error('Error fetching task lists:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Fetch tasks from a specific task list
 */
export async function fetchTasks(
  taskListId: string = '@default',
  options?: {
    show_completed?: boolean;
    show_deleted?: boolean;
    max_results?: number;
  }
): Promise<{ success: boolean; tasks?: GoogleTask[]; error?: string }> {
  try {
    const queryParams = new URLSearchParams();
    if (options?.show_completed !== undefined) {
      queryParams.append('show_completed', options.show_completed.toString());
    }
    if (options?.show_deleted !== undefined) {
      queryParams.append('show_deleted', options.show_deleted.toString());
    }
    if (options?.max_results !== undefined) {
      queryParams.append('max_results', options.max_results.toString());
    }

    const response = await fetch(
      `${API_BASE_URL}/tasks/lists/${taskListId}/tasks?${queryParams.toString()}`,
      {
        method: 'GET',
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: data.success || false,
      tasks: data.tasks || [],
    };
  } catch (error) {
    console.error('Error fetching tasks:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Create a new task
 */
export async function createTask(
  taskListId: string = '@default',
  task: {
    title: string;
    notes?: string;
    due?: string;
    [key: string]: any;
  }
): Promise<{ success: boolean; task?: GoogleTask; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks/lists/${taskListId}/tasks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(task),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: data.success || false,
      task: data.task,
    };
  } catch (error) {
    console.error('Error creating task:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Update an existing task
 */
export async function updateTask(
  taskListId: string,
  taskId: string,
  updates: {
    title?: string;
    notes?: string;
    due?: string;
    status?: 'needsAction' | 'completed';
    [key: string]: any;
  }
): Promise<{ success: boolean; task?: GoogleTask; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks/lists/${taskListId}/tasks/${taskId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: data.success || false,
      task: data.task,
    };
  } catch (error) {
    console.error('Error updating task:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Delete a task
 */
export async function deleteTask(
  taskListId: string,
  taskId: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/tasks/lists/${taskListId}/tasks/${taskId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return {
      success: data.success || false,
    };
  } catch (error) {
    console.error('Error deleting task:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Schedule a task using AI
 */
export async function scheduleTask(
  taskListId: string,
  taskId: string,
  approvalState?: 'APPROVED' | 'REJECTED' | 'CHANGES_REQUESTED',
  approvalFeedback?: string,
  state?: AgentState
): Promise<ChatResponse> {
  try {
    const body: any = {};
    if (approvalState !== undefined) {
      body.approval_state = approvalState;
    }
    if (approvalFeedback !== undefined) {
      body.approval_feedback = approvalFeedback;
    }
    if (state !== undefined) {
      body.state = state;
    }

    const response = await fetch(`${API_BASE_URL}/tasks/lists/${taskListId}/tasks/${taskId}/schedule`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error scheduling task:', error);
    throw error;
  }
}

