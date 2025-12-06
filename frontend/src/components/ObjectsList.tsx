import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ObjectsList.css';

interface ObjectItem {
  object_id: number;
  object_name: string;
  object_type: string;
  pipeline_id: string;
  lat: number;
  lon: number;
  year: number;
  material: string;
}

const ObjectsList = () => {
  const [objects, setObjects] = useState<ObjectItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    pipeline_id: '',
    object_type: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchObjects();
  }, [filters]);

  const fetchObjects = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.pipeline_id) params.append('pipeline_id', filters.pipeline_id);
      if (filters.object_type) params.append('object_type', filters.object_type);

      const response = await axios.get(`/api/objects?${params.toString()}`);
      setObjects(response.data);
      setLoading(false);
    } catch (err: any) {
      console.error('Ошибка загрузки объектов:', err);
      setObjects([]);
      setLoading(false);
    }
  };

  const handleObjectClick = (objectId: number) => {
    navigate(`/objects/${objectId}`);
  };

  if (loading) return <div className="loading">Загрузка объектов...</div>;
  if (!Array.isArray(objects)) return <div className="error">Ошибка загрузки данных</div>;

  return (
    <div className="objects-list">
      <div className="list-header">
        <h2>📦 Список объектов контроля</h2>
        <div className="list-filters">
          <select 
            value={filters.pipeline_id} 
            onChange={(e) => setFilters({...filters, pipeline_id: e.target.value})}
          >
            <option value="">Все трубопроводы</option>
            <option value="MT-01">MT-01</option>
            <option value="MT-02">MT-02</option>
            <option value="MT-03">MT-03</option>
          </select>

          <select 
            value={filters.object_type} 
            onChange={(e) => setFilters({...filters, object_type: e.target.value})}
          >
            <option value="">Все типы</option>
            <option value="pipeline_section">Участок трубопровода</option>
            <option value="crane">Кран</option>
            <option value="compressor">Компрессор</option>
          </select>

          <div className="results-count">
            Найдено: <strong>{objects.length}</strong> объектов
          </div>
        </div>
      </div>

      <div className="objects-grid">
        {objects.map((obj) => (
          <div 
            key={obj.object_id} 
            className="object-card"
            onClick={() => handleObjectClick(obj.object_id)}
          >
            <div className="object-icon">
              {obj.object_type === 'crane' && '🔧'}
              {obj.object_type === 'compressor' && '⚙️'}
              {obj.object_type === 'pipeline_section' && '🔗'}
            </div>
            <div className="object-info">
              <h3>{obj.object_name}</h3>
              <div className="object-meta">
                <span className="meta-item">
                  <strong>ID:</strong> {obj.object_id}
                </span>
                <span className="meta-item">
                  <strong>Трубопровод:</strong> {obj.pipeline_id}
                </span>
                <span className="meta-item">
                  <strong>Год:</strong> {obj.year}
                </span>
                <span className="meta-item">
                  <strong>Материал:</strong> {obj.material}
                </span>
              </div>
              <div className="object-coords">
                📍 {obj.lat.toFixed(4)}, {obj.lon.toFixed(4)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {objects.length === 0 && (
        <div className="no-results">
          Объекты не найдены
        </div>
      )}
    </div>
  );
};

export default ObjectsList;
