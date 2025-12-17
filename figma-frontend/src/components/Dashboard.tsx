import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Calendar, Plus, Target, ChevronLeft, ChevronRight, Sparkles, Settings, List } from 'lucide-react';
import type { Task, UserPreferences, Category } from '../App';
import { AIPanel } from './AIPanel';
import { TaskForm } from './TaskForm';
import { CalendarView } from './CalendarView';
import { TaskDetailModal } from './TaskDetailModal';
import { RescheduleModal } from './RescheduleModal';
import { CalendarSettings } from './CalendarSettings';

interface DashboardProps {
  tasks: Task[];
  preferences: UserPreferences;
  onAddTask: (task: Task) => void;
  onUpdateTask: (taskId: string, updates: Partial<Task>) => void;
  onDeleteTask: (taskId: string) => void;
  onNavigateToGoals: () => void;
  onNavigateToTasks: () => void;
  isCalendarConnected?: boolean;
  showTaskForm: boolean;
  onToggleTaskForm: () => void;
}

export type ViewMode = 'day' | 'week' | 'month';

export function Dashboard({
  tasks,
  preferences,
  onAddTask,
  onUpdateTask,
  onDeleteTask,
  onNavigateToGoals,
  onNavigateToTasks,
  isCalendarConnected = false,
  showTaskForm,
  onToggleTaskForm,
}: DashboardProps) {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('week');
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showRescheduleModal, setShowRescheduleModal] = useState(false);
  const [conflictingTask, setConflictingTask] = useState<Task | null>(null);
  const [showCalendarSettings, setShowCalendarSettings] = useState(false);

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
  };

  const handleAddTaskComplete = (task: Task) => {
    onAddTask(task);
    onToggleTaskForm();
    setIsPanelOpen(false);
  };

  const handleDateChange = (direction: 'prev' | 'next') => {
    const newDate = new Date(selectedDate);
    if (viewMode === 'day') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 1 : -1));
    } else if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
    } else {
      newDate.setMonth(newDate.getMonth() + (direction === 'next' ? 1 : -1));
    }
    setSelectedDate(newDate);
  };

  const handleDisconnectCalendar = () => {
    // Handle disconnect logic here
    console.log('Disconnect calendar');
  };

  return (
    <div className="min-h-screen relative">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-200/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-200/20 rounded-full blur-3xl" />
      </div>

      {/* Top Bar */}
      <div className="relative z-10 border-b border-gray-200 glass">
        <div className="max-w-[1800px] mx-auto px-8 py-4 flex items-center justify-between">
          {/* Left: AI Avatar */}
          <div className="flex items-center gap-4">
            <motion.div
              className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-300 via-purple-300 to-pink-300 flex items-center justify-center shadow-md cursor-pointer"
              whileHover={{ scale: 1.1 }}
              animate={{
                boxShadow: [
                  '0 4px 20px rgba(147, 197, 253, 0.3)',
                  '0 4px 20px rgba(216, 180, 254, 0.4)',
                  '0 4px 20px rgba(147, 197, 253, 0.3)',
                ],
              }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              <Sparkles className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <div className="text-gray-800">AI Schedule Assistant</div>
              <div className="text-xs text-gray-500">
                {isCalendarConnected ? (
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    Google Calendar synced
                  </span>
                ) : (
                  'Ready to optimize your day'
                )}
              </div>
            </div>
          </div>

          {/* Center: View Mode Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleDateChange('prev')}
              className="p-2 rounded-lg bg-white/80 border border-gray-200 hover:border-gray-300 transition-all"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>

            <div className="bg-white/80 rounded-xl border border-gray-200 p-1 flex gap-1 shadow-sm">
              {(['day', 'week', 'month'] as ViewMode[]).map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode)}
                  className={`px-6 py-2 rounded-lg capitalize transition-all ${
                    viewMode === mode
                      ? 'bg-gradient-to-r from-blue-400 to-purple-400 text-white shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>

            <button
              onClick={() => handleDateChange('next')}
              className="p-2 rounded-lg bg-white/80 border border-gray-200 hover:border-gray-300 transition-all"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-3">
            <button
              onClick={onNavigateToTasks}
              className="px-4 py-2 rounded-lg bg-white/80 border border-gray-200 hover:border-purple-300 transition-all flex items-center gap-2 text-gray-700"
            >
              <List className="w-4 h-4" />
              Tasks
            </button>
            {isCalendarConnected && (
              <button
                onClick={() => setShowCalendarSettings(true)}
                className="px-4 py-2 rounded-lg bg-white/80 border border-gray-200 hover:border-blue-300 transition-all flex items-center gap-2 text-gray-700"
                aria-label="Calendar settings"
              >
                <Settings className="w-4 h-4" />
                Settings
              </button>
            )}
            <button
              onClick={onNavigateToGoals}
              className="px-4 py-2 rounded-lg bg-white/80 border border-gray-200 hover:border-emerald-300 transition-all flex items-center gap-2 text-gray-700"
            >
              <Target className="w-4 h-4" />
              Goals
            </button>
            <button
              onClick={onToggleTaskForm}
              className="px-6 py-2 rounded-lg bg-gradient-to-r from-blue-400 to-purple-400 text-white shadow-md hover:shadow-lg hover:scale-105 transition-all flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add task
            </button>
          </div>
        </div>

        {/* Calendar Sync Banner */}
        {isCalendarConnected && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-emerald-100 to-teal-100 border-t border-emerald-300 px-8 py-2"
          >
            <div className="max-w-[1800px] mx-auto flex items-center justify-between text-sm">
              <span className="text-emerald-800">
                <Calendar className="w-4 h-4 inline mr-2" aria-hidden="true" />
                Google Calendar sync active
              </span>
              <button
                onClick={() => setShowCalendarSettings(true)}
                className="text-emerald-700 hover:text-emerald-900 underline focus:outline-none focus:ring-2 focus:ring-emerald-500 rounded"
              >
                Manage sync
              </button>
            </div>
          </motion.div>
        )}
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex h-[calc(100vh-80px)]">
        {/* Calendar View */}
        <div className={`flex-1 transition-all duration-500 ${isPanelOpen ? 'mr-[450px]' : 'mr-0'}`}>
          <CalendarView
            tasks={tasks}
            viewMode={viewMode}
            selectedDate={selectedDate}
            onTaskClick={handleTaskClick}
            preferences={preferences}
          />
        </div>

        {/* AI Panel */}
        <AIPanel
          isOpen={isPanelOpen}
          onToggle={() => setIsPanelOpen(!isPanelOpen)}
          onAddTask={handleAddTaskComplete}
        />
      </div>

      {/* Task Form Modal */}
      <AnimatePresence>
        {showTaskForm && (
          <TaskForm
            onClose={onToggleTaskForm}
            onSubmit={handleAddTaskComplete}
          />
        )}
      </AnimatePresence>

      {/* Task Detail Modal */}
      <AnimatePresence>
        {selectedTask && (
          <TaskDetailModal
            task={selectedTask}
            onClose={() => setSelectedTask(null)}
            onUpdate={(updates) => {
              onUpdateTask(selectedTask.id, updates);
              setSelectedTask(null);
            }}
            onDelete={() => {
              onDeleteTask(selectedTask.id);
              setSelectedTask(null);
            }}
          />
        )}
      </AnimatePresence>

      {/* Reschedule Modal */}
      <AnimatePresence>
        {showRescheduleModal && conflictingTask && (
          <RescheduleModal
            task={conflictingTask}
            tasks={tasks}
            onClose={() => {
              setShowRescheduleModal(false);
              setConflictingTask(null);
            }}
            onReschedule={(updatedTasks) => {
              updatedTasks.forEach((t) => onUpdateTask(t.id, t));
              setShowRescheduleModal(false);
              setConflictingTask(null);
            }}
          />
        )}
      </AnimatePresence>

      {/* Calendar Settings Modal */}
      <AnimatePresence>
        {showCalendarSettings && (
          <CalendarSettings
            isConnected={isCalendarConnected}
            onDisconnect={handleDisconnectCalendar}
            onClose={() => setShowCalendarSettings(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}