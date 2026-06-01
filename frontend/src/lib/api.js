import axios from 'axios';
import { getToken, removeToken } from './auth';

// If NEXT_PUBLIC_API_URL is not set (or is wrong), fall back to relative URLs.
// This allows calling the backend via Next.js reverse proxy/rewrite if configured,
// and avoids hardcoding localhost from a different runtime.
const API_URL =
  (process.env.NEXT_PUBLIC_API_URL && process.env.NEXT_PUBLIC_API_URL.trim().length > 0)
    ? process.env.NEXT_PUBLIC_API_URL
    : 'http://localhost:8000';




// If NEXT_PUBLIC_API_URL is injected as undefined/missing, axios will try localhost.
// In Docker/compose this must point to the backend service name (http://backend:8000).
// console.log('API_URL:', API_URL);

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  signup: (data) => api.post('/api/auth/signup', data),
  login: (data) => api.post('/api/auth/login', data),
  getProfile: () => api.get('/api/auth/me'),
};

// Portfolio APIs
export const portfolioAPI = {
  getPortfolio: () => api.get('/api/portfolio/'),
  addHolding: (data) => api.post('/api/portfolio/holdings', data),
  deleteHolding: (id) => api.delete(`/api/portfolio/holdings/${id}`),
  getMetrics: () => api.get('/api/portfolio/metrics'),
  addToWatchlist: (data) => api.post('/api/portfolio/watchlist', data),
  getWatchlist: () => api.get('/api/portfolio/watchlist'),
  removeFromWatchlist: (id) => api.delete(`/api/portfolio/watchlist/${id}`),
};

// Stock APIs
export const stockAPI = {
  getQuote: (symbol) => api.get(`/api/stocks/quote/${symbol}`),
  getHistory: (symbol, period = '1mo') => api.get(`/api/stocks/history/${symbol}?period=${period}`),
  search: (query) => api.get(`/api/stocks/search?query=${query}`),
  getTrending: () => api.get('/api/stocks/trending'),
  getMovers: () => api.get('/api/stocks/movers'),
  getNews: (symbol) => api.get(`/api/stocks/news/${symbol}`),
  getGeneralNews: () => api.get('/api/stocks/news'),
};

// Chat APIs
export const chatAPI = {
  sendMessage: (data) => api.post('/api/chat/', data),
  getHistory: () => api.get('/api/chat/history'),
  clearHistory: () => api.delete('/api/chat/history'),
};

// Report APIs
export const reportAPI = {
  analyzePortfolio: () => api.post('/api/reports/analyze-portfolio'),
  analyzeStock: (symbol) => api.post(`/api/reports/analyze-stock/${symbol}`),
  getReports: () => api.get('/api/reports/'),
  getReport: (id) => api.get(`/api/reports/${id}`),
  generatePDF: (id) => api.post(`/api/reports/${id}/generate-pdf`),
  downloadReport: (id) => `${API_URL}/api/reports/${id}/download`,
};

export default api;