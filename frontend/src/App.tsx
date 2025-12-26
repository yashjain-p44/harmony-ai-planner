import React, { useState, useEffect } from 'react';
import { OnboardingFlow } from './components/OnboardingFlow';
import { Dashboard } from './components/Dashboard';
import { MonthlyGoals } from './components/MonthlyGoals';
import { GoogleCalendarFlow } from './components/GoogleCalendarFlow';
import { TaskManagement } from './components/TaskManagement';
import { 
  fetchCalendarEvents, 
  checkAPIHealth, 
  type CalendarEvent,
  fetchTasks,
  fetchTaskLists,
  createTask as createGoogleTask,
  updateTask as updateGoogleTask,
  deleteTask as deleteGoogleTask,
  type GoogleTask,
  type TaskList
} from './services/api';

export type Category = 'work' | 'personal' | 'focus';

export interface Task {
  id: string;
  title: string;
  category: Category;
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
  isFromGoogleCalendar?: boolean;
}

export interface UserPreferences {
  workHoursStart: number;
  workHoursEnd: number;
  focusTimeBlocks: string[];
  calendarConnected: boolean;
}

// Helper function to convert calendar event to task
function convertCalendarEventToTask(event: CalendarEvent): Task {
  const startTime = event.start.dateTime ? new Date(event.start.dateTime) : new Date(event.start.date!);
  const endTime = event.end.dateTime ? new Date(event.end.dateTime) : new Date(event.end.date!);
  const duration = (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60); // Convert to hours

  return {
    id: event.id,
    title: event.summary,
    category: 'work', // Default category for Google Calendar events
    duration: duration,
    scheduledStart: startTime,
    scheduledEnd: endTime,
    notes: event.description,
    constraints: {
      location: event.location,
    },
    isFromGoogleCalendar: true,
  };
}

// Helper function to convert Google Task to frontend Task
function convertGoogleTaskToTask(googleTask: GoogleTask): Task {
  // Try to infer category from title or notes
  let category: Category = 'work';
  const text = `${googleTask.title} ${googleTask.notes || ''}`.toLowerCase();
  if (text.includes('personal') || text.includes('home')) {
    category = 'personal';
  } else if (text.includes('focus') || text.includes('deep work')) {
    category = 'focus';
  }

  // Parse due date if available
  let deadline: Date | undefined;
  if (googleTask.due) {
    deadline = new Date(googleTask.due);
  }

  // Default duration to 1 hour if not specified
  const duration = 1;

  return {
    id: googleTask.id,
    title: googleTask.title,
    category,
    duration,
    deadline,
    notes: googleTask.notes,
    // Mark as scheduled if task is completed
    scheduledStart: googleTask.status === 'completed' ? new Date() : undefined,
    // Store Google Task metadata
    isFromGoogleCalendar: false,
  };
}

// Helper function to convert frontend Task to Google Task format
function convertTaskToGoogleTask(task: Partial<Task>): {
  title: string;
  notes?: string;
  due?: string;
  status?: 'needsAction' | 'completed';
} {
  const googleTask: {
    title: string;
    notes?: string;
    due?: string;
    status?: 'needsAction' | 'completed';
  } = {
    title: task.title || '',
  };

  if (task.notes) {
    googleTask.notes = task.notes;
  }

  if (task.deadline) {
    // Convert Date to RFC3339 format
    googleTask.due = new Date(task.deadline).toISOString();
  }

  // Determine status: if task has scheduledEnd in the past, mark as completed
  // Otherwise, check if there's an explicit status or default to needsAction
  if (task.scheduledEnd && new Date(task.scheduledEnd) < new Date()) {
    googleTask.status = 'completed';
  } else {
    // Default to needsAction for new/active tasks
    googleTask.status = 'needsAction';
  }

  return googleTask;
}

