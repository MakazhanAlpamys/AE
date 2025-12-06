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
        """Подготовка признаков для модели"""
        features = []
        
        for _, row in df.iterrows():
            # Используем параметры дефекта
            param1 = row.get("param1", 0) if pd.notna(row.get("param1")) else 0
            param2 = row.get("param2", 0) if pd.notna(row.get("param2")) else 0
            param3 = row.get("param3", 0) if pd.notna(row.get("param3")) else 0
            
            # Кодируем качественную оценку
            quality_grade = row.get("quality_grade", "удовлетворительно")
            quality_score = {
                "удовлетворительно": 0,
                "допустимо": 1,
                "требует_мер": 2,
                "недопустимо": 3
            }.get(quality_grade, 0)
            
            # Признак наличия дефекта
            defect_found = 1 if row.get("defect_found", False) else 0
            
            features.append([
                param1,  # Глубина/процент потери металла
                param2,  # Длина дефекта
                param3,  # Ширина дефекта
                quality_score,  # Оценка качества
                defect_found  # Наличие дефекта
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
        """Предсказание критичности для нового дефекта"""
        if not self.is_trained:
            # Fallback на rule-based классификацию
            return self.rule_based_classification(data)
        
        # Подготовка признаков
        param1 = data.get("param1", 0)
        param2 = data.get("param2", 0)
        param3 = data.get("param3", 0)
        quality_grade = data.get("quality_grade", "удовлетворительно")
        defect_found = data.get("defect_found", False)
        
        quality_score = {
            "удовлетворительно": 0,
            "допустимо": 1,
            "требует_мер": 2,
            "недопустимо": 3
        }.get(quality_grade, 0)
        
        defect_score = 1 if defect_found else 0
        
        X = np.array([[param1, param2, param3, quality_score, defect_score]])
        
        # Предсказание
        pred_class = self.model.predict(X)[0]
        pred_proba = self.model.predict_proba(X)[0]
        
        label = self.label_encoder.inverse_transform([pred_class])[0]
        
        # Вероятности для каждого класса
        probabilities = {}
        for i, class_label in enumerate(self.label_encoder.classes_):
            probabilities[class_label] = float(pred_proba[i])
        
        return {
            "ml_label": label,
            "confidence": float(max(pred_proba)),
            "probabilities": probabilities,
            "method": "machine_learning"
        }
    
    def rule_based_classification(self, data):
        """Rule-based классификация (fallback)"""
        param1 = data.get("param1", 0)
        quality_grade = data.get("quality_grade", "удовлетворительно")
        defect_found = data.get("defect_found", False)
        
        if not defect_found:
            return {
                "ml_label": "normal",
                "confidence": 0.95,
                "method": "rule_based"
            }
        
        # Логика классификации
        if quality_grade == "недопустимо" or param1 > 50:
            label = "high"
            confidence = 0.9
        elif quality_grade == "требует_мер" or param1 > 30:
            label = "medium"
            confidence = 0.8
        else:
            label = "normal"
            confidence = 0.7
        
        return {
            "ml_label": label,
            "confidence": confidence,
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
