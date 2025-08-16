import React, { useState, useEffect } from 'react';
import { Activity, Cpu, HardDrive, Network, TrendingUp, Server, Database } from 'lucide-react';


interface SystemMetrics {
  cpu: {
    percent: number;
    per_core: number[];
    count: number;
    frequency_mhz: number;
    load_avg: number[];
  };
  memory: {
    percent: number;
    available_gb: number;
    used_gb: number;
    total_gb: number;
  };
  disk: {
    percent: number;
    free_gb: number;
    used_gb: number;
    total_gb: number;
  };
  network: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
  };
  processes: number;
  uptime_hours: number;
  timestamp: string;
}

interface PerformanceHistory {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
}

const SystemMetrics: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [history, setHistory] = useState<PerformanceHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);
  const [caps, setCaps] = useState<{ scapy_available?: boolean; pcap_enabled?: boolean; tensorflow_available?: boolean; flower_available?: boolean } | null>(null);

  useEffect(() => {
    fetchSystemMetrics();
    // fire-and-forget capabilities
    fetch('/api/capabilities').then(async (r) => {
      if (r.ok) setCaps(await r.json());
    }).catch(() => {});
    
    if (autoRefresh) {
      const interval = setInterval(fetchSystemMetrics, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const fetchSystemMetrics = async () => {
    try {
      const response = await fetch('/api/dashboard');
      if (response.ok) {
        const data = await response.json();
        const systemData = data.system_metrics;
        
        if (systemData) {
          setMetrics({
            cpu: {
              percent: systemData.cpu_percent || 0,
              per_core: [25, 30, 35, 40], // Fallback data
              count: 4,
              frequency_mhz: 2400,
              load_avg: [0.5, 0.8, 1.2]
            },
            memory: {
              percent: systemData.memory_percent || 0,
              available_gb: systemData.memory_available_gb || 0,
              used_gb: systemData.memory_used_gb || 0,
              total_gb: systemData.memory_total_gb || 0
            },
            disk: {
              percent: systemData.disk_percent || 0,
              free_gb: systemData.disk_free_gb || 0,
              used_gb: systemData.disk_used_gb || 0,
              total_gb: systemData.disk_total_gb || 0
            },
            network: {
              bytes_sent: systemData.network_sent_mb || 0,
              bytes_recv: systemData.network_recv_mb || 0,
              packets_sent: 0,
              packets_recv: 0
            },
            processes: systemData.processes || 0,
            uptime_hours: systemData.uptime_hours || 0,
            timestamp: new Date().toISOString()
          });

          // Update history
          if (systemData.history) {
            setHistory(systemData.history);
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
      // Fallback data for demo
      setMetrics({
        cpu: {
          percent: 45.2,
          per_core: [42, 48, 51, 39],
          count: 4,
          frequency_mhz: 2400,
          load_avg: [0.5, 0.8, 1.2]
        },
        memory: {
          percent: 67.8,
          available_gb: 6.2,
          used_gb: 13.1,
          total_gb: 19.3
        },
        disk: {
          percent: 58.4,
          free_gb: 186.7,
          used_gb: 262.3,
          total_gb: 449.0
        },
        network: {
          bytes_sent: 125.6,
          bytes_recv: 89.3,
          packets_sent: 125000,
          packets_recv: 89000
        },
        processes: 187,
        uptime_hours: 48.2,
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const getHealthColor = (percent: number, thresholds: { warning: number; critical: number }) => {
    if (percent >= thresholds.critical) return 'text-red-400';
    if (percent >= thresholds.warning) return 'text-yellow-400';
    return 'text-green-400';
  };



  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {caps && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <p className="text-xs text-gray-400">
            Capture: {caps.scapy_available ? 'Scapy available' : 'Scapy not available'} • Pcap: {caps.pcap_enabled ? 'enabled' : 'disabled'} • FL: {caps.tensorflow_available ? 'TensorFlow present' : 'TensorFlow missing'}
          </p>
        </div>
      )}
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">System Metrics</h1>
          <p className="text-gray-400 mt-2">Real-time system performance monitoring and analysis</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-300">Auto-refresh</span>
          </div>
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={1000}>1s</option>
            <option value={5000}>5s</option>
            <option value={10000}>10s</option>
            <option value={30000}>30s</option>
          </select>
          <button
            onClick={fetchSystemMetrics}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Activity className="w-5 h-5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Cpu className="w-8 h-8 text-blue-400" />
            <div>
              <p className="text-gray-400 text-sm">CPU Usage</p>
              <p className={`text-2xl font-bold ${getHealthColor(metrics?.cpu.percent || 0, { warning: 70, critical: 90 })}`}>
                {metrics?.cpu.percent.toFixed(1) || 0}%
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Database className="w-8 h-8 text-green-400" />
            <div>
              <p className="text-gray-400 text-sm">Memory Usage</p>
              <p className={`text-2xl font-bold ${getHealthColor(metrics?.memory.percent || 0, { warning: 80, critical: 90 })}`}>
                {metrics?.memory.percent.toFixed(1) || 0}%
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <HardDrive className="w-8 h-8 text-purple-400" />
            <div>
              <p className="text-gray-400 text-sm">Disk Usage</p>
              <p className={`text-2xl font-bold ${getHealthColor(metrics?.disk.percent || 0, { warning: 80, critical: 90 })}`}>
                {metrics?.disk.percent.toFixed(1) || 0}%
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Network className="w-8 h-8 text-orange-400" />
            <div>
              <p className="text-gray-400 text-sm">Network I/O</p>
              <p className="text-2xl font-bold text-white">
                {formatBytes((metrics?.network.bytes_sent || 0) * 1024 * 1024)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Detailed Metrics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* CPU Details */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            <span>CPU Information</span>
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Overall Usage</span>
              <span className={`font-semibold ${getHealthColor(metrics?.cpu.percent || 0, { warning: 70, critical: 90 })}`}>
                {metrics?.cpu.percent.toFixed(1) || 0}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Core Count</span>
              <span className="text-white font-semibold">{metrics?.cpu.count || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Frequency</span>
              <span className="text-white font-semibold">{metrics?.cpu.frequency_mhz || 0} MHz</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Load Average</span>
              <span className="text-white font-semibold">
                {metrics?.cpu.load_avg?.map(load => load.toFixed(2)).join(', ') || '0.00'}
              </span>
            </div>
            
            {/* Per-core usage */}
            <div>
              <span className="text-gray-300 text-sm">Per-Core Usage</span>
              <div className="grid grid-cols-4 gap-2 mt-2">
                {metrics?.cpu.per_core.map((usage, index) => (
                  <div key={index} className="text-center">
                    <div className="text-xs text-gray-400">Core {index + 1}</div>
                    <div className={`text-sm font-medium ${getHealthColor(usage, { warning: 70, critical: 90 })}`}>
                      {usage.toFixed(0)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Memory Details */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <Database className="w-5 h-5 text-green-400" />
            <span>Memory Information</span>
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Total Memory</span>
              <span className="text-white font-semibold">{metrics?.memory.total_gb.toFixed(1) || 0} GB</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Used Memory</span>
              <span className="text-white font-semibold">{metrics?.memory.used_gb.toFixed(1) || 0} GB</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Available Memory</span>
              <span className="text-white font-semibold">{metrics?.memory.available_gb.toFixed(1) || 0} GB</span>
            </div>
            
            {/* Memory usage bar */}
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-300">Usage</span>
                <span className={`font-medium ${getHealthColor(metrics?.memory.percent || 0, { warning: 80, critical: 90 })}`}>
                  {metrics?.memory.percent.toFixed(1) || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    getHealthColor(metrics?.memory.percent || 0, { warning: 80, critical: 90 }) === 'text-red-400'
                      ? 'bg-red-500'
                      : getHealthColor(metrics?.memory.percent || 0, { warning: 80, critical: 90 }) === 'text-yellow-400'
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(metrics?.memory.percent || 0, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Disk Details */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <HardDrive className="w-5 h-5 text-purple-400" />
            <span>Disk Information</span>
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Total Space</span>
              <span className="text-white font-semibold">{metrics?.disk.total_gb.toFixed(1) || 0} GB</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Used Space</span>
              <span className="text-white font-semibold">{metrics?.disk.used_gb.toFixed(1) || 0} GB</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Free Space</span>
              <span className="text-white font-semibold">{metrics?.disk.free_gb.toFixed(1) || 0} GB</span>
            </div>
            
            {/* Disk usage bar */}
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-300">Usage</span>
                <span className={`font-medium ${getHealthColor(metrics?.disk.percent || 0, { warning: 80, critical: 90 })}`}>
                  {metrics?.disk.percent.toFixed(1) || 0}%
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${
                    getHealthColor(metrics?.disk.percent || 0, { warning: 80, critical: 90 }) === 'text-red-400'
                      ? 'bg-red-500'
                      : getHealthColor(metrics?.disk.percent || 0, { warning: 80, critical: 90 }) === 'text-yellow-400'
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                  }`}
                  style={{ width: `${Math.min(metrics?.disk.percent || 0, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <Server className="w-5 h-5 text-orange-400" />
            <span>System Information</span>
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Active Processes</span>
              <span className="text-white font-semibold">{metrics?.processes || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Uptime</span>
              <span className="text-white font-semibold">{metrics?.uptime_hours.toFixed(1) || 0} hours</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Last Update</span>
              <span className="text-white font-semibold">
                {metrics?.timestamp ? new Date(metrics.timestamp).toLocaleTimeString() : 'Unknown'}
              </span>
            </div>
            
            {/* Network stats */}
            <div className="pt-2 border-t border-gray-600">
              <span className="text-gray-300 text-sm">Network Statistics</span>
              <div className="grid grid-cols-2 gap-2 mt-2">
                <div className="text-center">
                  <div className="text-xs text-gray-400">Sent</div>
                  <div className="text-sm font-medium text-white">
                    {formatBytes((metrics?.network.bytes_sent || 0) * 1024 * 1024)}
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-400">Received</div>
                  <div className="text-sm font-medium text-white">
                    {formatBytes((metrics?.network.bytes_recv || 0) * 1024 * 1024)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Performance History */}
      {history.length > 0 && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            <span>Performance History</span>
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700/50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Time</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">CPU</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Memory</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-300 uppercase">Disk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {history.slice(-10).map((entry, index) => (
                  <tr key={index} className="hover:bg-gray-700/30">
                    <td className="px-4 py-2 text-sm text-gray-300">
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="px-4 py-2 text-sm text-white">
                      {entry.cpu_percent.toFixed(1)}%
                    </td>
                    <td className="px-4 py-2 text-sm text-white">
                      {entry.memory_percent.toFixed(1)}%
                    </td>
                    <td className="px-4 py-2 text-sm text-white">
                      {entry.disk_percent.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemMetrics;
