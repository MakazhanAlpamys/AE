# -*- coding: utf-8 -*-
"""
ML модуль для классификации критичности дефектов
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle


class MLClassifier:
    """Классификатор критичности дефектов"""
    
    def __init__(self):
        self.model = None
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
    def prepare_features(self, df):
        """Подготовка признаков для модели - 15 признаков для высокой точности"""
        features = []
        
        # Критичные методы контроля
        critical_methods = ['UZK', 'RGK', 'MFL', 'UTWM', 'TFI']
        
        for _, row in df.iterrows():
            # Базовые параметры дефекта
            param1 = row.get("param1", 0) if pd.notna(row.get("param1")) else 0  # Глубина
            param2 = row.get("param2", 0) if pd.notna(row.get("param2")) else 0  # Длина
            param3 = row.get("param3", 0) if pd.notna(row.get("param3")) else 0  # Ширина
            
            # Качественная оценка (1-4)
            quality_grade = row.get("quality_grade", "удовлетворительно")
            quality_score = {
                "удовлетворительно": 1,
                "допустимо": 2,
                "требует_мер": 3,
                "недопустимо": 4
            }.get(quality_grade, 1)
            
            # Признак наличия дефекта
            defect_found = 1 if row.get("defect_found", False) else 0
            
            # НОВЫЕ ПРИЗНАКИ для повышения точности
            # 1. Площадь дефекта
            defect_area = param2 * param3 if (param2 > 0 and param3 > 0) else 0
            
            # 2. Объем дефекта (приближенный)
            defect_volume = param1 * param2 * param3 if (param1 > 0 and param2 > 0 and param3 > 0) else 0
            
            # 3. Критичность метода контроля
            method = row.get("method", "VIK")
            is_critical_method = 1 if method in critical_methods else 0
            
            # 4. Температурные условия (нормализованные)
            temperature = row.get("temperature", 0) if pd.notna(row.get("temperature")) else 0
            temp_normalized = (temperature + 50) / 100  # Нормализация от -50 до +50
            
            # 5. Влажность (нормализованная)
            humidity = row.get("humidity", 0) if pd.notna(row.get("humidity")) else 0
            humidity_normalized = humidity / 100
            
            # 6. Освещенность (для методов визуального контроля)
            illumination = row.get("illumination", 0) if pd.notna(row.get("illumination")) else 0
            illumination_normalized = illumination / 1000
            
            # 7. Соотношение глубины к площади (критичный показатель)
            depth_to_area_ratio = param1 / (defect_area + 1) if defect_area > 0 else 0
            
            # 8. Индекс формы дефекта (длина/ширина)
            shape_index = param2 / param3 if param3 > 0 else 1
            
            # 9. Критичность по глубине (процент от толщины стенки)
            is_deep_defect = 1 if param1 > 30 else 0  # Более 30% потери металла
            
            # 10. Критичность по размеру
            is_large_defect = 1 if defect_area > 10000 else 0  # Более 100x100 мм
            
            features.append([
                param1,                    # 1. Глубина дефекта (%)
                param2,                    # 2. Длина дефекта (мм)
                param3,                    # 3. Ширина дефекта (мм)
                quality_score,             # 4. Оценка качества (1-4)
                defect_found,              # 5. Наличие дефекта
                defect_area,               # 6. Площадь дефекта
                defect_volume,             # 7. Объем дефекта
                is_critical_method,        # 8. Критичный метод
                temp_normalized,           # 9. Температура (норм)
                humidity_normalized,       # 10. Влажность (норм)
                illumination_normalized,   # 11. Освещенность (норм)
                depth_to_area_ratio,       # 12. Глубина/площадь
                shape_index,               # 13. Форма дефекта
                is_deep_defect,            # 14. Глубокий дефект
                is_large_defect            # 15. Большой дефект
            ])
        
        return np.array(features)
    
    def train(self, diagnostics_df):
        """Обучение модели на исторических данных"""
        # Фильтруем только записи с дефектами для обучения
        df = diagnostics_df[diagnostics_df["defect_found"] == True].copy()
        
        if len(df) < 10:
            print("⚠️ Недостаточно данных для обучения ML модели")
            self.is_trained = False
            return
        
        # Подготовка данных
        X = self.prepare_features(df)
        y = self.label_encoder.fit_transform(df["ml_label"])
        
        # Разделение на train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Обучение Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight="balanced"
        )
        
        self.model.fit(X_train, y_train)
        
        # Оценка точности
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        print(f"✅ ML модель обучена: train_acc={train_score:.3f}, test_acc={test_score:.3f}")
        self.is_trained = True
        
        return {
            "train_accuracy": train_score,
            "test_accuracy": test_score,
            "n_samples": len(df),
            "classes": self.label_encoder.classes_.tolist()
        }
    
    def predict(self, data):
        """Предсказание критичности для нового дефекта с вероятностями"""
        if not self.is_trained:
            # Fallback на rule-based классификацию
            result = self.rule_based_classification(data)
            result["probabilities"] = {result["prediction"]: 1.0}  # 100% уверенность для rule-based
            result["confidence"] = 100.0
            return result
        
        # Подготовка всех 15 признаков
        param1 = data.get("param1", 0)
        param2 = data.get("param2", 0)
        param3 = data.get("param3", 0)
        quality_grade = data.get("quality_grade", "удовлетворительно")
        defect_found = data.get("defect_found", False)
        method = data.get("method", "VIK")
        temperature = data.get("temperature", 0)
        humidity = data.get("humidity", 0)
        illumination = data.get("illumination", 0)
        
        quality_score = {
            "удовлетворительно": 1,
            "допустимо": 2,
            "требует_мер": 3,
            "недопустимо": 4
        }.get(quality_grade, 1)
        
        defect_score = 1 if defect_found else 0
        
        # Расчет дополнительных признаков (как в prepare_features)
        critical_methods = ['UZK', 'RGK', 'MFL', 'UTWM', 'TFI']
        
        defect_area = param2 * param3 if (param2 > 0 and param3 > 0) else 0
        defect_volume = param1 * param2 * param3 if (param1 > 0 and param2 > 0 and param3 > 0) else 0
        is_critical_method = 1 if method in critical_methods else 0
        temp_normalized = (temperature + 50) / 100
        humidity_normalized = humidity / 100
        illumination_normalized = illumination / 1000
        depth_to_area_ratio = param1 / (defect_area + 1) if defect_area > 0 else 0
        shape_index = param2 / param3 if param3 > 0 else 1
        is_deep_defect = 1 if param1 > 30 else 0
        is_large_defect = 1 if defect_area > 10000 else 0
        
        X = np.array([[
            param1, param2, param3, quality_score, defect_score,
            defect_area, defect_volume, is_critical_method,
            temp_normalized, humidity_normalized, illumination_normalized,
            depth_to_area_ratio, shape_index, is_deep_defect, is_large_defect
        ]])
        
        # Предсказание
        pred_class = self.model.predict(X)[0]
        pred_proba = self.model.predict_proba(X)[0]
        
        label = self.label_encoder.inverse_transform([pred_class])[0]
        
        # Вероятности для каждого класса
        probabilities = {}
        for i, class_label in enumerate(self.label_encoder.classes_):
            probabilities[class_label] = float(pred_proba[i] * 100)  # В процентах
        
        # Уверенность модели (макс. вероятность)
        confidence = float(max(pred_proba) * 100)
        
        return {
            "prediction": label,
            "ml_label": label,
            "probabilities": probabilities,
            "confidence": round(confidence, 2),
            "model_type": "ml",
            "method": "machine_learning"
        }
    
    def rule_based_classification(self, data):
        """Rule-based классификация (fallback)"""
        param1 = data.get("param1", 0)
        quality_grade = data.get("quality_grade", "удовлетворительно")
        defect_found = data.get("defect_found", False)
        
        if not defect_found:
            return {
                "prediction": "normal",
                "ml_label": "normal",
                "confidence": 95.0,
                "model_type": "rule_based",
                "method": "rule_based"
            }
        
        # Логика классификации
        if quality_grade == "недопустимо" or param1 > 50:
            label = "high"
            confidence = 90.0
        elif quality_grade == "требует_мер" or param1 > 30:
            label = "medium"
            confidence = 80.0
        else:
            label = "normal"
            confidence = 70.0
        
        return {
            "prediction": label,
            "ml_label": label,
            "confidence": confidence,
            "model_type": "rule_based",
            "method": "rule_based"
        }
    
    def get_feature_importance(self):
        """Получить важность признаков"""
        if not self.is_trained or self.model is None:
            return None
        
        feature_names = ["param1 (глубина)", "param2 (длина)", "param3 (ширина)", 
                        "quality_score", "defect_found"]
        
        importances = self.model.feature_importances_
        
        return {
            name: float(imp) 
            for name, imp in zip(feature_names, importances)
        }
