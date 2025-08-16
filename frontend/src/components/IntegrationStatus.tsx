import React from 'react';
import { CheckCircle, AlertCircle, XCircle, Clock } from 'lucide-react';
import { clsx } from 'clsx';

interface Integration {
  status: string;
  [key: string]: any;
}

interface IntegrationStatusProps {
  integrations: Record<string, Integration>;
}

const statusIcons = {
  active: CheckCircle,
  connected: CheckCircle,
  monitoring: CheckCircle,
  online: CheckCircle,
  warning: AlertCircle,
  error: XCircle,
  offline: XCircle,
  connecting: Clock,
};

const statusColors = {
  active: 'text-green-400',
  connected: 'text-green-400',
  monitoring: 'text-green-400',
  online: 'text-green-400',
  warning: 'text-yellow-400',
  error: 'text-red-400',
  offline: 'text-red-400',
  connecting: 'text-blue-400',
};

export const IntegrationStatus: React.FC<IntegrationStatusProps> = ({ integrations }) => {
  const integrationList = Object.entries(integrations).map(([name, config]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    status: config.status || 'unknown',
    details: config
  }));

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Integration Status</h2>
      <div className="space-y-3">
        {integrationList.map((integration) => {
          const Icon = statusIcons[integration.status as keyof typeof statusIcons] || AlertCircle;
          const colorClass = statusColors[integration.status as keyof typeof statusColors] || 'text-gray-400';
          
          return (
            <div
              key={integration.name}
              className="flex items-center justify-between p-3 bg-gray-750 rounded-lg hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center space-x-3">
                <Icon className={clsx('w-4 h-4', colorClass)} />
                <div>
                  <p className="text-sm font-medium text-white">{integration.name}</p>
                  {integration.details.server_address && (
                    <p className="text-xs text-gray-400">{integration.details.server_address}</p>
                  )}
                  {integration.details.packets_per_second && (
                    <p className="text-xs text-gray-400">
                      {integration.details.packets_per_second} packets/sec
                    </p>
                  )}
                  {integration.details.rules_loaded && (
                    <p className="text-xs text-gray-400">
                      {integration.details.rules_loaded.toLocaleString()} rules loaded
                    </p>
                  )}
                </div>
              </div>
              <div className="text-right">
                <span className={clsx(
                  'px-2 py-1 text-xs font-medium rounded-full',
                  integration.status === 'active' || integration.status === 'connected' || 
                  integration.status === 'monitoring' || integration.status === 'online'
                    ? 'bg-green-100 text-green-800'
                    : integration.status === 'warning' || integration.status === 'connecting'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                )}>
                  {integration.status.toUpperCase()}
                </span>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex justify-between text-sm">
          <span className="text-gray-400">Total Integrations</span>
          <span className="text-white font-medium">{integrationList.length}</span>
        </div>
        <div className="flex justify-between text-sm mt-1">
          <span className="text-gray-400">Healthy</span>
          <span className="text-green-400 font-medium">
            {integrationList.filter(i => 
              ['active', 'connected', 'monitoring', 'online'].includes(i.status)
            ).length}
          </span>
        </div>
      </div>
    </div>
  );
};