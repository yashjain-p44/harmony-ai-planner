import React, { useState } from 'react';
import { motion } from 'motion/react';
import { X, Edit2, Trash2, Calendar, Clock, MapPin, Zap } from 'lucide-react';
import type { Task, Category } from '../App';

interface TaskDetailModalProps {
  task: Task;
  onClose: () => void;
  onUpdate: (updates: Partial<Task>) => void;
  onDelete: () => void;
}

export function TaskDetailModal({ task, onClose, onUpdate, onDelete }: TaskDetailModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTitle, setEditedTitle] = useState(task.title);
  const [editedDuration, setEditedDuration] = useState(task.duration);

  const categoryColors: Record<Category, { gradient: string; border: string; icon: string }> = {
    work: { gradient: 'from-blue-500 to-blue-600', border: 'border-blue-400', icon: '💼' },
    personal: { gradient: 'from-purple-500 to-pink-600', border: 'border-purple-400', icon: '✨' },
    focus: { gradient: 'from-emerald-500 to-teal-600', border: 'border-emerald-400', icon: '🎯' },
  };

  const colors = categoryColors[task.category];

  const handleSave = () => {
    onUpdate({
      title: editedTitle,
      duration: editedDuration,
    });
    setIsEditing(false);
  };

  const handleMove = () => {
    const newStart = new Date(task.scheduledStart!);
    newStart.setDate(newStart.getDate() + 1);
    const newEnd = new Date(newStart.getTime() + task.duration * 60 * 60 * 1000);

    onUpdate({
      scheduledStart: newStart,
      scheduledEnd: newEnd,
    });
    onClose();
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-8"
      onClick={onClose}
      role="dialog"
      aria-labelledby="task-detail-title"
      aria-modal="true"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className={`glass-strong rounded-3xl p-8 max-w-lg w-full border-2 ${colors.border} relative overflow-hidden`}
      >
        {/* Background gradient */}
        <div className={`absolute top-0 right-0 w-64 h-64 bg-gradient-to-br ${colors.gradient} opacity-10 rounded-full blur-3xl pointer-events-none`} aria-hidden="true" />

        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-start gap-3 flex-1">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colors.gradient} flex items-center justify-center text-2xl shrink-0 shadow-md`} aria-hidden="true">
                {colors.icon}
              </div>
              <div className="flex-1">
                {isEditing ? (
                  <label htmlFor="edit-task-title" className="sr-only">Task title</label>
                ) : null}
                {isEditing ? (
                  <input
                    id="edit-task-title"
                    type="text"
                    value={editedTitle}
                    onChange={(e) => setEditedTitle(e.target.value)}
                    className="w-full text-2xl text-gray-900 bg-transparent border-b-2 border-gray-300 focus:outline-none focus:border-blue-500 pb-1"
                    autoFocus
                  />
                ) : (
                  <h2 id="task-detail-title" className="text-2xl text-gray-900 mb-1">{task.title}</h2>
                )}
                <div className={`inline-block px-3 py-1 rounded-full bg-gradient-to-r ${colors.gradient} text-sm text-white capitalize mt-2 shadow-sm`}>
                  {task.category}
                </div>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-white/80 border border-gray-300 hover:border-gray-400 transition-all shrink-0 focus:outline-none focus:ring-4 focus:ring-blue-300"
              aria-label="Close task details"
            >
              <X className="w-5 h-5 text-gray-700" />
            </button>
          </div>

          {/* Details */}
          <div className="space-y-4 mb-6">
            <div className="bg-white/80 rounded-xl p-4 border border-gray-200 shadow-sm">
              <div className="flex items-center gap-2 text-gray-600 mb-2">
                <Clock className="w-4 h-4" aria-hidden="true" />
                <span className="text-sm font-semibold">Duration</span>
              </div>
              {isEditing ? (
                <>
                  <label htmlFor="edit-task-duration" className="sr-only">Duration in hours</label>
                  <input
                    id="edit-task-duration"
                    type="number"
                    min="0.5"
                    step="0.5"
                    value={editedDuration}
                    onChange={(e) => setEditedDuration(parseFloat(e.target.value))}
                    className="w-full text-lg text-gray-900 bg-transparent border-b-2 border-gray-300 focus:outline-none focus:border-blue-500"
                  />
                </>
              ) : (
                <div className="text-lg text-gray-900">{task.duration} hour(s)</div>
              )}
            </div>

            {task.scheduledStart && (
              <div className="bg-white/80 rounded-xl p-4 border border-gray-200 shadow-sm">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Calendar className="w-4 h-4" aria-hidden="true" />
                  <span className="text-sm font-semibold">Scheduled</span>
                </div>
                <div className="text-lg text-gray-900">
                  {new Date(task.scheduledStart).toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric',
                  })}
                </div>
                <div className="text-sm text-gray-600 mt-1">
                  {new Date(task.scheduledStart).toLocaleTimeString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                  {' - '}
                  {task.scheduledEnd &&
                    new Date(task.scheduledEnd).toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                </div>
              </div>
            )}

            {task.deadline && (
              <div className="bg-white/80 rounded-xl p-4 border border-gray-200 shadow-sm">
                <div className="flex items-center gap-2 text-gray-600 mb-2">
                  <Calendar className="w-4 h-4" aria-hidden="true" />
                  <span className="text-sm font-semibold">Deadline</span>
                </div>
                <div className="text-lg text-gray-900">
                  {new Date(task.deadline).toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </div>
              </div>
            )}

            {task.constraints && (
              <>
                {task.constraints.location && (
                  <div className="bg-white/80 rounded-xl p-4 border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-2 text-gray-600 mb-2">
                      <MapPin className="w-4 h-4" aria-hidden="true" />
                      <span className="text-sm font-semibold">Location</span>
                    </div>
                    <div className="text-lg text-gray-900">{task.constraints.location}</div>
                  </div>
                )}
                {task.constraints.energyLevel && (
                  <div className="bg-white/80 rounded-xl p-4 border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-2 text-gray-600 mb-2">
                      <Zap className="w-4 h-4" aria-hidden="true" />
                      <span className="text-sm font-semibold">Energy level</span>
                    </div>
                    <div className="text-lg text-gray-900 capitalize">{task.constraints.energyLevel}</div>
                  </div>
                )}
              </>
            )}
          </div>

          {/* Actions */}
          <nav className="flex gap-3" aria-label="Task actions">
            {isEditing ? (
              <>
                <button
                  onClick={() => setIsEditing(false)}
                  className="flex-1 px-4 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSave}
                  className="flex-1 px-4 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md hover:from-blue-700 hover:to-purple-700 hover:shadow-lg hover:scale-105 transition-all focus:outline-none focus:ring-4 focus:ring-blue-300"
                >
                  Save changes
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex-1 px-4 py-3 rounded-xl bg-white/80 border-2 border-gray-300 text-gray-800 hover:border-blue-400 transition-all flex items-center justify-center gap-2 focus:outline-none focus:ring-4 focus:ring-blue-300"
                  aria-label="Edit task"
                >
                  <Edit2 className="w-4 h-4" aria-hidden="true" />
                  Edit
                </button>
                <button
                  onClick={handleMove}
                  className="flex-1 px-4 py-3 rounded-xl bg-white/80 border-2 border-gray-300 text-gray-800 hover:border-purple-400 transition-all focus:outline-none focus:ring-4 focus:ring-purple-300"
                  aria-label="Move task to next day"
                >
                  Move
                </button>
                <button
                  onClick={onDelete}
                  className="px-4 py-3 rounded-xl bg-white/80 border-2 border-red-400 text-red-700 hover:bg-red-50 transition-all flex items-center gap-2 focus:outline-none focus:ring-4 focus:ring-red-300"
                  aria-label="Delete task"
                >
                  <Trash2 className="w-4 h-4" aria-hidden="true" />
                  Delete
                </button>
              </>
            )}
          </nav>
        </div>
      </motion.div>
    </motion.div>
  );
}
