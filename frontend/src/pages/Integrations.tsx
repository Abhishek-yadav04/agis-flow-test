import React, { useState, useEffect } from 'react';
import { Link, Settings, Activity, CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';

interface Integration {
  name: string;
  description: string;
  status: 'active' | 'inactive' | 'error' | 'connecting';
  category: string;
  version: string;
  last_updated: string;
  config_status: 'configured' | 'not_configured' | 'misconfigured';
  health_score: number;
  endpoints: string[];
  features: string[];
}

const Integrations: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      const response = await fetch('/api/integrations');
      if (response.ok) {
        const data = await response.json();
        setIntegrations(data.integrations || []);
      }
    } catch (error) {
      console.error('Failed to fetch integrations:', error);
      // Fallback data for demo
      setIntegrations([
        {
          name: "Scapy Network Monitor",
          description: "Advanced network packet capture and analysis using Scapy",
          status: "active",
          category: "Network Security",
          version: "2.5.0",
          last_updated: new Date().toISOString(),
          config_status: "configured",
          health_score: 95,
          endpoints: ["/api/network/capture", "/api/network/analyze"],
          features: ["Packet Capture", "Protocol Analysis", "Threat Detection"]
        },
        {
          name: "Flower FL Server",
          description: "Federated Learning coordination server for distributed training",
          status: "active",
          category: "Machine Learning",
          version: "1.4.0",
          last_updated: new Date(Date.now() - 300000).toISOString(),
          config_status: "configured",
          health_score: 88,
          endpoints: ["/api/fl/server", "/api/fl/clients"],
          features: ["FL Coordination", "Client Management", "Model Aggregation"]
        },
        {
          name: "Suricata IDS",
          description: "Intrusion Detection System for real-time threat analysis",
          status: "active",
          category: "Security",
          version: "6.0.0",
          last_updated: new Date(Date.now() - 600000).toISOString(),
          config_status: "configured",
          health_score: 92,
          endpoints: ["/api/security/alerts", "/api/security/rules"],
          features: ["Threat Detection", "Rule Management", "Alert Correlation"]
        },
        {
          name: "Grafana Dashboard",
          description: "Advanced monitoring and visualization dashboard",
          status: "active",
          category: "Monitoring",
          version: "9.5.0",
          last_updated: new Date(Date.now() - 900000).toISOString(),
          config_status: "configured",
          health_score: 98,
          endpoints: ["/api/monitoring/metrics", "/api/monitoring/alerts"],
          features: ["Metrics Visualization", "Alert Management", "Custom Dashboards"]
        },
        {
          name: "Redis Cache",
          description: "High-performance in-memory data structure store",
          status: "active",
          category: "Data Storage",
          version: "7.0.0",
          last_updated: new Date(Date.now() - 1200000).toISOString(),
          config_status: "configured",
          health_score: 96,
          endpoints: ["/api/cache/keys", "/api/cache/stats"],
          features: ["Caching", "Session Storage", "Real-time Data"]
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400';
      case 'inactive': return 'text-gray-400';
      case 'error': return 'text-red-400';
      case 'connecting': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-600/20 text-green-400 border-green-500/30';
      case 'inactive': return 'bg-gray-600/20 text-gray-400 border-gray-500/30';
      case 'error': return 'bg-red-600/20 text-red-400 border-red-500/30';
      case 'connecting': return 'bg-yellow-600/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-600/20 text-gray-400 border-gray-500/30';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-5 h-5" />;
      case 'inactive': return <XCircle className="w-5 h-5" />;
      case 'error': return <AlertTriangle className="w-5 h-5" />;
      case 'connecting': return <RefreshCw className="w-5 h-5 animate-spin" />;
      default: return <XCircle className="w-5 h-5" />;
    }
  };

  const getConfigStatusBadge = (status: string) => {
    switch (status) {
      case 'configured': return 'bg-green-600/20 text-green-400 border-green-500/30';
      case 'not_configured': return 'bg-red-600/20 text-red-400 border-red-500/30';
      case 'misconfigured': return 'bg-yellow-600/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-600/20 text-gray-400 border-gray-500/30';
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 75) return 'text-yellow-400';
    return 'text-red-400';
  };

  const filteredIntegrations = integrations.filter(integration => {
    if (filterCategory !== 'all' && integration.category !== filterCategory) return false;
    if (filterStatus !== 'all' && integration.status !== filterStatus) return false;
    return true;
  });

  const categories = [...new Set(integrations.map(i => i.category))];
  const statuses = ['active', 'inactive', 'error', 'connecting'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Integrations</h1>
          <p className="text-gray-400 mt-2">Manage and monitor external service integrations</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchIntegrations}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Link className="w-8 h-8 text-blue-400" />
            <div>
              <p className="text-gray-400 text-sm">Total Integrations</p>
              <p className="text-2xl font-bold text-white">{integrations.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-8 h-8 text-green-400" />
            <div>
              <p className="text-gray-400 text-sm">Active</p>
              <p className="text-2xl font-bold text-white">
                {integrations.filter(i => i.status === 'active').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-8 h-8 text-yellow-400" />
            <div>
              <p className="text-gray-400 text-sm">Issues</p>
              <p className="text-2xl font-bold text-white">
                {integrations.filter(i => i.status === 'error' || i.status === 'connecting').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Settings className="w-8 h-8 text-purple-400" />
            <div>
              <p className="text-gray-400 text-sm">Avg Health</p>
              <p className="text-2xl font-bold text-white">
                {integrations.length > 0
                  ? Math.round(integrations.reduce((sum, i) => sum + i.health_score, 0) / integrations.length)
                  : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Filter Integrations</h3>
        <div className="flex items-center space-x-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Statuses</option>
              {statuses.map(status => (
                <option key={status} value={status}>{status.charAt(0).toUpperCase() + status.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Integrations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredIntegrations.map((integration) => (
          <div key={integration.name} className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-blue-500/50 transition-colors">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">{integration.name}</h3>
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusBadge(integration.status)}`}>
                    {integration.status.toUpperCase()}
                  </span>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getConfigStatusBadge(integration.config_status)}`}>
                    {integration.config_status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <div className={`${getStatusColor(integration.status)}`}>
                  {getStatusIcon(integration.status)}
                </div>
              </div>
            </div>

            <p className="text-gray-300 text-sm mb-4">{integration.description}</p>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-gray-400 text-xs uppercase tracking-wider mb-1">Category</p>
                <p className="text-white text-sm">{integration.category}</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs uppercase tracking-wider mb-1">Version</p>
                <p className="text-white text-sm">{integration.version}</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs uppercase tracking-wider mb-1">Health Score</p>
                <p className={`text-sm font-medium ${getHealthColor(integration.health_score)}`}>
                  {integration.health_score}%
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-xs uppercase tracking-wider mb-1">Last Updated</p>
                <p className="text-white text-sm">
                  {new Date(integration.last_updated).toLocaleTimeString()}
                </p>
              </div>
            </div>

            <div className="mb-4">
              <p className="text-gray-400 text-xs uppercase tracking-wider mb-2">Features</p>
              <div className="flex flex-wrap gap-2">
                {integration.features.map((feature, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-blue-600/20 text-blue-400 text-xs rounded-full border border-blue-500/30"
                  >
                    {feature}
                  </span>
                ))}
              </div>
            </div>

            <div className="mb-4">
              <p className="text-gray-400 text-xs uppercase tracking-wider mb-2">API Endpoints</p>
              <div className="space-y-1">
                {integration.endpoints.map((endpoint, index) => (
                  <div key={index} className="text-xs font-mono text-gray-300 bg-gray-700 px-2 py-1 rounded">
                    {endpoint}
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-3 pt-4 border-t border-gray-600">
              <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors text-sm">
                <Settings className="w-4 h-4 inline mr-2" />
                Configure
              </button>
              <button className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors text-sm">
                <Activity className="w-4 h-4 inline mr-2" />
                Monitor
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Integration Status Summary */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Integration Status Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {categories.map(category => {
            const categoryIntegrations = integrations.filter(i => i.category === category);
            const activeCount = categoryIntegrations.filter(i => i.status === 'active').length;
            const totalCount = categoryIntegrations.length;
            
            return (
              <div key={category} className="bg-gray-700 rounded-lg p-4">
                <h4 className="text-white font-medium mb-2">{category}</h4>
                <div className="flex items-center justify-between">
                  <span className="text-gray-300 text-sm">Active</span>
                  <span className="text-white font-semibold">{activeCount}/{totalCount}</span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-2 mt-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(activeCount / totalCount) * 100}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Integrations;
