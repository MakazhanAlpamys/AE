import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import axios from 'axios';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './MapView.css';

interface MapPoint {
  object_id: number;
  object_name: string;
  object_type: string;
  pipeline_id: string;
  lat: number;
  lon: number;
  ml_label: string;
  method: string;
  date: string;
  defect_description: string | null;
  quality_grade: string;
}

interface PipelineData {
  pipeline_id: string;
  name: string;
  coordinates: [number, number][];
}

interface MapData {
  points: MapPoint[];
  pipelines: PipelineData[];
  total_points: number;
}

// Fix для иконок Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// Кастомные иконки по критичности
const createCustomIcon = (color: string) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
};

const MapView = () => {
  const [mapData, setMapData] = useState<MapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    pipeline_id: '',
    ml_label: '',
    method: '',
    defect_only: true
  });

  useEffect(() => {
    fetchMapData();
  }, [filters]);

  const fetchMapData = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.pipeline_id) params.append('pipeline_id', filters.pipeline_id);
      if (filters.ml_label) params.append('ml_label', filters.ml_label);
      if (filters.method) params.append('method', filters.method);
      params.append('defect_only', filters.defect_only.toString());

      const response = await axios.get(`/api/map-data?${params.toString()}`);
      setMapData(response.data);
      setLoading(false);
    } catch (err: any) {
      console.error('Ошибка загрузки данных карты:', err);
      setMapData({ points: [], pipelines: [], total_points: 0 });
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Загрузка карты...</div>;
  if (!mapData) return <div className="error">Нет данных для отображения</div>;

  const { points, pipelines } = mapData;

  // Проверка на валидность данных
  if (!Array.isArray(points) || !Array.isArray(pipelines)) {
    return <div className="error">Ошибка формата данных</div>;
  }

  // Центр карты - Казахстан
  const center: [number, number] = [48.0, 66.0];

  const getMarkerColor = (mlLabel: string) => {
    switch (mlLabel) {
      case 'high': return '#e74c3c';
      case 'medium': return '#f39c12';
      case 'normal': return '#2ecc71';
      default: return '#95a5a6';
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
    <div className="map-view">
      <div className="map-header">
        <h2>🗺️ Карта трубопроводов</h2>
        <div className="map-filters">
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
            value={filters.ml_label} 
            onChange={(e) => setFilters({...filters, ml_label: e.target.value})}
          >
            <option value="">Все риски</option>
            <option value="high">Высокий</option>
            <option value="medium">Средний</option>
            <option value="normal">Низкий</option>
          </select>

          <select 
            value={filters.method} 
            onChange={(e) => setFilters({...filters, method: e.target.value})}
          >
            <option value="">Все методы</option>
            <option value="VIK">VIK</option>
            <option value="UZK">UZK</option>
            <option value="MFL">MFL</option>
            <option value="TFI">TFI</option>
            <option value="GEO">GEO</option>
          </select>

          <label className="checkbox-label">
            <input 
              type="checkbox" 
              checked={filters.defect_only}
              onChange={(e) => setFilters({...filters, defect_only: e.target.checked})}
            />
            Только дефекты
          </label>
        </div>
      </div>

      <div className="map-legend">
        <div className="legend-item">
          <div className="legend-marker" style={{backgroundColor: '#e74c3c'}}></div>
          <span>Высокий риск</span>
        </div>
        <div className="legend-item">
          <div className="legend-marker" style={{backgroundColor: '#f39c12'}}></div>
          <span>Средний риск</span>
        </div>
        <div className="legend-item">
          <div className="legend-marker" style={{backgroundColor: '#2ecc71'}}></div>
          <span>Низкий риск</span>
        </div>
        <div className="legend-count">
          Отображено точек: <strong>{points.length}</strong>
        </div>
      </div>

      <div className="map-container">
        <MapContainer 
          center={center} 
          zoom={6} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Линии трубопроводов */}
          {pipelines.map((pipeline) => (
            <Polyline
              key={pipeline.pipeline_id}
              positions={pipeline.coordinates}
              pathOptions={{ color: '#3498db', weight: 3, opacity: 0.7 }}
            >
              <Popup>
                <strong>{pipeline.name}</strong>
                <br />
                ID: {pipeline.pipeline_id}
              </Popup>
            </Polyline>
          ))}

          {/* Маркеры объектов */}
          {points.map((point) => (
            <Marker
              key={point.object_id}
              position={[point.lat, point.lon]}
              icon={createCustomIcon(getMarkerColor(point.ml_label))}
            >
              <Popup>
                <div className="popup-content">
                  <h3>{point.object_name}</h3>
                  <div className="popup-field">
                    <strong>Тип:</strong> {point.object_type}
                  </div>
                  <div className="popup-field">
                    <strong>Трубопровод:</strong> {point.pipeline_id}
                  </div>
                  <div className="popup-field">
                    <strong>Метод:</strong> {point.method}
                  </div>
                  <div className="popup-field">
                    <strong>Дата:</strong> {point.date}
                  </div>
                  <div className="popup-field">
                    <strong>Риск:</strong> 
                    <span className={`risk-badge ${point.ml_label}`}>
                      {getRiskLabel(point.ml_label)}
                    </span>
                  </div>
                  {point.defect_description && (
                    <div className="popup-field">
                      <strong>Дефект:</strong> {point.defect_description}
                    </div>
                  )}
                  <div className="popup-field">
                    <strong>Оценка:</strong> {point.quality_grade}
                  </div>
                  <a href={`/objects/${point.object_id}`} className="popup-link">
                    Подробнее →
                  </a>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
};

export default MapView;
