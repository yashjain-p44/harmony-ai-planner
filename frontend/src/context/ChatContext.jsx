import { createContext, useContext, useState, useRef, useEffect } from 'react';
import { sendUserPrompt } from '../services/api';

const ChatContext = createContext(null);

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
};

export const ChatProvider = ({ children }) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (role, content) => {
    const newMessage = {
      id: Date.now() + Math.random(),
      role, // 'user' or 'assistant'
      content,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newMessage]);
    return newMessage;
  };

  const sendMessage = async (prompt) => {
    if (!prompt.trim() || isLoading) return;

    // Add user message
    addMessage('user', prompt);

    // Set loading state
    setIsLoading(true);

    try {
      // Call API service
      const response = await sendUserPrompt(prompt);
      
      // Add assistant response
      addMessage('assistant', response);
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages([]);
  };

  const value = {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    messagesEndRef,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
