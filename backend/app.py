# -*- coding: utf-8 -*-
"""
IntegrityOS Backend API
FastAPI приложение для работы с данными трубопроводов
"""

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from typing import Optional, List
import pandas as pd
import os
from datetime import datetime
import uvicorn

from ml_model import MLClassifier
from report_generator import generate_html_report
from pdf_generator import generate_pdf_report
from notifications import notification_manager, NotificationType
from import_handler import DataImporter
from predictive_analytics import PredictiveAnalytics

app = FastAPI(title="IntegrityOS API", version="1.0.0")

# CORS для работы с frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальные переменные для хранения данных
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
pipelines_df = None
objects_df = None
diagnostics_df = None
ml_classifier = None
data_importer = DataImporter(DATA_DIR)
predictive_analytics = PredictiveAnalytics()


def validate_data():
    """Валидация загруженных данных согласно ТЗ"""
    errors = []
    
    # Проверка Objects
    if objects_df.empty:
        errors.append("Objects.csv пуст")
    else:
        required_cols = ["object_id", "object_name", "pipeline_id", "lat", "lon"]
        missing = [c for c in required_cols if c not in objects_df.columns]
        if missing:
            errors.append(f"Objects.csv: отсутствуют колонки {missing}")
        
        # Проверка на дубликаты object_id
        duplicates = objects_df["object_id"].duplicated().sum()
        if duplicates > 0:
            errors.append(f"Objects.csv: найдено {duplicates} дубликатов object_id")
    
    # Проверка Diagnostics
    if diagnostics_df.empty:
        errors.append("Diagnostics.csv пуст")
    else:
        required_cols = ["diag_id", "object_id", "method", "date"]
        missing = [c for c in required_cols if c not in diagnostics_df.columns]
        if missing:
            errors.append(f"Diagnostics.csv: отсутствуют колонки {missing}")
        
        # Проверка method
        valid_methods = ["VIK", "PVK", "MPK", "UZK", "RGK", "TVK", "VIBRO", "MFL", "TFI", "GEO", "UTWM"]
        invalid_methods = diagnostics_df[~diagnostics_df["method"].isin(valid_methods)]
        if len(invalid_methods) > 0:
            errors.append(f"Diagnostics.csv: найдено {len(invalid_methods)} записей с некорректным method")
        
        # Проверка дат
        try:
            pd.to_datetime(diagnostics_df["date"])
        except:
            errors.append("Diagnostics.csv: некорректный формат дат")
        
        # Проверка связей object_id
        orphans = diagnostics_df[~diagnostics_df["object_id"].isin(objects_df["object_id"])]
        if len(orphans) > 0:
            errors.append(f"Diagnostics.csv: найдено {len(orphans)} записей с несуществующим object_id")
    
    if errors:
        print("⚠️ Обнаружены ошибки валидации:")
        for err in errors:
            print(f"  - {err}")
    else:
        print("✅ Валидация данных прошла успешно")
    
    return errors


def load_data():
    """Загрузка CSV данных в память"""
    global pipelines_df, objects_df, diagnostics_df, ml_classifier
    
    try:
        pipelines_df = pd.read_csv(os.path.join(DATA_DIR, "Pipelines.csv"))
        objects_df = pd.read_csv(os.path.join(DATA_DIR, "Objects.csv"))
        diagnostics_df = pd.read_csv(os.path.join(DATA_DIR, "Diagnostics.csv"))
        
        print(f"✅ Загружено: {len(pipelines_df)} трубопроводов, {len(objects_df)} объектов, {len(diagnostics_df)} диагностик")
        
        # Валидация данных
        validation_errors = validate_data()
        
        # Инициализация ML модели
        ml_classifier = MLClassifier()
        ml_classifier.train(diagnostics_df)
        
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        raise


# Загрузка данных при старте
load_data()


