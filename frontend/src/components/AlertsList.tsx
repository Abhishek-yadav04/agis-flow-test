import React from 'react';
import { Alert } from '@/types';
import { AlertTriangle, Info, AlertCircle, XCircle, Clock } from 'lucide-react';
import { clsx } from 'clsx';
import { formatDistanceToNow } from 'date-fns';

interface AlertsListProps {
  alerts: Alert[];
  limit?: number;
}

const severityIcons = {
  LOW: Info,
  MEDIUM: AlertCircle,
  HIGH: AlertTriangle,
  CRITICAL: XCircle,
};

const severityColors = {
  LOW: 'text-blue-400',
  MEDIUM: 'text-yellow-400',
  HIGH: 'text-orange-400',
  CRITICAL: 'text-red-400',
};

export const AlertsList: React.FC<AlertsListProps> = ({ alerts, limit = 10 }) => {
  const displayAlerts = alerts.slice(0, limit);

  if (displayAlerts.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Recent Alerts</h2>
        <div className="text-center py-8">
          <Info className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No alerts at this time</p>
          <p className="text-sm text-gray-500 mt-1">System is operating normally</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold text-white mb-4">Recent Alerts</h2>
      <div className="space-y-3 max-h-80 overflow-y-auto">
        {displayAlerts.map((alert) => {
          const Icon = severityIcons[alert.severity];
          return (
            <div
              key={alert.id}
              className={clsx(
                'flex items-start space-x-3 p-3 rounded-lg transition-colors',
                alert.acknowledged ? 'bg-gray-700 opacity-60' : 'bg-gray-750 hover:bg-gray-700'
              )}
            >
              <Icon className={clsx('w-4 h-4 mt-0.5 flex-shrink-0', severityColors[alert.severity])} />
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-white truncate">
                    {alert.message}
                  </p>
                  <span className={clsx(
                    'px-2 py-1 text-xs font-medium rounded-full flex-shrink-0 ml-2',
                    alert.severity === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                    alert.severity === 'HIGH' ? 'bg-orange-100 text-orange-800' :
                    alert.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  )}>
                    {alert.severity}
                  </span>
                </div>
                <div className="flex items-center mt-1 text-xs text-gray-400">
                  <Clock className="w-3 h-3 mr-1" />
                  <span>{formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true })}</span>
                  <span className="mx-2">•</span>
                  <span>{alert.source}</span>
                  {alert.acknowledged && (
                    <>
                      <span className="mx-2">•</span>
                      <span className="text-green-400">Acknowledged</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      {alerts.length > limit && (
        <div className="mt-4 text-center">
          <button className="text-blue-400 hover:text-blue-300 text-sm font-medium">
            View all {alerts.length} alerts
          </button>
        </div>
      )}
    </div>
  );
};