# -*- coding: utf-8 -*-
"""
Модуль предиктивной аналитики - прогнозирование будущих дефектов
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sklearn.linear_model import LinearRegression


class PredictiveAnalytics:
    """Предиктивная аналитика для прогнозирования дефектов"""
    
    def __init__(self):
        self.model = LinearRegression()
        
    def predict_next_failure(self, diagnostics_df: pd.DataFrame, object_id: int) -> Dict:
        """
        Предсказание следующего критического дефекта для объекта
        
        Args:
            diagnostics_df: DataFrame с историей диагностик
            object_id: ID объекта для анализа
            
        Returns:
            Dict с прогнозом
        """
        # Фильтруем данные по объекту
        obj_data = diagnostics_df[diagnostics_df['object_id'] == object_id].copy()
        
        if len(obj_data) < 3:
            return {
                'status': 'insufficient_data',
                'message': 'Недостаточно данных для прогноза (нужно минимум 3 обследования)',
                'next_inspection_date': None,
                'risk_probability': 0,
                'recommended_method': None
            }
        
        # Сортируем по дате
        obj_data['date'] = pd.to_datetime(obj_data['date'])
        obj_data = obj_data.sort_values('date')
        
        # Анализ тренда глубины дефектов
        defect_data = obj_data[obj_data['defect_found'] == True].copy()
        
        if len(defect_data) == 0:
            # Нет дефектов - низкий риск
            last_inspection = obj_data['date'].max()
            next_date = last_inspection + timedelta(days=365)
            
            return {
                'status': 'success',
                'next_inspection_date': next_date.strftime('%Y-%m-%d'),
                'risk_probability': 0.05,
                'recommended_method': 'VIK',
                'trend': 'stable',
                'message': 'Объект в хорошем состоянии. Плановое обследование через год.'
            }
        
        # Подготовка данных для регрессии
        defect_data['days_since_start'] = (defect_data['date'] - defect_data['date'].min()).dt.days
        
        X = defect_data[['days_since_start']].values
        y = defect_data['param1'].fillna(0).values  # Глубина дефекта
        
        if len(X) < 2:
            # Только один дефект
            last_inspection = obj_data['date'].max()
            next_date = last_inspection + timedelta(days=180)
            
            return {
                'status': 'success',
                'next_inspection_date': next_date.strftime('%Y-%m-%d'),
                'risk_probability': 0.3,
                'recommended_method': 'UZK',
                'trend': 'unknown',
                'message': 'Обнаружен дефект. Рекомендуется повторное обследование через 6 месяцев.'
            }
        
        # Обучаем модель линейной регрессии
        self.model.fit(X, y)
        
        # Коэффициент тренда
        slope = self.model.coef_[0]
        
        # Предсказываем на 365 дней вперед
        last_day = X[-1][0]
        future_days = last_day + 365
        predicted_depth = self.model.predict([[future_days]])[0]
        
        # Определяем тренд
        if slope > 0.01:
            trend = 'increasing'
            message = '⚠️ Обнаружена тенденция к ухудшению состояния'
        elif slope < -0.01:
            trend = 'decreasing'
            message = '✅ Состояние стабилизируется'
        else:
            trend = 'stable'
            message = '📊 Состояние стабильное'
        
        # Расчет вероятности критического дефекта
        current_depth = y[-1]
        
        if predicted_depth > 50 or current_depth > 40:
            risk_probability = 0.85
            days_until_inspection = 90  # 3 месяца
            recommended_method = 'UZK'
            message = '🚨 ВЫСОКИЙ РИСК! Требуется срочное обследование'
        elif predicted_depth > 30 or current_depth > 25:
            risk_probability = 0.65
            days_until_inspection = 180  # 6 месяцев
            recommended_method = 'UZK'
            message = '⚠️ Средний риск. Требуется внеплановое обследование'
        else:
            risk_probability = 0.25
            days_until_inspection = 365  # 1 год
            recommended_method = 'VIK'
            message = '✅ Низкий риск. Плановое обследование'
        
        last_inspection = obj_data['date'].max()
        next_date = last_inspection + timedelta(days=days_until_inspection)
        
        return {
            'status': 'success',
            'next_inspection_date': next_date.strftime('%Y-%m-%d'),
            'risk_probability': round(risk_probability, 2),
            'recommended_method': recommended_method,
            'trend': trend,
            'message': message,
            'current_depth': round(current_depth, 2),
            'predicted_depth': round(max(0, predicted_depth), 2),
            'slope': round(slope, 4),
            'defect_count': len(defect_data),
            'last_inspection': last_inspection.strftime('%Y-%m-%d')
        }
    
    def get_pipeline_forecast(self, diagnostics_df: pd.DataFrame, objects_df: pd.DataFrame, 
                              pipeline_id: str) -> Dict:
        """
        Прогноз для всего трубопровода
        
        Args:
            diagnostics_df: DataFrame с диагностиками
            objects_df: DataFrame с объектами
            pipeline_id: ID трубопровода
            
        Returns:
            Dict с прогнозом по трубопроводу
        """
        # Объекты на этом трубопроводе
        pipeline_objects = objects_df[objects_df['pipeline_id'] == pipeline_id]['object_id'].tolist()
        
        if not pipeline_objects:
            return {
                'status': 'error',
                'message': 'Нет объектов на этом трубопроводе'
            }
        
        # Диагностики для этих объектов
        pipeline_diags = diagnostics_df[diagnostics_df['object_id'].isin(pipeline_objects)].copy()
        
        if len(pipeline_diags) == 0:
            return {
                'status': 'error',
                'message': 'Нет данных диагностик для этого трубопровода'
            }
        
        # Статистика
        total_objects = len(pipeline_objects)
        defect_objects = len(pipeline_diags[pipeline_diags['defect_found'] == True]['object_id'].unique())
        defect_rate = defect_objects / total_objects if total_objects > 0 else 0
        
        # Критичные объекты
        critical_objects = []
        for obj_id in pipeline_objects:
            prediction = self.predict_next_failure(diagnostics_df, obj_id)
            if prediction['status'] == 'success' and prediction['risk_probability'] > 0.6:
                critical_objects.append({
                    'object_id': obj_id,
                    'risk': prediction['risk_probability'],
                    'next_inspection': prediction['next_inspection_date']
                })
        
        # Сортируем по риску
        critical_objects.sort(key=lambda x: x['risk'], reverse=True)
        
        # Прогноз на следующий год
        pipeline_diags['date'] = pd.to_datetime(pipeline_diags['date'])
        recent_diags = pipeline_diags[pipeline_diags['date'] > (datetime.now() - timedelta(days=365))]
        
        defects_last_year = len(recent_diags[recent_diags['defect_found'] == True])
        
        # Простой прогноз: предполагаем, что тренд сохранится
        predicted_defects_next_year = int(defects_last_year * 1.1)  # +10% на износ
        
        return {
            'status': 'success',
            'pipeline_id': pipeline_id,
            'total_objects': total_objects,
            'defect_rate': round(defect_rate, 2),
            'critical_objects_count': len(critical_objects),
            'critical_objects': critical_objects[:10],  # Топ-10
            'defects_last_year': defects_last_year,
            'predicted_defects_next_year': predicted_defects_next_year,
            'recommendation': self._get_pipeline_recommendation(defect_rate, len(critical_objects))
        }
    
    def _get_pipeline_recommendation(self, defect_rate: float, critical_count: int) -> str:
        """Рекомендация для трубопровода"""
        if defect_rate > 0.5 or critical_count > 10:
            return '🚨 Требуется масштабная программа ремонтов и замен'
        elif defect_rate > 0.3 or critical_count > 5:
            return '⚠️ Необходимо усиленное внимание и внеплановые обследования'
        elif defect_rate > 0.15:
            return '📊 Штатный режим эксплуатации с регулярным мониторингом'
        else:
            return '✅ Трубопровод в хорошем состоянии'
    
    def get_top_risks(self, diagnostics_df: pd.DataFrame, objects_df: pd.DataFrame, 
                      limit: int = 20) -> List[Dict]:
        """
        Получить топ объектов по риску
        
        Args:
            diagnostics_df: DataFrame с диагностиками
            objects_df: DataFrame с объектами
            limit: Количество объектов в топе
            
        Returns:
            Список объектов с прогнозами, отсортированный по риску
        """
        all_objects = objects_df['object_id'].unique()
        
        risks = []
        for obj_id in all_objects:
            prediction = self.predict_next_failure(diagnostics_df, obj_id)
            
            if prediction['status'] == 'success':
                obj_info = objects_df[objects_df['object_id'] == obj_id].iloc[0]
                
                risks.append({
                    'object_id': int(obj_id),
                    'object_name': obj_info['object_name'],
                    'object_type': obj_info['object_type'],
                    'pipeline_id': obj_info['pipeline_id'],
                    'risk_probability': prediction['risk_probability'],
                    'next_inspection_date': prediction['next_inspection_date'],
                    'recommended_method': prediction['recommended_method'],
                    'trend': prediction['trend'],
                    'message': prediction['message'],
                    'current_depth': prediction.get('current_depth', 0),
                    'predicted_depth': prediction.get('predicted_depth', 0)
                })
        
        # Сортируем по риску
        risks.sort(key=lambda x: x['risk_probability'], reverse=True)
        
        return risks[:limit]
