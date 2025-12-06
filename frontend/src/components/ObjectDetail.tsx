import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './ObjectDetail.css';

const ObjectDetail = () => {
  const { objectId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  return (
    <div className="object-detail">
      <button className="back-button" onClick={() => navigate('/objects')}>
        ← Назад к списку
      </button>

      <div className="detail-header">
        <div className="header-icon">
          {object.object_type === 'crane' && '🔧'}
          {object.object_type === 'compressor' && '⚙️'}
          {object.object_type === 'pipeline_section' && '🔗'}
        </div>
        <div className="header-info">
          <h1>{object.object_name}</h1>
          <div className="header-meta">
            <span>ID: {object.object_id}</span>
            <span>•</span>
            <span>Трубопровод: {object.pipeline_id}</span>
            <span>•</span>
            <span>Год: {object.year}</span>
          </div>
        </div>
      </div>

      <div className="detail-stats">
        <div className="stat-box">
          <div className="stat-value">{total_inspections}</div>
          <div className="stat-label">Обследований</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{defects_count}</div>
          <div className="stat-label">Дефектов найдено</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">{object.material}</div>
          <div className="stat-label">Материал</div>
        </div>
        <div className="stat-box">
          <div className="stat-value">
            {object.lat.toFixed(4)}, {object.lon.toFixed(4)}
          </div>
          <div className="stat-label">Координаты</div>
        </div>
      </div>

      {history.length > 0 && (
        <div className="history-section">
          <h2>История обследований</h2>
          <div style={{padding: '1.25rem'}}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a3f54" />
                <XAxis dataKey="year" stroke="#aab7c4" tick={{fill: '#aab7c4'}} />
                <YAxis stroke="#aab7c4" tick={{fill: '#aab7c4'}} />
                <Tooltip contentStyle={{backgroundColor: '#232f3e', border: '1px solid #2a3f54', color: '#fff'}} />
                <Legend wrapperStyle={{color: '#aab7c4'}} />
                <Line type="monotone" dataKey="total_inspections" stroke="#0972d3" name="Обследований" strokeWidth={2} />
                <Line type="monotone" dataKey="defects_found" stroke="#ff9900" name="Дефектов" strokeWidth={2} />
                <Line type="monotone" dataKey="high_risk" stroke="#d13212" name="Высокий риск" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="diagnostics-section">
        <h2>История диагностик</h2>
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
              {diagnostics.map((diag: any) => (
                <tr key={diag.diag_id} className={diag.defect_found ? 'has-defect' : ''}>
                  <td>{diag.date}</td>
                  <td><span className="method-badge">{diag.method}</span></td>
                  <td>
                    {diag.defect_found ? (
                      <span className="defect-yes">✓ Да</span>
                    ) : (
                      <span className="defect-no">✗ Нет</span>
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
