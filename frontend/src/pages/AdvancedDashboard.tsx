import React, { useEffect, useState } from 'react';
// DEPRECATED: Page archived; features merged into main Dashboard via unified /api/dashboard endpoint.
import api from '../services/api';
import { 
  Shield, 
  Activity, 
  AlertTriangle, 
  Brain, 
  Network, 
  Zap,
  Target,
  Eye,
  Cpu
} from 'lucide-react';

export const AdvancedDashboard: React.FC = () => {
  const [flIdsData, setFlIdsData] = useState<any>(null);
  const [features, setFeatures] = useState<any>(null);
  const [threats, setThreats] = useState<any[]>([]);
  const [attackSimulation, setAttackSimulation] = useState(false);
  const [realTimeMode, setRealTimeMode] = useState(true);

  useEffect(() => {
    loadFlIdsData();
    const interval = setInterval(loadFlIdsData, realTimeMode ? 1000 : 5000);
    return () => clearInterval(interval);
  }, [realTimeMode]);

  const loadFlIdsData = async () => {
    try {
      const [statusData, featuresData, threatsData] = await Promise.all([
        api.get('/fl-ids/metrics/real-time'),
        api.get('/fl-ids/features'),
        api.get('/fl-ids/threats/live')
      ]);
      
      setFlIdsData(statusData.data);
      setFeatures(featuresData.data);
      setThreats(threatsData.data?.threats || []);
    } catch (error) {
      console.error('Failed to load FL-IDS data:', error);
    }
  };

  const toggleAttackSimulation = async () => {
    try {
      await api.post(`/fl-ids/simulation/toggle?enabled=${!attackSimulation}`);
      setAttackSimulation(!attackSimulation);
    } catch (error) {
      console.error('Failed to toggle attack simulation:', error);
    }
  };

  const simulateAttack = async (attackType: string) => {
    try {
      await api.post(`/fl-ids/simulation/attack/${attackType}`);
    } catch (error) {
      console.error('Failed to simulate attack:', error);
    }
  };

  if (!flIdsData) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const coreFeatures = features ? Object.entries(features.features).slice(0, 10) : [];
  const securityFeatures = features ? Object.entries(features.features).slice(10, 30) : [];
  const enterpriseFeatures = features ? Object.entries(features.features).slice(30, 50) : [];

  return (
    <div className="space-y-6">
      {/* Header with Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center">
            <Brain className="w-8 h-8 mr-3 text-blue-500" />
            Advanced FL-IDS Dashboard
          </h1>
          <p className="text-gray-400">Real-time Federated Learning Intrusion Detection System</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setRealTimeMode(!realTimeMode)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              realTimeMode ? 'bg-green-600 text-white' : 'bg-gray-600 text-gray-300'
            }`}
          >
            <Activity className="w-4 h-4 mr-2 inline" />
            Real-time: {realTimeMode ? 'ON' : 'OFF'}
          </button>
          <button
            onClick={toggleAttackSimulation}
            className={`px-4 py-2 rounded-lg transition-colors ${
              attackSimulation ? 'bg-red-600 text-white' : 'bg-gray-600 text-gray-300'
            }`}
          >
            <Target className="w-4 h-4 mr-2 inline" />
            Attack Simulation: {attackSimulation ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium opacity-90">Engine Status</h3>
              <p className="text-2xl font-bold">{flIdsData.engine_status?.toUpperCase()}</p>
              <p className="text-xs opacity-75">{flIdsData.features_active}/50 Features Active</p>
            </div>
            <Cpu className="w-8 h-8 opacity-75" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium opacity-90">Threats Detected</h3>
              <p className="text-2xl font-bold">{flIdsData.metrics?.threats_detected || 0}</p>
              <p className="text-xs opacity-75">Accuracy: {(flIdsData.metrics?.accuracy * 100 || 0).toFixed(1)}%</p>
            </div>
            <Shield className="w-8 h-8 opacity-75" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium opacity-90">FL Accuracy</h3>
              <p className="text-2xl font-bold">{(flIdsData.fl_status?.global_accuracy * 100 || 0).toFixed(1)}%</p>
              <p className="text-xs opacity-75">Round {flIdsData.fl_status?.current_round || 0}</p>
            </div>
            <Brain className="w-8 h-8 opacity-75" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-yellow-600 to-yellow-700 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium opacity-90">Throughput</h3>
              <p className="text-2xl font-bold">{Math.round(flIdsData.metrics?.throughput_pps || 0)}</p>
              <p className="text-xs opacity-75">Packets/Second</p>
            </div>
            <Zap className="w-8 h-8 opacity-75" />
          </div>
        </div>

        <div className="bg-gradient-to-br from-red-600 to-red-700 rounded-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium opacity-90">Latency</h3>
              <p className="text-2xl font-bold">{flIdsData.metrics?.latency_ms?.toFixed(1) || '0.0'}</p>
              <p className="text-xs opacity-75">Milliseconds</p>
            </div>
            <Activity className="w-8 h-8 opacity-75" />
          </div>
        </div>
      </div>

      {/* Feature Status Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Core FL Features */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Brain className="w-5 h-5 mr-2 text-blue-500" />
            Core FL Features (1-10)
          </h2>
          <div className="space-y-3">
            {coreFeatures.map(([id, feature]: [string, any]) => (
              <div key={id} className="flex items-center justify-between p-3 bg-gray-750 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">{feature.name}</p>
                  {feature.accuracy && (
                    <p className="text-xs text-green-400">Accuracy: {(feature.accuracy * 100).toFixed(1)}%</p>
                  )}
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  feature.status === 'active' ? 'bg-green-500' : 'bg-red-500'
                }`} />
              </div>
            ))}
          </div>
        </div>

        {/* Security Features */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-green-500" />
            Security Features (11-30)
          </h2>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {securityFeatures.map(([id, feature]: [string, any]) => (
              <div key={id} className="flex items-center justify-between p-3 bg-gray-750 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">{feature.name}</p>
                  {feature.detection_rate && (
                    <p className="text-xs text-blue-400">Detection: {(feature.detection_rate * 100).toFixed(1)}%</p>
                  )}
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  feature.status === 'active' ? 'bg-green-500' : 'bg-red-500'
                }`} />
              </div>
            ))}
          </div>
        </div>

        {/* Enterprise Features */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Network className="w-5 h-5 mr-2 text-purple-500" />
            Enterprise Features (31-50)
          </h2>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {enterpriseFeatures.map(([id, feature]: [string, any]) => (
              <div key={id} className="flex items-center justify-between p-3 bg-gray-750 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">{feature.name}</p>
                  {feature.nodes && (
                    <p className="text-xs text-yellow-400">Nodes: {feature.nodes}</p>
                  )}
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  feature.status === 'active' ? 'bg-green-500' : 'bg-red-500'
                }`} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Live Threats */}
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2 text-red-500" />
          Live Threat Detection
        </h2>
        {threats.length > 0 ? (
          <div className="space-y-3 max-h-60 overflow-y-auto">
            {threats.slice(0, 10).map((threat, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-red-900/20 border border-red-500/30 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">
                    {threat.type || threat.attack_type || 'Unknown Threat'}
                  </p>
                  <p className="text-xs text-gray-400">
                    {threat.source_ip || threat.src_ip} → {threat.destination_ip || threat.dst_ip}
                  </p>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                    threat.severity === 'critical' ? 'bg-red-100 text-red-800' :
                    threat.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {threat.severity?.toUpperCase() || 'MEDIUM'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Eye className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400">No threats detected</p>
            <p className="text-sm text-gray-500 mt-1">System is secure</p>
          </div>
        )}
      </div>

      {/* Attack Simulation Controls */}
      {attackSimulation && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-red-500" />
            Attack Simulation Controls
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {['port_scan', 'brute_force', 'ddos', 'malware', 'data_exfiltration'].map(attackType => (
              <button
                key={attackType}
                onClick={() => simulateAttack(attackType)}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm"
              >
                {attackType.replace('_', ' ').toUpperCase()}
              </button>
            ))}
          </div>
          <p className="text-sm text-red-300 mt-3">
            ⚠️ Attack simulation is active. Simulated attacks will be generated for testing purposes.
          </p>
        </div>
      )}
    </div>
  );
};