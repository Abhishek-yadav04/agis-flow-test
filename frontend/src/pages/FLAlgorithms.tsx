import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, Users, Shield, BarChart3, Play, Pause, Settings } from 'lucide-react';

interface FLAlgorithm {
  name: string;
  category: string;
  description: string;
  implementation_status: string;
  performance_metrics: {
    convergence_rate: number;
    communication_efficiency: number;
    privacy_preservation: number;
  };
  use_cases: string[];
}

const FLAlgorithms: React.FC = () => {
  const [algorithms, setAlgorithms] = useState<FLAlgorithm[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<FLAlgorithm | null>(null);
  const [activeTraining, setActiveTraining] = useState<string | null>(null);

  useEffect(() => {
    fetchAlgorithms();
  }, []);

  const fetchAlgorithms = async () => {
    try {
      const response = await fetch('/api/research/enterprise/research-algorithms');
      if (response.ok) {
        const data = await response.json();
        setAlgorithms(data.algorithms || []);
      }
    } catch (error) {
      console.error('Failed to fetch algorithms:', error);
      // Fallback data for demo
      setAlgorithms([
        {
          name: "FedAvg",
          category: "Aggregation",
          description: "Federated Averaging - The foundational FL algorithm that averages model parameters across clients",
          implementation_status: "PRODUCTION",
          performance_metrics: {
            convergence_rate: 0.87,
            communication_efficiency: 0.88,
            privacy_preservation: 0.80
          },
          use_cases: ["Base FL Training", "Model Aggregation", "Client Coordination"]
        },
        {
          name: "FedProx",
          category: "Optimization",
          description: "Federated Proximal Optimization for handling heterogeneous data distributions",
          implementation_status: "PRODUCTION",
          performance_metrics: {
            convergence_rate: 0.89,
            communication_efficiency: 0.92,
            privacy_preservation: 0.85
          },
          use_cases: ["IDS Model Training", "Anomaly Detection", "Threat Classification"]
        },
        {
          name: "FedNova",
          category: "Normalization",
          description: "Federated Learning with Normalized Averaging for improved convergence",
          implementation_status: "RESEARCH",
          performance_metrics: {
            convergence_rate: 0.91,
            communication_efficiency: 0.89,
            privacy_preservation: 0.87
          },
          use_cases: ["Advanced FL", "Research Projects", "Experimental Deployments"]
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const startTraining = async (algorithmName: string) => {
    setActiveTraining(algorithmName);
    // Simulate training start
    setTimeout(() => {
      setActiveTraining(null);
    }, 3000);
  };



  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PRODUCTION': return 'bg-green-600/20 text-green-400 border-green-500/30';
      case 'RESEARCH': return 'bg-yellow-600/20 text-yellow-400 border-yellow-500/30';
      case 'PLANNING': return 'bg-blue-600/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-600/20 text-gray-400 border-gray-500/30';
    }
  };

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
          <h1 className="text-3xl font-bold text-white">Federated Learning Algorithms</h1>
          <p className="text-gray-400 mt-2">Advanced FL algorithms for enterprise IDS applications</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
            <Settings className="w-5 h-5" />
            <span>Configure</span>
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Brain className="w-8 h-8 text-blue-400" />
            <div>
              <p className="text-gray-400 text-sm">Total Algorithms</p>
              <p className="text-2xl font-bold text-white">{algorithms.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-8 h-8 text-green-400" />
            <div>
              <p className="text-gray-400 text-sm">Production Ready</p>
              <p className="text-2xl font-bold text-white">
                {algorithms.filter(alg => alg.implementation_status === 'PRODUCTION').length}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Users className="w-8 h-8 text-purple-400" />
            <div>
              <p className="text-gray-400 text-sm">Active Training</p>
              <p className="text-2xl font-bold text-white">
                {activeTraining ? 1 : 0}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-orange-400" />
            <div>
              <p className="text-gray-400 text-sm">Avg Privacy Score</p>
              <p className="text-2xl font-bold text-white">
                {Math.round(algorithms.reduce((sum, alg) => sum + alg.performance_metrics.privacy_preservation, 0) / algorithms.length * 100)}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Algorithms Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {algorithms.map((algorithm) => (
          <div key={algorithm.name} className="bg-gray-800 rounded-lg border border-gray-700 p-6 hover:border-blue-500/50 transition-colors">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-semibold text-white mb-2">{algorithm.name}</h3>
                <span className={`px-3 py-1 text-xs font-medium rounded-full border ${getStatusBadge(algorithm.implementation_status)}`}>
                  {algorithm.implementation_status}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setSelectedAlgorithm(algorithm)}
                  className="p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-600/20 rounded-lg transition-colors"
                  title="View Details"
                >
                  <BarChart3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => startTraining(algorithm.name)}
                  disabled={activeTraining === algorithm.name}
                  className={`p-2 rounded-lg transition-colors ${
                    activeTraining === algorithm.name
                      ? 'bg-yellow-600/20 text-yellow-400'
                      : 'text-green-400 hover:text-green-300 hover:bg-green-600/20'
                  }`}
                  title={activeTraining === algorithm.name ? 'Training...' : 'Start Training'}
                >
                  {activeTraining === algorithm.name ? (
                    <Pause className="w-4 h-4" />
                  ) : (
                    <Play className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            <p className="text-gray-300 text-sm mb-4">{algorithm.description}</p>

            <div className="mb-4">
              <p className="text-gray-400 text-xs uppercase tracking-wider mb-2">Category</p>
              <p className="text-white text-sm">{algorithm.category}</p>
            </div>

            <div className="mb-4">
              <p className="text-gray-400 text-xs uppercase tracking-wider mb-2">Performance Metrics</p>
              <div className="grid grid-cols-3 gap-3">
                <div className="text-center">
                  <p className="text-xs text-gray-400">Convergence</p>
                  <p className="text-sm font-medium text-green-400">
                    {(algorithm.performance_metrics.convergence_rate * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-400">Efficiency</p>
                  <p className="text-sm font-medium text-blue-400">
                    {(algorithm.performance_metrics.communication_efficiency * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-xs text-gray-400">Privacy</p>
                  <p className="text-sm font-medium text-purple-400">
                    {(algorithm.performance_metrics.privacy_preservation * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>

            <div>
              <p className="text-gray-400 text-xs uppercase tracking-wider mb-2">Use Cases</p>
              <div className="flex flex-wrap gap-2">
                {algorithm.use_cases.map((useCase, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded-full"
                  >
                    {useCase}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Algorithm Details Modal */}
      {selectedAlgorithm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Algorithm Details</h3>
              <button
                onClick={() => setSelectedAlgorithm(null)}
                className="text-gray-400 hover:text-gray-300"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300">Name</label>
                <p className="text-white text-lg font-semibold">{selectedAlgorithm.name}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300">Category</label>
                <p className="text-white">{selectedAlgorithm.category}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300">Description</label>
                <p className="text-white">{selectedAlgorithm.description}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300">Implementation Status</label>
                <span className={`px-3 py-1 text-sm font-medium rounded-full border ${getStatusBadge(selectedAlgorithm.implementation_status)}`}>
                  {selectedAlgorithm.implementation_status}
                </span>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300">Performance Metrics</label>
                <div className="grid grid-cols-3 gap-4 mt-2">
                  <div className="bg-gray-700 rounded-lg p-3 text-center">
                    <p className="text-xs text-gray-400">Convergence Rate</p>
                    <p className="text-lg font-bold text-green-400">
                      {(selectedAlgorithm.performance_metrics.convergence_rate * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-700 rounded-lg p-3 text-center">
                    <p className="text-xs text-gray-400">Communication Efficiency</p>
                    <p className="text-lg font-bold text-blue-400">
                      {(selectedAlgorithm.performance_metrics.communication_efficiency * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-gray-700 rounded-lg p-3 text-center">
                    <p className="text-xs text-gray-400">Privacy Preservation</p>
                    <p className="text-lg font-bold text-purple-400">
                      {(selectedAlgorithm.performance_metrics.privacy_preservation * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300">Use Cases</label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedAlgorithm.use_cases.map((useCase, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-600/20 text-blue-400 text-sm rounded-full border border-blue-500/30"
                    >
                      {useCase}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="flex space-x-3 pt-4">
                <button
                  onClick={() => startTraining(selectedAlgorithm.name)}
                  disabled={activeTraining === selectedAlgorithm.name}
                  className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center justify-center space-x-2"
                >
                  {activeTraining === selectedAlgorithm.name ? (
                    <>
                      <Pause className="w-4 h-4" />
                      <span>Training...</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      <span>Start Training</span>
                    </>
                  )}
                </button>
                <button
                  onClick={() => setSelectedAlgorithm(null)}
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

export default FLAlgorithms;