@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "IntegrityOS API",
        "version": "1.0.0",
        "endpoints": {
            "pipelines": "/api/pipelines",
            "objects": "/api/objects",
            "diagnostics": "/api/diagnostics",
            "dashboard": "/api/dashboard",
            "report": "/api/report"
        }
    }


@app.get("/api/pipelines")
async def get_pipelines():
    """Получить список всех трубопроводов"""
    return pipelines_df.to_dict(orient="records")


@app.get("/api/objects")
async def get_objects(
    pipeline_id: Optional[str] = Query(None, description="Фильтр по трубопроводу"),
    object_type: Optional[str] = Query(None, description="Фильтр по типу объекта")
):
    """Получить список объектов с фильтрацией"""
    df = objects_df.copy()
    
    if pipeline_id:
        df = df[df["pipeline_id"] == pipeline_id]
    
    if object_type:
        df = df[df["object_type"] == object_type]
    
    return df.to_dict(orient="records")


@app.get("/api/objects/{object_id}")
async def get_object_detail(object_id: int):
    """Получить детальную информацию об объекте"""
    obj = objects_df[objects_df["object_id"] == object_id]
    
    if obj.empty:
        raise HTTPException(status_code=404, detail="Объект не найден")
    
    # Получаем диагностики для этого объекта
    diags = diagnostics_df[diagnostics_df["object_id"] == object_id].copy()
    
    if len(diags) == 0:
        # Если нет диагностик, возвращаем минимальные данные
        obj_dict = obj.to_dict(orient="records")[0]
        obj_clean = {k: (None if pd.isna(v) or v in [float('inf'), float('-inf')] else v) 
                     for k, v in obj_dict.items()}
        
        return {
            "object": obj_clean,
            "diagnostics": [],
            "history": [],
            "total_inspections": 0,
            "defects_count": 0
        }
    
    diags = diags.sort_values("date", ascending=False)
    
    # История диагностик по годам
    try:
        diags_with_year = diags.copy()
        diags_with_year["year"] = pd.to_datetime(diags_with_year["date"]).dt.year
        history = diags_with_year.groupby("year").agg({
            "diag_id": "count",
            "defect_found": "sum",
            "ml_label": lambda x: (x == "high").sum()
        }).reset_index()
        history.columns = ["year", "total_inspections", "defects_found", "high_risk"]
        
        # Очистка от NaN
        history = history.fillna(0)
        history = history.replace([float('inf'), float('-inf')], 0)
    except Exception as e:
        print(f"Ошибка создания истории: {e}")
        history = pd.DataFrame(columns=["year", "total_inspections", "defects_found", "high_risk"])
    
    # Очистка данных объекта
    obj_dict = obj.to_dict(orient="records")[0]
    obj_clean = {k: (None if pd.isna(v) or v in [float('inf'), float('-inf')] else v) 
                 for k, v in obj_dict.items()}
    
    # Очистка диагностик
    diags_list = diags.to_dict(orient="records")
    diags_clean = [
        {k: (None if pd.isna(v) or v in [float('inf'), float('-inf')] else v) 
         for k, v in record.items()}
        for record in diags_list
    ]
    
    # Подсчет дефектов
    defects_count = int(diags["defect_found"].sum()) if "defect_found" in diags.columns else 0
    
    return {
        "object": obj_clean,
        "diagnostics": diags_clean,
        "history": history.to_dict(orient="records"),
        "total_inspections": len(diags),
        "defects_count": defects_count
    }


