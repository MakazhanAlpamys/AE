import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import MapView from './components/MapView';
import ObjectsList from './components/ObjectsList';
import ObjectDetail from './components/ObjectDetail';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Проверка доступности API
    fetch('/api/dashboard')
      .then(() => setIsLoading(false))
      .catch(() => {
        console.error('Backend API недоступен');
        setIsLoading(false);
      });
  }, []);

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
        <header className="app-header">
          <div className="header-content">
            <h1 className="logo">IntegrityOS</h1>
            <p className="subtitle">Система мониторинга трубопроводов</p>
          </div>
          <nav className="main-nav">
            <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
              Дашборд
            </NavLink>
            <NavLink to="/map" className={({ isActive }) => isActive ? 'active' : ''}>
              Карта
            </NavLink>
            <NavLink to="/objects" className={({ isActive }) => isActive ? 'active' : ''}>
              Объекты
            </NavLink>
            <a href="/api/report" target="_blank" rel="noopener noreferrer">
              Отчеты
            </a>
          </nav>
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
