import { useChat } from '../../context/ChatContext';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

const ChatWindow = () => {
  const { messages, messagesEndRef } = useChat();

  const emptyState = (
    <div className="flex-1 flex items-center justify-center px-4">
      <div className="max-w-2xl text-center">
        <div className="mb-6">
          <svg
            className="w-16 h-16 mx-auto text-accent-purple opacity-50"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        </div>
        <h2 className="text-2xl font-semibold text-primary mb-3">
          Welcome to Task AI Scheduler
        </h2>
        <p className="text-secondary text-lg mb-6">
          I'm your smart scheduling assistant. I can help you plan your time, find available slots, and optimize your schedule.
        </p>
        <div className="text-left space-y-2 text-secondary">
          <p className="font-medium text-primary">Try asking:</p>
          <ul className="list-disc list-inside space-y-1 ml-4">
            <li>"Help me create a scheduling plan"</li>
            <li>"What are my plan requirements?"</li>
            <li>"Find available time slots"</li>
          </ul>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="animate-in fade-in">{emptyState}</div>
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      {/* Input Area */}
      <ChatInput />
    </div>
  );
};

export default ChatWindow;
