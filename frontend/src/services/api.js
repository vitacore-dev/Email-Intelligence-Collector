// API service for Email Intelligence Collector
const API_BASE_URL = 'http://localhost:8001/api';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Helper method for making requests
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };
    
    const requestOptions = { ...defaultOptions, ...options };
    
    try {
      const response = await fetch(url, requestOptions);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Existing search endpoints
  async searchSingle(email, forceRefresh = false) {
    return this.makeRequest('/search', {
      method: 'POST',
      body: JSON.stringify({
        email: email,
        force_refresh: forceRefresh
      })
    });
  }

  async searchBulk(formData) {
    return this.makeRequest('/bulk_search', {
      method: 'POST',
      headers: {}, // Remove Content-Type for FormData
      body: formData
    });
  }

  async getStats() {
    return this.makeRequest('/stats');
  }

  // New Digital Twin endpoints
  async createDigitalTwin(email) {
    return this.makeRequest('/digital-twin', {
      method: 'POST',
      body: JSON.stringify({ email })
    });
  }

  async getDigitalTwin(email) {
    return this.makeRequest(`/digital-twin/${encodeURIComponent(email)}`);
  }

  async getVisualization(email) {
    return this.makeRequest(`/visualization/${encodeURIComponent(email)}`);
  }

  async getAcademicProfile(email) {
    return this.makeRequest(`/academic-profile/${encodeURIComponent(email)}`);
  }

  // Academic Search endpoint
  async performAcademicSearch(email, name = null, affiliation = null) {
    return this.makeRequest('/academic-search', {
      method: 'POST',
      body: JSON.stringify({
        email,
        name,
        affiliation
      })
    });
  }

  // Network Analysis endpoints
  async getNetworkAnalysis(email) {
    return this.makeRequest(`/network-analysis/${encodeURIComponent(email)}`);
  }

  async getCollaborationGraph(email) {
    return this.makeRequest(`/collaboration-graph/${encodeURIComponent(email)}`);
  }

  // Research Metrics endpoints
  async getResearchMetrics(email) {
    return this.makeRequest(`/research-metrics/${encodeURIComponent(email)}`);
  }

  async getCitationAnalysis(email) {
    return this.makeRequest(`/citation-analysis/${encodeURIComponent(email)}`);
  }

  // Timeline endpoints
  async getResearchTimeline(email) {
    return this.makeRequest(`/research-timeline/${encodeURIComponent(email)}`);
  }

  async getActivityTimeline(email) {
    return this.makeRequest(`/activity-timeline/${encodeURIComponent(email)}`);
  }

  // Trending and Predictions
  async getTrendingTopics(email) {
    return this.makeRequest(`/trending-topics/${encodeURIComponent(email)}`);
  }

  async getResearchPredictions(email) {
    return this.makeRequest(`/research-predictions/${encodeURIComponent(email)}`);
  }

  // Export functionality
  async exportProfile(email, format = 'json') {
    const response = await fetch(
      `${this.baseURL}/export-profile/${encodeURIComponent(email)}?format=${format}`,
      {
        method: 'GET',
        headers: {
          'Accept': format === 'pdf' ? 'application/pdf' : 'application/json'
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Export failed! status: ${response.status}`);
    }

    if (format === 'pdf') {
      return response.blob();
    } else {
      return response.json();
    }
  }

  // Batch operations
  async batchAnalysis(emails) {
    return this.makeRequest('/batch-analysis', {
      method: 'POST',
      body: JSON.stringify({ emails })
    });
  }

  // Real-time data endpoints
  async getRealtimeMetrics(email) {
    return this.makeRequest(`/realtime-metrics/${encodeURIComponent(email)}`);
  }

  // Search suggestions
  async getSearchSuggestions(query) {
    return this.makeRequest(`/search-suggestions?q=${encodeURIComponent(query)}`);
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;

// Export individual methods for convenience
export const {
  searchSingle,
  searchBulk,
  getStats,
  createDigitalTwin,
  getDigitalTwin,
  getVisualization,
  getAcademicProfile,
  performAcademicSearch,
  getNetworkAnalysis,
  getCollaborationGraph,
  getResearchMetrics,
  getCitationAnalysis,
  getResearchTimeline,
  getActivityTimeline,
  getTrendingTopics,
  getResearchPredictions,
  exportProfile,
  batchAnalysis,
  getRealtimeMetrics,
  getSearchSuggestions
} = apiService;
