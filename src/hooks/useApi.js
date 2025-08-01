/**
 * Custom React hook for API integration with loading states and error handling
 */

import { useState, useEffect, useCallback } from 'react';
import apiService from '../services/api';

// Generic API hook
export const useApi = (apiFunction, dependencies = [], immediate = true) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiFunction(...args);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiFunction]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, dependencies);

  return { data, loading, error, execute, refetch: execute };
};

// Authentication hooks
export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const login = async (credentials) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.login(credentials);
      const userData = await apiService.getCurrentUser();
      setUser(userData);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.register(userData);
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
      setUser(null);
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  const checkAuth = useCallback(async () => {
    try {
      setLoading(true);
      const userData = await apiService.getCurrentUser();
      setUser(userData);
    } catch (err) {
      setUser(null);
      apiService.setToken(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      checkAuth();
    } else {
      setLoading(false);
    }
  }, [checkAuth]);

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    checkAuth,
    isAuthenticated: !!user,
  };
};

// Waste detection hooks
export const useWasteDetection = () => {
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState(null);

  const scanWaste = async (imageFile, location, coordinates) => {
    try {
      setScanning(true);
      setError(null);
      const result = await apiService.scanWaste(imageFile, location, coordinates);
      setScanResult(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setScanning(false);
    }
  };

  const submitFeedback = async (feedbackData) => {
    try {
      const result = await apiService.submitFeedback(feedbackData);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  return {
    scanning,
    scanResult,
    error,
    scanWaste,
    submitFeedback,
    clearResult: () => setScanResult(null),
  };
};

// Smart card hooks
export const useSmartCard = () => {
  const {
    data: card,
    loading,
    error,
    execute: fetchCard,
  } = useApi(apiService.getSmartCard, [], false);

  const createCard = async (cardData) => {
    try {
      const result = await apiService.createSmartCard(cardData);
      await fetchCard(); // Refresh card data
      return result;
    } catch (err) {
      throw err;
    }
  };

  const updateCard = async (cardData) => {
    try {
      const result = await apiService.updateSmartCard(cardData);
      await fetchCard(); // Refresh card data
      return result;
    } catch (err) {
      throw err;
    }
  };

  const renewCard = async () => {
    try {
      const result = await apiService.renewSmartCard();
      await fetchCard(); // Refresh card data
      return result;
    } catch (err) {
      throw err;
    }
  };

  return {
    card,
    loading,
    error,
    createCard,
    updateCard,
    renewCard,
    fetchCard,
  };
};

// Shop hooks
export const useShop = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProducts = async (filters = {}) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiService.getProducts(filters);
      setProducts(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const result = await apiService.getProductCategories();
      setCategories(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const createOrder = async (orderData) => {
    try {
      const result = await apiService.createOrder(orderData);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, []);

  return {
    products,
    categories,
    loading,
    error,
    fetchProducts,
    fetchCategories,
    createOrder,
  };
};

// Analytics hooks
export const useAnalytics = () => {
  const {
    data: overview,
    loading: overviewLoading,
    error: overviewError,
    execute: fetchOverview,
  } = useApi(apiService.getAnalyticsOverview, [], false);

  const {
    data: environmentalImpact,
    loading: impactLoading,
    execute: fetchImpact,
  } = useApi(apiService.getEnvironmentalImpact, [], false);

  const {
    data: leaderboard,
    loading: leaderboardLoading,
    execute: fetchLeaderboard,
  } = useApi(() => apiService.getLeaderboard('monthly'), [], false);

  const fetchTrends = async (days = 30) => {
    try {
      const result = await apiService.getWasteTrends(days);
      return result;
    } catch (err) {
      throw err;
    }
  };

  return {
    overview,
    environmentalImpact,
    leaderboard,
    loading: overviewLoading || impactLoading || leaderboardLoading,
    error: overviewError,
    fetchOverview,
    fetchImpact,
    fetchLeaderboard,
    fetchTrends,
  };
};

// DIY Projects hooks
export const useDIYProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProjects = async (filters = {}) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiService.getDIYProjects(filters);
      setProjects(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const createProject = async (projectData) => {
    try {
      const result = await apiService.createDIYProject(projectData);
      await fetchProjects(); // Refresh projects
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const likeProject = async (projectId) => {
    try {
      const result = await apiService.likeProject(projectId);
      // Update local state
      setProjects(prev => 
        prev.map(project => 
          project.id === projectId 
            ? { ...project, likes: project.likes + 1 }
            : project
        )
      );
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return {
    projects,
    loading,
    error,
    fetchProjects,
    createProject,
    likeProject,
  };
};

// Profile hooks
export const useProfile = () => {
  const {
    data: profile,
    loading,
    error,
    execute: fetchProfile,
  } = useApi(apiService.getProfile, [], false);

  const updateProfile = async (profileData) => {
    try {
      const result = await apiService.updateProfile(profileData);
      await fetchProfile(); // Refresh profile data
      return result;
    } catch (err) {
      throw err;
    }
  };

  const uploadAvatar = async (avatarFile) => {
    try {
      const result = await apiService.uploadAvatar(avatarFile);
      await fetchProfile(); // Refresh profile data
      return result;
    } catch (err) {
      throw err;
    }
  };

  const changePassword = async (passwordData) => {
    try {
      const result = await apiService.changePassword(passwordData);
      return result;
    } catch (err) {
      throw err;
    }
  };

  return {
    profile,
    loading,
    error,
    updateProfile,
    uploadAvatar,
    changePassword,
    fetchProfile,
  };
};
