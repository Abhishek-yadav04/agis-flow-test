import axios, { AxiosError } from 'axios';

// Auto-detect API base: prefer same origin, fallback to localhost dev port
const detectedOrigin = typeof window !== 'undefined' ? window.location.origin : 'http://127.0.0.1:8001';
export const API_BASE_URL = `${detectedOrigin.replace(/\/$/, '')}/api`;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
// Basic exponential backoff retry for transient network errors (up to 3 attempts)
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config: any = error.config || {};
    const status = error.response?.status;
    const isNetwork = !error.response;
    if (status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }
    if ((isNetwork || status === 502 || status === 503 || status === 504) && !config.__retry) {
      config.__retry = 0;
    }
    if (config.__retry !== undefined && config.__retry < 3) {
      config.__retry += 1;
      const delay = 300 * Math.pow(2, config.__retry - 1) + Math.random() * 150;
      await new Promise(res => setTimeout(res, delay));
      return api(config);
    }
    return Promise.reject(error);
  }
);

export const dashboardAPI = {
  getDashboard: () => api.get('/dashboard'),
  getHealth: () => api.get('/health'),
  getSystemMetrics: () => api.get('/system/metrics'),
};

export const federatedLearningAPI = {
  getStrategies: () => api.get('/fl/strategies'),
  getExperiments: () => api.get('/experiments'),
  getStatus: () => api.get('/federated/status'),
  startTraining: () => api.post('/federated/train'),
};

export const securityAPI = {
  getThreats: () => api.get('/threats'),
  getSecurityMetrics: () => api.get('/security/metrics'),
  getSecurityThreats: () => api.get('/security/threats'),
};

export const networkAPI = {
  getStats: () => api.get('/network/stats'),
  getPackets: () => api.get('/network/packets'),
};

export const datasetsAPI = {
  getDatasets: () => api.get('/datasets'),
  uploadDataset: (formData: FormData) => api.post('/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteDataset: (id: string) => api.delete(`/datasets/${id}`),
};

export const researchAPI = {
  getAlgorithms: () => api.get('/research/enterprise/research-algorithms'),
};

export const settingsAPI = {
  getSettings: () => api.get('/settings'),
  updateSettings: (settings: any) => api.post('/settings', settings),
};

export const integrationsAPI = {
  getOverview: () => api.get('/integrations/overview'),
  refresh: () => api.post('/integrations/refresh'),
};

export default api;