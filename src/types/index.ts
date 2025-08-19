export interface MetricData {
  label: string;
  value: number;
  change?: number;
  unit?: string;
  status?: 'success' | 'warning' | 'error' | 'info';
}

export interface Alert {
  id: string;
  type: 'security' | 'system' | 'network' | 'fl';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  acknowledged?: boolean;
}

export interface FederatedLearningClient {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'training';
  accuracy: number;
  dataSize: number;
  lastSeen: string;
  ipAddress: string;
}

export interface SecurityThreat {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  target: string;
  timestamp: string;
  status: 'active' | 'mitigated' | 'investigating';
  description: string;
}

export interface NetworkConnection {
  id: string;
  source: string;
  destination: string;
  protocol: string;
  port: number;
  status: 'active' | 'closed' | 'listening';
  traffic: number;
  timestamp: string;
}

export interface Dataset {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadedAt: string;
  status: 'ready' | 'processing' | 'error';
  samples: number;
  features: number;
}

export interface Experiment {
  id: string;
  name: string;
  type: string;
  status: 'running' | 'completed' | 'failed' | 'pending';
  startTime: string;
  endTime?: string;
  accuracy?: number;
  participants: number;
  dataset: string;
}

export interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: {
    inbound: number;
    outbound: number;
  };
  uptime: number;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
    fill?: boolean;
  }[];
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface Integration {
  name: string;
  displayName: string;
  status: 'enabled' | 'disabled' | 'error';
  description: string;
  icon: string;
  category: 'security' | 'monitoring' | 'ml' | 'network';
  version?: string;
  lastUpdated?: string;
}