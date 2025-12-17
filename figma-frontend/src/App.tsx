import React, { useState, useEffect } from 'react';
import { OnboardingFlow } from './components/OnboardingFlow';
import { Dashboard } from './components/Dashboard';
import { MonthlyGoals } from './components/MonthlyGoals';
import { GoogleCalendarFlow } from './components/GoogleCalendarFlow';
import { TaskManagement } from './components/TaskManagement';
import { fetchCalendarEvents, checkAPIHealth, type CalendarEvent } from './services/api';

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

export default function App() {
  const [currentFlow, setCurrentFlow] = useState<'onboarding' | 'dashboard' | 'goals' | 'google-calendar' | 'task-management'>('onboarding');
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isCalendarConnected, setIsCalendarConnected] = useState(false);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [isLoadingCalendar, setIsLoadingCalendar] = useState(false);
  const [apiHealthy, setApiHealthy] = useState(false);

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

  // Load calendar events when calendar is connected
  useEffect(() => {
    if (isCalendarConnected && currentFlow === 'dashboard') {
      loadCalendarEvents();
    }
  }, [isCalendarConnected, currentFlow]);

  const handleAddTask = (task: Task) => {
    setTasks([...tasks, task]);
  };

  const handleUpdateTask = (taskId: string, updates: Partial<Task>) => {
    setTasks(tasks.map(t => t.id === taskId ? { ...t, ...updates } : t));
  };

  const handleDeleteTask = (taskId: string) => {
    setTasks(tasks.filter(t => t.id !== taskId));
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
            tasks={tasks}
            onBack={() => setCurrentFlow('dashboard')}
            onAddTask={() => setShowTaskForm(true)}
            onUpdateTask={handleUpdateTask}
            onDeleteTask={handleDeleteTask}
            onScheduleTask={handleScheduleTask}
          />
        )}
      </main>
    </div>
  );
}