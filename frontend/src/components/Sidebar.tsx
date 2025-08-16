import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Network, 
  Shield, 
  Database, 
  Settings, 
  Brain,
  Activity,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const navItems = [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/federated-learning', icon: Brain, label: 'Federated Learning' },
    { path: '/security', icon: Shield, label: 'Security Center' },
    { path: '/network', icon: Network, label: 'Network Monitor' },
    { path: '/datasets', icon: Database, label: 'Datasets' },
    { path: '/research', icon: Activity, label: 'Research Lab' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className={`fixed left-0 top-0 h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 z-30 ${
      isOpen ? 'w-64' : 'w-16'
    }`}>
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        {isOpen && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-gray-900 dark:text-white tracking-tight">AgisFL Enterprise</span>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          {isOpen ? (
            <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          )}
        </button>
      </div>

      <nav className="mt-6 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `group flex items-center px-4 py-2.5 text-sm font-medium rounded-lg mx-2 transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <div
                  className={`w-9 h-9 flex items-center justify-center rounded-md mr-2 transition-colors ${
                    isActive ? 'bg-white/10' : 'bg-gray-100 dark:bg-gray-700 group-hover:bg-white/20'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                </div>
                {isOpen && (
                  <span className="ml-1 font-medium tracking-wide">{item.label}</span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {isOpen && (
        <div className="absolute bottom-4 left-4 right-4 text-xs text-gray-500 dark:text-gray-400 space-y-2">
          <div className="bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 rounded-xl p-4 text-white shadow-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="font-semibold tracking-wide">AgisFL</span>
              <span className="text-white/80">v3.1.1</span>
            </div>
            <div className="flex items-center text-[10px] uppercase tracking-wider text-white/70">College Project Mode</div>
          </div>
          <div className="px-1 leading-relaxed hidden xl:block">
            <span className="font-medium">Tip:</span> Toggle the sidebar to maximize workspace.
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;