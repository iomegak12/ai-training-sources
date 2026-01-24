// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// API Service for communicating with the backend
const apiService = {
  // Query the agent with a question
  async query(question) {
    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: question
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.answer;
    } catch (error) {
      if (error.message.includes('Failed to fetch')) {
        throw new Error('Unable to connect to the server. Please make sure the backend is running on port 8000.');
      }
      throw error;
    }
  },

  // Check backend health
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) {
        throw new Error('Health check failed');
      }
      const data = await response.json();
      return data.status === 'healthy';
    } catch (error) {
      return false;
    }
  }
};

export default apiService;
