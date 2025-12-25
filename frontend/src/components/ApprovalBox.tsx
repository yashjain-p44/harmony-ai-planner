import React, { useState } from 'react';
import { motion } from 'motion/react';
import { CheckCircle2, XCircle, Edit3, Send } from 'lucide-react';
import type { ApprovalSummary } from '../services/api';

interface ApprovalBoxProps {
  summary: ApprovalSummary;
  onApprove: () => void;
  onReject: () => void;
  onSuggestChanges: (feedback: string) => void;
  isLoading?: boolean;
}

export function ApprovalBox({
  summary,
  onApprove,
  onReject,
  onSuggestChanges,
  isLoading = false,
}: ApprovalBoxProps) {
  const [showFeedbackInput, setShowFeedbackInput] = useState(false);
  const [feedback, setFeedback] = useState('');

  const handleSuggestChanges = () => {
    if (showFeedbackInput) {
      // Submit feedback
      if (feedback.trim()) {
        onSuggestChanges(feedback.trim());
        setFeedback('');
        setShowFeedbackInput(false);
      }
    } else {
      // Show input
      setShowFeedbackInput(true);
    }
  };

  const slots = summary.slots_summary || [];
  const habitName = summary.habit_name || summary.task_name || 'Scheduled Item';
  const frequency = summary.frequency || 'one-time';
  const duration = summary.duration_minutes || 30;
  const priority = summary.priority;

  // Format date to be more readable
  const formatDate = (dateStr: string): string => {
    try {
      const date = new Date(dateStr + 'T00:00:00'); // Add time to avoid timezone issues
      return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return dateStr;
    }
  };

  // Format time to 12-hour format with AM/PM
  const formatTime = (timeStr: string): string => {
    try {
      const [hours, minutes] = timeStr.split(':');
      const hour = parseInt(hours, 10);
      const ampm = hour >= 12 ? 'PM' : 'AM';
      const hour12 = hour % 12 || 12;
      return `${hour12}:${minutes} ${ampm}`;
    } catch {
      return timeStr;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-5 border-2 border-blue-200 shadow-lg overflow-hidden"
    >
      <div className="mb-4">
        <h4 className="text-lg font-semibold text-gray-800 mb-2">
          📅 Schedule Approval Request
        </h4>
        <p className="text-sm text-gray-600 mb-3">
          Ready to schedule <strong>{habitName}</strong> {priority && `(Priority: ${priority})`} ({duration} min)
        </p>
        
        {slots.length > 0 && (
          <div className="bg-white/80 rounded-xl p-4 mb-4">
            <p className="text-sm font-medium text-gray-700 mb-3">
              Selected Time Slots ({slots.length}):
            </p>
            <div className="space-y-3">
              {slots.map((slot) => (
                <div
                  key={slot.slot_number}
                  className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm"
                >
                  <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                        Date:
                      </span>
                      <span className="text-sm font-semibold text-blue-600">
                        {formatDate(slot.date)}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                        Time:
                      </span>
                      <span className="text-sm font-semibold text-gray-800">
                        {formatTime(slot.time)}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                        Duration:
                      </span>
                      <span className="text-sm font-semibold text-emerald-600">
                        {slot.duration_minutes} minutes
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {showFeedbackInput && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4"
          >
            <label className="block text-sm font-medium text-gray-700 mb-2">
              What changes would you like?
            </label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="E.g., Change times to morning, reduce frequency, different days..."
              className="w-full px-4 py-3 rounded-xl bg-white border border-gray-300 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-blue-400 transition-all resize-none"
              rows={3}
            />
          </motion.div>
        )}
      </div>

      <div className="flex gap-2 flex-wrap">
        <button
          onClick={onApprove}
          disabled={isLoading}
          className="flex-1 min-w-0 flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-white text-sm font-medium shadow-md hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          style={{ 
            backgroundColor: '#22c55e',
            color: '#ffffff',
            flexBasis: 'calc(33.333% - 0.5rem)'
          }}
        >
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" style={{ color: '#ffffff' }} />
          <span className="truncate" style={{ color: '#ffffff', fontWeight: 600 }}>Approve</span>
        </button>

        <button
          onClick={onReject}
          disabled={isLoading}
          className="flex-1 min-w-0 flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl bg-gradient-to-r from-red-400 to-pink-400 text-white text-sm font-medium shadow-md hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          style={{ 
            flexBasis: 'calc(33.333% - 0.5rem)'
          }}
        >
          <XCircle className="w-4 h-4 flex-shrink-0" />
          <span className="truncate">Reject</span>
        </button>

        <button
          onClick={handleSuggestChanges}
          disabled={isLoading || (showFeedbackInput && !feedback.trim())}
          className="flex-1 min-w-0 flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl text-white text-sm font-medium shadow-md hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          style={{ 
            backgroundColor: '#f59e0b',
            color: '#ffffff',
            flexBasis: 'calc(33.333% - 0.5rem)'
          }}
        >
          {showFeedbackInput ? (
            <>
              <Send className="w-4 h-4 flex-shrink-0" style={{ color: '#ffffff' }} />
              <span className="truncate" style={{ color: '#ffffff', fontWeight: 600 }}>Submit</span>
            </>
          ) : (
            <>
              <Edit3 className="w-4 h-4 flex-shrink-0" style={{ color: '#ffffff' }} />
              <span className="truncate" style={{ color: '#ffffff', fontWeight: 600 }}>Suggest</span>
            </>
          )}
        </button>
      </div>
    </motion.div>
  );
}

