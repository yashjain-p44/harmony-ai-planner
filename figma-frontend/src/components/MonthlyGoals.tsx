import React from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, Target, TrendingUp, CheckCircle2, Circle } from 'lucide-react';
import type { Task, Category } from '../App';

interface MonthlyGoalsProps {
  tasks: Task[];
  onBack: () => void;
}

interface Goal {
  id: string;
  title: string;
  category: Category;
  targetDate: Date;
  progress: number;
  milestones: string[];
  completedMilestones: number;
}

export function MonthlyGoals({ tasks, onBack }: MonthlyGoalsProps) {
  const goals: Goal[] = [
    {
      id: '1',
      title: 'Complete Q4 strategic planning',
      category: 'work',
      targetDate: new Date(2025, 11, 31),
      progress: 65,
      milestones: ['Market research', 'Competitor analysis', 'Budget planning', 'Final presentation'],
      completedMilestones: 2,
    },
    {
      id: '2',
      title: 'Launch personal website',
      category: 'personal',
      targetDate: new Date(2025, 11, 20),
      progress: 40,
      milestones: ['Design mockups', 'Development', 'Content writing', 'Deploy'],
      completedMilestones: 1,
    },
    {
      id: '3',
      title: 'Deep learning certification',
      category: 'focus',
      targetDate: new Date(2026, 0, 15),
      progress: 30,
      milestones: ['Course modules 1-5', 'Modules 6-10', 'Final project', 'Exam'],
      completedMilestones: 1,
    },
  ];

  const categoryColors: Record<Category, { gradient: string; text: string; bg: string }> = {
    work: { gradient: 'from-blue-500 to-blue-600', text: 'text-blue-700', bg: 'bg-blue-100' },
    personal: { gradient: 'from-purple-500 to-pink-600', text: 'text-purple-700', bg: 'bg-purple-100' },
    focus: { gradient: 'from-emerald-500 to-teal-600', text: 'text-emerald-700', bg: 'bg-emerald-100' },
  };

  const getRelatedTasks = (goal: Goal) => {
    return tasks.filter(t => t.category === goal.category).slice(0, 3);
  };

  return (
    <div className="min-h-screen relative">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-200/20 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-200/20 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 p-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={onBack}
            className="mb-6 px-4 py-2 rounded-xl bg-white/80 border-2 border-gray-300 hover:border-gray-400 transition-all flex items-center gap-2 text-gray-800 focus:outline-none focus:ring-4 focus:ring-blue-300"
            aria-label="Back to calendar"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            Back to calendar
          </button>

          <div className="flex items-center gap-4 mb-2">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center shadow-md" aria-hidden="true">
              <Target className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl text-gray-900">Monthly goals</h1>
              <p className="text-gray-600">Track your progress and milestones</p>
            </div>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-3 gap-6 mb-8" role="list" aria-label="Goals statistics">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-strong rounded-2xl p-6 border-2 border-blue-300 shadow-md"
            role="listitem"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-sm" aria-hidden="true">
                <Target className="w-5 h-5 text-white" />
              </div>
              <div className="text-sm text-gray-600 font-semibold">Active goals</div>
            </div>
            <div className="text-3xl text-gray-900 font-bold">{goals.length}</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-strong rounded-2xl p-6 border-2 border-purple-300 shadow-md"
            role="listitem"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-sm" aria-hidden="true">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div className="text-sm text-gray-600 font-semibold">Avg. progress</div>
            </div>
            <div className="text-3xl text-gray-900 font-bold">
              {Math.round(goals.reduce((acc, g) => acc + g.progress, 0) / goals.length)}%
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-strong rounded-2xl p-6 border-2 border-emerald-300 shadow-md"
            role="listitem"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-emerald-600 flex items-center justify-center shadow-sm" aria-hidden="true">
                <CheckCircle2 className="w-5 h-5 text-white" />
              </div>
              <div className="text-sm text-gray-600 font-semibold">Milestones</div>
            </div>
            <div className="text-3xl text-gray-900 font-bold">
              {goals.reduce((acc, g) => acc + g.completedMilestones, 0)} /{' '}
              {goals.reduce((acc, g) => acc + g.milestones.length, 0)}
            </div>
          </motion.div>
        </div>

        {/* Goals List */}
        <div className="space-y-6" role="list" aria-label="Your goals">
          {goals.map((goal, index) => {
            const colors = categoryColors[goal.category];
            const relatedTasks = getRelatedTasks(goal);

            return (
              <motion.article
                key={goal.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-strong rounded-2xl p-6 border-2 border-gray-200 hover:border-gray-300 transition-all shadow-md"
                role="listitem"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-2xl text-gray-900">{goal.title}</h3>
                      <span className={`px-3 py-1 rounded-full bg-gradient-to-r ${colors.gradient} text-sm text-white capitalize shadow-sm`}>
                        {goal.category}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      Target: {goal.targetDate.toLocaleDateString('en-US', {
                        month: 'long',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-3xl ${colors.text} font-bold`}>{goal.progress}%</div>
                    <div className="text-sm text-gray-600">Complete</div>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-6" role="progressbar" aria-valuenow={goal.progress} aria-valuemin={0} aria-valuemax={100} aria-label={`${goal.title} progress`}>
                  <div className="h-3 rounded-full bg-gray-200 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${goal.progress}%` }}
                      transition={{ duration: 1, delay: index * 0.1 + 0.3 }}
                      className={`h-full bg-gradient-to-r ${colors.gradient} rounded-full relative overflow-hidden`}
                    >
                      <motion.div
                        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                        animate={{ x: ['-100%', '200%'] }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                        aria-hidden="true"
                      />
                    </motion.div>
                  </div>
                </div>

                {/* Milestones */}
                <div className="mb-6">
                  <div className="text-sm text-gray-700 mb-3 font-semibold">Milestones</div>
                  <div className="grid grid-cols-2 gap-3" role="list" aria-label={`Milestones for ${goal.title}`}>
                    {goal.milestones.map((milestone, i) => {
                      const isCompleted = i < goal.completedMilestones;
                      return (
                        <div
                          key={i}
                          className={`flex items-center gap-3 p-3 rounded-lg transition-all ${
                            isCompleted
                              ? `${colors.bg} border-2 border-${goal.category}-400`
                              : 'bg-white/80 border-2 border-gray-200'
                          }`}
                          role="listitem"
                          aria-label={`${milestone} - ${isCompleted ? 'completed' : 'pending'}`}
                        >
                          {isCompleted ? (
                            <CheckCircle2 className={`w-5 h-5 ${colors.text} shrink-0`} aria-hidden="true" />
                          ) : (
                            <Circle className="w-5 h-5 text-gray-400 shrink-0" aria-hidden="true" />
                          )}
                          <span className={`text-sm ${isCompleted ? 'text-gray-900 font-semibold' : 'text-gray-600'}`}>
                            {milestone}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Related Tasks */}
                {relatedTasks.length > 0 && (
                  <div>
                    <div className="text-sm text-gray-700 mb-3 font-semibold">Upcoming tasks</div>
                    <div className="flex gap-2 flex-wrap" role="list" aria-label={`Upcoming tasks for ${goal.title}`}>
                      {relatedTasks.map((task) => (
                        <div
                          key={task.id}
                          className={`px-3 py-2 rounded-lg ${colors.bg} text-sm text-gray-900 shadow-sm`}
                          role="listitem"
                        >
                          {task.title}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.article>
            );
          })}
        </div>

        {/* Empty State */}
        {goals.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
            role="status"
            aria-live="polite"
          >
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-200/40 to-purple-200/40 flex items-center justify-center mx-auto mb-4" aria-hidden="true">
              <Target className="w-12 h-12 text-gray-500" />
            </div>
            <h3 className="text-2xl text-gray-900 mb-2">No goals yet</h3>
            <p className="text-gray-600">Start adding tasks to automatically track your goals</p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