export default function App() {
  const [currentFlow, setCurrentFlow] = useState<'onboarding' | 'dashboard' | 'goals' | 'google-calendar' | 'task-management'>('onboarding');
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isCalendarConnected, setIsCalendarConnected] = useState(false);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [isLoadingCalendar, setIsLoadingCalendar] = useState(false);
  const [apiHealthy, setApiHealthy] = useState(false);
  const [selectedTaskListId, setSelectedTaskListId] = useState<string>('@default');
  const [taskLists, setTaskLists] = useState<TaskList[]>([]);

  const handleOnboardingComplete = (prefs: UserPreferences) => {
    setPreferences(prefs);
    if (prefs.calendarConnected) {
      setCurrentFlow('google-calendar');
    } else {
      setCurrentFlow('dashboard');
    }
  };

  const handleGoogleCalendarComplete = () => {
    setIsCalendarConnected(true);
    setCurrentFlow('dashboard');
    // Fetch calendar events after connection
    loadCalendarEvents();
  };

  // Check API health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await checkAPIHealth();
        setApiHealthy(health.status === 'ok' || health.status === 'healthy');
      } catch (error) {
        console.error('API health check failed:', error);
        setApiHealthy(false);
      }
    };
    checkHealth();
  }, []);

  // Load calendar events
  const loadCalendarEvents = async () => {
    if (!isCalendarConnected) return;

    setIsLoadingCalendar(true);
    try {
      // Fetch events for the next 30 days
      const now = new Date();
      const thirtyDaysLater = new Date(now);
      thirtyDaysLater.setDate(thirtyDaysLater.getDate() + 30);

      const response = await fetchCalendarEvents({
        calendar_id: 'primary',
        time_min: now.toISOString(),
        time_max: thirtyDaysLater.toISOString(),
        max_results: 100,
        single_events: true,
        order_by: 'startTime',
      });

      if (response.success && response.events) {
        // Convert calendar events to tasks and merge with existing tasks
        const calendarTasks = response.events.map(convertCalendarEventToTask);
        
        // Remove old calendar tasks and add new ones
        setTasks(prevTasks => [
          ...prevTasks.filter(t => !t.isFromGoogleCalendar),
          ...calendarTasks,
        ]);
      }
    } catch (error) {
      console.error('Error loading calendar events:', error);
    } finally {
      setIsLoadingCalendar(false);
    }
  };

  // Load task lists
  const loadTaskLists = async () => {
    try {
      const response = await fetchTaskLists();
      console.log('Task lists response:', response);
      if (response.success && response.task_lists) {
        setTaskLists(response.task_lists);
        // Set default task list if not already set or if current selection is invalid
        if (selectedTaskListId === '@default' || !response.task_lists.find(tl => tl.id === selectedTaskListId)) {
          const defaultList = response.task_lists.find(tl => tl.id === '@default') || response.task_lists[0];
          if (defaultList) {
            setSelectedTaskListId(defaultList.id);
          }
        }
      } else {
        console.error('Failed to load task lists:', response.error);
        // Set a default task list even if API fails
        if (taskLists.length === 0) {
          setTaskLists([{ id: '@default', title: 'My Tasks' }]);
          setSelectedTaskListId('@default');
        }
      }
    } catch (error) {
      console.error('Error loading task lists:', error);
      // Set a default task list even if API fails
      if (taskLists.length === 0) {
        setTaskLists([{ id: '@default', title: 'My Tasks' }]);
        setSelectedTaskListId('@default');
      }
    }
  };

  // Load Google Tasks
  const loadGoogleTasks = async (taskListId?: string) => {
    const listId = taskListId || selectedTaskListId;
    try {
      const response = await fetchTasks(listId, {
        show_completed: false,
        max_results: 100,
      });

      if (response.success && response.tasks) {
        // Convert Google Tasks to frontend Task format
        const googleTasks = response.tasks.map(convertGoogleTaskToTask);
        
        // Merge with existing tasks, keeping calendar tasks
        setTasks(prevTasks => [
          ...prevTasks.filter(t => t.isFromGoogleCalendar),
          ...googleTasks,
        ]);
      }
    } catch (error) {
      console.error('Error loading Google Tasks:', error);
    }
  };

  // Load task lists and tasks on mount and when navigating to task management
  useEffect(() => {
    if (currentFlow === 'task-management') {
      // Always load task lists when entering task management
      loadTaskLists().then(() => {
        // Tasks will be loaded by the selectedTaskListId effect or here
        if (selectedTaskListId) {
          loadGoogleTasks(selectedTaskListId);
        }
      });
    } else if (currentFlow === 'dashboard') {
      loadGoogleTasks(selectedTaskListId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentFlow]);

  // Reload tasks when task list changes (only in task-management view)
  useEffect(() => {
    if (currentFlow === 'task-management' && selectedTaskListId && taskLists.length > 0) {
      loadGoogleTasks(selectedTaskListId);
    }
  }, [selectedTaskListId, currentFlow]);

  // Load calendar events when calendar is connected
  useEffect(() => {
    if (isCalendarConnected && currentFlow === 'dashboard') {
      loadCalendarEvents();
    }
  }, [isCalendarConnected, currentFlow]);

  const handleAddTask = async (task: Task) => {
    try {
      // Convert to Google Task format
      const googleTaskData = convertTaskToGoogleTask(task);
      
      // Create task in Google Tasks
      const response = await createGoogleTask(selectedTaskListId, googleTaskData);
      
      if (response.success && response.task) {
        // Convert back to frontend format and add to state
        const newTask = convertGoogleTaskToTask(response.task);
        setTasks([...tasks, newTask]);
      } else {
        console.error('Failed to create task:', response.error);
        // Still add to local state as fallback
        setTasks([...tasks, task]);
      }
    } catch (error) {
      console.error('Error creating task:', error);
      // Fallback: add to local state
      setTasks([...tasks, task]);
    }
  };

  const handleUpdateTask = async (taskId: string, updates: Partial<Task>) => {
    console.log('[App] handleUpdateTask called');
    console.log('[App] Task ID:', taskId);
    console.log('[App] Updates:', updates);
    console.log('[App] Current tasks:', tasks);
    console.log('[App] Selected task list ID:', selectedTaskListId);
    
    try {
      // Find the task to get its Google Task ID
      const task = tasks.find(t => t.id === taskId);
      console.log('[App] Found task:', task);
      if (!task) {
        console.warn('[App] Task not found with ID:', taskId);
        return;
      }

      // Skip if it's a calendar event (those are managed separately)
      if (task.isFromGoogleCalendar) {
        console.log('[App] Task is from Google Calendar, updating local state only');
        setTasks(tasks.map(t => t.id === taskId ? { ...t, ...updates } : t));
        console.log('[App] Local state updated for calendar task');
        return;
      }

      // Convert updates to Google Task format
      const updatedTask = { ...task, ...updates };
      console.log('[App] Updated task object:', updatedTask);
      const googleTaskData = convertTaskToGoogleTask(updatedTask);
      console.log('[App] Google Task data:', googleTaskData);
      
      // Update task in Google Tasks
      console.log('[App] Calling updateGoogleTask API...');
      const response = await updateGoogleTask(selectedTaskListId, taskId, googleTaskData);
      console.log('[App] API response:', response);
      
      if (response.success && response.task) {
        console.log('[App] API update successful, converting and updating state');
        // Convert back to frontend format and update state
        const updatedGoogleTask = convertGoogleTaskToTask(response.task);
        console.log('[App] Converted Google Task:', updatedGoogleTask);
        setTasks(tasks.map(t => t.id === taskId ? updatedGoogleTask : t));
        console.log('[App] State updated successfully');
      } else {
        console.error('[App] Failed to update task:', response.error);
        // Fallback: update local state
        console.log('[App] Falling back to local state update');
        setTasks(tasks.map(t => t.id === taskId ? { ...t, ...updates } : t));
        console.log('[App] Local state updated as fallback');
      }
    } catch (error) {
      console.error('[App] Error updating task:', error);
      // Fallback: update local state
      setTasks(tasks.map(t => t.id === taskId ? { ...t, ...updates } : t));
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      // Find the task to check if it's a Google Task
      const task = tasks.find(t => t.id === taskId);
      if (!task) return;

      // Skip if it's a calendar event (those are managed separately)
      if (task.isFromGoogleCalendar) {
        setTasks(tasks.filter(t => t.id !== taskId));
        return;
      }

      // Delete task from Google Tasks
      const response = await deleteGoogleTask(selectedTaskListId, taskId);
      
      if (response.success) {
        // Remove from local state
        setTasks(tasks.filter(t => t.id !== taskId));
      } else {
        console.error('Failed to delete task:', response.error);
        // Fallback: remove from local state
        setTasks(tasks.filter(t => t.id !== taskId));
      }
    } catch (error) {
      console.error('Error deleting task:', error);
      // Fallback: remove from local state
      setTasks(tasks.filter(t => t.id !== taskId));
    }
  };

  const handleScheduleTask = (taskId: string) => {
    // Simulate AI scheduling - in real app, this would use AI to find optimal time
    const task = tasks.find(t => t.id === taskId);
    if (task) {
      const scheduledStart = new Date();
      scheduledStart.setHours(9, 0, 0, 0);
      scheduledStart.setDate(scheduledStart.getDate() + 1); // Tomorrow at 9 AM
      
      handleUpdateTask(taskId, {
        scheduledStart,
        scheduledEnd: new Date(scheduledStart.getTime() + task.duration * 60 * 60 * 1000),
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Skip to main content - WCAG 2.4.1 */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      <main id="main-content">
        {currentFlow === 'onboarding' && (
          <OnboardingFlow onComplete={handleOnboardingComplete} />
        )}
        {currentFlow === 'google-calendar' && (
          <GoogleCalendarFlow 
            onComplete={handleGoogleCalendarComplete}
            onCancel={() => setCurrentFlow('dashboard')}
          />
        )}
        {currentFlow === 'dashboard' && (
          <Dashboard
            tasks={tasks}
            preferences={preferences!}
            onAddTask={handleAddTask}
            onUpdateTask={handleUpdateTask}
            onDeleteTask={handleDeleteTask}
            onNavigateToGoals={() => setCurrentFlow('goals')}
            onNavigateToTasks={() => setCurrentFlow('task-management')}
            isCalendarConnected={isCalendarConnected}
            showTaskForm={showTaskForm}
            onToggleTaskForm={() => setShowTaskForm(!showTaskForm)}
            onRefreshCalendar={loadCalendarEvents}
            isLoadingCalendar={isLoadingCalendar}
            apiHealthy={apiHealthy}
          />
        )}
        {currentFlow === 'goals' && (
          <MonthlyGoals
            tasks={tasks}
            onBack={() => setCurrentFlow('dashboard')}
          />
        )}
        {currentFlow === 'task-management' && (
          <TaskManagement
            tasks={tasks.filter(t => !t.isFromGoogleCalendar)}
            taskLists={taskLists}
            selectedTaskListId={selectedTaskListId}
            onTaskListChange={(taskListId: string) => {
              setSelectedTaskListId(taskListId);
            }}
            onBack={() => setCurrentFlow('dashboard')}
            onAddTask={handleAddTask}
            onUpdateTask={handleUpdateTask}
            onDeleteTask={handleDeleteTask}
            onScheduleTask={handleScheduleTask}
            onRefreshTasks={() => loadGoogleTasks(selectedTaskListId)}
          />
        )}
      </main>
    </div>
  );
}