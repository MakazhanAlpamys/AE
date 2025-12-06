import { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
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
    color: key === 'normal' ? '#2ecc71' : key === 'medium' ? '#f39c12' : '#e74c3c'
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
      <h2 className="dashboard-title">📊 Панель управления</h2>

      {/* Статистика */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{background: 'linear-gradient(135deg, #667eea, #764ba2)'}}>📦</div>
          <div className="stat-content">
            <h3>{summary.total_objects}</h3>
            <p>Всего объектов</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{background: 'linear-gradient(135deg, #11998e, #38ef7d)'}}>🔍</div>
          <div className="stat-content">
            <h3>{summary.total_inspections}</h3>
            <p>Обследований</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{background: 'linear-gradient(135deg, #f093fb, #f5576c)'}}>⚠️</div>
          <div className="stat-content">
            <h3>{summary.total_defects}</h3>
            <p>Дефектов найдено</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{background: 'linear-gradient(135deg, #fa709a, #fee140)'}}>📈</div>
          <div className="stat-content">
            <h3>{summary.defect_rate}%</h3>
            <p>Процент дефектности</p>
          </div>
        </div>
      </div>

      {/* Графики */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>Распределение по критичности</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {riskData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Методы контроля</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={methodsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#667eea" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Динамика обследований по годам</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={yearly_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="inspections" stroke="#667eea" name="Обследований" />
              <Line type="monotone" dataKey="defects" stroke="#e74c3c" name="Дефектов" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Оценка качества</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={qualityData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={150} />
              <Tooltip />
              <Bar dataKey="count" fill="#764ba2" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Трубопроводы */}
      <div className="section">
        <h3>Статистика по трубопроводам</h3>
        <div className="pipelines-grid">
          {pipelines.map((pipeline: any) => (
            <div key={pipeline.pipeline_id} className="pipeline-card">
              <h4>{pipeline.name}</h4>
              <div className="pipeline-stats">
                <div className="pipeline-stat">
                  <span className="label">Объектов:</span>
                  <span className="value">{pipeline.objects_count}</span>
                </div>
                <div className="pipeline-stat">
                  <span className="label">Обследований:</span>
                  <span className="value">{pipeline.inspections_count}</span>
                </div>
                <div className="pipeline-stat">
                  <span className="label">Дефектов:</span>
                  <span className="value">{pipeline.defects_count}</span>
                </div>
                <div className="pipeline-stat">
                  <span className="label">Высокий риск:</span>
                  <span className="value danger">{pipeline.high_risk_count}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Топ объекты */}
      <div className="tables-grid">
        <div className="table-card">
          <h3>Топ-5 объектов с дефектами</h3>
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
                  <td>{obj.object_name}</td>
                  <td>{obj.pipeline_id}</td>
                  <td><strong>{obj.count}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="table-card">
          <h3>Топ-5 объектов высокого риска</h3>
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
                  <td>{obj.object_name}</td>
                  <td>{obj.pipeline_id}</td>
                  <td><strong className="danger">{obj.count}</strong></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
