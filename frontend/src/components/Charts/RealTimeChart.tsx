import { Line } from 'react-chartjs-2';
import { useThemeStore } from '../../stores/themeStore';

interface RealTimeChartProps {
  data: number[];
  label: string;
  color?: string;
  height?: number;
}

const RealTimeChart = ({ data, label, color = '#3B82F6', height = 200 }: RealTimeChartProps) => {
  const { isDark } = useThemeStore();

  const chartData = {
    labels: Array.from({ length: data.length }, (_, i) => i),
    datasets: [
      {
        label,
        data,
        borderColor: color,
        backgroundColor: `${color}20`,
        fill: true,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 4,
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        backgroundColor: isDark ? '#374151' : '#ffffff',
        titleColor: isDark ? '#ffffff' : '#000000',
        bodyColor: isDark ? '#ffffff' : '#000000',
        borderColor: isDark ? '#6B7280' : '#E5E7EB',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        display: false,
      },
      y: {
        display: false,
        beginAtZero: true,
      },
    },
    elements: {
      point: {
        radius: 0,
      },
    },
    interaction: {
      intersect: false,
    },
  };

  return (
    <div style={{ height }}>
      <Line data={chartData} options={options} />
    </div>
  );
};

export default RealTimeChart;