# -*- coding: utf-8 -*-
"""Генератор мок-данных для IntegrityOS"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Настройки генерации
NUM_OBJECTS = 800  # Увеличено с 150
NUM_DIAGNOSTICS = 10000  # Увеличено с 2000

# Казахстанские города и координаты для трубопроводов
PIPELINES = {
    "MT-01": {
        "name": "Атырау - Самара",
        "start": {"lat": 46.92, "lon": 51.88, "city": "Атырау"},
        "end": {"lat": 53.20, "lon": 50.15, "city": "Самара"},
        "length_km": 695,
        "diameter_mm": 720,
        "year_built": 1972
    },
    "MT-02": {
        "name": "Узень - Атырау",
        "start": {"lat": 43.22, "lon": 53.60, "city": "Узень"},
        "end": {"lat": 46.92, "lon": 51.88, "city": "Атырау"},
        "length_km": 650,
        "diameter_mm": 530,
        "year_built": 1969
    },
    "MT-03": {
        "name": "Каражанбас - Актау",
        "start": {"lat": 44.63, "lon": 50.85, "city": "Каражанбас"},
        "end": {"lat": 43.65, "lon": 51.16, "city": "Актау"},
        "length_km": 150,
        "diameter_mm": 530,
        "year_built": 1985
    }
}

# Материалы труб
MATERIALS = ["Ст3", "09Г2С", "17Г1С", "10Г2ФБ", "Х70", "Х65"]

# Типы объектов
OBJECT_TYPES = ["pipeline_section", "crane", "compressor"]
OBJECT_TYPE_WEIGHTS = [0.7, 0.2, 0.1]

# Методы диагностики (критичные помечены как приоритетные)
# UZK, RGK, MFL, UTWM, TFI - критичные методы с повышенной точностью
METHODS = ["VIK", "UZK", "MFL", "TFI", "GEO", "MPK", "PVK", "RGK", "TVK", "VIBRO", "UTWM"]
METHOD_WEIGHTS = [0.12, 0.22, 0.25, 0.10, 0.06, 0.04, 0.04, 0.05, 0.03, 0.03, 0.04]
CRITICAL_METHODS = ["UZK", "RGK", "MFL", "UTWM", "TFI"]  # Для ML признака

# Типы дефектов
DEFECT_TYPES = [
    "потеря металла",
    "коррозия", 
    "вмятина",
    "расслоение",
    "трещина",
    "аномалия сварного шва",
    "овальность"
]

DEFECT_IDENTIFICATIONS = ["ЯЗВА", "ОБШР", "ПОКН", "ВМТ", "ТРЩ", "ШОВ", "ОВЛ"]

QUALITY_GRADES = ["удовлетворительно", "допустимо", "требует_мер", "недопустимо"]
QUALITY_WEIGHTS = [0.35, 0.35, 0.20, 0.10]


def interpolate_coords(start, end, ratio):
    """Интерполяция координат вдоль трубопровода"""
    lat = start["lat"] + (end["lat"] - start["lat"]) * ratio
    lon = start["lon"] + (end["lon"] - start["lon"]) * ratio
    return lat, lon


def generate_pipelines_csv():
    """Генерация таблицы трубопроводов"""
    data = []
    for pid, info in PIPELINES.items():
        data.append({
            "pipeline_id": pid,
            "name": info["name"],
            "length_km": info["length_km"],
            "diameter_mm": info["diameter_mm"],
            "start_point": info["start"]["city"],
            "end_point": info["end"]["city"],
            "year_built": info["year_built"],
            "operator": "ТОО КазТрансОйл"
        })
    return pd.DataFrame(data)


def generate_objects_csv():
    """Генерация таблицы объектов контроля"""
    data = []
    object_id = 1
    
    for pid, info in PIPELINES.items():
        # Количество объектов на трубопровод пропорционально длине
        n_objects = int(NUM_OBJECTS * (info["length_km"] / sum(p["length_km"] for p in PIPELINES.values())))
        
        for i in range(n_objects):
            ratio = i / max(n_objects - 1, 1)
            lat, lon = interpolate_coords(info["start"], info["end"], ratio)
            
            # Добавляем небольшой шум к координатам
            lat += random.uniform(-0.05, 0.05)
            lon += random.uniform(-0.05, 0.05)
            
            obj_type = random.choices(OBJECT_TYPES, OBJECT_TYPE_WEIGHTS)[0]
            
            # Генерируем название
            if obj_type == "pipeline_section":
                name = f"Участок {pid} км {int(ratio * info['length_km'])}"
            elif obj_type == "crane":
                name = f"Кран шаровой №{object_id}"
            else:
                name = f"Компрессорная станция №{object_id}"
            
            data.append({
                "object_id": object_id,
                "object_name": name,
                "object_type": obj_type,
                "pipeline_id": pid,
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "year": random.randint(1965, 2020),
                "material": random.choice(MATERIALS)
            })
            object_id += 1
    
    return pd.DataFrame(data)


def calculate_ml_label(depth_percent, erf_value, quality_grade):
    """Рассчитать метку критичности для ML"""
    # Rule-based логика
    if quality_grade == "недопустимо" or depth_percent > 50 or (erf_value and erf_value > 0.7):
        return "high"
    elif quality_grade == "требует_мер" or depth_percent > 30 or (erf_value and erf_value > 0.5):
        return "medium"
    else:
        return "normal"


def generate_diagnostics_csv(objects_df):
    """Генерация таблицы диагностик"""
    data = []
    diag_id = 1
    
    for _ in range(NUM_DIAGNOSTICS):
        obj = objects_df.sample(1).iloc[0]
        method = random.choices(METHODS, METHOD_WEIGHTS)[0]
        
        # Дата диагностики (последние 10 лет)
        days_ago = random.randint(0, 3650)
        date = datetime.now() - timedelta(days=days_ago)
        
        # Условия обследования
        temperature = round(random.uniform(-30, 45), 1)
        humidity = round(random.uniform(20, 95), 1)
        illumination = round(random.uniform(100, 1000), 1)
        
        # Обнаружен ли дефект (60% вероятность)
        defect_found = random.random() < 0.6
        
        if defect_found:
            defect_idx = random.randint(0, len(DEFECT_TYPES) - 1)
            defect_type = DEFECT_TYPES[defect_idx]
            defect_id = DEFECT_IDENTIFICATIONS[min(defect_idx, len(DEFECT_IDENTIFICATIONS) - 1)]
            defect_description = f"{defect_type} - {defect_id}"
            quality_grade = random.choices(QUALITY_GRADES, QUALITY_WEIGHTS)[0]
            
            # Параметры дефекта
            param1 = round(random.uniform(0.5, 60), 2)  # Глубина %
            param2 = round(random.uniform(10, 500), 1)  # Длина мм
            param3 = round(random.uniform(5, 200), 1)   # Ширина мм
            
            # ERF для ML
            erf = random.uniform(0.3, 0.9) if param1 > 20 else random.uniform(0.1, 0.5)
            ml_label = calculate_ml_label(param1, erf, quality_grade)
        else:
            defect_description = None
            quality_grade = "удовлетворительно"
            param1 = None
            param2 = None
            param3 = None
            ml_label = "normal"
        
        data.append({
            "diag_id": diag_id,
            "object_id": obj["object_id"],
            "method": method,
            "date": date.strftime("%Y-%m-%d"),
            "temperature": temperature,
            "humidity": humidity,
            "illumination": illumination,
            "defect_found": defect_found,
            "defect_description": defect_description,
            "quality_grade": quality_grade,
            "param1": param1,
            "param2": param2,
            "param3": param3,
            "ml_label": ml_label
        })
        diag_id += 1
    
    return pd.DataFrame(data)


def main():
    """Генерация всех мок-данных"""
    print("Генерация мок-данных для IntegrityOS...")
    
    # Создаём директорию если не существует
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Генерируем данные
    print("1. Генерация трубопроводов...")
    pipelines_df = generate_pipelines_csv()
    pipelines_df.to_csv(os.path.join(data_dir, "Pipelines.csv"), index=False, encoding="utf-8")
    print(f"   Создано {len(pipelines_df)} трубопроводов")
    
    print("2. Генерация объектов...")
    objects_df = generate_objects_csv()
    objects_df.to_csv(os.path.join(data_dir, "Objects.csv"), index=False, encoding="utf-8")
    print(f"   Создано {len(objects_df)} объектов")
    
    print("3. Генерация диагностик...")
    diagnostics_df = generate_diagnostics_csv(objects_df)
    diagnostics_df.to_csv(os.path.join(data_dir, "Diagnostics.csv"), index=False, encoding="utf-8")
    print(f"   Создано {len(diagnostics_df)} записей диагностик")
    
    # Статистика
    print("\n=== Статистика данных ===")
    print(f"Дефектов найдено: {diagnostics_df['defect_found'].sum()}")
    print(f"Распределение по критичности:")
    print(diagnostics_df['ml_label'].value_counts())
    print(f"\nРаспределение по методам:")
    print(diagnostics_df['method'].value_counts())
    
    print("\n✅ Мок-данные успешно сгенерированы в папке 'data/'")


if __name__ == "__main__":
    main()