@app.get("/api/diagnostics")
async def get_diagnostics(
    object_id: Optional[int] = Query(None, description="Фильтр по объекту"),
    method: Optional[str] = Query(None, description="Фильтр по методу контроля"),
    pipeline_id: Optional[str] = Query(None, description="Фильтр по трубопроводу"),
    ml_label: Optional[str] = Query(None, description="Фильтр по критичности"),
    defect_only: Optional[bool] = Query(False, description="Только дефекты"),
    date_from: Optional[str] = Query(None, description="Дата начала (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Дата окончания (YYYY-MM-DD)"),
    limit: Optional[int] = Query(1000, description="Макс. количество записей")
):
    """Получить список диагностик с фильтрацией"""
    df = diagnostics_df.copy()
    
    # Применяем фильтры
    if object_id:
        df = df[df["object_id"] == object_id]
    
    if method:
        df = df[df["method"] == method]
    
    if ml_label:
        df = df[df["ml_label"] == ml_label]
    
    if defect_only:
        df = df[df["defect_found"] == True]
    
    if pipeline_id:
        # Джойн с objects для фильтрации по трубопроводу
        obj_ids = objects_df[objects_df["pipeline_id"] == pipeline_id]["object_id"].tolist()
        df = df[df["object_id"].isin(obj_ids)]
    
    if date_from:
        df = df[df["date"] >= date_from]
    
    if date_to:
        df = df[df["date"] <= date_to]
    
    # Сортировка по дате (новые первыми)
    df = df.sort_values("date", ascending=False)
    
    # Ограничение количества
    df = df.head(limit)
    
    # Добавляем информацию об объектах
    df = df.merge(objects_df[["object_id", "object_name", "lat", "lon", "pipeline_id"]], 
                  on="object_id", how="left")
    
    # Замена NaN/Inf на None
    df = df.replace([float('inf'), float('-inf')], None)
    df = df.where(pd.notnull(df), None)
    
    return {
        "total": len(df),
        "data": df.to_dict(orient="records")
    }


@app.get("/api/dashboard")
async def get_dashboard_stats():
    """Получить статистику для дашборда"""
    
    # Базовая статистика
    total_objects = len(objects_df)
    total_inspections = len(diagnostics_df)
    total_defects = int(diagnostics_df["defect_found"].sum())
    
    # Распределение по методам
    methods_stats = diagnostics_df["method"].value_counts().to_dict()
    
    # Распределение по критичности
    risk_stats = diagnostics_df["ml_label"].value_counts().to_dict()
    
    # Распределение по типам дефектов (только где есть дефекты)
    defects_df = diagnostics_df[diagnostics_df["defect_found"] == True]
    quality_stats = defects_df["quality_grade"].value_counts().to_dict()
    
    # Топ-5 объектов с наибольшим количеством дефектов
    top_defects = defects_df.groupby("object_id").size().reset_index(name="count")
    top_defects = top_defects.sort_values("count", ascending=False).head(5)
    top_defects = top_defects.merge(objects_df[["object_id", "object_name", "pipeline_id"]], 
                                    on="object_id")
    top_defects = top_defects.where(pd.notnull(top_defects), None)
    
    # Топ-5 высокорисковых объектов
    high_risk = diagnostics_df[diagnostics_df["ml_label"] == "high"]
    top_risks = high_risk.groupby("object_id").size().reset_index(name="count")
    top_risks = top_risks.sort_values("count", ascending=False).head(5)
    top_risks = top_risks.merge(objects_df[["object_id", "object_name", "pipeline_id"]], 
                               on="object_id")
    top_risks = top_risks.where(pd.notnull(top_risks), None)
    
    # Распределение по годам
    diagnostics_df["year"] = pd.to_datetime(diagnostics_df["date"]).dt.year
    years_stats = diagnostics_df.groupby("year").agg({
        "diag_id": "count",
        "defect_found": "sum"
    }).reset_index()
    years_stats.columns = ["year", "inspections", "defects"]
    years_stats = years_stats.sort_values("year")
    years_stats = years_stats.where(pd.notnull(years_stats), None)
    
    # Статистика по трубопроводам
    pipeline_stats = []
    for _, pipeline in pipelines_df.iterrows():
        pid = pipeline["pipeline_id"]
        obj_ids = objects_df[objects_df["pipeline_id"] == pid]["object_id"].tolist()
        diags = diagnostics_df[diagnostics_df["object_id"].isin(obj_ids)]
        
        pipeline_stats.append({
            "pipeline_id": pid,
            "name": pipeline["name"],
            "objects_count": len(obj_ids),
            "inspections_count": len(diags),
            "defects_count": int(diags["defect_found"].sum()),
            "high_risk_count": int((diags["ml_label"] == "high").sum())
        })
    
    return {
        "summary": {
            "total_objects": total_objects,
            "total_inspections": total_inspections,
            "total_defects": total_defects,
            "defect_rate": round(total_defects / total_inspections * 100, 2)
        },
        "methods": methods_stats,
        "risk_levels": risk_stats,
        "quality_grades": quality_stats,
        "top_defect_objects": top_defects.to_dict(orient="records"),
        "top_risk_objects": top_risks.to_dict(orient="records"),
        "yearly_trend": years_stats.to_dict(orient="records"),
        "pipelines": pipeline_stats
    }


