import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class NotificationManager:
    def __init__(self, storage_file: str = "data/notifications.json"):
        self.storage_file = storage_file
        self.notifications: List[Dict] = []
        self.load_notifications()
    
    def load_notifications(self):
        """Загрузка уведомлений из файла"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.notifications = json.load(f)
            except Exception as e:
                print(f"Ошибка загрузки уведомлений: {e}")
                self.notifications = []
        else:
            self.notifications = []
    
    def save_notifications(self):
        """Сохранение уведомлений в файл"""
        try:
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.notifications, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения уведомлений: {e}")
    
    def create_notification(
        self,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Создание нового уведомления"""
        notification = {
            "id": len(self.notifications) + 1,
            "message": message,
            "type": notification_type.value,
            "is_read": False,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.notifications.insert(0, notification)  # Добавляем в начало списка
        self.save_notifications()
        
        return notification
    
    def get_notifications(
        self,
        unread_only: bool = False,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """Получение списка уведомлений"""
        notifications = self.notifications
        
        if unread_only:
            notifications = [n for n in notifications if not n.get("is_read", False)]
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Пометить уведомление как прочитанное"""
        for notification in self.notifications:
            if notification["id"] == notification_id:
                notification["is_read"] = True
                self.save_notifications()
                return True
        return False
    
    def mark_all_as_read(self) -> int:
        """Пометить все уведомления как прочитанные"""
        count = 0
        for notification in self.notifications:
            if not notification.get("is_read", False):
                notification["is_read"] = True
                count += 1
        
        if count > 0:
            self.save_notifications()
        
        return count
    
    def delete_notification(self, notification_id: int) -> bool:
        """Удаление уведомления"""
        initial_count = len(self.notifications)
        self.notifications = [n for n in self.notifications if n["id"] != notification_id]
        
        if len(self.notifications) < initial_count:
            self.save_notifications()
            return True
        return False
    
    def get_unread_count(self) -> int:
        """Получение количества непрочитанных уведомлений"""
        return len([n for n in self.notifications if not n.get("is_read", False)])
    
    def create_defect_alert(self, pipeline_id: str, object_id: str, risk_level: str):
        """Специальный метод для уведомлений о дефектах"""
        message = f"Обнаружен дефект на трубопроводе {pipeline_id}, объект {object_id}"
        
        notification_type = NotificationType.INFO
        if risk_level == "high":
            notification_type = NotificationType.ERROR
            message += " (КРИТИЧЕСКИЙ УРОВЕНЬ РИСКА)"
        elif risk_level == "medium":
            notification_type = NotificationType.WARNING
            message += " (средний уровень риска)"
        
        return self.create_notification(
            message=message,
            notification_type=notification_type,
            metadata={
                "pipeline_id": pipeline_id,
                "object_id": object_id,
                "risk_level": risk_level,
                "category": "defect_detection"
            }
        )
    
    def create_report_notification(self, report_type: str, pipeline_id: str):
        """Уведомление о создании отчета"""
        return self.create_notification(
            message=f"Отчет ({report_type}) для трубопровода {pipeline_id} успешно создан",
            notification_type=NotificationType.SUCCESS,
            metadata={
                "pipeline_id": pipeline_id,
                "report_type": report_type,
                "category": "report_generation"
            }
        )
    
    def create_ml_training_notification(self, accuracy: float, features_count: int):
        """Уведомление об обучении ML модели"""
        return self.create_notification(
            message=f"ML модель обучена. Точность: {accuracy:.2%}, признаков: {features_count}",
            notification_type=NotificationType.SUCCESS,
            metadata={
                "accuracy": accuracy,
                "features_count": features_count,
                "category": "ml_training"
            }
        )

# Глобальный экземпляр менеджера уведомлений
notification_manager = NotificationManager()
