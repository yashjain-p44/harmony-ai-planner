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
  const habitName = summary.habit_name || 'Scheduled Habit';
  const frequency = summary.frequency || 'unknown';
  const duration = summary.duration_minutes || 30;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-5 border-2 border-blue-200 shadow-lg"
    >
      <div className="mb-4">
        <h4 className="text-lg font-semibold text-gray-800 mb-2">
          📅 Schedule Approval Request
        </h4>
        <p className="text-sm text-gray-600 mb-3">
          Ready to schedule <strong>{habitName}</strong> ({frequency}, {duration} min)
        </p>
        
        {slots.length > 0 && (
          <div className="bg-white/80 rounded-xl p-4 mb-4">
            <p className="text-sm font-medium text-gray-700 mb-2">
              Selected Time Slots ({slots.length}):
            </p>
            <div className="space-y-2">
              {slots.map((slot) => (
                <div
                  key={slot.slot_number}
                  className="flex items-center justify-between text-sm bg-white rounded-lg p-2 border border-gray-200"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-blue-600 font-medium">
                      {slot.date}
                    </span>
                    <span className="text-gray-600">at</span>
                    <span className="text-gray-800 font-medium">
                      {slot.time}
                    </span>
                  </div>
                  <span className="text-gray-500 text-xs">
                    {slot.duration_minutes} min
                  </span>
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

      <div className="flex gap-3">
        <button
          onClick={onApprove}
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-white font-medium shadow-md hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          style={{ 
            backgroundColor: '#22c55e',
            color: '#ffffff'
          }}
        >
          <CheckCircle2 className="w-5 h-5" style={{ color: '#ffffff' }} />
          <span style={{ color: '#ffffff', fontWeight: 600 }}>Approve</span>
        </button>

        <button
          onClick={onReject}
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-red-400 to-pink-400 text-white font-medium shadow-md hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          <XCircle className="w-5 h-5" />
          Reject
        </button>

        <button
          onClick={handleSuggestChanges}
          disabled={isLoading || (showFeedbackInput && !feedback.trim())}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-amber-400 to-orange-400 text-white font-medium shadow-md hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          {showFeedbackInput ? (
            <>
              <Send className="w-5 h-5" />
              Submit
            </>
          ) : (
            <>
              <Edit3 className="w-5 h-5" />
              Suggest Changes
            </>
          )}
        </button>
      </div>
    </motion.div>
  );
}

