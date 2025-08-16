import { create } from 'zustand';
import { DashboardData, Alert, ResearchProject, Dataset, FLAlgorithm } from '@/types';

interface AppState {
  dashboardData: DashboardData | null;
  realTimeData: any;
  isLoading: boolean;
  error: string | null;
  isConnected: boolean;
  connectionStatus: 'connected' | 'disconnected' | 'connecting' | 'error';
  alerts: Alert[];
  unreadAlerts: number;
  researchProjects: ResearchProject[];
  activeProject: ResearchProject | null;
  datasets: Dataset[];
  selectedDataset: Dataset | null;
  flAlgorithms: FLAlgorithm[];
  activeAlgorithm: FLAlgorithm | null;
  sidebarOpen: boolean;
  theme: 'dark' | 'light';
  notifications: any[];

  setDashboardData: (data: DashboardData) => void;
  setRealTimeData: (data: any) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setConnectionStatus: (status: 'connected' | 'disconnected' | 'connecting' | 'error') => void;
  addAlert: (alert: Alert) => void;
  acknowledgeAlert: (alertId: string) => void;
  setResearchProjects: (projects: ResearchProject[]) => void;
  setActiveProject: (project: ResearchProject | null) => void;
  addResearchProject: (project: ResearchProject) => void;
  setDatasets: (datasets: Dataset[]) => void;
  setSelectedDataset: (dataset: Dataset | null) => void;
  setFLAlgorithms: (algorithms: FLAlgorithm[]) => void;
  setActiveAlgorithm: (algorithm: FLAlgorithm | null) => void;
  toggleSidebar: () => void;
  setTheme: (theme: 'dark' | 'light') => void;
  addNotification: (notification: any) => void;
  removeNotification: (id: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  dashboardData: null,
  realTimeData: null,
  isLoading: false,
  error: null,
  isConnected: false,
  connectionStatus: 'disconnected',
  alerts: [],
  unreadAlerts: 0,
  researchProjects: [],
  activeProject: null,
  datasets: [],
  selectedDataset: null,
  flAlgorithms: [],
  activeAlgorithm: null,
  sidebarOpen: true,
  theme: 'dark',
  notifications: [],

  setDashboardData: (data) => set({ dashboardData: data, error: null }),
  setRealTimeData: (data) => set({ realTimeData: data }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  setConnectionStatus: (status) => set({ connectionStatus: status, isConnected: status === 'connected' }),
  addAlert: (alert) => set(state => ({ alerts: [alert, ...state.alerts].slice(0, 100), unreadAlerts: state.unreadAlerts + 1 })),
  acknowledgeAlert: (alertId) => set(state => ({ 
    alerts: state.alerts.map(alert => alert.id === alertId ? { ...alert, acknowledged: true } : alert),
    unreadAlerts: Math.max(0, state.unreadAlerts - 1)
  })),
  setResearchProjects: (projects) => set({ researchProjects: projects }),
  setActiveProject: (project) => set({ activeProject: project }),
  addResearchProject: (project) => set(state => ({ researchProjects: [project, ...state.researchProjects] })),
  setDatasets: (datasets) => set({ datasets }),
  setSelectedDataset: (dataset) => set({ selectedDataset: dataset }),
  setFLAlgorithms: (algorithms) => set({ flAlgorithms: algorithms }),
  setActiveAlgorithm: (algorithm) => set({ activeAlgorithm: algorithm }),
  toggleSidebar: () => set(state => ({ sidebarOpen: !state.sidebarOpen })),
  setTheme: (theme) => set({ theme }),
  addNotification: (notification) => set(state => ({ notifications: [notification, ...state.notifications] })),
  removeNotification: (id) => set(state => ({ notifications: state.notifications.filter(n => n.id !== id) })),
}));