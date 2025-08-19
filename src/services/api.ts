import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and retries
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 errors (unauthorized)
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    // Retry logic for network errors and specific server errors
    if (
      !originalRequest._retry &&
      (error.code === 'NETWORK_ERROR' ||
        error.response?.status === 502 ||
        error.response?.status === 503 ||
        error.response?.status === 504)
    ) {
      originalRequest._retry = true;
      const delay = originalRequest._retryCount ? originalRequest._retryCount * 1000 : 1000;
      originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;

      if (originalRequest._retryCount <= 3) {
        await new Promise((resolve) => setTimeout(resolve, delay));
        return api(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);

// API endpoints
export const dashboardAPI = {
  getDashboard: () => api.get('/api/dashboard'),
  getMetrics: () => api.get('/api/dashboard/metrics'),
  getSystemStatus: () => api.get('/api/dashboard/system-status'),
  getAlerts: () => api.get('/api/dashboard/alerts'),
};

export const federatedLearningAPI = {
  getStatus: () => api.get('/api/federated-learning/status'),
  startTraining: (config: any) => api.post('/api/federated-learning/start', config),
  stopTraining: () => api.post('/api/federated-learning/stop'),
  getClients: () => api.get('/api/federated-learning/clients'),
  getMetrics: () => api.get('/api/federated-learning/metrics'),
  getAlgorithms: () => api.get('/api/federated-learning/algorithms'),
};

export const securityAPI = {
  getThreats: () => api.get('/api/security/threats'),
  getIncidents: () => api.get('/api/security/incidents'),
  getVulnerabilities: () => api.get('/api/security/vulnerabilities'),
  scanSystem: () => api.post('/api/security/scan'),
  updateRules: (rules: any) => api.post('/api/security/rules', rules),
};

export const networkAPI = {
  getStatus: () => api.get('/api/network/status'),
  getTraffic: () => api.get('/api/network/traffic'),
  getConnections: () => api.get('/api/network/connections'),
  getMetrics: () => api.get('/api/network/metrics'),
  scanNetwork: () => api.post('/api/network/scan'),
};

export const datasetsAPI = {
  getDatasets: () => api.get('/api/datasets'),
  uploadDataset: (formData: FormData) => api.post('/api/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  deleteDataset: (id: string) => api.delete(`/api/datasets/${id}`),
  getDatasetInfo: (id: string) => api.get(`/api/datasets/${id}`),
};

export const researchAPI = {
  getExperiments: () => api.get('/api/research/experiments'),
  createExperiment: (config: any) => api.post('/api/research/experiments', config),
  getResults: (id: string) => api.get(`/api/research/experiments/${id}/results`),
  getPublications: () => api.get('/api/research/publications'),
};

export const settingsAPI = {
  getSettings: () => api.get('/api/settings'),
  updateSettings: (settings: any) => api.put('/api/settings', settings),
  exportSettings: () => api.get('/api/settings/export'),
  importSettings: (file: File) => api.post('/api/settings/import', file, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

export const integrationsAPI = {
  getIntegrations: () => api.get('/api/integrations'),
  enableIntegration: (name: string) => api.post(`/api/integrations/${name}/enable`),
  disableIntegration: (name: string) => api.post(`/api/integrations/${name}/disable`),
  getIntegrationStatus: (name: string) => api.get(`/api/integrations/${name}/status`),
};

export default api;