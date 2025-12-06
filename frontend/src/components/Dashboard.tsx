import { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Box, Search, AlertTriangle, TrendingUp, Activity, AlertCircle } from 'lucide-react';
import './Dashboard.css';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/dashboard');
      setDashboardData(response.data);
      setLoading(false);
    } catch (err: any) {
      console.error('Ошибка загрузки данных дашборда:', err);
      setError(`Ошибка загрузки: ${err.message || 'Проверьте подключение к backend'}`);
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка дашборда...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!dashboardData) return null;

  const { summary, methods, risk_levels, quality_grades, top_defect_objects, top_risk_objects, yearly_trend, pipelines } = dashboardData;

  // Проверка на наличие данных
  if (!methods || !risk_levels || !quality_grades) return <div className="loading">Обработка данных...</div>;

  // Данные для графиков
  const riskData = Object.entries(risk_levels).map(([key, value]: [string, any]) => ({
    name: key === 'normal' ? 'Низкий' : key === 'medium' ? 'Средний' : 'Высокий',
    value: value,
    color: key === 'normal' ? '#10b981' : key === 'medium' ? '#f59e0b' : '#ef4444'
  }));

  const methodsData = Object.entries(methods).map(([key, value]: [string, any]) => ({
    name: key,
    count: value
  })).sort((a, b) => b.count - a.count);

  const qualityData = Object.entries(quality_grades).map(([key, value]: [string, any]) => ({
    name: key,
    count: value
  }));

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2 className="dashboard-title">
          <Activity className="icon-title" /> Панель управления
        </h2>
        <span className="last-updated">Обновлено: {new Date().toLocaleDateString()}</span>
      </div>

      {/* Статистика */}
      <div className="stats-grid">
        <div className="stat-card card">
          <div className="stat-icon-wrapper primary">
            <Box className="stat-icon" />
          </div>
          <div className="stat-content">
            <h3>{summary.total_objects}</h3>
            <p>Всего объектов</p>
          </div>
        </div>

        <div className="stat-card card">
          <div className="stat-icon-wrapper success">
            <Search className="stat-icon" />
          </div>
          <div className="stat-content">
            <h3>{summary.total_inspections}</h3>
            <p>Обследований</p>
          </div>
        </div>

        <div className="stat-card card">
          <div className="stat-icon-wrapper danger">
            <AlertTriangle className="stat-icon" />
          </div>
          <div className="stat-content">
            <h3>{summary.total_defects}</h3>
            <p>Дефектов найдено</p>
          </div>
        </div>

        <div className="stat-card card">
          <div className="stat-icon-wrapper warning">
            <TrendingUp className="stat-icon" />
          </div>
          <div className="stat-content">
            <h3>{summary.defect_rate}%</h3>
            <p>Процент дефектности</p>
          </div>
        </div>
      </div>

      {/* Графики */}
      <div className="charts-grid">
        <div className="chart-card card">
          <h3>Распределение по критичности</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card card">
          <h3>Методы контроля</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={methodsData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} />
              <Tooltip
                cursor={{ fill: '#f1f5f9' }}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Bar dataKey="count" fill="#4f46e5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card card">
          <h3>Динамика обследований</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={yearly_trend}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="year" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Legend />
              <Line type="monotone" dataKey="inspections" stroke="#4f46e5" strokeWidth={3} dot={{ r: 4 }} name="Обследований" />
              <Line type="monotone" dataKey="defects" stroke="#ef4444" strokeWidth={3} dot={{ r: 4 }} name="Дефектов" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card card">
          <h3>Оценка качества</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={qualityData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
              <XAxis type="number" axisLine={false} tickLine={false} />
              <YAxis dataKey="name" type="category" width={100} axisLine={false} tickLine={false} />
              <Tooltip
                cursor={{ fill: '#f1f5f9' }}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Bar dataKey="count" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Трубопроводы */}
      <div className="section">
        <h3>Статистика по трубопроводам</h3>
        <div className="pipelines-grid">
          {pipelines.map((pipeline: any) => (
            <div key={pipeline.pipeline_id} className="pipeline-card card">
              <div className="pipeline-header">
                <h4>{pipeline.name}</h4>
                <div className={`status-badge ${pipeline.high_risk_count > 0 ? 'danger' : 'success'}`}>
                  {pipeline.high_risk_count > 0 ? 'Требует внимания' : 'В норме'}
                </div>
              </div>
              <div className="pipeline-stats">
                <div className="pipeline-stat">
                  <span className="label">Объектов</span>
                  <span className="value">{pipeline.objects_count}</span>
                </div>
                <div className="pipeline-stat">
                  <span className="label">Обследований</span>
                  <span className="value">{pipeline.inspections_count}</span>
                </div>
                <div className="pipeline-stat">
                  <span className="label">Дефектов</span>
                  <span className="value">{pipeline.defects_count}</span>
                </div>
                <div className="pipeline-stat">
                  <span className="label">Высокий риск</span>
                  <span className="value danger">{pipeline.high_risk_count}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Топ объекты */}
      <div className="tables-grid">
        <div className="table-card card">
          <h3>Топ-5 объектов с дефектами</h3>
          <div className="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Объект</th>
                  <th>Трубопровод</th>
                  <th>Дефектов</th>
                </tr>
              </thead>
              <tbody>
                {top_defect_objects.map((obj: any) => (
                  <tr key={obj.object_id}>
                    <td>
                      <div className="object-cell">
                        <AlertCircle size={16} className="text-danger" />
                        {obj.object_name}
                      </div>
                    </td>
                    <td>{obj.pipeline_id}</td>
                    <td><span className="badge danger">{obj.count}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="table-card card">
          <h3>Топ-5 объектов высокого риска</h3>
          <div className="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Объект</th>
                  <th>Трубопровод</th>
                  <th>Критичных</th>
                </tr>
              </thead>
              <tbody>
                {top_risk_objects.map((obj: any) => (
                  <tr key={obj.object_id}>
                    <td>
                      <div className="object-cell">
                        <AlertTriangle size={16} className="text-danger" />
                        {obj.object_name}
                      </div>
                    </td>
                    <td>{obj.pipeline_id}</td>
                    <td><span className="badge danger">{obj.count}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
