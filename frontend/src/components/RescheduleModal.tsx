import React, { useState } from 'react';
import { motion } from 'motion/react';
import { AlertTriangle, Check, X, ArrowRight } from 'lucide-react';
import type { Task, Category } from '../App';

interface RescheduleModalProps {
  task: Task;
  tasks: Task[];
  onClose: () => void;
  onReschedule: (updatedTasks: Task[]) => void;
}

type RescheduleOption = 'today' | 'week' | 'alternatives';

export function RescheduleModal({ task, tasks, onClose, onReschedule }: RescheduleModalProps) {
  const [selectedOption, setSelectedOption] = useState<RescheduleOption | null>(null);
  const [showComparison, setShowComparison] = useState(false);

  const categoryColors: Record<Category, { bg: string; border: string }> = {
    work: { bg: 'bg-blue-100', border: 'border-blue-400' },
    personal: { bg: 'bg-purple-100', border: 'border-purple-400' },
    focus: { bg: 'bg-emerald-100', border: 'border-emerald-400' },
  };

  const handleSelectOption = (option: RescheduleOption) => {
    setSelectedOption(option);
    setShowComparison(true);
  };

  const handleConfirm = () => {
    const updatedTasks = tasks.map((t) => {
      if (t.id === task.id) {
        const newStart = new Date(t.scheduledStart!);
        if (selectedOption === 'today') {
          newStart.setHours(newStart.getHours() + 2);
        } else if (selectedOption === 'week') {
          newStart.setDate(newStart.getDate() + 1);
        }
        return {
          ...t,
          scheduledStart: newStart,
          scheduledEnd: new Date(newStart.getTime() + t.duration * 60 * 60 * 1000),
        };
      }
      return t;
    });

    onReschedule(updatedTasks);
  };

  const getCurrentSchedule = () => {
    return tasks.filter(t => t.scheduledStart).slice(0, 3);
  };

  const getProposedSchedule = () => {
    return getCurrentSchedule().map((t, i) => ({
      ...t,
      scheduledStart: new Date(new Date(t.scheduledStart!).getTime() + i * 60 * 60 * 1000),
    }));
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-8"
      onClick={onClose}
      role="dialog"
      aria-labelledby="reschedule-title"
      aria-modal="true"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
        className="glass-strong rounded-3xl p-8 max-w-4xl w-full border-2 border-orange-400 relative overflow-hidden"
      >
        {/* Background glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-orange-200/30 rounded-full blur-3xl pointer-events-none" aria-hidden="true" />

        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-400 to-red-500 flex items-center justify-center shadow-md" aria-hidden="true">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 id="reschedule-title" className="text-2xl text-gray-900">Schedule conflict detected</h2>
                <p className="text-gray-600">AI detected an overlap in your calendar</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-white/80 border border-gray-300 hover:border-gray-400 transition-all focus:outline-none focus:ring-4 focus:ring-orange-300"
              aria-label="Close reschedule dialog"
            >
              <X className="w-5 h-5 text-gray-700" />
            </button>
          </div>

          {/* Conflicting Task Info */}
          <div className="bg-white/80 rounded-xl p-4 border-2 border-orange-400 mb-6 shadow-sm">
            <div className="text-sm text-orange-700 mb-2 font-semibold">Conflicting task</div>
            <div className="text-lg text-gray-900 font-semibold">{task.title}</div>
            <div className="text-sm text-gray-600 mt-1">
              {task.scheduledStart && new Date(task.scheduledStart).toLocaleString()}
            </div>
          </div>

          {!showComparison ? (
            /* Reschedule Options */
            <div className="space-y-3 mb-6">
              <div className="text-gray-900 mb-4 font-semibold">How would you like AI to reorganize?</div>
              
              <button
                onClick={() => handleSelectOption('today')}
                className="w-full p-4 rounded-xl bg-white/80 border-2 border-gray-300 hover:border-blue-400 transition-all text-left group focus:outline-none focus:ring-4 focus:ring-blue-300"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-gray-900 mb-1 font-semibold">Reschedule today only</div>
                    <div className="text-sm text-gray-600">
                      AI will adjust tasks within the same day
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity" aria-hidden="true" />
                </div>
              </button>

              <button
                onClick={() => handleSelectOption('week')}
                className="w-full p-4 rounded-xl bg-white/80 border-2 border-gray-300 hover:border-purple-400 transition-all text-left group focus:outline-none focus:ring-4 focus:ring-purple-300"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-gray-900 mb-1 font-semibold">Reschedule this week</div>
                    <div className="text-sm text-gray-600">
                      AI will optimize your entire week
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-purple-600 opacity-0 group-hover:opacity-100 transition-opacity" aria-hidden="true" />
                </div>
              </button>

              <button
                onClick={() => handleSelectOption('alternatives')}
                className="w-full p-4 rounded-xl bg-white/80 border-2 border-gray-300 hover:border-emerald-400 transition-all text-left group focus:outline-none focus:ring-4 focus:ring-emerald-300"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-gray-900 mb-1 font-semibold">Suggest alternatives</div>
                    <div className="text-sm text-gray-600">
                      Show me different scheduling options
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity" aria-hidden="true" />
                </div>
              </button>
            </div>
          ) : (
            /* Side-by-side Comparison */
            <div className="mb-6">
              <div className="text-gray-900 mb-4 font-semibold">Review proposed changes</div>
              <div className="grid grid-cols-2 gap-4">
                {/* Current Schedule */}
                <div>
                  <div className="text-sm text-gray-600 mb-3 font-semibold">Current schedule</div>
                  <div className="space-y-2">
                    {getCurrentSchedule().map((t) => {
                      const colors = categoryColors[t.category];
                      return (
                        <motion.div
                          key={t.id}
                          className={`${colors.bg} ${colors.border} border-2 rounded-lg p-3 shadow-sm`}
                        >
                          <div className="text-gray-900 text-sm mb-1 font-semibold">{t.title}</div>
                          <div className="text-xs text-gray-600">
                            {t.scheduledStart && new Date(t.scheduledStart).toLocaleTimeString('en-US', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>

                {/* Proposed Schedule */}
                <div>
                  <div className="text-sm text-emerald-700 mb-3 flex items-center gap-2 font-semibold">
                    <Check className="w-4 h-4" aria-hidden="true" />
                    Proposed schedule
                  </div>
                  <div className="space-y-2">
                    {getProposedSchedule().map((t, index) => {
                      const colors = categoryColors[t.category];
                      const isChanged = index === 0;
                      return (
                        <motion.div
                          key={t.id}
                          initial={{ x: 20, opacity: 0 }}
                          animate={{ x: 0, opacity: 1 }}
                          transition={{ delay: index * 0.1 }}
                          className={`${colors.bg} ${colors.border} border-2 rounded-lg p-3 relative shadow-sm ${
                            isChanged ? 'ring-2 ring-emerald-500' : ''
                          }`}
                        >
                          {isChanged && (
                            <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-emerald-500 flex items-center justify-center shadow-md" aria-label="Changed">
                              <Check className="w-4 h-4 text-white" aria-hidden="true" />
                            </div>
                          )}
                          <div className="text-gray-900 text-sm mb-1 font-semibold">{t.title}</div>
                          <div className="text-xs text-gray-600">
                            {t.scheduledStart && new Date(t.scheduledStart).toLocaleTimeString('en-US', {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* AI Insight */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-4 bg-emerald-50 rounded-lg p-4 border-2 border-emerald-300"
                role="status"
                aria-live="polite"
              >
                <div className="text-sm text-emerald-800">
                  ✨ AI insight: I've moved "{task.title}" to a less congested time slot while maintaining your focus time preferences.
                </div>
              </motion.div>
            </div>
          )}

          {/* Actions */}
          <nav className="flex gap-3" aria-label="Reschedule actions">
            <button
              onClick={onClose}
              className="px-6 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
            >
              Cancel
            </button>
            {showComparison && (
              <>
                <button
                  onClick={() => setShowComparison(false)}
                  className="px-6 py-3 rounded-xl bg-white border-2 border-gray-400 text-gray-800 hover:border-gray-500 hover:bg-gray-50 transition-all focus:outline-none focus:ring-4 focus:ring-gray-300"
                >
                  Back
                </button>
                <button
                  onClick={handleConfirm}
                  className="flex-1 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md hover:from-emerald-700 hover:to-teal-700 hover:shadow-lg hover:scale-105 transition-all flex items-center justify-center gap-2 focus:outline-none focus:ring-4 focus:ring-emerald-300"
                >
                  <Check className="w-5 h-5" aria-hidden="true" />
                  Accept changes
                </button>
              </>
            )}
          </nav>
        </div>
      </motion.div>
    </motion.div>
  );
}
