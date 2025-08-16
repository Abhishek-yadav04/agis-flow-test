import React from 'react';
import { clsx } from 'clsx';

interface ChartContainerProps {
  title: string;
  children: React.ReactNode;
  height?: string;
  className?: string;
  loading?: boolean;
}

export const ChartContainer: React.FC<ChartContainerProps> = ({
  title,
  children,
  height = '300px',
  className,
  loading = false
}) => {
  return (
    <div className={clsx('bg-gray-800 rounded-lg p-6', className)}>
      <h2 className="text-xl font-semibold text-white mb-4">{title}</h2>
      <div style={{ height }} className="relative">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};