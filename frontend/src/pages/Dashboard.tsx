import { useState, useEffect } from 'react';
import axios from 'axios';
import { useQuery } from 'react-query';
import { 
  Shield, 
  Brain, 
  TrendingUp, 
  AlertTriangle,
  Activity,
  Zap,
  RefreshCw
} from 'lucide-react';
import RealTimeChart from '../components/Charts/RealTimeChart';
import { dashboardAPI } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import toast from 'react-hot-toast';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

interface DashboardData {
  system?: {
    cpu_percent: number;
    memory_percent: number;
    disk_percent: number;
    network_sent_mb: number;
    network_recv_mb: number;
    processes: number;
  };
  performance?: {
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_traffic_mb: number;
  };
  overview?: {
    system_health: number;
    security_score: number;
    fl_round: number;
    total_processes: number;
  };
  federated_learning: {
    current_round: number;
    global_accuracy: number;
    active_clients: number;
    participating_clients?: number;
    training_active: boolean;
    strategy: string;
    model_accuracy?: number;
    convergence_rate?: number;
  };
  security: {
    threats_detected: number;
    alerts_active: number;
    security_score: number;
    intrusions_blocked: number;
    threats_blocked?: number;
  };
  network: {
    packets_analyzed: number;
    bandwidth_usage: number;
    connections_active: number;
  };
}

const fetchDashboardData = async (): Promise<DashboardData> => {
  const response = await dashboardAPI.getDashboard();
  return response.data;
};

