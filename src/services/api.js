/**
 * API Service for Smart Waste Sorter Backend Integration
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  // Helper method to get headers
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };

    if (includeAuth && this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Helper method for file upload headers
  getFileHeaders() {
    const headers = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  // Generic request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: this.getHeaders(options.auth !== false),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return await response.text();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  }

  // Authentication endpoints
  async register(userData) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
      auth: false,
    });
  }

  async login(credentials) {
    const formData = new FormData();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await this.request('/api/auth/login', {
      method: 'POST',
      headers: {},
      body: formData,
      auth: false,
    });

    if (response.access_token) {
      this.setToken(response.access_token);
    }

    return response;
  }

  async logout() {
    try {
      await this.request('/api/auth/logout', { method: 'POST' });
    } finally {
      this.setToken(null);
    }
  }

  async getCurrentUser() {
    return this.request('/api/auth/me');
  }

  async refreshToken(refreshToken) {
    return this.request('/api/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
      auth: false,
    });
  }

  // Waste detection endpoints
  async scanWaste(imageFile, location = null, coordinates = null) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    if (location) formData.append('location', location);
    if (coordinates?.latitude) formData.append('latitude', coordinates.latitude);
    if (coordinates?.longitude) formData.append('longitude', coordinates.longitude);

    return this.request('/api/detection/scan', {
      method: 'POST',
      headers: this.getFileHeaders(),
      body: formData,
    });
  }

  async getScanHistory(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/detection/history?${queryString}`);
  }

  async submitFeedback(feedbackData) {
    return this.request('/api/detection/feedback', {
      method: 'POST',
      body: JSON.stringify(feedbackData),
    });
  }

  async getWasteCategories() {
    return this.request('/api/detection/categories');
  }

  async getDetectionStats() {
    return this.request('/api/detection/stats');
  }

  // User profile endpoints
  async getProfile() {
    return this.request('/api/profile/');
  }

  async updateProfile(profileData) {
    return this.request('/api/profile/', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  async uploadAvatar(avatarFile) {
    const formData = new FormData();
    formData.append('avatar', avatarFile);

    return this.request('/api/profile/avatar', {
      method: 'POST',
      headers: this.getFileHeaders(),
      body: formData,
    });
  }

  async changePassword(passwordData) {
    return this.request('/api/profile/change-password', {
      method: 'POST',
      body: JSON.stringify(passwordData),
    });
  }

  async getEcoProgress() {
    return this.request('/api/profile/eco-progress');
  }

  // Smart card endpoints
  async createSmartCard(cardData) {
    return this.request('/api/smart-card/create', {
      method: 'POST',
      body: JSON.stringify(cardData),
    });
  }

  async getSmartCard() {
    return this.request('/api/smart-card/');
  }

  async updateSmartCard(cardData) {
    return this.request('/api/smart-card/', {
      method: 'PUT',
      body: JSON.stringify(cardData),
    });
  }

  async renewSmartCard() {
    return this.request('/api/smart-card/renew', {
      method: 'POST',
    });
  }

  async validateCardNumber(cardNumber) {
    return this.request(`/api/smart-card/validate/${cardNumber}`, {
      auth: false,
    });
  }

  // Shop endpoints
  async getProducts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/shop/products?${queryString}`);
  }

  async getProduct(productId) {
    return this.request(`/api/shop/products/${productId}`);
  }

  async getProductCategories() {
    return this.request('/api/shop/categories');
  }

  async createOrder(orderData) {
    return this.request('/api/shop/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  }

  async getOrders() {
    return this.request('/api/shop/orders');
  }

  async getRecommendations() {
    return this.request('/api/shop/recommendations');
  }

  // Analytics endpoints
  async getAnalyticsOverview() {
    return this.request('/api/analytics/overview');
  }

  async getEnvironmentalImpact() {
    return this.request('/api/analytics/environmental-impact');
  }

  async getLeaderboard(period = 'monthly') {
    return this.request(`/api/analytics/leaderboard?period=${period}`);
  }

  async getWasteTrends(days = 30) {
    return this.request(`/api/analytics/trends?days=${days}`);
  }

  // DIY Projects endpoints
  async getDIYProjects(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/diy/?${queryString}`);
  }

  async getDIYProject(projectId) {
    return this.request(`/api/diy/${projectId}`);
  }

  async createDIYProject(projectData) {
    return this.request('/api/diy/', {
      method: 'POST',
      body: JSON.stringify(projectData),
    });
  }

  async uploadProjectImages(projectId, imageFiles) {
    const formData = new FormData();
    imageFiles.forEach((file, index) => {
      formData.append('images', file);
    });

    return this.request(`/api/diy/${projectId}/images`, {
      method: 'POST',
      headers: this.getFileHeaders(),
      body: formData,
    });
  }

  async likeProject(projectId) {
    return this.request(`/api/diy/${projectId}/like`, {
      method: 'POST',
    });
  }

  async getMyProjects() {
    return this.request('/api/diy/my/projects');
  }

  async getCategoryStats() {
    return this.request('/api/diy/categories/stats');
  }

  // Health check
  async healthCheck() {
    return this.request('/api/health', { auth: false });
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;

// Export individual methods for convenience
export const {
  register,
  login,
  logout,
  getCurrentUser,
  scanWaste,
  getScanHistory,
  getProfile,
  updateProfile,
  getSmartCard,
  createSmartCard,
  updateSmartCard,
  getProducts,
  createOrder,
  getAnalyticsOverview,
  getDIYProjects,
  createDIYProject,
  healthCheck,
} = apiService;
