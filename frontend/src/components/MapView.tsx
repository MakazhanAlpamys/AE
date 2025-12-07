import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import axios from 'axios';
import L from 'leaflet';
import { Map as MapIcon, Filter, Layers, AlertTriangle } from 'lucide-react';
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
    html: `<div style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  });
};

const MapView = () => {
  const [mapData, setMapData] = useState<MapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    pipeline_id: '',
    ml_label: '',
    method: '',
    defect_only: true,
    date_from: '',
    date_to: ''
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
      if (filters.date_from) params.append('date_from', filters.date_from);
      if (filters.date_to) params.append('date_to', filters.date_to);
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
      case 'high': return '#ef4444';
      case 'medium': return '#f97316';
      case 'normal': return '#22c55e';
      default: return '#94a3b8';
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
        <h2 className="page-title">
          <MapIcon className="icon-title" /> Карта трубопроводов
        </h2>

        <div className="map-controls card">
          <div className="controls-header">
            <Filter size={16} />
            <span>Фильтры отображения</span>
          </div>

          <div className="map-filters">
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
              value={filters.ml_label}
              onChange={(e) => setFilters({ ...filters, ml_label: e.target.value })}
              className="filter-select"
            >
              <option value="">Все риски</option>
              <option value="high">Высокий</option>
              <option value="medium">Средний</option>
              <option value="normal">Низкий</option>
            </select>

            <select
              value={filters.method}
              onChange={(e) => setFilters({ ...filters, method: e.target.value })}
              className="filter-select"
            >
              <option value="">Все методы</option>
              <option value="VIK">VIK - Визуальный контроль</option>
              <option value="UZK">UZK - Ультразвуковой контроль</option>
              <option value="MFL">MFL - Магнитная дефектоскопия</option>
              <option value="TFI">TFI - Трубная инспекция</option>
              <option value="GEO">GEO - Геодезический контроль</option>
              <option value="MPK">MPK - Магнитопорошковый</option>
              <option value="PVK">PVK - Проникающие вещества</option>
              <option value="RGK">RGK - Радиографический</option>
              <option value="TVK">TVK - Телевизионный контроль</option>
              <option value="VIBRO">VIBRO - Вибродиагностика</option>
              <option value="UTWM">UTWM - УЗ толщинометрия</option>
              <option value="AE">AE - Акустическая эмиссия</option>
              <option value="TOFD">TOFD - Дифракционно-временной</option>
            </select>

            <input
              type="date"
              value={filters.date_from}
              onChange={(e) => setFilters({ ...filters, date_from: e.target.value })}
              className="filter-select"
              placeholder="Дата от"
            />

            <input
              type="date"
              value={filters.date_to}
              onChange={(e) => setFilters({ ...filters, date_to: e.target.value })}
              className="filter-select"
              placeholder="Дата до"
            />

            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={filters.defect_only}
                onChange={(e) => setFilters({ ...filters, defect_only: e.target.checked })}
              />
              <span className="checkbox-text">Только дефекты</span>
            </label>
          </div>
        </div>
      </div>

      <div className="map-content-wrapper card">
        <div className="map-legend">
          <div className="legend-title">
            <Layers size={14} /> Легенда
          </div>
          <div className="legend-items">
            <div className="legend-item">
              <div className="legend-marker" style={{ backgroundColor: '#ef4444' }}></div>
              <span>Высокий риск</span>
            </div>
            <div className="legend-item">
              <div className="legend-marker" style={{ backgroundColor: '#f97316' }}></div>
              <span>Средний риск</span>
            </div>
            <div className="legend-item">
              <div className="legend-marker" style={{ backgroundColor: '#22c55e' }}></div>
              <span>Низкий риск</span>
            </div>
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
            zoomControl={false}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            />

            {/* Линии трубопроводов */}
            {pipelines.map((pipeline) => (
              <Polyline
                key={pipeline.pipeline_id}
                positions={pipeline.coordinates}
                pathOptions={{ color: '#3b82f6', weight: 4, opacity: 0.8 }}
              >
                <Popup>
                  <div className="popup-content">
                    <strong>{pipeline.name}</strong>
                    <br />
                    ID: {pipeline.pipeline_id}
                  </div>
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
                    <div className="popup-row">
                      <span className="popup-label">Тип:</span>
                      <span className="popup-value">{point.object_type}</span>
                    </div>
                    <div className="popup-row">
                      <span className="popup-label">Трубопровод:</span>
                      <span className="popup-value">{point.pipeline_id}</span>
                    </div>
                    <div className="popup-row">
                      <span className="popup-label">Метод:</span>
                      <span className="popup-value">{point.method}</span>
                    </div>
                    <div className="popup-row">
                      <span className="popup-label">Дата:</span>
                      <span className="popup-value">{point.date}</span>
                    </div>
                    <div className="popup-row">
                      <span className="popup-label">Риск:</span>
                      <span className={`risk-badge ${point.ml_label}`}>
                        {getRiskLabel(point.ml_label)}
                      </span>
                    </div>
                    {point.defect_description && (
                      <div className="popup-defect">
                        <AlertTriangle size={14} />
                        {point.defect_description}
                      </div>
                    )}
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
    </div>
  );
};

export default MapView;
