import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import {
  ArrowLeft,
  Wrench,
  Settings,
  Link,
  Activity,
  AlertTriangle,
  Layers,
  MapPin,
  Calendar,
  CheckCircle,
  XCircle,
  FileText
} from 'lucide-react';
import './ObjectDetail.css';

const ObjectDetail = () => {
  const { objectId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState<'date' | 'depth'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    fetchObjectDetail();
  }, [objectId]);

  const fetchObjectDetail = async () => {
    try {
      const response = await axios.get(`/api/objects/${objectId}`);
      setData(response.data);
      setLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных');
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка данных объекта...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!data) return null;

  const { object, diagnostics, history, total_inspections, defects_count } = data;

  // Сортировка диагностик
  const sortedDiagnostics = [...diagnostics].sort((a, b) => {
    if (sortBy === 'depth') {
      const depthA = a.param1 || 0;
      const depthB = b.param1 || 0;
      return sortOrder === 'desc' ? depthB - depthA : depthA - depthB;
    } else {
      // Сортировка по дате
      const dateA = new Date(a.date).getTime();
      const dateB = new Date(b.date).getTime();
      return sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
    }
  });

  const toggleSort = (field: 'date' | 'depth') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const getRiskClass = (mlLabel: string) => {
    switch (mlLabel) {
      case 'high': return 'high';
      case 'medium': return 'medium';
      case 'normal': return 'normal';
      default: return '';
    }
  };

  const getRiskLabel = (mlLabel: string) => {
    switch (mlLabel) {
      case 'high': return 'Высокий';
      case 'medium': return 'Средний';
      case 'normal': return 'Низкий';
      default: return mlLabel;
    }
  };

  const getObjectIcon = (type: string) => {
    switch (type) {
      case 'crane': return <Wrench size={32} />;
      case 'compressor': return <Settings size={32} />;
      case 'pipeline_section': return <Link size={32} />;
      default: return <Settings size={32} />;
    }
  };

  return (
    <div className="object-detail">
      <button className="back-button" onClick={() => navigate('/objects')}>
        <ArrowLeft size={16} /> Назад к списку
      </button>

      <div className="detail-header card">
        <div className={`header-icon-wrapper ${object.object_type}`}>
          {getObjectIcon(object.object_type)}
        </div>
        <div className="header-info">
          <h1>{object.object_name}</h1>
          <div className="header-meta">
            <span className="meta-pill">ID: {object.object_id}</span>
            <span className="meta-pill">Трубопровод: {object.pipeline_id}</span>
            <span className="meta-pill">Год: {object.year}</span>
          </div>
        </div>
      </div>

      <div className="detail-stats">
        <div className="stat-box card">
          <div className="stat-icon-bg blue">
            <Activity size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{total_inspections}</div>
            <div className="stat-label">Обследований</div>
          </div>
        </div>
        <div className="stat-box card">
          <div className="stat-icon-bg orange">
            <AlertTriangle size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{defects_count}</div>
            <div className="stat-label">Дефектов найдено</div>
          </div>
        </div>
        <div className="stat-box card">
          <div className="stat-icon-bg purple">
            <Layers size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value">{object.material}</div>
            <div className="stat-label">Материал</div>
          </div>
        </div>
        <div className="stat-box card">
          <div className="stat-icon-bg green">
            <MapPin size={24} />
          </div>
          <div className="stat-content">
            <div className="stat-value coords">
              {object.lat.toFixed(4)}, {object.lon.toFixed(4)}
            </div>
            <div className="stat-label">Координаты</div>
          </div>
        </div>
      </div>

      {history.length > 0 && (
        <div className="history-section card">
          <div className="section-header">
            <Calendar size={20} />
            <h2>История обследований</h2>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis
                  dataKey="year"
                  stroke="var(--text-secondary)"
                  tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="var(--text-secondary)"
                  tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--surface)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    boxShadow: 'var(--shadow-md)',
                    color: 'var(--text-primary)'
                  }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Line type="monotone" dataKey="total_inspections" stroke="var(--primary)" name="Обследований" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                <Line type="monotone" dataKey="defects_found" stroke="var(--status-warning)" name="Дефектов" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                <Line type="monotone" dataKey="high_risk" stroke="var(--status-error)" name="Высокий риск" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="diagnostics-section card">
        <div className="section-header">
          <FileText size={20} />
          <h2>История диагностик</h2>
          <div className="sort-buttons">
            <button 
              className={`sort-btn ${sortBy === 'date' ? 'active' : ''}`}
              onClick={() => toggleSort('date')}
              title="Сортировка по дате"
            >
              Дата {sortBy === 'date' && (sortOrder === 'desc' ? '↓' : '↑')}
            </button>
            <button 
              className={`sort-btn ${sortBy === 'depth' ? 'active' : ''}`}
              onClick={() => toggleSort('depth')}
              title="Сортировка по глубине дефекта"
            >
              Глубина {sortBy === 'depth' && (sortOrder === 'desc' ? '↓' : '↑')}
            </button>
          </div>
        </div>
        <div className="diagnostics-table-container">
          <table className="diagnostics-table">
            <thead>
              <tr>
                <th>Дата</th>
                <th>Метод</th>
                <th>Дефект</th>
                <th>Описание</th>
                <th>Оценка</th>
                <th>Риск</th>
                <th>Параметры</th>
              </tr>
            </thead>
            <tbody>
              {sortedDiagnostics.map((diag: any) => (
                <tr key={diag.diag_id} className={diag.defect_found ? 'has-defect' : ''}>
                  <td>{diag.date}</td>
                  <td><span className="method-badge">{diag.method}</span></td>
                  <td>
                    {diag.defect_found ? (
                      <span className="defect-status yes">
                        <CheckCircle size={14} /> Да
                      </span>
                    ) : (
                      <span className="defect-status no">
                        <XCircle size={14} /> Нет
                      </span>
                    )}
                  </td>
                  <td>{diag.defect_description || '—'}</td>
                  <td>{diag.quality_grade}</td>
                  <td>
                    <span className={`risk-badge ${getRiskClass(diag.ml_label)}`}>
                      {getRiskLabel(diag.ml_label)}
                    </span>
                  </td>
                  <td className="params-cell">
                    {diag.param1 && (
                      <div>Глубина: {diag.param1}%</div>
                    )}
                    {diag.param2 && (
                      <div>Длина: {diag.param2} мм</div>
                    )}
                    {diag.param3 && (
                      <div>Ширина: {diag.param3} мм</div>
                    )}
                    {!diag.param1 && '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ObjectDetail;
