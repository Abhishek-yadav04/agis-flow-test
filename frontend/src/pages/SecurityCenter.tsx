import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Lock, Eye, Settings, Target } from 'lucide-react';

interface SecurityThreat {
  id: string;
  timestamp: string;
  threat_type: string;
  severity: string;
  source_ip: string;
  target_ip: string;
  description: string;
  status: string;
  confidence_score: number;
  mitigation_action: string;
}

interface SecurityMetrics {
  total_threats: number;
  active_threats: number;
  blocked_attacks: number;
  security_score: number;
  vulnerability_score: number;
  firewall_rules: number;
  ids_alerts: number;
  suspicious_ips: number;
}

const SecurityCenter: React.FC = () => {
  const [threats, setThreats] = useState<SecurityThreat[]>([]);
  const [metrics, setMetrics] = useState<SecurityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedThreat, setSelectedThreat] = useState<SecurityThreat | null>(null);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchSecurityData();
  }, []);

  const fetchSecurityData = async () => {
    try {
      // Fetch security metrics
      const metricsResponse = await fetch('/api/security/metrics');
      if (metricsResponse.ok) {
        const metricsData = await metricsResponse.json();
        setMetrics(metricsData);
      }

      // Fetch security threats
      const threatsResponse = await fetch('/api/security/threats');
      if (threatsResponse.ok) {
        const threatsData = await threatsResponse.json();
        setThreats(threatsData.threats || []);
      }
    } catch (error) {
      console.error('Failed to fetch security data:', error);
      // Fallback data for demo
      setMetrics({
        total_threats: 45,
        active_threats: 12,
        blocked_attacks: 28,
        security_score: 87,
        vulnerability_score: 92,
        firewall_rules: 2500,
        ids_alerts: 156,
        suspicious_ips: 34
      });
      setThreats([
        {
          id: '1',
          timestamp: new Date().toISOString(),
          threat_type: 'Port Scan',
          severity: 'MEDIUM',
          source_ip: '192.168.1.100',
          target_ip: '10.0.0.50',
          description: 'Multiple port scan attempts detected from suspicious IP',
          status: 'ACTIVE',
          confidence_score: 85,
          mitigation_action: 'Blocked IP and increased monitoring'
        },
        {
          id: '2',
          timestamp: new Date(Date.now() - 300000).toISOString(),
          threat_type: 'DDoS Attack',
          severity: 'HIGH',
          source_ip: '203.0.113.0/24',
          target_ip: '10.0.0.1',
          description: 'Distributed denial of service attack detected',
          status: 'MITIGATED',
          confidence_score: 95,
          mitigation_action: 'Activated DDoS protection and blocked source range'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };



  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high': return 'bg-red-600/20 text-red-400 border-red-500/30';
      case 'medium': return 'bg-yellow-600/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-green-600/20 text-green-400 border-green-500/30';
      default: return 'bg-gray-600/20 text-gray-400 border-gray-500/30';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active': return 'bg-red-600/20 text-red-400 border-red-500/30';
      case 'mitigated': return 'bg-green-600/20 text-green-400 border-green-500/30';
      case 'investigating': return 'bg-yellow-600/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-600/20 text-gray-400 border-gray-500/30';
    }
  };

  const filteredThreats = threats.filter(threat => {
    if (filterSeverity !== 'all' && threat.severity !== filterSeverity) return false;
    if (filterStatus !== 'all' && threat.status !== filterStatus) return false;
    return true;
  });

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
          <h1 className="text-3xl font-bold text-white">Security Center</h1>
          <p className="text-gray-400 mt-2">Comprehensive threat detection and security management</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
            <Settings className="w-5 h-5" />
            <span>Security Settings</span>
          </button>
        </div>
      </div>

      {/* Security Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-blue-400" />
            <div>
              <p className="text-gray-400 text-sm">Security Score</p>
              <p className="text-2xl font-bold text-white">{metrics?.security_score || 0}%</p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-8 h-8 text-red-400" />
            <div>
              <p className="text-gray-400 text-sm">Active Threats</p>
              <p className="text-2xl font-bold text-white">{metrics?.active_threats || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Lock className="w-8 h-8 text-green-400" />
            <div>
              <p className="text-gray-400 text-sm">Blocked Attacks</p>
              <p className="text-2xl font-bold text-white">{metrics?.blocked_attacks || 0}</p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Target className="w-8 h-8 text-purple-400" />
            <div>
              <p className="text-gray-400 text-sm">Vulnerability Score</p>
              <p className="text-2xl font-bold text-white">{metrics?.vulnerability_score || 0}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Security Metrics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Firewall Status */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Firewall Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Active Rules</span>
              <span className="text-white font-semibold">{metrics?.firewall_rules || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Blocked IPs</span>
              <span className="text-white font-semibold">{metrics?.suspicious_ips || 0}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">IDS Alerts</span>
              <span className="text-white font-semibold">{metrics?.ids_alerts || 0}</span>
            </div>
          </div>
        </div>

        {/* Threat Distribution */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Threat Distribution</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">High Severity</span>
              <span className="text-red-400 font-semibold">
                {threats.filter(t => t.severity === 'HIGH').length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Medium Severity</span>
              <span className="text-yellow-400 font-semibold">
                {threats.filter(t => t.severity === 'MEDIUM').length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Low Severity</span>
              <span className="text-green-400 font-semibold">
                {threats.filter(t => t.severity === 'LOW').length}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Threat Filters</h3>
        <div className="flex items-center space-x-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Severity</label>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Severities</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
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
              <option value="ACTIVE">Active</option>
              <option value="MITIGATED">Mitigated</option>
              <option value="INVESTIGATING">Investigating</option>
            </select>
          </div>
        </div>
      </div>

      {/* Threats Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">Security Threats</h3>
          <p className="text-gray-400 text-sm">Real-time threat detection and response</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Threat Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Severity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Source IP
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {filteredThreats.map((threat) => (
                <tr key={threat.id} className="hover:bg-gray-700/30">
                  <td className="px-6 py-4 text-sm text-gray-300">
                    {new Date(threat.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-white">
                    {threat.threat_type}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getSeverityBadge(threat.severity)}`}>
                      {threat.severity}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-white font-mono">
                    {threat.source_ip}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusBadge(threat.status)}`}>
                      {threat.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300">
                    {threat.confidence_score}%
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setSelectedThreat(threat)}
                        className="p-1 text-blue-400 hover:text-blue-300 hover:bg-blue-600/20 rounded-lg transition-colors"
                        title="View Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Threat Details Modal */}
      {selectedThreat && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Threat Details</h3>
              <button
                onClick={() => setSelectedThreat(null)}
                className="text-gray-400 hover:text-gray-300"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300">Threat ID</label>
                  <p className="text-white font-mono">{selectedThreat.id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Timestamp</label>
                  <p className="text-white">{new Date(selectedThreat.timestamp).toLocaleString()}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Threat Type</label>
                  <p className="text-white">{selectedThreat.threat_type}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Severity</label>
                  <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getSeverityBadge(selectedThreat.severity)}`}>
                    {selectedThreat.severity}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Source IP</label>
                  <p className="text-white font-mono">{selectedThreat.source_ip}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Target IP</label>
                  <p className="text-white font-mono">{selectedThreat.target_ip}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Status</label>
                  <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getStatusBadge(selectedThreat.status)}`}>
                    {selectedThreat.status}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Confidence Score</label>
                  <p className="text-white">{selectedThreat.confidence_score}%</p>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300">Description</label>
                <p className="text-white">{selectedThreat.description}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300">Mitigation Action</label>
                <p className="text-white">{selectedThreat.mitigation_action}</p>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  onClick={() => setSelectedThreat(null)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityCenter;
