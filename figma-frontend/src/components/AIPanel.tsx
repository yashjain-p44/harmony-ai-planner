import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Sparkles, Send, X, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import type { Task, Category } from '../App';
import { sendChatMessage, type AgentState, type ChatMessage as APIChatMessage } from '../services/api';

interface AIPanelProps {
  isOpen: boolean;
  onToggle: () => void;
  onAddTask: (task: Task) => void;
}

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  taskPreview?: Partial<Task>;
}

export function AIPanel({ isOpen, onToggle, onAddTask }: AIPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'ai',
      content: "Hi! I'm your AI scheduling assistant. You can ask me to schedule meetings, create tasks, check your calendar, and more!",
    },
  ]);
  const [input, setInput] = useState('');
  const [pendingTask, setPendingTask] = useState<Partial<Task> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [agentState, setAgentState] = useState<AgentState | null>(null);

  const parseTaskFromMessage = (message: string): Partial<Task> | null => {
    const categories: Record<string, Category> = {
      work: 'work',
      personal: 'personal',
      focus: 'focus',
    };

    let category: Category = 'work';
    for (const [key, value] of Object.entries(categories)) {
      if (message.toLowerCase().includes(key)) {
        category = value;
        break;
      }
    }

    const durationMatch = message.match(/(\d+)\s*(hour|hr|h)/i);
    const duration = durationMatch ? parseInt(durationMatch[1]) : 1;

    let deadline: Date | undefined;
    const today = new Date();
    if (message.toLowerCase().includes('tomorrow')) {
      deadline = new Date(today);
      deadline.setDate(deadline.getDate() + 1);
    } else if (message.toLowerCase().includes('friday')) {
      deadline = new Date(today);
      const daysUntilFriday = (5 - today.getDay() + 7) % 7 || 7;
      deadline.setDate(deadline.getDate() + daysUntilFriday);
    } else if (message.toLowerCase().includes('next week')) {
      deadline = new Date(today);
      deadline.setDate(deadline.getDate() + 7);
    }

    let title = message;
    Object.keys(categories).forEach((cat) => {
      title = title.replace(new RegExp(cat, 'gi'), '');
    });
    title = title.replace(/\d+\s*(hour|hr|h)/gi, '');
    title = title.replace(/\b(tomorrow|friday|next week|by)\b/gi, '');
    title = title.trim();
    if (!title) {
      title = 'New Task';
    }

    return {
      title,
      category,
      duration,
      deadline,
    };
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send message to backend AI agent
      const response = await sendChatMessage({
        prompt: input,
        state: agentState || undefined,
      });

      if (response.success) {
        // Update agent state for conversation continuity
        if (response.state) {
          setAgentState(response.state);
        }

        // Add AI response to messages
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'ai',
          content: response.response,
        };
        setMessages((prev) => [...prev, aiMessage]);

        // Try to parse task from the AI response if it mentions scheduling
        if (response.response.toLowerCase().includes('schedule') || 
            response.response.toLowerCase().includes('created') ||
            response.response.toLowerCase().includes('added')) {
          const parsedTask = parseTaskFromMessage(input);
          if (parsedTask) {
            setPendingTask(parsedTask);
            const taskPreviewMessage: Message = {
              id: (Date.now() + 2).toString(),
              role: 'ai',
              content: "Here's what I understood from your request:",
              taskPreview: parsedTask,
            };
            setMessages((prev) => [...prev, taskPreviewMessage]);
          }
        }
      } else {
        // Handle error
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'ai',
          content: `Sorry, I encountered an error: ${response.error || 'Unknown error'}. Please try again.`,
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'ai',
        content: 'Sorry, I had trouble connecting to the server. Please make sure the backend is running and try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirmTask = (task: Partial<Task>) => {
    const newTask: Task = {
      id: Date.now().toString(),
      title: task.title || 'New Task',
      category: task.category || 'work',
      duration: task.duration || 1,
      deadline: task.deadline,
      scheduledStart: task.scheduledStart || new Date(),
      scheduledEnd: task.scheduledEnd || new Date(Date.now() + (task.duration || 1) * 60 * 60 * 1000),
      notes: task.notes,
      constraints: task.constraints,
    };

    onAddTask(newTask);
    setPendingTask(null);

    setTimeout(() => {
      const successMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'ai',
        content: "✨ Task added to your schedule! I've placed it during optimal hours for maximum productivity.",
      };
      setMessages((prev) => [...prev, successMessage]);
    }, 300);
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0 }}
            onClick={onToggle}
            className="fixed right-8 top-1/2 -translate-y-1/2 w-16 h-16 rounded-full bg-gradient-to-br from-blue-300 via-purple-300 to-pink-300 flex items-center justify-center shadow-lg z-50"
            whileHover={{ scale: 1.1, boxShadow: '0 8px 30px rgba(147, 197, 253, 0.4)' }}
            whileTap={{ scale: 0.9 }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
            >
              <Sparkles className="w-8 h-8 text-white" />
            </motion.div>
          </motion.button>
        )}
      </AnimatePresence>

      {/* AI Panel */}
      <motion.div
        initial={false}
        animate={{
          x: isOpen ? 0 : 450,
        }}
        transition={{ type: 'spring', damping: 30, stiffness: 300 }}
        className="fixed right-0 top-0 h-full w-[450px] glass-strong border-l border-gray-200 z-40 flex flex-col shadow-xl"
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between bg-gradient-to-r from-blue-100/50 to-purple-100/50">
          <div className="flex items-center gap-3">
            <motion.div
              className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-300 to-purple-300 flex items-center justify-center shadow-md"
              animate={{
                boxShadow: [
                  '0 4px 20px rgba(147, 197, 253, 0.3)',
                  '0 4px 20px rgba(216, 180, 254, 0.4)',
                  '0 4px 20px rgba(147, 197, 253, 0.3)',
                ],
              }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              <Sparkles className="w-5 h-5 text-white" />
            </motion.div>
            <div>
              <h3 className="text-gray-800">AI assistant</h3>
              <p className="text-xs text-gray-500">Chat to create tasks</p>
            </div>
          </div>
          <button
            onClick={onToggle}
            className="p-2 rounded-lg bg-white/80 border border-gray-200 hover:border-gray-300 transition-all"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-white/30 to-white/10">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-blue-400 to-purple-400 text-white'
                    : 'bg-white/90 border border-gray-200 text-gray-800'
                }`}
              >
                <div className={`text-sm prose prose-sm max-w-none ${
                  message.role === 'user' ? 'prose-invert' : ''
                }`}>
                  <ReactMarkdown
                    components={{
                      h1: ({ node, ...props }) => <h1 className="text-lg font-bold mt-3 mb-2" {...props} />,
                      h2: ({ node, ...props }) => <h2 className="text-base font-bold mt-2 mb-1" {...props} />,
                      h3: ({ node, ...props }) => <h3 className="text-sm font-semibold mt-2 mb-1" {...props} />,
                      p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                      ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2 space-y-1" {...props} />,
                      ol: ({ node, ...props }) => <ol className="list-decimal ml-4 mb-2 space-y-1" {...props} />,
                      li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                      strong: ({ node, ...props }) => <strong className="font-semibold" {...props} />,
                      em: ({ node, ...props }) => <em className="italic" {...props} />,
                      code: ({ node, ...props }) => (
                        <code className="bg-gray-100 px-1 py-0.5 rounded text-xs" {...props} />
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>

                {/* Task Preview */}
                {message.taskPreview && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="mt-4 bg-white/95 rounded-xl p-4 border border-gray-200 shadow-sm"
                  >
                    <TaskPreviewCard
                      task={message.taskPreview}
                      onConfirm={() => handleConfirmTask(message.taskPreview!)}
                    />
                  </motion.div>
                )}
              </div>
            </motion.div>
          ))}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="bg-white/90 border border-gray-200 rounded-2xl p-4 shadow-sm">
                <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
              </div>
            </motion.div>
          )}
        </div>

        {/* Input */}
        <div className="p-6 border-t border-gray-200 bg-gradient-to-r from-blue-50/50 to-purple-50/50">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Type your task naturally..."
              className="flex-1 px-4 py-3 rounded-xl bg-white/90 border border-gray-200 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-blue-400 transition-all shadow-sm"
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !input.trim()}
              className="px-4 py-3 rounded-xl bg-gradient-to-r from-blue-400 to-purple-400 text-white shadow-md hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <div className="mt-3 text-xs text-gray-500">
            Try: "Schedule a meeting tomorrow at 2pm for 1 hour" or "What events do I have today?"
          </div>
        </div>
      </motion.div>
    </>
  );
}

function TaskPreviewCard({ task, onConfirm }: { task: Partial<Task>; onConfirm: () => void }) {
  const categoryColors: Record<Category, string> = {
    work: 'from-blue-300 to-blue-400',
    personal: 'from-purple-300 to-pink-300',
    focus: 'from-emerald-300 to-teal-300',
  };

  const gradient = categoryColors[task.category || 'work'];

  return (
    <div>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="text-gray-800 mb-2">{task.title}</div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`px-2 py-1 rounded-full bg-gradient-to-r ${gradient} text-xs text-white capitalize shadow-sm`}>
              {task.category}
            </span>
            <span className="text-xs text-gray-500">{task.duration}h</span>
            {task.deadline && (
              <span className="text-xs text-gray-500">
                Due: {new Date(task.deadline).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>

      <button
        onClick={onConfirm}
        className="w-full py-2 rounded-lg bg-gradient-to-r from-blue-400 to-purple-400 text-white text-sm shadow-md hover:shadow-lg hover:scale-105 transition-all"
      >
        Add to schedule
      </button>
    </div>
  );
}