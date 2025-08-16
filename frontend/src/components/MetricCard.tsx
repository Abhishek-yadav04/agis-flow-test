import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { clsx } from 'clsx';

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  color: 'blue' | 'green' | 'purple' | 'yellow' | 'red';
  trend?: number;
  loading?: boolean;
}

const colorClasses = {
  blue: 'from-blue-600 to-blue-700 text-blue-200',
  green: 'from-green-600 to-green-700 text-green-200',
  purple: 'from-purple-600 to-purple-700 text-purple-200',
  yellow: 'from-yellow-600 to-yellow-700 text-yellow-200',
  red: 'from-red-600 to-red-700 text-red-200',
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
  trend,
  loading = false
}) => {
  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 animate-pulse">
        <div className="h-4 bg-gray-700 rounded w-3/4 mb-2"></div>
        <div className="h-8 bg-gray-700 rounded w-1/2 mb-2"></div>
        <div className="h-3 bg-gray-700 rounded w-2/3"></div>
      </div>
    );
  }

  return (
    <div className={clsx(
      'bg-gradient-to-br rounded-lg p-6 transition-all duration-300 hover:scale-105 hover:shadow-lg',
      colorClasses[color]
    )}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <h3 className="text-sm font-medium opacity-90">{title}</h3>
          <p className="text-3xl font-bold text-white mt-1">{value}</p>
          {subtitle && (
            <p className="text-xs opacity-75 mt-1">{subtitle}</p>
          )}
          {trend !== undefined && (
            <div className="flex items-center mt-2">
              {trend > 0 ? (
                <TrendingUp className="w-3 h-3 text-green-400 mr-1" />
              ) : (
                <TrendingDown className="w-3 h-3 text-red-400 mr-1" />
              )}
              <span className={clsx(
                'text-xs font-medium',
                trend > 0 ? 'text-green-400' : 'text-red-400'
              )}>
                {Math.abs(trend)}%
              </span>
            </div>
          )}
        </div>
        <div className="opacity-75">
          <Icon className="w-8 h-8" />
        </div>
      </div>
    </div>
  );
};