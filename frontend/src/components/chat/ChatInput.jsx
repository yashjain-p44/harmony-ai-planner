import { useState, useRef, useEffect } from 'react';
import { useChat } from '../../context/ChatContext';
import { usePlan } from '../../context/PlanContext';

const ChatInput = () => {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);
  const { sendMessage, isLoading } = useChat();
  const { openSidebar } = usePlan();

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const prompt = input.trim();
    setInput('');

    // Check if response should trigger sidebar
    const lowerPrompt = prompt.toLowerCase();
    if (
      lowerPrompt.includes('plan') ||
      lowerPrompt.includes('requirements') ||
      lowerPrompt.includes('preferences')
    ) {
      // Small delay to let message appear first
      setTimeout(() => {
        openSidebar();
      }, 500);
    }

    sendMessage(prompt);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-subtle bg-charcoal-light p-4">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="flex items-end gap-3">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
              disabled={isLoading}
              rows={1}
              className="w-full px-4 py-3 bg-charcoal border border-subtle rounded-lg text-primary placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-accent-purple focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:border-gray-700"
              style={{ minHeight: '48px', maxHeight: '200px' }}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-accent-purple text-white rounded-lg font-medium hover:bg-purple-600 active:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-accent-purple focus:ring-offset-2 focus:ring-offset-charcoal disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Sending...</span>
              </>
            ) : (
              <>
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                  />
                </svg>
                <span>Send</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInput;
