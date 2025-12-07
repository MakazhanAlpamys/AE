import { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, AlertTriangle, Calendar, Activity, Target, ArrowUp, ArrowDown, Minus } from 'lucide-react';
import './Predictions.css';

interface RiskObject {
  object_id: number;
  object_name: string;
  object_type: string;
  pipeline_id: string;
  risk_probability: number;
  next_inspection_date: string;
  recommended_method: string;
  trend: string;
  message: string;
  current_depth?: number;
  predicted_depth?: number;
}

interface PipelineForecast {
  pipeline_id: string;
  pipeline_name: string;
  critical_count: number;
  defect_rate: number;
  predicted_defects: number;
}

interface PredictionsDashboard {
  top_risks: RiskObject[];
  pipeline_forecasts: PipelineForecast[];
  summary: {
    high_risk_objects: number;
    medium_risk_objects: number;
    total_analyzed: number;
  };
}

const Predictions = () => {
  const [data, setData] = useState<PredictionsDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPipeline, setSelectedPipeline] = useState<string>('all');
  const [selectedObject, setSelectedObject] = useState<number | null>(null);
  const [objectPrediction, setObjectPrediction] = useState<any>(null);

  useEffect(() => {
    fetchPredictionsData();
  }, []);

  const fetchPredictionsData = async () => {
    try {
      const response = await axios.get('/api/predictions/dashboard');
      setData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Ошибка загрузки прогнозов:', error);
      setLoading(false);
    }
  };

  const fetchObjectPrediction = async (objectId: number) => {
    try {
      const response = await axios.get(`/api/predictions/object/${objectId}`);
      setObjectPrediction(response.data);
      setSelectedObject(objectId);
    } catch (error) {
      console.error('Ошибка загрузки прогноза объекта:', error);
    }
  };

  const getRiskColor = (risk: number) => {
    if (risk > 0.6) return '#ef4444'; // red
    if (risk > 0.3) return '#f59e0b'; // orange
    return '#10b981'; // green
  };

  const getRiskLabel = (risk: number) => {
    if (risk > 0.6) return 'Высокий';
    if (risk > 0.3) return 'Средний';
    return 'Низкий';
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'increasing') return <ArrowUp size={16} color="#ef4444" />;
    if (trend === 'decreasing') return <ArrowDown size={16} color="#10b981" />;
    return <Minus size={16} color="#6b7280" />;
  };

  const getTrendLabel = (trend: string) => {
    if (trend === 'increasing') return 'Ухудшение';
    if (trend === 'decreasing') return 'Улучшение';
    return 'Стабильно';
  };

  if (loading) return <div className="loading">Загрузка прогнозов...</div>;
  if (!data) return <div className="error">Нет данных для прогнозирования</div>;

  const filteredRisks = selectedPipeline === 'all' 
    ? data.top_risks 
    : data.top_risks.filter(r => r.pipeline_id === selectedPipeline);

  return (
    <div className="predictions-page">
      <div className="predictions-header">
        <h2 className="page-title">
          <TrendingUp className="icon-title" /> Предиктивная аналитика
        </h2>
        <p className="predictions-description">
          Прогнозирование критических дефектов на основе ML-анализа исторических данных
        </p>
      </div>

      {/* Общая статистика */}
      <div className="predictions-summary">
        <div className="summary-card high-risk">
          <div className="summary-icon">
            <AlertTriangle size={32} />
          </div>
          <div className="summary-content">
            <h3>{data.summary.high_risk_objects}</h3>
            <p>Объектов высокого риска</p>
            <span className="summary-badge">Требуют срочного обследования</span>
          </div>
        </div>

        <div className="summary-card medium-risk">
          <div className="summary-icon">
            <Activity size={32} />
          </div>
          <div className="summary-content">
            <h3>{data.summary.medium_risk_objects}</h3>
            <p>Объектов среднего риска</p>
            <span className="summary-badge">Внеплановый контроль</span>
          </div>
        </div>

        <div className="summary-card total">
          <div className="summary-icon">
            <Target size={32} />
          </div>
          <div className="summary-content">
            <h3>{data.summary.total_analyzed}</h3>
            <p>Всего проанализировано</p>
            <span className="summary-badge">Объектов контроля</span>
          </div>
        </div>
      </div>

      {/* Прогноз по трубопроводам */}
      <div className="card pipeline-forecasts">
        <h3>Прогноз по трубопроводам на следующий год</h3>
        <div className="pipeline-grid">
          {data.pipeline_forecasts.map((forecast) => (
            <div key={forecast.pipeline_id} className="pipeline-forecast-card">
              <div className="pipeline-forecast-header">
                <h4>{forecast.pipeline_name}</h4>
                <span className="pipeline-id">{forecast.pipeline_id}</span>
              </div>
              
              <div className="pipeline-forecast-stats">
                <div className="forecast-stat">
                  <span className="stat-label">Критичных объектов</span>
                  <span className="stat-value critical">{forecast.critical_count}</span>
                </div>
                
                <div className="forecast-stat">
                  <span className="stat-label">Уровень дефектности</span>
                  <span className="stat-value">{(forecast.defect_rate * 100).toFixed(0)}%</span>
                </div>
                
                <div className="forecast-stat">
                  <span className="stat-label">Прогноз дефектов</span>
                  <span className="stat-value warning">{forecast.predicted_defects}</span>
                </div>
              </div>

              <div className="forecast-progress">
                <div 
                  className="progress-bar" 
                  style={{ 
                    width: `${Math.min(forecast.defect_rate * 100, 100)}%`,
                    backgroundColor: forecast.defect_rate > 0.5 ? '#ef4444' : forecast.defect_rate > 0.3 ? '#f59e0b' : '#10b981'
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Фильтр по трубопроводу */}
      <div className="card filter-section">
        <label>Фильтр по трубопроводу:</label>
        <select 
          value={selectedPipeline} 
          onChange={(e) => setSelectedPipeline(e.target.value)}
          className="filter-select"
        >
          <option value="all">Все трубопроводы</option>
          {data.pipeline_forecasts.map(p => (
            <option key={p.pipeline_id} value={p.pipeline_id}>
              {p.pipeline_name} ({p.pipeline_id})
            </option>
          ))}
        </select>
      </div>

      {/* Топ рисков */}
      <div className="card risks-table">
        <h3>
          <AlertTriangle size={20} /> 
          Топ объектов по риску критических дефектов
        </h3>
        
        <div className="table-responsive">
          <table className="predictions-table">
            <thead>
              <tr>
                <th>№</th>
                <th>Объект</th>
                <th>Тип</th>
                <th>Трубопровод</th>
                <th>Риск</th>
                <th>Тренд</th>
                <th>Глубина (текущая)</th>
                <th>Прогноз глубины</th>
                <th>Следующее обследование</th>
                <th>Метод</th>
              </tr>
            </thead>
            <tbody>
              {filteredRisks.map((risk, index) => (
                <tr 
                  key={risk.object_id} 
                  className="risk-row"
                  onClick={() => fetchObjectPrediction(risk.object_id)}
                  style={{ cursor: 'pointer' }}
                >
                  <td>{index + 1}</td>
                  <td className="object-name">{risk.object_name}</td>
                  <td>
                    <span className="type-badge">{risk.object_type}</span>
                  </td>
                  <td>{risk.pipeline_id}</td>
                  <td>
                    <div className="risk-cell">
                      <div 
                        className="risk-bar"
                        style={{ 
                          width: `${risk.risk_probability * 100}%`,
                          backgroundColor: getRiskColor(risk.risk_probability)
                        }}
                      />
                      <span style={{ color: getRiskColor(risk.risk_probability), fontWeight: 'bold' }}>
                        {(risk.risk_probability * 100).toFixed(0)}%
                      </span>
                      <span className="risk-label">{getRiskLabel(risk.risk_probability)}</span>
                    </div>
                  </td>
                  <td>
                    <div className="trend-cell">
                      {getTrendIcon(risk.trend)}
                      <span>{getTrendLabel(risk.trend)}</span>
                    </div>
                  </td>
                  <td>
                    <span className={risk.current_depth && risk.current_depth > 30 ? 'depth-critical' : ''}>
                      {risk.current_depth ? `${risk.current_depth.toFixed(1)}%` : '—'}
                    </span>
                  </td>
                  <td>
                    <span className={risk.predicted_depth && risk.predicted_depth > 50 ? 'depth-critical' : ''}>
                      {risk.predicted_depth ? `${risk.predicted_depth.toFixed(1)}%` : '—'}
                    </span>
                  </td>
                  <td>
                    <div className="date-cell">
                      <Calendar size={14} />
                      {new Date(risk.next_inspection_date).toLocaleDateString('ru-RU')}
                    </div>
                  </td>
                  <td>
                    <span className="method-badge">{risk.recommended_method}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Детали выбранного объекта */}
      {objectPrediction && selectedObject && (
        <div className="modal-overlay" onClick={() => setSelectedObject(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Детальный прогноз для объекта #{selectedObject}</h3>
              <button className="modal-close" onClick={() => setSelectedObject(null)}>✕</button>
            </div>
            
            <div className="modal-body">
              {objectPrediction.status === 'success' ? (
                <>
                  <div className="prediction-message" style={{
                    backgroundColor: objectPrediction.risk_probability > 0.6 ? '#fee2e2' : objectPrediction.risk_probability > 0.3 ? '#fef3c7' : '#d1fae5',
                    color: objectPrediction.risk_probability > 0.6 ? '#991b1b' : objectPrediction.risk_probability > 0.3 ? '#92400e' : '#065f46',
                    padding: '15px',
                    borderRadius: '8px',
                    marginBottom: '20px',
                    fontWeight: 'bold'
                  }}>
                    {objectPrediction.message}
                  </div>

                  <div className="prediction-details">
                    <div className="detail-row">
                      <span className="detail-label">Вероятность критического дефекта:</span>
                      <span className="detail-value" style={{ color: getRiskColor(objectPrediction.risk_probability), fontSize: '24px', fontWeight: 'bold' }}>
                        {(objectPrediction.risk_probability * 100).toFixed(0)}%
                      </span>
                    </div>

                    <div className="detail-row">
                      <span className="detail-label">Рекомендуемый метод:</span>
                      <span className="detail-value method-badge-large">{objectPrediction.recommended_method}</span>
                    </div>

                    <div className="detail-row">
                      <span className="detail-label">Дата следующего обследования:</span>
                      <span className="detail-value">
                        {new Date(objectPrediction.next_inspection_date).toLocaleDateString('ru-RU', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </span>
                    </div>

                    {objectPrediction.current_depth !== undefined && (
                      <>
                        <div className="detail-row">
                          <span className="detail-label">Текущая глубина дефекта:</span>
                          <span className="detail-value">{objectPrediction.current_depth.toFixed(2)}%</span>
                        </div>

                        <div className="detail-row">
                          <span className="detail-label">Прогнозируемая глубина (через год):</span>
                          <span className="detail-value">{objectPrediction.predicted_depth.toFixed(2)}%</span>
                        </div>

                        <div className="detail-row">
                          <span className="detail-label">Тренд развития:</span>
                          <span className="detail-value">
                            {getTrendIcon(objectPrediction.trend)}
                            {getTrendLabel(objectPrediction.trend)}
                          </span>
                        </div>
                      </>
                    )}

                    {objectPrediction.last_inspection && (
                      <div className="detail-row">
                        <span className="detail-label">Последнее обследование:</span>
                        <span className="detail-value">
                          {new Date(objectPrediction.last_inspection).toLocaleDateString('ru-RU')}
                        </span>
                      </div>
                    )}

                    {objectPrediction.defect_count !== undefined && (
                      <div className="detail-row">
                        <span className="detail-label">Количество обнаруженных дефектов:</span>
                        <span className="detail-value">{objectPrediction.defect_count}</span>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="prediction-message" style={{ backgroundColor: '#f3f4f6', padding: '15px', borderRadius: '8px' }}>
                  {objectPrediction.message}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Predictions;
