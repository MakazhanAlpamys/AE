import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, Map, Box, Sun, Moon } from 'lucide-react';
import Dashboard from './components/Dashboard';
import MapView from './components/MapView';
import ObjectsList from './components/ObjectsList';
import ObjectDetail from './components/ObjectDetail';
import Logo from './components/Logo';
import ReportsMenu from './components/ReportsMenu';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  useEffect(() => {
    // Load theme from local storage
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute('data-theme', savedTheme);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setTheme('dark');
      document.documentElement.setAttribute('data-theme', 'dark');
    }

    // Check API availability
    fetch('/api/dashboard')
      .then(() => setIsLoading(false))
      .catch(() => {
        console.error('Backend API недоступен');
        setIsLoading(false);
      });
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Загрузка IntegrityOS...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="app">
        <header className="app-header glass">
          <div className="header-content">
            <Logo />
          </div>

          <div className="header-actions">
            <nav className="main-nav">
              <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''} title="Дашборд">
                <LayoutDashboard size={20} />
                <span>Дашборд</span>
              </NavLink>
              <NavLink to="/map" className={({ isActive }) => isActive ? 'active' : ''} title="Карта">
                <Map size={20} />
                <span>Карта</span>
              </NavLink>
              <NavLink to="/objects" className={({ isActive }) => isActive ? 'active' : ''} title="Объекты">
                <Box size={20} />
                <span>Объекты</span>
              </NavLink>
            </nav>

            <div className="header-right-actions">
              <ReportsMenu />
              <button onClick={toggleTheme} className="theme-toggle" title="Переключить тему">
                {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
              </button>
            </div>
          </div>
        </header>

        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/map" element={<MapView />} />
            <Route path="/objects" element={<ObjectsList />} />
            <Route path="/objects/:objectId" element={<ObjectDetail />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>© 2025 IntegrityOS | Все данные синтетические</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
