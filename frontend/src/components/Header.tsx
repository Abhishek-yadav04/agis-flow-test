import React from 'react';
import { Menu, Sun, Moon, Bell, User } from 'lucide-react';
import { useThemeStore } from '../stores/themeStore';

interface HeaderProps {
  onMenuClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const { isDark, toggleTheme } = useThemeStore();

  return (
  <header className="backdrop-blur bg-white/80 dark:bg-gray-800/70 border-b border-gray-200 dark:border-gray-700 px-6 py-3 sticky top-0 z-20">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onMenuClick}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors lg:hidden"
          >
            <Menu className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
          
          <div className="leading-tight">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
              Federated Learning IDS
              <span className="px-2 py-0.5 text-[10px] rounded-full bg-blue-600 text-white font-medium">LIVE</span>
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Real-time threat detection & privacy-preserving ML
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 bg-gradient-to-r from-green-500 to-emerald-600 px-3 py-1.5 rounded-full shadow text-white">
            <div className="w-2 h-2 bg-white rounded-full animate-ping"></div>
            <span className="text-xs font-medium uppercase tracking-wide">System Active</span>
          </div>

          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            {isDark ? (
              <Sun className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            ) : (
              <Moon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            )}
          </button>

          <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative">
            <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
          </button>

          <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <User className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;