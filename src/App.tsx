import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import MainLayout from './components/Layout/MainLayout';
import Dashboard from './pages/Dashboard';
import FederatedLearning from './pages/FederatedLearning';
import Security from './pages/Security';
import Network from './pages/Network';
import Datasets from './pages/Datasets';
import Settings from './pages/Settings';
import Research from './pages/Research';
import { useThemeStore } from './stores/themeStore';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 2,
      staleTime: 5000,
      refetchInterval: 10000,
    },
  },
});

function App() {
  const { isDark } = useThemeStore();

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="federated-learning" element={<FederatedLearning />} />
            <Route path="security" element={<Security />} />
            <Route path="network" element={<Network />} />
            <Route path="datasets" element={<Datasets />} />
            <Route path="research" element={<Research />} />
            <Route path="settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Route>
        </Routes>

        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: isDark ? 'hsl(var(--card))' : 'hsl(var(--background))',
              color: 'hsl(var(--foreground))',
              border: '1px solid hsl(var(--border))',
            },
          }}
        />
      </Router>
    </QueryClientProvider>
  );
}

export default App;