// Core Application Types
export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  network_sent_mb: number;
  network_recv_mb: number;
  processes: number;
  uptime_hours: number;
}

export interface FederatedLearning {
  status: 'active' | 'inactive' | 'training' | 'error';
  current_round: number;
  global_accuracy: number;
  participating_clients: number;
  total_clients: number;
  convergence_rate: number;
  training_loss: number;
  data_samples: number;
  model_size_mb: number;
  strategy: string;
}

export interface SecurityMetrics {
  threat_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  threats_detected_today: number;
  blocked_attacks: number;
  suspicious_ips: number;
  security_score: number;
  firewall_rules: number;
  ids_alerts: number;
  vulnerability_score: number;
}

export interface NetworkMonitoring {
  packets_captured: number;
  suspicious_packets: number;
  bandwidth_utilization: number;
  active_connections: number;
  packet_loss: number;
  latency_ms: number;
  scapy_available: boolean;
  admin_privileges: boolean;
  capture_mode: 'real' | 'simulation';
}

export interface Integration {
  name: string;
  status: 'active' | 'inactive' | 'error' | 'connecting';
  last_update: string;
  health_score: number;
  details: Record<string, any>;
}

export interface Alert {
  id: string;
  type: 'SECURITY' | 'PERFORMANCE' | 'SYSTEM' | 'NETWORK';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  timestamp: string;
  source: string;
  acknowledged: boolean;
}

export interface DashboardData {
  overview: {
    system_health: number;
    active_threats: number;
    fl_accuracy: number;
    network_traffic: number;
    uptime_hours: number;
  };
  system_metrics: SystemMetrics & {
    history: TimeSeriesData[];
  };
  federated_learning: FederatedLearning & {
    accuracy_history: TimeSeriesData[];
    client_distribution: ClientDistribution[];
    strategy_performance: StrategyPerformance[];
  };
  security: SecurityMetrics & {
    threat_history: TimeSeriesData[];
    attack_types: AttackType[];
    geographic_threats: GeographicThreat[];
  };
  network_monitoring: NetworkMonitoring & {
    protocol_distribution: ProtocolDistribution[];
    traffic_patterns: TimeSeriesData[];
    top_talkers: TopTalker[];
  };
  integrations: Record<string, Integration>;
  performance: PerformanceMetrics;
  alerts: Alert[];
  analytics: AnalyticsData;
  timestamp: string;
  version: string;
  environment: string;
}

export interface TimeSeriesData {
  timestamp: string;
  value: number;
}

export interface ClientDistribution {
  region: string;
  clients: number;
  accuracy: number;
}

export interface StrategyPerformance {
  strategy: string;
  accuracy: number;
  convergence: string;
}

export interface AttackType {
  type: string;
  count: number;
  severity: string;
}

export interface GeographicThreat {
  country: string;
  threats: number;
  blocked: number;
}

export interface ProtocolDistribution {
  protocol: string;
  percentage: number;
  packets: number;
}

export interface TopTalker {
  ip: string;
  bytes: number;
  packets: number;
}

export interface PerformanceMetrics {
  response_time_ms: number;
  throughput_rps: number;
  error_rate: number;
  availability: number;
  cache_hit_rate: number;
  database_connections: number;
}

export interface AnalyticsData {
  user_sessions: number;
  api_calls_today: number;
  data_processed_gb: number;
  ml_predictions: number;
  anomalies_detected: number;
}

// Research Lab Types
export interface ResearchProject {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'paused';
  progress: number;
  datasets: string[];
  algorithms: string[];
  results: ResearchResult[];
  created_at: string;
  updated_at: string;
}

export interface ResearchResult {
  id: string;
  experiment_name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  training_time: number;
  dataset_size: number;
  algorithm: string;
  parameters: Record<string, any>;
  timestamp: string;
}

// Dataset Types
export interface Dataset {
  id: string;
  name: string;
  description: string;
  type: 'network_traffic' | 'intrusion_detection' | 'malware' | 'federated_learning';
  size_mb: number;
  samples: number;
  features: number;
  labels: string[];
  source: string;
  license: string;
  download_url: string;
  preprocessing_required: boolean;
  quality_score: number;
  last_updated: string;
}

// FL Algorithm Types
export interface FLAlgorithm {
  name: string;
  description: string;
  type: 'aggregation' | 'optimization' | 'privacy' | 'personalization';
  parameters: Record<string, any>;
  performance_metrics: {
    convergence_speed: number;
    communication_efficiency: number;
    privacy_level: number;
    accuracy: number;
  };
  supported_models: string[];
  implementation_status: 'implemented' | 'in_progress' | 'planned';
}

// WebSocket Types
export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  timestamp: string;
}

// User Types
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'operator' | 'viewer';
  permissions: string[];
  last_login: string;
  created_at: string;
}

// Configuration Types
export interface AppConfig {
  api_base_url: string;
  websocket_url: string;
  refresh_interval: number;
  chart_update_interval: number;
  max_alerts: number;
  theme: 'dark' | 'light';
  features: {
    real_time_monitoring: boolean;
    advanced_analytics: boolean;
    research_lab: boolean;
    dataset_management: boolean;
  };
}