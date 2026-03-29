import axios from 'axios';

// Use internal URL for SSR, relative path for client
const getBaseURL = () => {
  if (typeof window === 'undefined') {
    // Server-side: use internal docker network URL with /api prefix
    return process.env.INTERNAL_API_URL || 'http://api:8000/api';
  }
  // Client-side: use relative path through nginx proxy
  return process.env.NEXT_PUBLIC_API_URL || '/api';
};

const API_BASE_URL = getBaseURL();

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
      }
    }
    return Promise.reject(error);
  }
);
