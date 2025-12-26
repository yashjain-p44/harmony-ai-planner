import React, { useState, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  ArrowLeft, 
  Filter, 
  List, 
  LayoutGrid, 
  Calendar, 
  Clock, 
  AlertCircle, 
  CheckCircle2,
  Plus,
  Sparkles,
  TrendingUp,
  X,
  Edit2,
  Trash2,
  Zap,
  Folder
} from 'lucide-react';
import type { Task, Category } from '../App';
import type { TaskList } from '../services/api';
import { TaskForm } from './TaskForm';
import { AIPanel } from './AIPanel';

interface TaskManagementProps {
  tasks: Task[];
  taskLists: TaskList[];
  selectedTaskListId: string;
  onTaskListChange: (taskListId: string) => void;
  onBack: () => void;
  onAddTask: (task: Task) => void;
  onUpdateTask: (taskId: string, updates: Partial<Task>) => void;
  onDeleteTask: (taskId: string) => void;
  onScheduleTask: (taskId: string) => void;
  onRefreshTasks?: () => void;
}

type ViewMode = 'list' | 'kanban';
type FilterStatus = 'all' | 'scheduled' | 'unscheduled' | 'completed';
type FilterTime = 'all' | 'today' | 'week' | 'later';
type FilterPriority = 'all' | 'high' | 'medium' | 'low';

