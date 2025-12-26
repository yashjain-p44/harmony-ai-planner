import React, { useMemo } from 'react';
import { motion } from 'motion/react';
import type { Task, UserPreferences, Category } from '../App';
import type { ViewMode } from './Dashboard';

interface CalendarViewProps {
  tasks: Task[];
  viewMode: ViewMode;
  selectedDate: Date;
  onTaskClick: (task: Task) => void;
  preferences: UserPreferences;
}

const CATEGORY_COLORS: Record<Category, { bg: string; border: string; text: string }> = {
  work: {
    bg: 'bg-blue-100',
    border: 'border-blue-400',
    text: 'text-blue-800',
  },
  personal: {
    bg: 'bg-purple-100',
    border: 'border-purple-400',
    text: 'text-purple-800',
  },
  focus: {
    bg: 'bg-emerald-100',
    border: 'border-emerald-400',
    text: 'text-emerald-800',
  },
};

export function CalendarView({ tasks, viewMode, selectedDate, onTaskClick, preferences }: CalendarViewProps) {
  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Get tasks for the current week
  const weekTasks = useMemo(() => {
    const startOfWeek = new Date(selectedDate);
    startOfWeek.setDate(selectedDate.getDate() - selectedDate.getDay());
    startOfWeek.setHours(0, 0, 0, 0);

    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(endOfWeek.getDate() + 7);

    return tasks.filter((task) => {
      if (!task.scheduledStart) return false;
      const taskDate = new Date(task.scheduledStart);
      return taskDate >= startOfWeek && taskDate < endOfWeek;
    });
  }, [tasks, selectedDate]);

  const weekDays = useMemo(() => {
    const startOfWeek = new Date(selectedDate);
    startOfWeek.setDate(selectedDate.getDate() - selectedDate.getDay());
    return Array.from({ length: 7 }, (_, i) => {
      const day = new Date(startOfWeek);
      day.setDate(day.getDate() + i);
      return day;
    });
  }, [selectedDate]);

  if (viewMode === 'month') {
    return <MonthView tasks={tasks} selectedDate={selectedDate} onTaskClick={onTaskClick} />;
  }

  if (viewMode === 'day') {
    return (
      <DayView
        tasks={weekTasks.filter(
          (t) =>
            t.scheduledStart &&
            new Date(t.scheduledStart).toDateString() === selectedDate.toDateString()
        )}
        selectedDate={selectedDate}
        onTaskClick={onTaskClick}
        preferences={preferences}
      />
    );
  }

  // Week View
  return (
    <div className="h-full overflow-auto p-8">
      <div className="glass-strong rounded-2xl overflow-hidden shadow-lg border border-gray-200" role="region" aria-label="Weekly calendar view">
        {/* Month Header */}
        <div className="p-6 border-b border-gray-200 bg-white/50">
          <h2 className="text-3xl text-gray-900 text-center font-bold">
            {selectedDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </h2>
        </div>
        {/* Week Header */}
        <div className="grid grid-cols-8 border-b border-gray-200 bg-white/50">
          <div className="p-4 border-r border-gray-200">
            <span className="sr-only">Time column</span>
          </div>
          {weekDays.map((day, i) => {
            const isToday = day.toDateString() === new Date().toDateString();
            return (
              <div
                key={i}
                className={`p-4 text-center border-r border-gray-200 last:border-r-0 ${
                  isToday ? 'bg-blue-100/50' : ''
                }`}
                role="columnheader"
                aria-label={day.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
              >
                <div className="text-sm text-gray-800 font-semibold">
                  {day.toLocaleDateString('en-US', { weekday: 'short' })}
                </div>
                <div className={`text-xl mt-1 font-bold ${isToday ? 'text-blue-700' : 'text-gray-900'}`}>
                  {day.getDate()}
                </div>
                {isToday && <span className="sr-only">(Today)</span>}
              </div>
            );
          })}
        </div>

        {/* Time Grid */}
        <div className="relative bg-white/30">
          {hours.map((hour) => (
            <div key={hour} className="grid grid-cols-8 border-b border-gray-100 h-20">
              <div className="p-4 border-r border-gray-200 flex items-start bg-white/40" role="rowheader">
                <time className="text-sm text-gray-600 font-semibold">
                  {hour.toString().padStart(2, '0')}:00
                </time>
              </div>
              {weekDays.map((day, dayIndex) => {
                const dayTasks = weekTasks.filter((task) => {
                  if (!task.scheduledStart) return false;
                  const taskDate = new Date(task.scheduledStart);
                  return (
                    taskDate.toDateString() === day.toDateString() &&
                    taskDate.getHours() === hour
                  );
                });

                return (
                  <div
                    key={dayIndex}
                    className="border-r border-gray-100 last:border-r-0 p-1 relative"
                    role="gridcell"
                    aria-label={`${day.toLocaleDateString('en-US', { weekday: 'short' })} ${hour}:00 - ${dayTasks.length} tasks`}
                  >
                    {dayTasks.map((task, taskIndex) => {
                      const colors = CATEGORY_COLORS[task.category];
                      const heightInPixels = (task.duration / 1) * 80;

                      return (
                        <motion.button
                          key={task.id}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          onClick={() => onTaskClick(task)}
                          className={`absolute left-1 right-1 ${colors.bg} ${colors.border} border-2 rounded-lg p-2 cursor-pointer hover:scale-105 hover:shadow-md transition-all overflow-hidden focus:outline-none focus:ring-4 focus:ring-blue-400 ${
                            task.isFromGoogleCalendar ? 'border-dashed' : ''
                          }`}
                          style={{
                            height: `${heightInPixels}px`,
                            top: `${taskIndex * 4}px`,
                            zIndex: taskIndex + 1,
                          }}
                          aria-label={`${task.title}, ${task.category} category, ${task.duration} hours${task.isFromGoogleCalendar ? ', imported from Google Calendar' : ''}, click to view details`}
                          title={task.isFromGoogleCalendar ? 'Imported from Google Calendar' : undefined}
                        >
                          <div className={`text-sm ${colors.text} truncate font-semibold`}>
                            {task.isFromGoogleCalendar && <span className="mr-1">📅</span>}
                            {task.title}
                          </div>
                          <div className="text-xs text-gray-700">{task.duration}h</div>
                        </motion.button>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Empty State */}
      {tasks.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center"
          role="status"
          aria-live="polite"
        >
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-200/40 to-purple-200/40 flex items-center justify-center mx-auto mb-4" aria-hidden="true">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
              className="text-3xl"
            >
              ✨
            </motion.div>
          </div>
          <h3 className="text-2xl text-gray-900 mb-2">Your calendar awaits</h3>
          <p className="text-gray-700 mb-6">Let's start by adding your first task</p>
          <div className="inline-block px-6 py-3 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md">
            Click "Add Task" above
          </div>
        </motion.div>
      )}
    </div>
  );
}

function MonthView({
  tasks,
  selectedDate,
  onTaskClick,
}: {
  tasks: Task[];
  selectedDate: Date;
  onTaskClick: (task: Task) => void;
}) {
  const monthDays = useMemo(() => {
    const year = selectedDate.getFullYear();
    const month = selectedDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - startDate.getDay());

    const days: Date[] = [];
    const current = new Date(startDate);

    for (let i = 0; i < 42; i++) {
      days.push(new Date(current));
      current.setDate(current.getDate() + 1);
    }

    return days;
  }, [selectedDate]);

  const getTasksForDay = (day: Date) => {
    return tasks.filter((task) => {
      if (!task.scheduledStart) return false;
      return new Date(task.scheduledStart).toDateString() === day.toDateString();
    });
  };

  return (
    <div className="h-full overflow-auto p-8">
      <div className="glass-strong rounded-2xl overflow-hidden border-white/10 p-6">
        <h2 className="text-3xl text-gray-900 mb-6 text-center font-bold">
          {selectedDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
        </h2>

        <div className="grid grid-cols-7 gap-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div key={day} className="text-center text-gray-700 py-2 font-semibold">
              {day}
            </div>
          ))}

          {monthDays.map((day, i) => {
            const isToday = day.toDateString() === new Date().toDateString();
            const isCurrentMonth = day.getMonth() === selectedDate.getMonth();
            const dayTasks = getTasksForDay(day);

            return (
              <div
                key={i}
                className={`min-h-24 rounded-lg p-2 border transition-all ${
                  isToday
                    ? 'border-cyan-500 bg-cyan-500/10'
                    : 'border-white/10 glass'
                } ${!isCurrentMonth ? 'opacity-40' : ''}`}
              >
                <div className={`text-sm mb-1 font-semibold ${isToday ? 'text-cyan-600' : 'text-gray-900'}`}>
                  {day.getDate()}
                </div>
                <div className="space-y-1">
                  {dayTasks.slice(0, 3).map((task) => {
                    const colors = CATEGORY_COLORS[task.category];
                    return (
                      <div
                        key={task.id}
                        onClick={() => onTaskClick(task)}
                        className={`text-xs px-2 py-1 rounded ${colors.bg} ${colors.text} cursor-pointer hover:scale-105 transition-transform truncate`}
                      >
                        {task.title}
                      </div>
                    );
                  })}
                  {dayTasks.length > 3 && (
                    <div className="text-xs text-slate-400 px-2">
                      +{dayTasks.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function DayView({
  tasks,
  selectedDate,
  onTaskClick,
  preferences,
}: {
  tasks: Task[];
  selectedDate: Date;
  onTaskClick: (task: Task) => void;
  preferences: UserPreferences;
}) {
  const hours = Array.from({ length: 24 }, (_, i) => i);

  return (
    <div className="h-full overflow-auto p-8">
      <div className="max-w-4xl mx-auto">
        <div className="glass-strong rounded-2xl overflow-hidden border-white/10">
          <div className="p-6 border-b border-white/10 bg-gradient-to-r from-cyan-500/10 to-violet-500/10">
            <h2 className="text-3xl text-white">
              {selectedDate.toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
              })}
            </h2>
          </div>

          <div className="p-4">
            {hours.map((hour) => {
              const hourTasks = tasks.filter((task) => {
                if (!task.scheduledStart) return false;
                return new Date(task.scheduledStart).getHours() === hour;
              });

              return (
                <div
                  key={hour}
                  className="flex border-b border-white/5 min-h-20 hover:bg-white/5 transition-colors"
                >
                  <div className="w-20 p-4 text-slate-500 text-sm">
                    {hour.toString().padStart(2, '0')}:00
                  </div>
                  <div className="flex-1 p-2 relative">
                    {hourTasks.map((task) => {
                      const colors = CATEGORY_COLORS[task.category];
                      return (
                        <motion.div
                          key={task.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          onClick={() => onTaskClick(task)}
                          className={`${colors.bg} ${colors.border} border-2 rounded-lg p-4 mb-2 cursor-pointer hover:scale-105 transition-transform`}
                        >
                          <div className={`${colors.text} mb-1`}>{task.title}</div>
                          <div className="text-sm text-slate-400">{task.duration} hour(s)</div>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}