import React, { useState } from 'react';
import { motion } from 'motion/react';
import { X, Calendar, Clock, Sparkles, MapPin, Zap } from 'lucide-react';
import type { Task, Category } from '../App';

interface TaskFormProps {
  onClose: () => void;
  onSubmit: (task: Task) => void;
}

export function TaskForm({ onClose, onSubmit }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState<Category>('work');
  const [duration, setDuration] = useState(1);
  const [deadline, setDeadline] = useState('');
  const [location, setLocation] = useState('');
  const [timeOfDay, setTimeOfDay] = useState('');
  const [energyLevel, setEnergyLevel] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    const now = new Date();
    const scheduledStart = deadline ? new Date(deadline) : new Date(now.getTime() + 24 * 60 * 60 * 1000);
    scheduledStart.setHours(9, 0, 0, 0);

    const newTask: Task = {
      id: Date.now().toString(),
      title,
      category,
      duration,
      deadline: deadline ? new Date(deadline) : undefined,
      scheduledStart,
      scheduledEnd: new Date(scheduledStart.getTime() + duration * 60 * 60 * 1000),
      constraints: {
        location: location || undefined,
        timeOfDay: timeOfDay || undefined,
        energyLevel: energyLevel || undefined,
      },
    };

    onSubmit(newTask);
  };

  const categories: { value: Category; label: string; gradient: string; icon: string }[] = [
    { value: 'work', label: 'Work', gradient: 'from-blue-500 to-blue-600', icon: '💼' },
    { value: 'personal', label: 'Personal', gradient: 'from-purple-500 to-pink-600', icon: '✨' },
    { value: 'focus', label: 'Focus Time', gradient: 'from-emerald-500 to-teal-600', icon: '🎯' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-8"
      onClick={onClose}
      role="dialog"
      aria-labelledby="task-form-title"
      aria-modal="true"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="glass-strong rounded-3xl p-8 max-w-2xl w-full border-2 border-blue-300 relative overflow-hidden"
      >
        {/* Background glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-200/30 rounded-full blur-3xl pointer-events-none" aria-hidden="true" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-200/30 rounded-full blur-3xl pointer-events-none" aria-hidden="true" />

        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center shadow-md" aria-hidden="true">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 id="task-form-title" className="text-2xl text-gray-900">Create new task</h2>
                <p className="text-sm text-gray-600">AI will schedule it optimally</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-white/80 border border-gray-300 hover:border-gray-400 transition-all focus:outline-none focus:ring-4 focus:ring-blue-300"
              aria-label="Close task form"
            >
              <X className="w-5 h-5 text-gray-700" />
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Task Title */}
            <div className="mb-6">
              <label htmlFor="task-title" className="block text-gray-900 mb-2 font-semibold">
                Task Title <span className="text-red-600" aria-label="required">*</span>
              </label>
              <input
                id="task-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g., Finish Q4 Report"
                className="w-full px-4 py-3 rounded-xl bg-white/90 border-2 border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:border-blue-500 transition-all"
                autoFocus
                required
                aria-required="true"
              />
            </div>

            {/* Category Selector */}
            <fieldset className="mb-6">
              <legend className="block text-gray-900 mb-3 font-semibold">
                Category <span className="text-red-600" aria-label="required">*</span>
              </legend>
              <div className="grid grid-cols-3 gap-3" role="radiogroup" aria-label="Task category">
                {categories.map((cat) => (
                  <button
                    key={cat.value}
                    type="button"
                    onClick={() => setCategory(cat.value)}
                    className={`p-4 rounded-xl transition-all focus:outline-none focus:ring-4 focus:ring-blue-300 ${
                      category === cat.value
                        ? `bg-gradient-to-r ${cat.gradient} border-2 border-white text-white scale-105 shadow-md`
                        : 'bg-white/80 border-2 border-gray-300 text-gray-700 hover:border-gray-400'
                    }`}
                    role="radio"
                    aria-checked={category === cat.value}
                    aria-label={cat.label}
                  >
                    <div className="text-2xl mb-2" aria-hidden="true">{cat.icon}</div>
                    <div className="text-sm font-semibold">{cat.label}</div>
                  </button>
                ))}
              </div>
            </fieldset>

            {/* Duration and Deadline */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label htmlFor="task-duration" className="block text-gray-900 mb-2 font-semibold flex items-center gap-2">
                  <Clock className="w-4 h-4" aria-hidden="true" />
                  Duration (hours) <span className="text-red-600" aria-label="required">*</span>
                </label>
              </div>
              <div>
                <label htmlFor="task-deadline" className="block text-gray-900 mb-2 font-semibold flex items-center gap-2">
                  <Calendar className="w-4 h-4" aria-hidden="true" />
                  Deadline
                </label>
                <input
                  id="task-deadline"
                  type="date"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-white/90 border-2 border-gray-300 text-gray-900 focus:outline-none focus:border-blue-500 transition-all"
                />
              </div>
            </div>

            {/* Optional Constraints */}
            <details className="mb-6">
              <summary className="text-purple-700 cursor-pointer mb-3 flex items-center gap-2 font-semibold hover:text-purple-800 focus:outline-none focus:ring-2 focus:ring-purple-300 rounded p-2">
                <Zap className="w-4 h-4" aria-hidden="true" />
                Advanced options (optional)
              </summary>
              <div className="space-y-3 ml-6">
                <div>
                  <label htmlFor="task-location" className="block text-sm text-gray-700 mb-1 font-semibold">
                    <MapPin className="w-3 h-3 inline mr-1" aria-hidden="true" />
                    Location
                  </label>
                  <input
                    id="task-location"
                    type="text"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g., Office, Home"
                    className="w-full px-3 py-2 rounded-lg bg-white/90 border-2 border-gray-300 text-gray-900 text-sm placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-all"
                  />
                </div>
                <div>
                  <label htmlFor="task-time-preference" className="block text-sm text-gray-700 mb-1 font-semibold">
                    Time of Day Preference
                  </label>
                  <select
                    id="task-time-preference"
                    value={timeOfDay}
                    onChange={(e) => setTimeOfDay(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-white/90 border-2 border-gray-300 text-gray-900 text-sm focus:outline-none focus:border-purple-500 transition-all"
                  >
                    <option value="">No preference</option>
                    <option value="morning">Morning</option>
                    <option value="afternoon">Afternoon</option>
                    <option value="evening">Evening</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="task-energy-level" className="block text-sm text-gray-700 mb-1 font-semibold">
                    Energy Level Required
                  </label>
                  <select
                    id="task-energy-level"
                    value={energyLevel}
                    onChange={(e) => setEnergyLevel(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-white/90 border-2 border-gray-300 text-gray-900 text-sm focus:outline-none focus:border-purple-500 transition-all"
                  >
                    <option value="">No preference</option>
                    <option value="high">High Energy</option>
                    <option value="medium">Medium Energy</option>
                    <option value="low">Low Energy</option>
                  </select>
                </div>
              </div>
            </details>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={!title.trim()}
                className="flex-1 px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:from-blue-700 hover:to-purple-700 hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center justify-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300"
                aria-label="Schedule task with AI"
              >
                <Sparkles className="w-5 h-5" aria-hidden="true" />
                Schedule with AI
              </button>
            </div>
          </form>
        </div>
      </motion.div>
    </motion.div>
  );
}