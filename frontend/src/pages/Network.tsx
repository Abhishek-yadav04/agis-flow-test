import React from 'react';
import { Network as NetworkIcon, Activity, Wifi, Globe } from 'lucide-react';

const Network: React.FC = () => {
  return (
    <div className="space-y-10">
      <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-transparent">
        Network Monitor
      </h1>

  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <NetworkIcon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Active Connections</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">234</p>
            </div>
          </div>
        </div>

  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-green-100 dark:bg-green-900/20 rounded-lg">
              <Activity className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Bandwidth Usage</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">78.5%</p>
            </div>
          </div>
        </div>

  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <Wifi className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Packets Analyzed</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">15,420</p>
            </div>
          </div>
        </div>

  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
              <Globe className="w-6 h-6 text-orange-600 dark:text-orange-400" />
            </div>
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Latency</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">12.3ms</p>
            </div>
          </div>
        </div>
      </div>

  <div className="bg-white/80 dark:bg-gray-800/70 backdrop-blur rounded-2xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Network Traffic Analysis
        </h3>
        <div className="h-64 flex items-center justify-center text-gray-500 dark:text-gray-400">
          Network traffic visualization would go here
        </div>
      </div>
    </div>
  );
};

export default Network;