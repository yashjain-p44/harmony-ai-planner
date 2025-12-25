import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Sparkles, Loader2, CheckCircle2, XCircle, Clock, Calendar, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import type { Task } from '../App';
import { scheduleTask, type ChatResponse, type AgentState, type ApprovalSummary } from '../services/api';
import { ApprovalBox } from './ApprovalBox';

interface TaskSchedulingModalProps {
  task: Task;
  taskListId: string;
  isOpen: boolean;
  onClose: () => void;
  onScheduleComplete: (taskId: string, scheduledStart: Date, scheduledEnd: Date) => void;
}

interface Message {
  id: string;
  role: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
  approvalSummary?: ApprovalSummary;
}

type SchedulingStage = 'idle' | 'analyzing' | 'fetching_calendar' | 'finding_slots' | 'selecting_slot' | 'approval_pending' | 'creating_event' | 'completed' | 'error';

export function TaskSchedulingModal({
  task,
  taskListId,
  isOpen,
  onClose,
  onScheduleComplete,
}: TaskSchedulingModalProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [stage, setStage] = useState<SchedulingStage>('idle');
  const [agentState, setAgentState] = useState<AgentState | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0 && task) {
      setMessages([{
        id: '1',
        role: 'ai',
        content: `I'll help you schedule "${task.title}". Let me analyze the task, check your calendar, and find the best time slot.`,
        timestamp: new Date(),
      }]);
    }
  }, [isOpen, task, messages.length]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setMessages([]);
      setIsLoading(false);
      setStage('idle');
      setAgentState(null);
      setError(null);
    }
  }, [isOpen]);

  const addMessage = (role: 'user' | 'ai' | 'system', content: string, approvalSummary?: ApprovalSummary) => {
    setMessages(prev => [...prev, {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      role,
      content,
      timestamp: new Date(),
      approvalSummary,
    }]);
  };

  const updateStage = (newStage: SchedulingStage, message?: string) => {
    setStage(newStage);
    // Don't add system messages here - they'll be added from backend messages
    // System messages are only for local status updates
  };

  const handleStartScheduling = async () => {
    if (!task) return;
    
    setIsLoading(true);
    setError(null);
    setStage('analyzing');

    try {
      const response: ChatResponse = await scheduleTask(taskListId, task.id);

      // Update agent state
      if (response.state) {
        setAgentState(response.state);
      }

      // Process messages from response - avoid duplicates
      // Get existing message contents to check for duplicates
      const existingContents = new Set(messages.map(m => m.content.trim()));
      
      // Debug logging
      console.log('[TaskSchedulingModal] Response:', {
        needs_approval_from_human: response.needs_approval_from_human,
        approval_state: response.approval_state,
        has_approval_summary: !!response.approval_summary,
        selected_slots: response.approval_summary?.selected_slots,
        created_events: response.created_events,
      });
      
      // Check if we need to attach approval summary
      // Also check if we have selected_slots even if approval_summary is missing
      const hasSelectedSlots = response.approval_summary?.selected_slots && response.approval_summary.selected_slots.length > 0;
      const needsApproval = (response.needs_approval_from_human || response.approval_state === 'PENDING') && 
                            (response.approval_summary || hasSelectedSlots);
      
      // Find the last AIMessage in the response to attach approval summary
      let lastAIMessageIndex = -1;
      if (response.messages && response.messages.length > 0) {
        for (let i = response.messages.length - 1; i >= 0; i--) {
          if (response.messages[i].type === 'AIMessage') {
            lastAIMessageIndex = i;
            break;
          }
        }
      }
      
      // Process messages array if available
      if (response.messages && response.messages.length > 0) {
        // Add new messages that aren't already in our messages list
        response.messages.forEach((msg, index) => {
          const content = msg.content?.trim() || '';
          if (content && !existingContents.has(content)) {
            const role = msg.type === 'HumanMessage' ? 'user' : 
                        msg.type === 'AIMessage' ? 'ai' : 'system';
            
            // If this is the last AI message and we need approval, attach approval summary
            const isLastAIMessage = needsApproval && index === lastAIMessageIndex;
            
            if (isLastAIMessage) {
              addMessage(role, content, response.approval_summary);
            } else {
              addMessage(role, content);
            }
            existingContents.add(content); // Track added content
          }
        });
      } else if (response.response) {
        // Skip response.response if we already have messages - it's usually a duplicate
        // Only use response.response as fallback if we have no messages array
        const responseContent = response.response.trim();
        if (responseContent && !existingContents.has(responseContent)) {
          // If we need approval, attach approval summary to this message
          if (needsApproval) {
            addMessage('ai', responseContent, response.approval_summary);
          } else {
            addMessage('ai', responseContent);
          }
        }
      }

      // Update stage if approval is needed
      if (needsApproval) {
        updateStage('approval_pending');
      } else if (response.created_events && response.created_events.length > 0) {
        // Event was created successfully
        updateStage('completed');
        const event = response.created_events[0];
        // Handle both dateTime and date formats - API returns start/end as strings
        const startStr = event.start || '';
        const endStr = event.end || '';
        const scheduledStart = new Date(startStr);
        const scheduledEnd = new Date(endStr);
        
        if (isNaN(scheduledStart.getTime()) || isNaN(scheduledEnd.getTime())) {
          throw new Error('Invalid date format in event response');
        }
        
        addMessage('ai', `✅ Successfully scheduled "${task.title}"!`);
        addMessage('system', `📅 Event created: ${scheduledStart.toLocaleString()} - ${scheduledEnd.toLocaleString()}`);
        
        // Notify parent after a short delay
        setTimeout(() => {
          onScheduleComplete(task.id, scheduledStart, scheduledEnd);
          onClose();
        }, 2000);
      } else {
        // Check if no slots were found
        if (response.response && response.response.includes("couldn't find")) {
          updateStage('error');
          addMessage('ai', response.response);
        } else {
          updateStage('completed');
          addMessage('ai', response.response || 'Scheduling completed.');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to schedule task');
      updateStage('error');
      addMessage('system', `❌ Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApproval = async (action: 'APPROVED' | 'REJECTED' | 'CHANGES_REQUESTED', feedback?: string) => {
    if (!agentState || !task) return;

    setIsLoading(true);
    setError(null);

    if (action === 'APPROVED') {
      setStage('creating_event');
    } else if (action === 'REJECTED') {
      addMessage('user', 'Rejected the proposed schedule.');
      setStage('idle');
      setIsLoading(false);
      return;
    } else if (action === 'CHANGES_REQUESTED') {
      addMessage('user', `Requested changes: ${feedback}`);
      setStage('finding_slots');
    }

    try {
      const response: ChatResponse = await scheduleTask(
        taskListId,
        task.id,
        action,
        feedback,
        agentState
      );

      // Update agent state
      if (response.state) {
        setAgentState(response.state);
      }

      // Process messages from response - avoid duplicates
      // Get existing message contents to check for duplicates
      const existingContents = new Set(messages.map(m => m.content.trim()));
      
      // Track the last AI message to attach approval summary if needed
      let lastAIMessageIndex = -1;
      
      if (response.messages && response.messages.length > 0) {
        // Add new messages that aren't already in our messages list
        response.messages.forEach((msg) => {
          const content = msg.content?.trim() || '';
          if (content && !existingContents.has(content)) {
            const role = msg.type === 'HumanMessage' ? 'user' : 
                        msg.type === 'AIMessage' ? 'ai' : 'system';
            addMessage(role, content);
            existingContents.add(content); // Track added content
            
            // Track the last AI message index for approval summary attachment
            if (role === 'ai') {
              lastAIMessageIndex = messages.length; // Will be the new length after addMessage
            }
          }
        });
      }
      
      // Don't add response.response if we already processed messages - it's usually a duplicate
      // Only use response.response if we have no messages array
      if ((!response.messages || response.messages.length === 0) && response.response) {
        const responseContent = response.response.trim();
        if (responseContent && !existingContents.has(responseContent)) {
          addMessage('ai', responseContent);
          lastAIMessageIndex = messages.length;
        }
      }
      
      // Check if approval is needed and attach approval summary
      if (response.needs_approval_from_human && response.approval_state === 'PENDING' && response.approval_summary) {
        updateStage('approval_pending');
        
        // Attach approval summary to the last AI message
        setMessages(prev => {
          const updated = [...prev];
          // Find the last AI message (most recent one)
          for (let i = updated.length - 1; i >= 0; i--) {
            if (updated[i].role === 'ai') {
              updated[i] = {
                ...updated[i],
                approvalSummary: response.approval_summary,
              };
              break;
            }
          }
          return updated;
        });
      }

      if (action === 'APPROVED') {
        if (response.created_events && response.created_events.length > 0) {
          updateStage('completed');
          const event = response.created_events[0];
          // Handle both dateTime and date formats - API returns start/end as strings
          const startStr = event.start || '';
          const endStr = event.end || '';
          const scheduledStart = new Date(startStr);
          const scheduledEnd = new Date(endStr);
          
          if (isNaN(scheduledStart.getTime()) || isNaN(scheduledEnd.getTime())) {
            throw new Error('Invalid date format in event response');
          }
          
          // Check if success message already exists
          const successMsg = `✅ Successfully scheduled "${task.title}"!`;
          const hasSuccessMsg = messages.some(m => m.content === successMsg);
          if (!hasSuccessMsg) {
            addMessage('ai', successMsg);
          }
          addMessage('system', `📅 Event created: ${scheduledStart.toLocaleString()} - ${scheduledEnd.toLocaleString()}`);
          
          // Notify parent after a short delay
          setTimeout(() => {
            onScheduleComplete(task.id, scheduledStart, scheduledEnd);
            onClose();
          }, 2000);
        } else {
          updateStage('completed');
          // Only add if not already present
          if (response.response) {
            const lastMessage = messages[messages.length - 1];
            if (!lastMessage || lastMessage.content !== response.response) {
              addMessage('ai', response.response);
            }
          }
        }
      } else if (action === 'CHANGES_REQUESTED') {
        if (response.needs_approval_from_human && response.approval_state === 'PENDING') {
          updateStage('approval_pending');
          if (response.approval_summary) {
            // Update the last message with approval summary
            setMessages(prev => {
              const updated = [...prev];
              if (updated.length > 0) {
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  approvalSummary: response.approval_summary,
                };
              }
              return updated;
            });
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process approval');
      updateStage('error');
      addMessage('system', `❌ Error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getStageIcon = () => {
    switch (stage) {
      case 'analyzing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'fetching_calendar':
        return <Calendar className="w-5 h-5 text-blue-500" />;
      case 'finding_slots':
        return <Clock className="w-5 h-5 text-blue-500" />;
      case 'selecting_slot':
        return <Sparkles className="w-5 h-5 text-blue-500" />;
      case 'approval_pending':
        return <AlertCircle className="w-5 h-5 text-amber-500" />;
      case 'creating_event':
        return <Loader2 className="w-5 h-5 text-green-500 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Sparkles className="w-5 h-5 text-blue-500" />;
    }
  };

  const getStageMessage = () => {
    switch (stage) {
      case 'analyzing':
        return 'Analyzing task...';
      case 'fetching_calendar':
        return 'Checking your calendar...';
      case 'finding_slots':
        return 'Finding available time slots...';
      case 'selecting_slot':
        return 'Selecting best time slot...';
      case 'approval_pending':
        return 'Waiting for your approval...';
      case 'creating_event':
        return 'Creating calendar event...';
      case 'completed':
        return 'Scheduling completed!';
      case 'error':
        return 'An error occurred';
      default:
        return 'Ready to schedule';
    }
  };

  // Early return with safety checks (after hooks)
  if (!isOpen) {
    return null;
  }

  if (!task || !task.id || !task.title) {
    console.error('TaskSchedulingModal: Invalid task object', task);
    return null;
  }

  if (!taskListId) {
    console.error('TaskSchedulingModal: Missing taskListId');
    return null;
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        onClick={(e) => {
          // Close on backdrop click
          if (e.target === e.currentTarget) {
            onClose();
          }
        }}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Sparkles className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Schedule Task</h2>
                <p className="text-sm text-gray-500">{task.title}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Close"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Status Bar */}
          {stage !== 'idle' && (
            <div className="px-6 py-3 bg-gray-50 border-b border-gray-200">
              <div className="flex items-center gap-3">
                {getStageIcon()}
                <span className="text-sm font-medium text-gray-700">{getStageMessage()}</span>
              </div>
            </div>
          )}

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl p-4 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : message.role === 'system'
                      ? 'bg-gray-100 text-gray-700 text-sm'
                      : 'bg-gray-50 text-gray-900'
                  }`}
                >
                  {message.role === 'system' ? (
                    <div className="flex items-center gap-2">
                      {message.content.includes('✅') && <CheckCircle2 className="w-4 h-4 text-green-500" />}
                      {message.content.includes('❌') && <XCircle className="w-4 h-4 text-red-500" />}
                      {message.content.includes('🔍') && <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />}
                      {message.content.includes('📅') && <Calendar className="w-4 h-4 text-blue-500" />}
                      <span>{message.content}</span>
                    </div>
                  ) : (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  )}

                  {/* Approval Box */}
                  {message.approvalSummary && (
                    <div className="mt-4">
                      <ApprovalBox
                        summary={message.approvalSummary}
                        onApprove={() => handleApproval('APPROVED')}
                        onReject={() => handleApproval('REJECTED')}
                        onSuggestChanges={(feedback) => handleApproval('CHANGES_REQUESTED', feedback)}
                        isLoading={isLoading}
                      />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}

            {isLoading && stage !== 'approval_pending' && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-gray-50 rounded-2xl p-4 flex items-center gap-3">
                  <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                  <span className="text-sm text-gray-600">{getStageMessage()}</span>
                </div>
              </motion.div>
            )}
          </div>

          {/* Footer */}
          <div className="p-6 border-t border-gray-200">
            {stage === 'idle' && (
              <button
                onClick={handleStartScheduling}
                className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-medium hover:from-blue-700 hover:to-purple-700 transition-all flex items-center justify-center gap-2"
              >
                <Sparkles className="w-5 h-5" />
                Start AI Scheduling
              </button>
            )}
            {stage === 'completed' && (
              <div className="text-center text-sm text-gray-600">
                Task has been scheduled successfully!
              </div>
            )}
            {stage === 'error' && (
              <button
                onClick={handleStartScheduling}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-all"
              >
                Try Again
              </button>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