@app.get("/api/map-data")
async def get_map_data(
    pipeline_id: Optional[str] = Query(None, description="Фильтр по трубопроводу"),
    ml_label: Optional[str] = Query(None, description="Фильтр по критичности"),
    method: Optional[str] = Query(None, description="Фильтр по методу"),
    defect_only: Optional[bool] = Query(True, description="Только дефекты")
):
    """Получить данные для отображения на карте"""
    
    # Фильтруем диагностики
    df = diagnostics_df.copy()
    
    if defect_only:
        df = df[df["defect_found"] == True]
    
    if method:
        df = df[df["method"] == method]
    
    if ml_label:
        df = df[df["ml_label"] == ml_label]
    
    # Джойним с объектами для получения координат
    df = df.merge(objects_df[["object_id", "object_name", "object_type", "lat", "lon", "pipeline_id"]], 
                  on="object_id", how="left")
    
    if pipeline_id:
        df = df[df["pipeline_id"] == pipeline_id]
    
    # Группируем по объектам (берем последнюю диагностику)
    df = df.sort_values("date", ascending=False)
    df = df.drop_duplicates(subset=["object_id"], keep="first")
    
    # Замена NaN/Inf на None
    df = df.replace([float('inf'), float('-inf')], None)
    df = df.where(pd.notnull(df), None)
    
    # Формируем точки для карты
    points = []
    for _, row in df.iterrows():
        points.append({
            "object_id": int(row["object_id"]),
            "object_name": row["object_name"],
            "object_type": row["object_type"],
            "pipeline_id": row["pipeline_id"],
            "lat": float(row["lat"]) if row["lat"] is not None else 0,
            "lon": float(row["lon"]) if row["lon"] is not None else 0,
            "ml_label": row["ml_label"],
            "method": row["method"],
            "date": row["date"],
            "defect_description": row["defect_description"],
            "quality_grade": row["quality_grade"]
        })
    
    # Данные трубопроводов для отрисовки линий
    pipeline_lines = []
    for _, pipeline in pipelines_df.iterrows():
        pid = pipeline["pipeline_id"]
        
        # Получаем объекты этого трубопровода
        pipe_objects = objects_df[objects_df["pipeline_id"] == pid].sort_values("object_id")
        
        if len(pipe_objects) > 0:
            coordinates = []
            for _, obj in pipe_objects.iterrows():
                coordinates.append([float(obj["lat"]), float(obj["lon"])])
            
            pipeline_lines.append({
                "pipeline_id": pid,
                "name": pipeline["name"],
                "coordinates": coordinates
            })
    
    return {
        "points": points,
        "pipelines": pipeline_lines,
        "total_points": len(points)
    }


@app.post("/api/ml/predict")
async def predict_criticality(data: dict):
    """Предсказание критичности дефекта с помощью ML"""
    try:
        prediction = ml_classifier.predict(data)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/report", response_class=HTMLResponse)
