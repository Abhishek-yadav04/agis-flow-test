import { useState } from 'react';
import { useQuery } from 'react-query';
import { Brain, Users, TrendingUp, Play, Settings, Pause, BarChart3, Globe } from 'lucide-react';
import { federatedLearningAPI } from '../services/api';
import RealTimeChart from '../components/Charts/RealTimeChart';
import toast from 'react-hot-toast';

const FederatedLearning: React.FC = () => {
  const [isTraining, setIsTraining] = useState(false);
  const { data: flStatus } = useQuery(
    'flStatus',
    federatedLearningAPI.getStatus,
    { refetchInterval: 5000 }
  );

  const handleStartTraining = async () => {
    try {
      setIsTraining(true);
      await federatedLearningAPI.startTraining();
      toast.success('Federated learning training started');
    } catch (error) {
      toast.error('Failed to start training');
      setIsTraining(false);
    }
  };

  return (
    <div className="space-y-10">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-emerald-500 to-teal-600 bg-clip-text text-transparent flex items-center gap-3">
            Federated Learning Engine
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-600 text-white uppercase tracking-wide">Core</span>
          </h1>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Privacy-preserving distributed machine learning across untrusted domains
          </p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={handleStartTraining}
            disabled={isTraining}
            className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-lg shadow-md hover:shadow-lg hover:from-emerald-500 hover:to-teal-500 transition-all flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isTraining ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isTraining ? 'Stop Training' : 'Start Training'}</span>
          </button>
          <button className="px-5 py-2.5 bg-gray-800 text-white/90 rounded-lg hover:bg-gray-700 transition-colors flex items-center space-x-2 border border-gray-700/50">
            <Settings className="w-4 h-4" />
            <span>Configure</span>
          </button>
        </div>
      </div>

      {/* Training Status */}
  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Brain className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Current Round</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {flStatus?.data?.federated_learning?.current_round || 15}
              </p>
            </div>
          </div>
        </div>

  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Global Accuracy</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {flStatus?.data?.federated_learning?.global_accuracy || 94.2}%
              </p>
            </div>
          </div>
        </div>

  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <Users className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Active Clients</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {flStatus?.data?.federated_learning?.active_clients || 8}
              </p>
            </div>
          </div>
        </div>

  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
              <Globe className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Strategy</p>
              <p className="text-lg font-bold text-gray-900 dark:text-white">
                {flStatus?.data?.federated_learning?.strategy || 'FedAvg'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Training Progress & Accuracy Chart */}
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Training Progress
          </h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                <span>Round {flStatus?.data?.federated_learning?.current_round || 15} Progress</span>
                <span>78%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full transition-all duration-500" style={{ width: '78%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                <span>Model Convergence</span>
                <span>{flStatus?.data?.federated_learning?.convergence_rate * 100 || 92}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-green-600 h-2 rounded-full transition-all duration-500" style={{ width: `${flStatus?.data?.federated_learning?.convergence_rate * 100 || 92}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                <span>Privacy Budget</span>
                <span>0.1 ε</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div className="bg-purple-600 h-2 rounded-full transition-all duration-500" style={{ width: '10%' }}></div>
              </div>
            </div>
          </div>
        </div>

  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Accuracy Trend
            </h3>
            <BarChart3 className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-48">
            <RealTimeChart 
              data={[85, 87, 89, 91, 92, 93, 94, 94.2]} 
              label="Global Accuracy" 
              color="#10B981" 
              height={192}
            />
          </div>
        </div>
      </div>

      {/* Client Status */}
  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Client Status
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 dark:border-gray-700">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">Client ID</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">Location</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">Status</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">Accuracy</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-500 dark:text-gray-400">Last Update</th>
              </tr>
            </thead>
            <tbody>
              {[
                { id: 'client-001', location: 'New York', status: 'Active', accuracy: '95.1%', lastUpdate: '2 min ago' },
                { id: 'client-002', location: 'London', status: 'Active', accuracy: '93.8%', lastUpdate: '3 min ago' },
                { id: 'client-003', location: 'Tokyo', status: 'Training', accuracy: '94.5%', lastUpdate: '1 min ago' },
                { id: 'client-004', location: 'Sydney', status: 'Active', accuracy: '92.9%', lastUpdate: '4 min ago' },
              ].map((client) => (
                <tr key={client.id} className="border-b border-gray-100 dark:border-gray-700">
                  <td className="py-3 px-4 text-sm text-gray-900 dark:text-white font-medium">{client.id}</td>
                  <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{client.location}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      client.status === 'Active' 
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
                        : 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400'
                    }`}>
                      {client.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-900 dark:text-white">{client.accuracy}</td>
                  <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">{client.lastUpdate}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FederatedLearning;