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
  const [conversationState, setConversationState] = useState(null); // Store full conversation state
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

    // Add user message to UI
    addMessage('user', prompt);

    // Set loading state
    setIsLoading(true);

    try {
      // Prepare state to send - merge new user message into existing state
      let stateToSend = null;
      
      if (conversationState) {
        // Append new user message to existing state messages
        stateToSend = {
          ...conversationState,
          messages: [
            ...conversationState.messages,
            {
              type: "HumanMessage",
              content: prompt
            }
          ]
        };
      } else {
        // First message - create initial state with just the user message
        stateToSend = {
          messages: [
            {
              type: "HumanMessage",
              content: prompt
            }
          ],
          needs_approval_from_human: false
        };
      }

      // Call API service - always send the complete state with all messages
      const response = await sendUserPrompt(prompt, stateToSend);
      
      // Add assistant response to UI
      addMessage('assistant', response.response);
      
      // Update conversation state with the complete state returned from backend
      // Backend always returns state with all messages
      if (response.state) {
        setConversationState(response.state);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = error.message || 'Sorry, I encountered an error. Please try again.';
      addMessage('assistant', `Error: ${errorMessage}`);
      // Don't clear state on error - keep conversation history
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setMessages([]);
    setConversationState(null); // Clear conversation state when clearing messages
  };

  const value = {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    messagesEndRef,
    conversationState, // Expose conversation state for UI indication if needed
    needsApproval: conversationState?.needs_approval_from_human || false,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