const Dashboard: React.FC = () => {
  const [realTimeData, setRealTimeData] = useState<number[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [flStatus, setFlStatus] = useState<{mode:string; metrics:any; rounds:number; tensorflow:boolean; force_sim:boolean}>({mode:'disabled', metrics:{}, rounds:0, tensorflow:false, force_sim:false});
  
  const { data, isLoading, error, refetch } = useQuery(
    'dashboardData',
    fetchDashboardData,
    {
      refetchInterval: 5000,
      onSuccess: (data) => {
        setRealTimeData(prev => [...prev.slice(-19), data.performance?.cpu_usage || data.system?.cpu_percent || 0]);
      },
      onError: () => {
        toast.error('Failed to load dashboard data');
      }
    }
  );

  const { isConnected, lastMessage } = useWebSocket('ws://127.0.0.1:8001/ws');

  useEffect(() => {
    setWsConnected(isConnected);
    if (isConnected) {
      toast.success('Real-time connection established');
    }
  }, [isConnected]);

  useEffect(() => {
    if (lastMessage?.type === 'fl_update') {
      // Handle real-time FL updates
      console.log('FL Update:', lastMessage.data);
    }
  }, [lastMessage]);

  useEffect(() => {
    let cancelled = false;
    const fetchStatus = async () => {
      try {
        const res = await axios.get('/api/fl/status');
        if (!cancelled) {
          setFlStatus({
            mode: res.data.mode,
            metrics: res.data.metrics,
            rounds: res.data.rounds_total || res.data.metrics?.round || 0,
            tensorflow: res.data.tensorflow,
            force_sim: res.data.force_sim
          });
        }
      } catch (_) { /* ignore */ }
    };
    fetchStatus();
    const id = setInterval(fetchStatus, 8000);
    return () => { cancelled = true; clearInterval(id); };
  }, []);

  const StatCard = ({ title, value, icon: Icon, color, subtitle, trend }: any) => (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
            {wsConnected && <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>}
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{subtitle}</p>}
          {trend && (
            <div className={`flex items-center mt-2 text-xs ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
              <TrendingUp className="w-3 h-3 mr-1" />
              {trend > 0 ? '+' : ''}{trend}%
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color} relative`}>
          <Icon className="w-6 h-6 text-white" />
          {wsConnected && <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>}
        </div>
      </div>
    </div>
  );



  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-48 animate-pulse"></div>
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-24 animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-800 dark:text-red-200">Failed to load dashboard data</p>
        <button 
          onClick={() => refetch()}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-3">
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">FL-IDS Dashboard</span>
            {wsConnected && <span className="flex items-center gap-1 text-xs bg-green-600 text-white px-2 py-0.5 rounded-full"><div className="w-2 h-2 bg-white rounded-full animate-pulse"/>Live</span>}
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Unified observability for federated learning, security & system health</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-xs">
            <span className={`px-2 py-1 rounded-full font-medium border ${flStatus.mode==='full' ? 'bg-green-600 text-white border-green-500' : flStatus.mode==='simulation' ? 'bg-amber-500 text-white border-amber-400' : 'bg-gray-500 text-white border-gray-400'}`}>FL {flStatus.mode}</span>
            {flStatus.rounds > 0 && <span className="px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200">Round {flStatus.rounds}</span>}
            {typeof flStatus.metrics?.accuracy !== 'undefined' && <span className="px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">Acc {((flStatus.metrics.accuracy || flStatus.metrics.global_accuracy || flStatus.metrics.avg_accuracy || 0)*100).toFixed(1)}%</span>}
          </div>
          <button onClick={() => refetch()} className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors flex items-center gap-2">
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        </div>
      </div>

      {/* Key Metrics */}
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="FL Training Round"
          value={data?.federated_learning?.current_round || data?.overview?.fl_round || 15}
          subtitle={`${data?.federated_learning?.active_clients || data?.federated_learning?.participating_clients || 8} active clients`}
          icon={Brain}
          color="bg-blue-500"
          trend={2.3}
        />
        <StatCard
          title="Global Accuracy"
          value={`${data?.federated_learning?.global_accuracy || (data?.federated_learning?.model_accuracy ? data.federated_learning.model_accuracy * 100 : 94.2)}%`}
          subtitle={data?.federated_learning?.strategy || 'FedAvg'}
          icon={TrendingUp}
          color="bg-green-500"
          trend={1.8}
        />
        <StatCard
          title="Security Score"
          value={`${data?.security?.security_score || data?.overview?.security_score || 95}%`}
          subtitle={`${data?.security?.threats_detected || data?.security?.threats_blocked || 3} threats detected`}
          icon={Shield}
          color="bg-red-500"
          trend={-0.5}
        />
        <StatCard
          title="System Health"
          value={`${data?.overview?.system_health || 92}%`}
          subtitle={`${data?.overview?.total_processes || 150} processes`}
          icon={Activity}
          color="bg-purple-500"
          trend={0.8}
        />
      </div>

      {/* Charts Section */}
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Performance */}
  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              System Performance
            </h3>
            <div className="flex items-center space-x-2">
              {wsConnected ? (
                <div className="flex items-center text-green-600 dark:text-green-400">
                  <Zap className="w-4 h-4 mr-1" />
                  <span className="text-sm">Live</span>
                </div>
              ) : (
                <button onClick={() => refetch()} className="text-blue-600 hover:text-blue-800">
                  <RefreshCw className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          <div className="h-64">
            <RealTimeChart 
              data={realTimeData} 
              label="CPU Usage" 
              color="#3B82F6" 
              height={256}
            />
          </div>
          <div className="grid grid-cols-4 gap-4 mt-4">
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">CPU</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {data?.performance?.cpu_usage || data?.system?.cpu_percent || 0}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Memory</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {data?.performance?.memory_usage || data?.system?.memory_percent || 0}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Disk</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {data?.performance?.disk_usage || data?.system?.disk_percent || 0}%
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400">Network</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {data?.performance?.network_traffic_mb || 150}MB
              </p>
            </div>
          </div>
        </div>

        {/* FL Training Status */}
  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Federated Learning Status
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Training Status</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                data?.federated_learning.training_active 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400'
              }`}>
                {data?.federated_learning.training_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Current Round</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {data?.federated_learning.current_round || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Global Accuracy</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {data?.federated_learning.global_accuracy || 0}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Active Clients</span>
              <span className="font-semibold text-gray-900 dark:text-white">
                {data?.federated_learning.active_clients || 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Security Alerts */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Security Overview
          </h3>
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-yellow-500" />
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {data?.security.alerts_active || 0} active alerts
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {data?.security.threats_detected || 0}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Threats Detected</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {data?.security.intrusions_blocked || 0}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Intrusions Blocked</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {data?.security.security_score || 0}%
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Security Score</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;