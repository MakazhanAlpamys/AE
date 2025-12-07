import { useState } from 'react';
import { FileText, Download, FileType } from 'lucide-react';
import './ReportsMenu.css';

const ReportsMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [pipelineId, setPipelineId] = useState('');

  const handleOpenHTML = () => {
    const url = pipelineId 
      ? `/api/report?pipeline_id=${pipelineId}`
      : '/api/report';
    window.open(url, '_blank');
    setIsOpen(false);
  };

  const handleDownloadPDF = () => {
    const url = pipelineId 
      ? `/api/report/pdf?pipeline_id=${pipelineId}`
      : '/api/report/pdf';
    
    // Создаем временную ссылку для скачивания
    const link = document.createElement('a');
    link.href = url;
    link.download = `IntegrityOS_Report_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    setIsOpen(false);
  };

  return (
    <div className="reports-menu">
      <button 
        className="reports-trigger"
        onClick={() => setIsOpen(!isOpen)}
        title="Отчеты"
      >
        <FileText size={20} />
        <span>Отчеты</span>
      </button>

      {isOpen && (
        <>
          <div className="reports-overlay" onClick={() => setIsOpen(false)} />
          <div className="reports-dropdown glass">
            <div className="reports-header">
              <FileText size={20} />
              <h3>Генерация отчетов</h3>
            </div>

            <div className="reports-content">
              <div className="filter-section">
                <label htmlFor="pipeline-filter">Фильтр по трубопроводу</label>
                <select 
                  id="pipeline-filter"
                  value={pipelineId}
                  onChange={(e) => setPipelineId(e.target.value)}
                  className="pipeline-select"
                >
                  <option value="">Все трубопроводы</option>
                  <option value="MT-01">MT-01 - Атырау - Самара</option>
                  <option value="MT-02">MT-02 - Узень - Атырау</option>
                  <option value="MT-03">MT-03 - Каражанбас - Актау</option>
                </select>
              </div>

              <div className="report-actions">
                <button 
                  className="report-btn html-btn"
                  onClick={handleOpenHTML}
                >
                  <FileType size={18} />
                  <div className="btn-content">
                    <span className="btn-title">HTML отчет</span>
                    <span className="btn-subtitle">Открыть в браузере</span>
                  </div>
                </button>

                <button 
                  className="report-btn pdf-btn"
                  onClick={handleDownloadPDF}
                >
                  <Download size={18} />
                  <div className="btn-content">
                    <span className="btn-title">PDF отчет</span>
                    <span className="btn-subtitle">Скачать файл</span>
                  </div>
                </button>
              </div>

              <div className="reports-info">
                <p>💡 HTML отчет открывается в новой вкладке</p>
                <p>💡 PDF отчет автоматически скачивается</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ReportsMenu;
