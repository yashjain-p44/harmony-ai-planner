import React, { useState } from 'react';
import { OnboardingFlow } from './components/OnboardingFlow';
import { Dashboard } from './components/Dashboard';
import { MonthlyGoals } from './components/MonthlyGoals';
import { GoogleCalendarFlow } from './components/GoogleCalendarFlow';
import { TaskManagement } from './components/TaskManagement';

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

export default function App() {
  const [currentFlow, setCurrentFlow] = useState<'onboarding' | 'dashboard' | 'goals' | 'google-calendar' | 'task-management'>('onboarding');
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isCalendarConnected, setIsCalendarConnected] = useState(false);
  const [showTaskForm, setShowTaskForm] = useState(false);

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
  };

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