// lib/api/client.ts
import axios from 'axios';
import { config } from '@/lib/config';

// Create axios instance with gateway base URL
const apiClient = axios.create({
  baseURL: config.gateway.baseUrl, // http://localhost:8888
  timeout: config.gateway.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('healthflow_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // localStorage.removeItem('healthflow_token');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