async def generate_report(
    pipeline_id: Optional[str] = Query(None, description="Фильтр по трубопроводу")
):
    """Генерация HTML отчета"""
    try:
        html = generate_html_report(
            pipelines_df, 
            objects_df, 
            diagnostics_df,
            pipeline_id
        )
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/pdf")
async def generate_pdf_report_endpoint(
    pipeline_id: Optional[str] = Query(None, description="Фильтр по трубопроводу")
):
    """Генерация PDF отчета"""
    try:
        pdf_buffer = generate_pdf_report(
            pipelines_df, 
            objects_df, 
            diagnostics_df,
            pipeline_id
        )
        
        filename = f"IntegrityOS_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Создаем уведомление об успешной генерации PDF
        notification_manager.create_report_notification("PDF", pipeline_id)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== NOTIFICATIONS API ====================

@app.get("/api/notifications")
async def get_notifications(
    unread_only: bool = Query(False, description="Только непрочитанные"),
    limit: Optional[int] = Query(None, description="Лимит записей")
):
    """Получение списка уведомлений"""
    try:
        notifications = notification_manager.get_notifications(
            unread_only=unread_only,
            limit=limit
        )
        return {
            "notifications": notifications,
            "total": len(notifications),
            "unread_count": notification_manager.get_unread_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notifications/unread-count")
async def get_unread_count():
    """Получение количества непрочитанных уведомлений"""
    try:
        return {
            "unread_count": notification_manager.get_unread_count()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notifications/{notification_id}/read")
async def mark_notification_as_read(notification_id: int):
    """Пометить уведомление как прочитанное"""
    try:
        success = notification_manager.mark_as_read(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Уведомление не найдено")
        
        return {
            "success": True,
            "message": "Уведомление отмечено как прочитанное"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notifications/read-all")
async def mark_all_as_read():
    """Пометить все уведомления как прочитанные"""
    try:
        count = notification_manager.mark_all_as_read()
        return {
            "success": True,
            "marked_count": count,
            "message": f"Отмечено {count} уведомлений"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/notifications/{notification_id}")
async def delete_notification(notification_id: int):
    """Удаление уведомления"""
    try:
        success = notification_manager.delete_notification(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Уведомление не найдено")
        
        return {
            "success": True,
            "message": "Уведомление удалено"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notifications/create")
async def create_notification(
    message: str = Query(..., description="Текст уведомления"),
    notification_type: str = Query("info", description="Тип уведомления"),
):
    """Создание нового уведомления (для тестирования)"""
    try:
        notification = notification_manager.create_notification(
            message=message,
            notification_type=NotificationType(notification_type)
        )
        return {
            "success": True,
            "notification": notification
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== IMPORT API ====================

@app.post("/api/import/objects")
async def import_objects(file: UploadFile = File(...)):
    """Импорт таблицы объектов из CSV/XLSX"""
    try:
        # Проверка формата файла
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            raise HTTPException(
                status_code=400,
                detail="Неподдерживаемый формат. Используйте CSV или XLSX"
            )
        
        # Читаем содержимое
        content = await file.read()
        
        # Импортируем
        result = data_importer.import_objects(content, file.filename)
        
        # Если успешно - перезагружаем данные
        if result['success']:
            load_data()
            notification_manager.create_notification(
                message=f"Импортировано {result['rows_imported']} объектов из {file.filename}",
                notification_type=NotificationType.SUCCESS
            )
        else:
            notification_manager.create_notification(
                message=f"Ошибка импорта {file.filename}: {'; '.join(result['errors'][:2])}",
                notification_type=NotificationType.ERROR
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка импорта: {str(e)}")


@app.post("/api/import/diagnostics")
async def import_diagnostics(file: UploadFile = File(...)):
    """Импорт таблицы диагностик из CSV/XLSX"""
    try:
        # Проверка формата файла
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            raise HTTPException(
                status_code=400,
                detail="Неподдерживаемый формат. Используйте CSV или XLSX"
            )
        
        # Читаем содержимое
        content = await file.read()
        
        # Импортируем
        result = data_importer.import_diagnostics(content, file.filename)
        
        # Если успешно - перезагружаем данные
        if result['success']:
            load_data()
            
            # Переобучаем ML модель
            global ml_classifier
            ml_classifier = MLClassifier()
            ml_classifier.train(diagnostics_df)
            
            notification_manager.create_notification(
                message=f"Импортировано {result['rows_imported']} диагностик из {file.filename}. ML модель переобучена.",
                notification_type=NotificationType.SUCCESS
            )
        else:
            notification_manager.create_notification(
                message=f"Ошибка импорта {file.filename}: {'; '.join(result['errors'][:2])}",
                notification_type=NotificationType.ERROR
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка импорта: {str(e)}")


@app.get("/api/import/log")
async def get_import_log():
    """Получить историю импорта файлов"""
    try:
        return {
            "log": data_importer.get_import_log()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/import/validate-preview")
async def validate_and_preview(file: UploadFile = File(...)):
    """Предпросмотр файла перед импортом (первые 10 строк)"""
    try:
        content = await file.read()
        
        # Читаем файл
        if file.filename.endswith('.csv'):
            import io
            df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Неподдерживаемый формат")
        
        return {
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "preview": df.head(10).to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения файла: {str(e)}")


# ============================================
# PREDICTIVE ANALYTICS ENDPOINTS
# ============================================

@app.get("/api/predictions/object/{object_id}")
async def predict_object_failure(object_id: int):
    """Прогноз для конкретного объекта"""
    try:
        prediction = predictive_analytics.predict_next_failure(diagnostics_df, object_id)
        
        if prediction['status'] == 'success':
            # Добавляем информацию об объекте
            obj_info = objects_df[objects_df['object_id'] == object_id]
            if not obj_info.empty:
                obj_data = obj_info.iloc[0]
                prediction['object_name'] = obj_data['object_name']
                prediction['object_type'] = obj_data['object_type']
                prediction['pipeline_id'] = obj_data['pipeline_id']
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predictions/pipeline/{pipeline_id}")
async def predict_pipeline_status(pipeline_id: str):
    """Прогноз для всего трубопровода"""
    try:
        forecast = predictive_analytics.get_pipeline_forecast(
            diagnostics_df, objects_df, pipeline_id
        )
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predictions/top-risks")
async def get_top_risks(limit: int = Query(20, ge=1, le=100)):
    """Топ объектов по риску"""
    try:
        risks = predictive_analytics.get_top_risks(
            diagnostics_df, objects_df, limit
        )
        return {
            "total": len(risks),
            "risks": risks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predictions/dashboard")
async def get_predictions_dashboard():
    """Общая статистика для дашборда прогнозов"""
    try:
        # Топ-10 рисков
        top_risks = predictive_analytics.get_top_risks(diagnostics_df, objects_df, 10)
        
        # Статистика по трубопроводам
        pipeline_forecasts = []
        for _, pipeline in pipelines_df.iterrows():
            forecast = predictive_analytics.get_pipeline_forecast(
                diagnostics_df, objects_df, pipeline['pipeline_id']
            )
            if forecast['status'] == 'success':
                pipeline_forecasts.append({
                    'pipeline_id': pipeline['pipeline_id'],
                    'pipeline_name': pipeline['name'],
                    'critical_count': forecast['critical_objects_count'],
                    'defect_rate': forecast['defect_rate'],
                    'predicted_defects': forecast['predicted_defects_next_year']
                })
        
        # Общая статистика
        high_risk_count = len([r for r in top_risks if r['risk_probability'] > 0.6])
        medium_risk_count = len([r for r in top_risks if 0.3 < r['risk_probability'] <= 0.6])
        
        return {
            "top_risks": top_risks,
            "pipeline_forecasts": pipeline_forecasts,
            "summary": {
                "high_risk_objects": high_risk_count,
                "medium_risk_objects": medium_risk_count,
                "total_analyzed": len(objects_df)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
