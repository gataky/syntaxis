import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api/v1'; // Assuming backend runs on port 8000

export default {
  async generateSentence(template) {
    try {
      const response = await axios.post(`${API_BASE_URL}/generate`, { template });
      return response.data;
    } catch (error) {
      console.error('Error generating sentence:', error);
      let errorMessage = 'An unexpected error occurred.';
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        if (error.response.status === 400) {
          errorMessage = error.response.data.detail || 'Invalid template provided. Please check the syntax.';
        } else {
          errorMessage = `Server error: ${error.response.status} - ${error.response.data.detail || error.message}`;
        }
      } else if (error.request) {
        // The request was made but no response was received
        errorMessage = 'Could not connect to the service. Please check your network connection or try again later.';
      } else {
        // Something happened in setting up the request that triggered an Error
        errorMessage = error.message;
      }
      throw new Error(errorMessage); // Throw a new Error with a user-friendly message
    }
  },

  async getLexicalSchema() {
    const response = await axios.get(`${API_BASE_URL}/lexicals/schema`);
    return response.data;
  },

  async getFeatures() {
    const response = await axios.get(`${API_BASE_URL}/features`);
    return response.data;
  }
};