export function TaskManagement({ 
  tasks, 
  taskLists,
  selectedTaskListId,
  onTaskListChange,
  onBack, 
  onAddTask, 
  onUpdateTask, 
  onDeleteTask,
  onScheduleTask,
  onRefreshTasks
}: TaskManagementProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [filterCategory, setFilterCategory] = useState<Category | 'all'>('all');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');
  const [filterTime, setFilterTime] = useState<FilterTime>('all');
  const [filterPriority, setFilterPriority] = useState<FilterPriority>('all');
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [isPanelOpen, setIsPanelOpen] = useState(true);
  const aiPanelSendMessageRef = useRef<((message: string) => void) | null>(null);
  // Local state to track scheduled status for demo (frontend-only, no API calls)
  const [scheduledTaskIds, setScheduledTaskIds] = useState<Set<string>>(new Set());

  // Format task details into a scheduling prompt
  const formatTaskForScheduling = (task: Task): string => {
    let prompt = `Please schedule this task: "${task.title}"`;
    
    if (task.duration) {
      prompt += ` (${task.duration} hour${task.duration !== 1 ? 's' : ''})`;
    }
    
    if (task.deadline) {
      const deadlineDate = new Date(task.deadline);
      prompt += `. Deadline: ${deadlineDate.toLocaleDateString()}`;
    }
    
    if (task.category) {
      prompt += `. Category: ${task.category}`;
    }
    
    if (task.constraints) {
      const constraints: string[] = [];
      if (task.constraints.location) {
        constraints.push(`location: ${task.constraints.location}`);
      }
      if (task.constraints.timeOfDay) {
        constraints.push(`preferred time: ${task.constraints.timeOfDay}`);
      }
      if (task.constraints.energyLevel) {
        constraints.push(`energy level: ${task.constraints.energyLevel}`);
      }
      if (constraints.length > 0) {
        prompt += `. Constraints: ${constraints.join(', ')}`;
      }
    }
    
    if (task.notes) {
      prompt += `. Notes: ${task.notes}`;
    }
    
    prompt += '.';
    
    return prompt;
  };

  // Handle schedule task click - send to AI panel
  const handleScheduleTaskClick = (taskId: string) => {
    const task = tasks.find(t => t.id === taskId);
    if (!task) return;
    
    // Ensure panel is open
    if (!isPanelOpen) {
      setIsPanelOpen(true);
    }
    
    // Format task details and send to chatbot
    const prompt = formatTaskForScheduling(task);
    
    // Wait a bit for panel to open, then send message
    setTimeout(() => {
      if (aiPanelSendMessageRef.current) {
        aiPanelSendMessageRef.current(prompt);
      }
    }, 300);
  };

  // Toggle task scheduled status (frontend-only, no API calls)
  const handleToggleTaskStatus = (taskId: string) => {
    console.log('[TaskManagement] Toggling task status for:', taskId);
    setScheduledTaskIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
        console.log('[TaskManagement] Removed from scheduled set');
      } else {
        newSet.add(taskId);
        console.log('[TaskManagement] Added to scheduled set');
      }
      return newSet;
    });
  };

  // Helper to check if a task is scheduled (from backend or local state)
  const isTaskScheduled = (task: Task): boolean => {
    return task.scheduledStart !== undefined || scheduledTaskIds.has(task.id);
  };

  // Calculate statistics
  const stats = useMemo(() => {
    const total = tasks.length;
    const scheduled = tasks.filter(t => isTaskScheduled(t)).length;
    const unscheduled = tasks.filter(t => !isTaskScheduled(t)).length;
    const overdue = tasks.filter(t => 
      t.deadline && new Date(t.deadline) < new Date() && !isTaskScheduled(t)
    ).length;

    return { total, scheduled, unscheduled, overdue };
  }, [tasks, scheduledTaskIds]);

  // Filter tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      // Category filter
      if (filterCategory !== 'all' && task.category !== filterCategory) return false;

      // Status filter
      const isScheduled = isTaskScheduled(task);
      if (filterStatus === 'scheduled' && !isScheduled) return false;
      if (filterStatus === 'unscheduled' && isScheduled) return false;

      // Time filter
      if (filterTime === 'today' && task.deadline) {
        const today = new Date();
        const deadline = new Date(task.deadline);
        if (deadline.toDateString() !== today.toDateString()) return false;
      }
      if (filterTime === 'week' && task.deadline) {
        const today = new Date();
        const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        const deadline = new Date(task.deadline);
        if (deadline < today || deadline > weekFromNow) return false;
      }

      return true;
    });
  }, [tasks, filterCategory, filterStatus, filterTime, filterPriority, scheduledTaskIds]);

  // AI Suggestions
  const aiSuggestions = useMemo(() => {
    const suggestions: Array<{ id: string; message: string; action: string }> = [];
    
    const noDeadline = tasks.filter(t => !t.deadline).length;
    if (noDeadline > 0) {
      suggestions.push({
        id: '1',
        message: `${noDeadline} task${noDeadline > 1 ? 's have' : ' has'} no deadline — want me to assign reasonable ones?`,
        action: 'assign-deadlines',
      });
    }

    if (stats.unscheduled > 0) {
      suggestions.push({
        id: '2',
        message: `You have ${stats.unscheduled} unscheduled task${stats.unscheduled > 1 ? 's' : ''} — should I place them throughout this week?`,
        action: 'schedule-all',
      });
    }

    if (stats.overdue > 0) {
      suggestions.push({
        id: '3',
        message: `${stats.overdue} task${stats.overdue > 1 ? 's are' : ' is'} overdue — let me help you reschedule.`,
        action: 'reschedule-overdue',
      });
    }

    return suggestions;
  }, [tasks, stats]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 relative">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-200/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-200/20 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 p-8 max-w-[1800px] mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 rounded-xl bg-white/80 border-2 border-gray-300 hover:border-gray-400 transition-all flex items-center gap-2 text-gray-800 focus:outline-none focus:ring-4 focus:ring-blue-300"
              aria-label="Back to calendar"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-4xl text-gray-900">Task management</h1>
              <p className="text-gray-600">Manage your task backlog and schedule</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Task List Selector */}
            <div className="bg-white/80 rounded-xl border-2 border-gray-300 p-1 flex items-center gap-2 shadow-sm">
              <Folder className="w-4 h-4 text-gray-600 ml-2" aria-hidden="true" />
              {taskLists.length > 0 ? (
                <select
                  value={selectedTaskListId}
                  onChange={(e) => onTaskListChange(e.target.value)}
                  className="px-4 py-2 rounded-lg bg-transparent border-none text-gray-900 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-300 cursor-pointer appearance-none pr-8 min-w-[150px]"
                  aria-label="Select task list"
                >
                  {taskLists.map((taskList) => (
                    <option key={taskList.id} value={taskList.id}>
                      {taskList.title}
                    </option>
                  ))}
                </select>
              ) : (
                <span className="px-4 py-2 text-gray-500 text-sm">Loading lists...</span>
              )}
            </div>
            <div className="bg-white/80 rounded-xl border-2 border-gray-300 p-1 flex gap-1 shadow-sm">
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300 ${
                  viewMode === 'list'
                    ? 'bg-gradient-to-r from-blue-400 to-purple-400 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
                aria-label="List view"
                aria-pressed={viewMode === 'list'}
              >
                <List className="w-4 h-4" aria-hidden="true" />
                List
              </button>
              <button
                onClick={() => setViewMode('kanban')}
                className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300 ${
                  viewMode === 'kanban'
                    ? 'bg-gradient-to-r from-blue-400 to-purple-400 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
                aria-label="Kanban view"
                aria-pressed={viewMode === 'kanban'}
              >
                <LayoutGrid className="w-4 h-4" aria-hidden="true" />
                Kanban
              </button>
            </div>

            <button
              onClick={() => setShowTaskForm(true)}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:from-blue-700 hover:to-purple-700 hover:shadow-lg hover:scale-105 transition-all flex items-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300"
            >
              <Plus className="w-5 h-5" aria-hidden="true" />
              Add task
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={List}
            label="Total tasks"
            value={stats.total}
            color="blue"
          />
          <StatCard
            icon={Calendar}
            label="Scheduled"
            value={stats.scheduled}
            color="emerald"
          />
          <StatCard
            icon={Clock}
            label="Unscheduled"
            value={stats.unscheduled}
            color="purple"
          />
          <StatCard
            icon={AlertCircle}
            label="Overdue"
            value={stats.overdue}
            color="red"
          />
        </div>

        {/* Filter Bar */}
        <div className="glass-strong rounded-2xl p-6 border-2 border-gray-200 shadow-md mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-gray-700" aria-hidden="true" />
            <h2 className="text-gray-900 font-semibold">Filters</h2>
          </div>

          <div className="grid grid-cols-4 gap-4">
            {/* Category Filter */}
            <div>
              <label htmlFor="filter-category" className="block text-sm text-gray-700 mb-2 font-semibold">
                Category
              </label>
              <select
                id="filter-category"
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value as Category | 'all')}
                className="w-full px-4 py-2 rounded-lg bg-white border-2 border-gray-300 text-gray-900 focus:outline-none focus:border-blue-500 transition-all"
              >
                <option value="all">All categories</option>
                <option value="work">Work</option>
                <option value="personal">Personal</option>
                <option value="focus">Focus time</option>
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label htmlFor="filter-status" className="block text-sm text-gray-700 mb-2 font-semibold">
                Status
              </label>
              <select
                id="filter-status"
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
                className="w-full px-4 py-2 rounded-lg bg-white border-2 border-gray-300 text-gray-900 focus:outline-none focus:border-blue-500 transition-all"
              >
                <option value="all">All status</option>
                <option value="scheduled">Scheduled</option>
                <option value="unscheduled">Unscheduled</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            {/* Time Filter */}
            <div>
              <label htmlFor="filter-time" className="block text-sm text-gray-700 mb-2 font-semibold">
                Time
              </label>
              <select
                id="filter-time"
                value={filterTime}
                onChange={(e) => setFilterTime(e.target.value as FilterTime)}
                className="w-full px-4 py-2 rounded-lg bg-white border-2 border-gray-300 text-gray-900 focus:outline-none focus:border-blue-500 transition-all"
              >
                <option value="all">All time</option>
                <option value="today">Today</option>
                <option value="week">This week</option>
                <option value="later">Later</option>
              </select>
            </div>

            {/* Priority Filter */}
            <div>
              <label htmlFor="filter-priority" className="block text-sm text-gray-700 mb-2 font-semibold">
                Priority
              </label>
              <select
                id="filter-priority"
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value as FilterPriority)}
                className="w-full px-4 py-2 rounded-lg bg-white border-2 border-gray-300 text-gray-900 focus:outline-none focus:border-blue-500 transition-all"
              >
                <option value="all">All priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="relative flex gap-8">
          {/* Task List/Kanban */}
          <div className={`flex-1 transition-all duration-500 ${isPanelOpen ? 'mr-[450px]' : 'mr-0'}`}>
            <div className="flex gap-8">
              <div className="flex-1">
                {viewMode === 'list' ? (
                  <TaskListView 
                    tasks={filteredTasks} 
                    onTaskClick={setSelectedTask}
                    onScheduleTask={handleScheduleTaskClick}
                    onToggleStatus={handleToggleTaskStatus}
                    isTaskScheduled={isTaskScheduled}
                  />
                ) : (
                  <KanbanView 
                    tasks={filteredTasks} 
                    onTaskClick={setSelectedTask}
                    onScheduleTask={handleScheduleTaskClick}
                    isTaskScheduled={isTaskScheduled}
                  />
                )}
              </div>

              {/* Task Detail Drawer */}
              <AnimatePresence>
                {selectedTask && (
                  <TaskDetailDrawer
                    task={selectedTask}
                    onClose={() => setSelectedTask(null)}
                    onUpdate={(updates) => {
                      onUpdateTask(selectedTask.id, updates);
                      setSelectedTask({ ...selectedTask, ...updates });
                    }}
                    onDelete={() => {
                      onDeleteTask(selectedTask.id);
                      setSelectedTask(null);
                    }}
                    onSchedule={() => {
                      handleScheduleTaskClick(selectedTask.id);
                      setSelectedTask(null);
                    }}
                  />
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* AI Panel */}
          <AIPanel
            isOpen={isPanelOpen}
            onToggle={() => setIsPanelOpen(!isPanelOpen)}
            onAddTask={onAddTask}
            onSendMessageRef={aiPanelSendMessageRef}
          />
        </div>

        {/* AI Suggestions */}
        {aiSuggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8 glass-strong rounded-2xl p-6 border-2 border-purple-300 shadow-lg"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center shadow-sm" aria-hidden="true">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-gray-900 font-semibold">AI suggestions</h3>
            </div>

            <div className="space-y-3">
              {aiSuggestions.map((suggestion) => (
                <div
                  key={suggestion.id}
                  className="bg-white/80 rounded-xl p-4 border-2 border-purple-200 flex items-center justify-between hover:border-purple-400 transition-all"
                >
                  <p className="text-gray-800">{suggestion.message}</p>
                  <button
                    className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 transition-all flex items-center gap-2 focus:outline-none focus:ring-4 focus:ring-purple-300 shrink-0 ml-4"
                  >
                    <Zap className="w-4 h-4" aria-hidden="true" />
                    Apply
                  </button>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      {/* Task Form Modal */}
      <AnimatePresence>
        {showTaskForm && (
          <TaskForm
            onClose={() => setShowTaskForm(false)}
            onSubmit={(task) => {
              onAddTask(task);
              setShowTaskForm(false);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: { 
  icon: any; 
  label: string; 
  value: number; 
  color: string;
}) {
  const colorClasses = {
    blue: 'from-blue-400 to-blue-500 border-blue-300',
    emerald: 'from-emerald-400 to-emerald-500 border-emerald-300',
    purple: 'from-purple-400 to-purple-500 border-purple-300',
    red: 'from-red-400 to-red-500 border-red-300',
  }[color] || 'from-gray-400 to-gray-500 border-gray-300';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-strong rounded-2xl p-6 border-2 ${colorClasses.split(' ')[1]} shadow-md`}
    >
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${colorClasses.split(' ')[0]} flex items-center justify-center shadow-sm`} aria-hidden="true">
          <Icon className="w-5 h-5 text-white" />
        </div>
        <span className="text-sm text-gray-700 font-semibold">{label}</span>
      </div>
      <div className="text-3xl text-gray-900 font-bold">{value}</div>
    </motion.div>
  );
}

function TaskListView({ 
  tasks, 
  onTaskClick,
  onScheduleTask,
  onToggleStatus,
  isTaskScheduled
}: { 
  tasks: Task[]; 
  onTaskClick: (task: Task) => void;
  onScheduleTask: (taskId: string) => void;
  onToggleStatus: (taskId: string) => void;
  isTaskScheduled: (task: Task) => boolean;
}) {
  const categoryColors: Record<Category, string> = {
    work: 'from-blue-400 to-blue-500',
    personal: 'from-purple-400 to-pink-500',
    focus: 'from-emerald-400 to-teal-500',
  };

  if (tasks.length === 0) {
    return (
      <div className="glass-strong rounded-2xl p-12 border-2 border-gray-200 text-center">
        <div className="text-gray-500 mb-4">
          <List className="w-12 h-12 mx-auto opacity-50" aria-hidden="true" />
        </div>
        <h3 className="text-xl text-gray-900 mb-2">No tasks found</h3>
        <p className="text-gray-600">Try adjusting your filters or add a new task</p>
      </div>
    );
  }

  return (
    <div className="glass-strong rounded-2xl overflow-hidden border-2 border-gray-200 shadow-md">
      <table className="w-full" role="table" aria-label="Task list">
        <thead>
          <tr className="bg-white/50 border-b-2 border-gray-200">
            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Task</th>
            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Category</th>
            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Duration</th>
            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Deadline</th>
            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Status</th>
            <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Actions</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task, index) => (
            <motion.tr
              key={task.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="border-b border-gray-100 hover:bg-white/60 transition-colors cursor-pointer"
              onClick={() => onTaskClick(task)}
            >
              <td className="px-6 py-4">
                <div className="text-gray-900 font-semibold">{task.title}</div>
              </td>
              <td className="px-6 py-4">
                <span className={`px-3 py-1 rounded-full bg-gradient-to-r ${categoryColors[task.category]} text-white text-sm capitalize shadow-sm`}>
                  {task.category}
                </span>
              </td>
              <td className="px-6 py-4">
                <div className="text-gray-700">{task.duration}h</div>
              </td>
              <td className="px-6 py-4">
                {task.deadline ? (
                  <div className={`text-sm ${
                    new Date(task.deadline) < new Date() ? 'text-red-700 font-semibold' : 'text-gray-700'
                  }`}>
                    {new Date(task.deadline).toLocaleDateString()}
                  </div>
                ) : (
                  <span className="text-gray-400 text-sm">No deadline</span>
                )}
              </td>
              <td className="px-6 py-4">
                {isTaskScheduled(task) ? (
                  <button
                    onClick={(e) => {
                      console.log('[TaskManagement] Scheduled button clicked for task:', task.id);
                      e.stopPropagation();
                      onToggleStatus(task.id);
                    }}
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 text-sm hover:bg-emerald-200 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-emerald-400"
                    title="Click to mark as Unscheduled"
                  >
                    <CheckCircle2 className="w-4 h-4" aria-hidden="true" />
                    Scheduled
                  </button>
                ) : (
                  <button
                    onClick={(e) => {
                      console.log('[TaskManagement] Unscheduled button clicked for task:', task.id);
                      e.stopPropagation();
                      onToggleStatus(task.id);
                    }}
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-gray-100 text-gray-700 text-sm hover:bg-gray-200 transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-gray-400"
                    title="Click to mark as Scheduled"
                  >
                    <Clock className="w-4 h-4" aria-hidden="true" />
                    Unscheduled
                  </button>
                )}
              </td>
              <td className="px-6 py-4">
                {!isTaskScheduled(task) && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onScheduleTask(task.id);
                    }}
                    className="px-3 py-1 rounded-lg bg-blue-100 text-blue-700 hover:bg-blue-200 transition-all text-sm flex items-center gap-1 focus:outline-none focus:ring-4 focus:ring-blue-300"
                  >
                    <Sparkles className="w-3 h-3" aria-hidden="true" />
                    Schedule
                  </button>
                )}
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function KanbanView({ 
  tasks, 
  onTaskClick,
  onScheduleTask,
  isTaskScheduled
}: { 
  tasks: Task[]; 
  onTaskClick: (task: Task) => void;
  onScheduleTask: (taskId: string) => void;
  isTaskScheduled: (task: Task) => boolean;
}) {
  const columns = {
    backlog: tasks.filter(t => !isTaskScheduled(t)),
    scheduled: tasks.filter(t => isTaskScheduled(t) && !t.scheduledEnd),
    completed: tasks.filter(t => t.scheduledEnd && new Date(t.scheduledEnd) < new Date()),
  };

  return (
    <div className="grid grid-cols-3 gap-6">
      <KanbanColumn
        title="Backlog"
        tasks={columns.backlog}
        color="purple"
        onTaskClick={onTaskClick}
        onScheduleTask={onScheduleTask}
        isTaskScheduled={isTaskScheduled}
      />
      <KanbanColumn
        title="Scheduled"
        tasks={columns.scheduled}
        color="blue"
        onTaskClick={onTaskClick}
        onScheduleTask={onScheduleTask}
        isTaskScheduled={isTaskScheduled}
      />
      <KanbanColumn
        title="Completed"
        tasks={columns.completed}
        color="emerald"
        onTaskClick={onTaskClick}
        onScheduleTask={onScheduleTask}
        isTaskScheduled={isTaskScheduled}
      />
    </div>
  );
}

function KanbanColumn({ 
  title, 
  tasks, 
  color, 
  onTaskClick,
  onScheduleTask,
  isTaskScheduled
}: { 
  title: string; 
  tasks: Task[]; 
  color: string;
  onTaskClick: (task: Task) => void;
  onScheduleTask: (taskId: string) => void;
  isTaskScheduled: (task: Task) => boolean;
}) {
  const categoryColors: Record<Category, string> = {
    work: 'from-blue-400 to-blue-500',
    personal: 'from-purple-400 to-pink-500',
    focus: 'from-emerald-400 to-teal-500',
  };

  const headerColor = {
    purple: 'from-purple-400 to-purple-500 border-purple-300',
    blue: 'from-blue-400 to-blue-500 border-blue-300',
    emerald: 'from-emerald-400 to-emerald-500 border-emerald-300',
  }[color] || 'from-gray-400 to-gray-500 border-gray-300';

  return (
    <div className="glass-strong rounded-2xl p-4 border-2 border-gray-200 shadow-md">
      <div className={`bg-gradient-to-r ${headerColor.split(' ')[0]} rounded-xl p-4 mb-4 shadow-sm`}>
        <h3 className="text-white font-semibold flex items-center justify-between">
          <span>{title}</span>
          <span className="text-sm bg-white/20 px-2 py-1 rounded-full">{tasks.length}</span>
        </h3>
      </div>

      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {tasks.map((task, index) => (
          <motion.div
            key={task.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => onTaskClick(task)}
            className="bg-white/80 rounded-xl p-4 border-2 border-gray-200 hover:border-gray-300 hover:shadow-md transition-all cursor-pointer"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="text-gray-900 font-semibold flex-1">{task.title}</h4>
              <span className={`px-2 py-1 rounded-full bg-gradient-to-r ${categoryColors[task.category]} text-white text-xs capitalize ml-2 shrink-0`}>
                {task.category}
              </span>
            </div>

            <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" aria-hidden="true" />
                {task.duration}h
              </span>
              {task.deadline && (
                <span className={`flex items-center gap-1 ${
                  new Date(task.deadline) < new Date() ? 'text-red-700 font-semibold' : ''
                }`}>
                  <Calendar className="w-3 h-3" aria-hidden="true" />
                  {new Date(task.deadline).toLocaleDateString()}
                </span>
              )}
            </div>

            {!isTaskScheduled(task) && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onScheduleTask(task.id);
                }}
                className="w-full px-3 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:from-blue-600 hover:to-purple-600 transition-all text-sm flex items-center justify-center gap-1 focus:outline-none focus:ring-4 focus:ring-blue-300"
              >
                <Sparkles className="w-3 h-3" aria-hidden="true" />
                Ask AI to schedule
              </button>
            )}
          </motion.div>
        ))}

        {tasks.length === 0 && (
          <div className="text-center py-8 text-gray-400">
            <p className="text-sm">No tasks in {title.toLowerCase()}</p>
          </div>
        )}
      </div>
    </div>
  );
}

function TaskDetailDrawer({ 
  task, 
  onClose, 
  onUpdate, 
  onDelete,
  onSchedule 
}: { 
  task: Task; 
  onClose: () => void; 
  onUpdate: (updates: Partial<Task>) => void;
  onDelete: () => void;
  onSchedule: () => void;
}) {
  const categoryColors: Record<Category, { gradient: string; border: string }> = {
    work: { gradient: 'from-blue-500 to-blue-600', border: 'border-blue-400' },
    personal: { gradient: 'from-purple-500 to-pink-600', border: 'border-purple-400' },
    focus: { gradient: 'from-emerald-500 to-teal-600', border: 'border-emerald-400' },
  };

  const colors = categoryColors[task.category];

  return (
    <motion.div
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      transition={{ type: 'spring', damping: 30, stiffness: 300 }}
      className={`w-[400px] glass-strong rounded-2xl p-6 border-2 ${colors.border} shadow-xl shrink-0 max-h-[calc(100vh-200px)] overflow-y-auto`}
    >
      <div className="flex items-start justify-between mb-6">
        <h3 className="text-xl text-gray-900 font-semibold">Task details</h3>
        <button
          onClick={onClose}
          className="p-2 rounded-lg bg-white/80 border border-gray-300 hover:border-gray-400 transition-all focus:outline-none focus:ring-4 focus:ring-blue-300"
          aria-label="Close task details"
        >
          <X className="w-4 h-4 text-gray-700" />
        </button>
      </div>

      <div className="space-y-4">
        {/* Title */}
        <div>
          <label className="block text-sm text-gray-700 mb-2 font-semibold">Title</label>
          <div className="text-lg text-gray-900">{task.title}</div>
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm text-gray-700 mb-2 font-semibold">Category</label>
          <span className={`inline-block px-3 py-1 rounded-full bg-gradient-to-r ${colors.gradient} text-white capitalize`}>
            {task.category}
          </span>
        </div>

        {/* Duration */}
        <div>
          <label className="block text-sm text-gray-700 mb-2 font-semibold">Duration</label>
          <div className="text-gray-900">{task.duration} hour(s)</div>
        </div>

        {/* Deadline */}
        <div>
          <label className="block text-sm text-gray-700 mb-2 font-semibold">Deadline</label>
          <div className="text-gray-900">
            {task.deadline ? new Date(task.deadline).toLocaleDateString() : 'No deadline set'}
          </div>
        </div>

        {/* Scheduled Time */}
        {task.scheduledStart && (
          <div>
            <label className="block text-sm text-gray-700 mb-2 font-semibold">Scheduled</label>
            <div className="text-gray-900">
              {new Date(task.scheduledStart).toLocaleString()}
            </div>
          </div>
        )}

        {/* Constraints */}
        {task.constraints && (
          <>
            {task.constraints.location && (
              <div>
                <label className="block text-sm text-gray-700 mb-2 font-semibold">Location</label>
                <div className="text-gray-900">{task.constraints.location}</div>
              </div>
            )}
            {task.constraints.timeOfDay && (
              <div>
                <label className="block text-sm text-gray-700 mb-2 font-semibold">Time preference</label>
                <div className="text-gray-900 capitalize">{task.constraints.timeOfDay}</div>
              </div>
            )}
            {task.constraints.energyLevel && (
              <div>
                <label className="block text-sm text-gray-700 mb-2 font-semibold">Energy level</label>
                <div className="text-gray-900 capitalize">{task.constraints.energyLevel}</div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Actions */}
      <div className="mt-6 space-y-3">
        {!task.scheduledStart && (
          <button
            onClick={onSchedule}
            className="w-full px-4 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:from-blue-700 hover:to-purple-700 hover:shadow-lg transition-all flex items-center justify-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300"
          >
            <Sparkles className="w-5 h-5" aria-hidden="true" />
            Ask AI to schedule
          </button>
        )}

        <div className="flex gap-3">
          <button
            className="flex-1 px-4 py-2 rounded-lg bg-white border-2 border-gray-300 text-gray-700 hover:border-blue-400 transition-all flex items-center justify-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300"
          >
            <Edit2 className="w-4 h-4" aria-hidden="true" />
            Edit
          </button>
          <button
            onClick={onDelete}
            className="flex-1 px-4 py-2 rounded-lg bg-white border-2 border-red-400 text-red-700 hover:bg-red-50 transition-all flex items-center justify-center gap-2 focus:outline-none focus:ring-4 focus:ring-red-300"
          >
            <Trash2 className="w-4 h-4" aria-hidden="true" />
            Delete
          </button>
        </div>
      </div>
    </motion.div>
  );
}
