import React, { useState, useCallback } from 'react';
import { Upload, FileText, CheckCircle, XCircle, AlertTriangle, Download } from 'lucide-react';
import axios from 'axios';
import './ImportData.css';

interface ImportResult {
  success: boolean;
  rows_imported: number;
  errors: string[];
  warnings: string[];
  preview: any[];
}

interface PreviewData {
  columns: string[];
  row_count: number;
  preview: any[];
}

const ImportData: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileType, setFileType] = useState<'objects' | 'diagnostics'>('objects');
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [preview, setPreview] = useState<PreviewData | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    // Проверка формата
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
      alert('Поддерживаются только CSV и XLSX файлы');
      return;
    }

    setSelectedFile(file);
    setResult(null);

    // Получаем превью
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post('/api/import/validate-preview', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setPreview(response.data);
    } catch (error: any) {
      console.error('Ошибка получения превью:', error);
      alert('Не удалось прочитать файл');
    }
  };

  const handleImport = async () => {
    if (!selectedFile) return;

    setImporting(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const endpoint = fileType === 'objects' 
        ? '/api/import/objects' 
        : '/api/import/diagnostics';

      const response = await axios.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setResult(response.data);

      if (response.data.success) {
        // Перезагружаем страницу через 2 секунды для обновления данных
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    } catch (error: any) {
      setResult({
        success: false,
        rows_imported: 0,
        errors: [error.response?.data?.detail || 'Ошибка импорта'],
        warnings: [],
        preview: []
      });
    } finally {
      setImporting(false);
    }
  };

  const downloadTemplate = (type: 'objects' | 'diagnostics') => {
    const templates = {
      objects: 'object_id,object_name,object_type,pipeline_id,lat,lon,year,material\n1,"Кран-001",crane,MT-01,50.0,60.0,2020,Ст3\n2,"Компрессор-001",compressor,MT-01,51.0,61.0,2019,Ст5\n3,"Участок-001",pipeline_section,MT-02,52.0,62.0,2021,Ст10',
      diagnostics: 'diag_id,object_id,method,date,defect_found,temperature,humidity,illumination,defect_description,quality_grade,param1,param2,param3,ml_label\n1,1,UZK,2024-01-01,true,20,60,500,"Коррозия стенки",требует_мер,30,100,50,high\n2,1,VIK,2024-02-01,false,22,55,600,"",удовлетворительно,0,0,0,normal\n3,2,MFL,2024-03-01,true,18,65,450,"Трещина",недопустимо,45,150,80,high'
    };

    // Добавляем BOM (Byte Order Mark) для правильного отображения в Excel
    const BOM = '\uFEFF';
    const content = BOM + templates[type];
    
    const blob = new Blob([content], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `template_${type}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="import-data">
      <div className="import-header">
        <h2 className="page-title">
          <Upload className="icon-title" /> Импорт данных
        </h2>
        <p className="import-description">
          Загрузите CSV или XLSX файлы с данными объектов или диагностик.
          Система автоматически проверит формат и валидирует данные.
        </p>
      </div>

      <div className="import-content">
        {/* Выбор типа данных */}
        <div className="card type-selector">
          <h3>Тип импортируемых данных</h3>
          <div className="type-buttons">
            <button
              className={`type-button ${fileType === 'objects' ? 'active' : ''}`}
              onClick={() => setFileType('objects')}
            >
              <FileText size={20} />
              <span>Объекты контроля</span>
              <small>(Objects.csv)</small>
            </button>
            <button
              className={`type-button ${fileType === 'diagnostics' ? 'active' : ''}`}
              onClick={() => setFileType('diagnostics')}
            >
              <FileText size={20} />
              <span>Результаты диагностик</span>
              <small>(Diagnostics.csv)</small>
            </button>
          </div>
          
          <div className="template-download">
            <button
              className="btn-secondary"
              onClick={() => downloadTemplate(fileType)}
            >
              <Download size={16} />
              Скачать шаблон
            </button>
          </div>

          {/* Обязательные колонки */}
          <div style={{ marginTop: '15px', padding: '12px', background: 'var(--surface)', borderRadius: '8px', fontSize: '13px' }}>
            <strong>📋 Обязательные колонки для {fileType === 'objects' ? 'объектов' : 'диагностик'}:</strong>
            <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {fileType === 'objects' ? (
                <>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>object_id</code>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>object_name</code>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>object_type</code>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>pipeline_id</code>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>lat</code>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>lon</code>
                </>
              ) : (
                <>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>diag_id</code>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>object_id</code>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>method</code>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>date</code>
                  <code style={{ background: 'var(--primary)', color: 'white', padding: '2px 6px', borderRadius: '4px' }}>defect_found</code>
                </>
              )}
            </div>
            <p style={{ marginTop: '8px', color: 'var(--text-secondary)', fontSize: '12px' }}>
              💡 Скачайте шаблон выше - он уже содержит все нужные колонки с примерами
            </p>
          </div>
        </div>

        {/* Drag & Drop зона */}
        <div
          className={`card drop-zone ${dragActive ? 'drag-active' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          {!selectedFile ? (
            <>
              <Upload size={48} className="drop-icon" />
              <p className="drop-text">
                Перетащите файл сюда или{' '}
                <label className="file-label">
                  выберите файл
                  <input
                    type="file"
                    accept=".csv,.xlsx"
                    onChange={handleFileInput}
                    style={{ display: 'none' }}
                  />
                </label>
              </p>
              <p className="drop-hint">Поддерживаются форматы: CSV, XLSX</p>
            </>
          ) : (
            <div className="file-info">
              <FileText size={48} className="file-icon" />
              <div className="file-details">
                <h4>{selectedFile.name}</h4>
                <p>{(selectedFile.size / 1024).toFixed(2)} KB</p>
              </div>
              <button
                className="btn-remove"
                onClick={() => {
                  setSelectedFile(null);
                  setPreview(null);
                  setResult(null);
                }}
              >
                ✕
              </button>
            </div>
          )}
        </div>

        {/* Превью данных */}
        {preview && (
          <div className="card preview-section">
            <h3>Превью данных ({preview.row_count} строк)</h3>
            <div className="preview-table-wrapper">
              <table className="preview-table">
                <thead>
                  <tr>
                    {preview.columns.map((col, idx) => (
                      <th key={idx}>{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.preview.map((row, idx) => (
                    <tr key={idx}>
                      {preview.columns.map((col, colIdx) => (
                        <td key={colIdx}>{String(row[col] || '')}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div className="preview-actions">
              <button
                className="btn-primary"
                onClick={handleImport}
                disabled={importing}
              >
                {importing ? 'Импорт...' : `Импортировать ${preview.row_count} записей`}
              </button>
            </div>
          </div>
        )}

        {/* Результат импорта */}
        {result && (
          <div className={`card result-section ${result.success ? 'success' : 'error'}`}>
            <div className="result-header">
              {result.success ? (
                <>
                  <CheckCircle size={24} className="result-icon success-icon" />
                  <h3>Импорт успешно завершен!</h3>
                </>
              ) : (
                <>
                  <XCircle size={24} className="result-icon error-icon" />
                  <h3>Ошибка импорта</h3>
                </>
              )}
            </div>

            {result.success && (
              <p className="result-summary">
                Импортировано записей: <strong>{result.rows_imported}</strong>
              </p>
            )}

            {result.errors.length > 0 && (
              <div className="result-messages errors">
                <h4>
                  <XCircle size={16} /> Ошибки ({result.errors.length})
                </h4>
                <ul>
                  {result.errors.map((err, idx) => (
                    <li key={idx} style={{ whiteSpace: 'pre-line', lineHeight: '1.6' }}>{err}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.warnings.length > 0 && (
              <div className="result-messages warnings">
                <h4>
                  <AlertTriangle size={16} /> Предупреждения ({result.warnings.length})
                </h4>
                <ul>
                  {result.warnings.map((warn, idx) => (
                    <li key={idx}>{warn}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.success && (
              <p className="reload-notice">
                Страница автоматически обновится через 2 секунды...
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ImportData;
