import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Box, Wrench, Settings, Link, MapPin, Filter } from 'lucide-react';
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

  const getObjectIcon = (type: string) => {
    switch (type) {
      case 'crane': return <Wrench size={24} />;
      case 'compressor': return <Settings size={24} />;
      case 'pipeline_section': return <Link size={24} />;
      default: return <Box size={24} />;
    }
  };

  const getObjectTypeLabel = (type: string) => {
    switch (type) {
      case 'crane': return 'Кран';
      case 'compressor': return 'Компрессор';
      case 'pipeline_section': return 'Участок';
      default: return type;
    }
  };

  if (loading) return <div className="loading">Загрузка объектов...</div>;
  if (!Array.isArray(objects)) return <div className="error">Ошибка загрузки данных</div>;

  return (
    <div className="objects-list">
      <div className="list-header">
        <h2 className="page-title">
          <Box className="icon-title" /> Список объектов контроля
        </h2>

        <div className="filters-card card">
          <div className="filters-header">
            <Filter size={16} />
            <span>Фильтры</span>
          </div>

          <div className="list-filters">
            <select
              value={filters.pipeline_id}
              onChange={(e) => setFilters({ ...filters, pipeline_id: e.target.value })}
              className="filter-select"
            >
              <option value="">Все трубопроводы</option>
              <option value="MT-01">MT-01</option>
              <option value="MT-02">MT-02</option>
              <option value="MT-03">MT-03</option>
            </select>

            <select
              value={filters.object_type}
              onChange={(e) => setFilters({ ...filters, object_type: e.target.value })}
              className="filter-select"
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
      </div>

      <div className="objects-grid">
        {objects.map((obj) => (
          <div
            key={obj.object_id}
            className="object-card card"
            onClick={() => handleObjectClick(obj.object_id)}
          >
            <div className={`object-icon-wrapper ${obj.object_type}`}>
              {getObjectIcon(obj.object_type)}
            </div>
            <div className="object-info">
              <div className="object-header">
                <h3>{obj.object_name}</h3>
                <span className="object-type-badge">{getObjectTypeLabel(obj.object_type)}</span>
              </div>

              <div className="object-meta">
                <div className="meta-row">
                  <span className="meta-label">Трубопровод:</span>
                  <span className="meta-value">{obj.pipeline_id}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-label">Год ввода:</span>
                  <span className="meta-value">{obj.year}</span>
                </div>
                <div className="meta-row">
                  <span className="meta-label">Материал:</span>
                  <span className="meta-value">{obj.material}</span>
                </div>
              </div>

              <div className="object-coords">
                <MapPin size={14} />
                {obj.lat.toFixed(4)}, {obj.lon.toFixed(4)}
              </div>
            </div>
          </div>
        ))}
      </div>

      {objects.length === 0 && (
        <div className="no-results">
          <Box size={48} className="no-results-icon" />
          <p>Объекты не найдены</p>
        </div>
      )}
    </div>
  );
};

export default ObjectsList;
