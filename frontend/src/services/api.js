/**
 * API Service Layer
 * 
 * Mock implementation for now. Replace with actual API calls when backend is ready.
 * Uses VITE_API_URL environment variable for base URL.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Send a user prompt to the assistant
 * @param {string} prompt - User's message
 * @returns {Promise<string>} Assistant's response
 */
export const sendUserPrompt = async (prompt) => {
  // Mock implementation - simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1000 + Math.random() * 1000));

  // Mock responses based on keywords
  const lowerPrompt = prompt.toLowerCase();
  
  if (lowerPrompt.includes('plan') || lowerPrompt.includes('schedule') || lowerPrompt.includes('requirements')) {
    return `I'd be happy to help you create a scheduling plan! Let me gather some information about your preferences and requirements. 

I can help you set up:
- Your goals and focus areas
- Time commitments per week
- Preferred days for scheduling
- Fixed commitments to work around
- Energy preferences (morning vs evening)

Would you like to fill out the plan requirements?`;
  }

  if (lowerPrompt.includes('hello') || lowerPrompt.includes('hi') || lowerPrompt.includes('hey')) {
    return `Hello! I'm your smart scheduling assistant. I can help you plan your time, find available slots, and optimize your schedule. 

What would you like to work on today?`;
  }

  // Default response
  return `I understand you're asking about: "${prompt}"

As a scheduling assistant, I can help you:
- Create personalized scheduling plans
- Find available time slots
- Optimize your calendar
- Manage your time commitments

Would you like to start by setting up your plan requirements?`;
};

/**
 * Get plan requirements from the backend
 * @returns {Promise<Object>} Plan requirements object
 */
export const getPlanRequirements = async () => {
  // Mock implementation
  await new Promise((resolve) => setTimeout(resolve, 500));

  return {
    goal: 'Learn React and build projects',
    timeCommitment: '10',
    preferredDays: ['Monday', 'Wednesday', 'Friday'],
    fixedCommitments: 'Work 9-5, Monday to Friday',
    energyPreference: 'evening',
  };
};

/**
 * Submit plan requirements to the backend
 * @param {Object} requirements - Plan requirements object
 * @returns {Promise<Object>} Response from server
 */
export const submitPlanRequirements = async (requirements) => {
  // Mock implementation
  await new Promise((resolve) => setTimeout(resolve, 800));

  return {
    success: true,
    message: 'Plan requirements saved successfully',
    data: requirements,
  };
};

/**
 * Health check endpoint
 * @returns {Promise<Object>} Health status
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/calendar/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return await response.json();
  } catch (error) {
    console.warn('Backend health check failed:', error);
    return { status: 'unavailable', message: 'Backend not reachable' };
  }
};
