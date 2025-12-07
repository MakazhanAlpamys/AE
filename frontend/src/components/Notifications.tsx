import React, { useState, useEffect } from 'react';
import './Notifications.css';

interface Notification {
  id: number;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  is_read: boolean;
  created_at: string;
  metadata?: any;
}

interface NotificationsProps {
  apiUrl?: string;
}

const Notifications: React.FC<NotificationsProps> = ({ 
  apiUrl = 'http://localhost:8000' 
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [showUnreadOnly, setShowUnreadOnly] = useState<boolean>(false);

  // Загрузка уведомлений
  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${apiUrl}/api/notifications?unread_only=${showUnreadOnly}&limit=20`
      );
      const data = await response.json();
      setNotifications(data.notifications || []);
      setUnreadCount(data.unread_count || 0);
    } catch (error) {
      console.error('Ошибка загрузки уведомлений:', error);
    } finally {
      setLoading(false);
    }
  };

  // Загрузка количества непрочитанных
  const fetchUnreadCount = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/notifications/unread-count`);
      const data = await response.json();
      setUnreadCount(data.unread_count || 0);
    } catch (error) {
      console.error('Ошибка загрузки счетчика:', error);
    }
  };

  // Пометить как прочитанное
  const markAsRead = async (id: number) => {
    try {
      await fetch(`${apiUrl}/api/notifications/${id}/read`, {
        method: 'POST'
      });
      await fetchNotifications();
    } catch (error) {
      console.error('Ошибка отметки уведомления:', error);
    }
  };

  // Пометить все как прочитанные
  const markAllAsRead = async () => {
    try {
      await fetch(`${apiUrl}/api/notifications/read-all`, {
        method: 'POST'
      });
      await fetchNotifications();
    } catch (error) {
      console.error('Ошибка отметки всех уведомлений:', error);
    }
  };

  // Удалить уведомление
  const deleteNotification = async (id: number) => {
    try {
      await fetch(`${apiUrl}/api/notifications/${id}`, {
        method: 'DELETE'
      });
      await fetchNotifications();
    } catch (error) {
      console.error('Ошибка удаления уведомления:', error);
    }
  };

  // Периодическое обновление счетчика (каждые 30 секунд)
  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 30000);
    return () => clearInterval(interval);
  }, []);

  // Загрузка при открытии
  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
    }
  }, [isOpen, showUnreadOnly]);

  // Форматирование даты
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'только что';
    if (diffMins < 60) return `${diffMins} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    if (diffDays < 7) return `${diffDays} дн назад`;
    
    return date.toLocaleDateString('ru-RU');
  };

  // Иконка по типу уведомления
  const getIcon = (type: string) => {
    switch (type) {
      case 'error':
        return '🚨';
      case 'warning':
        return '⚠️';
      case 'success':
        return '✅';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className="notifications-container">
      {/* Кнопка уведомлений */}
      <button 
        className="notifications-button"
        onClick={() => setIsOpen(!isOpen)}
        title="Уведомления"
      >
        🔔
        {unreadCount > 0 && (
          <span className="notifications-badge">{unreadCount}</span>
        )}
      </button>

      {/* Панель уведомлений */}
      {isOpen && (
        <div className="notifications-panel">
          <div className="notifications-header">
            <h3>Уведомления</h3>
            <div className="notifications-actions">
              <label className="unread-filter">
                <input
                  type="checkbox"
                  checked={showUnreadOnly}
                  onChange={(e) => setShowUnreadOnly(e.target.checked)}
                />
                Непрочитанные
              </label>
              {unreadCount > 0 && (
                <button 
                  className="mark-all-read"
                  onClick={markAllAsRead}
                >
                  Прочитать все
                </button>
              )}
              <button 
                className="close-button"
                onClick={() => setIsOpen(false)}
              >
                ✕
              </button>
            </div>
          </div>

          <div className="notifications-list">
            {loading ? (
              <div className="notifications-loading">Загрузка...</div>
            ) : notifications.length === 0 ? (
              <div className="notifications-empty">
                {showUnreadOnly 
                  ? 'Нет непрочитанных уведомлений'
                  : 'Нет уведомлений'}
              </div>
            ) : (
              notifications.map(notification => (
                <div 
                  key={notification.id}
                  className={`notification-item ${notification.type} ${
                    notification.is_read ? 'read' : 'unread'
                  }`}
                  onClick={() => !notification.is_read && markAsRead(notification.id)}
                >
                  <div className="notification-icon">
                    {getIcon(notification.type)}
                  </div>
                  <div className="notification-content">
                    <div className="notification-message">
                      {notification.message}
                    </div>
                    <div className="notification-time">
                      {formatDate(notification.created_at)}
                    </div>
                  </div>
                  <button
                    className="notification-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteNotification(notification.id);
                    }}
                    title="Удалить"
                  >
                    🗑️
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Notifications;
