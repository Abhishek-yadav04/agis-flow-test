import React, { useState, useEffect } from 'react';
import { Activity, Shield, AlertTriangle, Eye, Play, Pause, Settings, Download } from 'lucide-react';

interface NetworkPacket {
  id: string;
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  protocol: string;
  length: number;
  flags: string;
  suspicious_score: number;
  threat_level: string;
}

interface NetworkStats {
  total_packets: number;
  suspicious_packets: number;
  bandwidth_utilization: number;
  active_connections: number;
  packet_loss: number;
  latency_ms: number;
  protocols: Record<string, number>;
}

const NetworkMonitoring: React.FC = () => {
  const [packets, setPackets] = useState<NetworkPacket[]>([]);
  const [stats, setStats] = useState<NetworkStats | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedPacket, setSelectedPacket] = useState<NetworkPacket | null>(null);
  const [filterProtocol, setFilterProtocol] = useState<string>('all');
  const [filterThreatLevel, setFilterThreatLevel] = useState<string>('all');

  useEffect(() => {
    fetchNetworkStats();
    fetchPackets();
  }, []);

  const fetchNetworkStats = async () => {
    try {
      const response = await fetch('/api/network/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch network stats:', error);
      // Fallback data
      setStats({
        total_packets: 125000,
        suspicious_packets: 250,
        bandwidth_utilization: 45.2,
        active_connections: 450,
        packet_loss: 0.5,
        latency_ms: 15.3,
        protocols: { tcp: 70, udp: 20, icmp: 10 }
      });
    }
  };

  const fetchPackets = async () => {
    try {
      const response = await fetch('/api/network/packets');
      if (response.ok) {
        const data = await response.json();
        setPackets(data.packets || []);
      }
    } catch (error) {
      console.error('Failed to fetch packets:', error);
      // Fallback data for demo
      setPackets([
        {
          id: '1',
          timestamp: new Date().toISOString(),
          source_ip: '192.168.1.100',
          destination_ip: '10.0.0.50',
          protocol: 'TCP',
          length: 1500,
          flags: 'SYN',
          suspicious_score: 85,
          threat_level: 'HIGH'
        },
        {
          id: '2',
          timestamp: new Date(Date.now() - 1000).toISOString(),
          source_ip: '10.0.0.25',
          destination_ip: '192.168.1.1',
          protocol: 'UDP',
          length: 512,
          flags: 'NONE',
          suspicious_score: 25,
          threat_level: 'LOW'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const startMonitoring = async () => {
    try {
      const response = await fetch('/api/network/start', { method: 'POST' });
      if (response.ok) {
        setIsMonitoring(true);
        // Start real-time updates
        const interval = setInterval(fetchPackets, 2000);
        return () => clearInterval(interval);
      }
    } catch (error) {
      console.error('Failed to start monitoring:', error);
    }
  };

  const stopMonitoring = async () => {
    try {
      const response = await fetch('/api/network/stop', { method: 'POST' });
      if (response.ok) {
        setIsMonitoring(false);
      }
    } catch (error) {
      console.error('Failed to stop monitoring:', error);
    }
  };

  const downloadPacketCapture = async () => {
    try {
      const response = await fetch('/api/network/download');
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `packet_capture_${new Date().toISOString().split('T')[0]}.pcap`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Download failed:', error);
    }
  };



  const getThreatBadge = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high': return 'bg-red-600/20 text-red-400 border-red-500/30';
      case 'medium': return 'bg-yellow-600/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-green-600/20 text-green-400 border-green-500/30';
      default: return 'bg-gray-600/20 text-gray-400 border-gray-500/30';
    }
  };

  const filteredPackets = packets.filter(packet => {
    if (filterProtocol !== 'all' && packet.protocol !== filterProtocol) return false;
    if (filterThreatLevel !== 'all' && packet.threat_level !== filterThreatLevel) return false;
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
          <h1 className="text-3xl font-bold text-white">Network Monitoring</h1>
          <p className="text-gray-400 mt-2">Real-time network traffic analysis and threat detection</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={downloadPacketCapture}
            className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Download className="w-5 h-5" />
            <span>Download Capture</span>
          </button>
          <button
            onClick={isMonitoring ? stopMonitoring : startMonitoring}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              isMonitoring
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isMonitoring ? (
              <>
                <Pause className="w-5 h-5" />
                <span>Stop Monitoring</span>
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                <span>Start Monitoring</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Activity className="w-8 h-8 text-blue-400" />
            <div>
              <p className="text-gray-400 text-sm">Total Packets</p>
              <p className="text-2xl font-bold text-white">
                {stats?.total_packets.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-8 h-8 text-red-400" />
            <div>
              <p className="text-gray-400 text-sm">Suspicious Packets</p>
              <p className="text-2xl font-bold text-white">
                {stats?.suspicious_packets.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-green-400" />
            <div>
              <p className="text-gray-400 text-sm">Active Connections</p>
              <p className="text-2xl font-bold text-white">
                {stats?.active_connections.toLocaleString() || 0}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Settings className="w-8 h-8 text-purple-400" />
            <div>
              <p className="text-gray-400 text-sm">Bandwidth Usage</p>
              <p className="text-2xl font-bold text-white">
                {stats?.bandwidth_utilization.toFixed(1) || 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Protocol Distribution */}
      {stats && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Protocol Distribution</h3>
          <div className="grid grid-cols-3 gap-6">
            {Object.entries(stats.protocols).map(([protocol, percentage]) => (
              <div key={protocol} className="text-center">
                <div className="w-20 h-20 mx-auto mb-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                  <span className="text-white font-bold text-lg">{percentage}%</span>
                </div>
                <p className="text-gray-300 font-medium">{protocol.toUpperCase()}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Packet Filters</h3>
        <div className="flex items-center space-x-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Protocol</label>
            <select
              value={filterProtocol}
              onChange={(e) => setFilterProtocol(e.target.value)}
              className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Protocols</option>
              <option value="TCP">TCP</option>
              <option value="UDP">UDP</option>
              <option value="ICMP">ICMP</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Threat Level</label>
            <select
              value={filterThreatLevel}
              onChange={(e) => setFilterThreatLevel(e.target.value)}
              className="bg-gray-700 border border-gray-600 text-white rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Levels</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
      </div>

      {/* Packets Table */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">Network Packets</h3>
          <p className="text-gray-400 text-sm">Real-time packet analysis and threat detection</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Source IP
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Destination IP
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Protocol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Length
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Threat Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {filteredPackets.map((packet) => (
                <tr key={packet.id} className="hover:bg-gray-700/30">
                  <td className="px-6 py-4 text-sm text-gray-300">
                    {new Date(packet.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-white font-mono">
                    {packet.source_ip}
                  </td>
                  <td className="px-6 py-4 text-sm text-white font-mono">
                    {packet.destination_ip}
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-blue-600/20 text-blue-400 text-xs rounded-full border border-blue-500/30">
                      {packet.protocol}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300">
                    {packet.length} bytes
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getThreatBadge(packet.threat_level)}`}>
                      {packet.threat_level}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setSelectedPacket(packet)}
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

      {/* Packet Details Modal */}
      {selectedPacket && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Packet Details</h3>
              <button
                onClick={() => setSelectedPacket(null)}
                className="text-gray-400 hover:text-gray-300"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300">Packet ID</label>
                  <p className="text-white font-mono">{selectedPacket.id}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Timestamp</label>
                  <p className="text-white">{new Date(selectedPacket.timestamp).toLocaleString()}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Source IP</label>
                  <p className="text-white font-mono">{selectedPacket.source_ip}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Destination IP</label>
                  <p className="text-white font-mono">{selectedPacket.destination_ip}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Protocol</label>
                  <p className="text-white">{selectedPacket.protocol}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Length</label>
                  <p className="text-white">{selectedPacket.length} bytes</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Flags</label>
                  <p className="text-white">{selectedPacket.flags}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300">Suspicious Score</label>
                  <p className="text-white">{selectedPacket.suspicious_score}%</p>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300">Threat Level</label>
                <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getThreatBadge(selectedPacket.threat_level)}`}>
                  {selectedPacket.threat_level}
                </span>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  onClick={() => setSelectedPacket(null)}
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

export default NetworkMonitoring;
