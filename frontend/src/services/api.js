/**
 * API Service Layer
 * 
 * Connects to the backend Flask API for AI agent interactions.
 * Uses VITE_API_URL environment variable for base URL.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5002';

/**
 * Send a user prompt to the assistant
 * @param {string} prompt - User's message
 * @returns {Promise<string>} Assistant's response
 */
export const sendUserPrompt = async (prompt) => {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Request failed');
    }

    // Return the agent's response
    return data.response || 'No response from agent';
  } catch (error) {
    console.error('Error sending prompt to backend:', error);
    throw error;
  }
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
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error('Health check failed');
    }
    return await response.json();
  } catch (error) {
    console.warn('Backend health check failed:', error);
    return { status: 'unavailable', message: 'Backend not reachable' };
  }
};
