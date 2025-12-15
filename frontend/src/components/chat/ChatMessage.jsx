import ReactMarkdown from 'react-markdown';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div
      className={`flex w-full mb-6 animate-in fade-in slide-in-from-bottom-2 duration-300 ${
        isUser ? 'justify-end' : 'justify-start'
      }`}
    >
      <div
        className={`max-w-3xl px-4 py-3 rounded-2xl ${
          isUser
            ? 'bg-accent-purple text-white rounded-br-sm'
            : 'bg-charcoal-light text-primary rounded-bl-sm border border-subtle'
        }`}
      >
        <div className="break-words leading-relaxed">
          <ReactMarkdown
            components={{
              h1: ({ node, ...props }) => (
                <h1 className="text-2xl font-bold mb-2 mt-4 first:mt-0" {...props} />
              ),
              h2: ({ node, ...props }) => (
                <h2 className="text-xl font-bold mb-2 mt-4 first:mt-0" {...props} />
              ),
              h3: ({ node, ...props }) => (
                <h3 className="text-lg font-semibold mb-2 mt-3 first:mt-0" {...props} />
              ),
              p: ({ node, ...props }) => (
                <p className="mb-2 last:mb-0 whitespace-pre-wrap" {...props} />
              ),
              ul: ({ node, ...props }) => (
                <ul className="list-disc list-inside mb-2 space-y-1 ml-4" {...props} />
              ),
              ol: ({ node, ...props }) => (
                <ol className="list-decimal list-inside mb-2 space-y-1 ml-4" {...props} />
              ),
              li: ({ node, ...props }) => (
                <li className="mb-1" {...props} />
              ),
              strong: ({ node, ...props }) => (
                <strong className="font-semibold" {...props} />
              ),
              em: ({ node, ...props }) => (
                <em className="italic" {...props} />
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
        <div
          className={`text-xs mt-2 opacity-70 ${
            isUser ? 'text-white' : 'text-secondary'
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
