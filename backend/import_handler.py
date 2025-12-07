# -*- coding: utf-8 -*-
"""
Модуль импорта CSV/XLSX файлов с валидацией
"""

import pandas as pd
import os
from datetime import datetime
from typing import Dict, List, Tuple
import io


class ImportValidator:
    """Валидатор данных при импорте"""
    
    REQUIRED_COLUMNS = {
        'objects': ['object_id', 'object_name', 'object_type', 'pipeline_id', 'lat', 'lon'],
        'diagnostics': ['diag_id', 'object_id', 'method', 'date', 'defect_found']
    }
    
    VALID_OBJECT_TYPES = ['crane', 'compressor', 'pipeline_section']
    VALID_METHODS = ['VIK', 'UZK', 'MFL', 'TFI', 'GEO', 'MPK', 'PVK', 'RGK', 'TVK', 'VIBRO', 'UTWM', 'AE', 'TOFD']
    VALID_QUALITY_GRADES = ['удовлетворительно', 'допустимо', 'требует_мер', 'недопустимо']
    VALID_ML_LABELS = ['normal', 'medium', 'high']
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_objects(self, df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        """Валидация таблицы объектов"""
        self.errors = []
        self.warnings = []
        
        # Проверка обязательных колонок
        missing_cols = set(self.REQUIRED_COLUMNS['objects']) - set(df.columns)
        if missing_cols:
            found_cols = ', '.join(df.columns.tolist())
            self.errors.append(
                f"❌ Отсутствуют обязательные колонки: {', '.join(missing_cols)}\n"
                f"📋 Найденные колонки в файле: {found_cols}\n"
                f"💡 Скачайте шаблон и проверьте названия колонок (регистр важен!)"
            )
            return False, self.errors, self.warnings
        
        # Проверка уникальности object_id
        if df['object_id'].duplicated().any():
            duplicates = df[df['object_id'].duplicated()]['object_id'].tolist()
            self.errors.append(f"Дублирующиеся object_id: {duplicates[:5]}")
        
        # Проверка типов объектов
        invalid_types = df[~df['object_type'].isin(self.VALID_OBJECT_TYPES)]['object_type'].unique()
        if len(invalid_types) > 0:
            self.warnings.append(f"Неизвестные типы объектов: {list(invalid_types)}")
        
        # Проверка координат
        if ((df['lat'] < -90) | (df['lat'] > 90)).any():
            self.errors.append("Некорректные значения широты (должны быть от -90 до 90)")
        
        if ((df['lon'] < -180) | (df['lon'] > 180)).any():
            self.errors.append("Некорректные значения долготы (должны быть от -180 до 180)")
        
        # Проверка на пустые значения
        null_counts = df[self.REQUIRED_COLUMNS['objects']].isnull().sum()
        if null_counts.any():
            for col, count in null_counts[null_counts > 0].items():
                self.warnings.append(f"Колонка '{col}' содержит {count} пустых значений")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def validate_diagnostics(self, df: pd.DataFrame, objects_df: pd.DataFrame = None) -> Tuple[bool, List[str], List[str]]:
        """Валидация таблицы диагностик"""
        self.errors = []
        self.warnings = []
        
        # Проверка обязательных колонок
        missing_cols = set(self.REQUIRED_COLUMNS['diagnostics']) - set(df.columns)
        if missing_cols:
            found_cols = ', '.join(df.columns.tolist())
            self.errors.append(
                f"❌ Отсутствуют обязательные колонки: {', '.join(missing_cols)}\n"
                f"📋 Найденные колонки в файле: {found_cols}\n"
                f"💡 Скачайте шаблон и проверьте названия колонок (регистр важен!)"
            )
            return False, self.errors, self.warnings
        
        # Проверка уникальности diag_id
        if df['diag_id'].duplicated().any():
            duplicates = df[df['diag_id'].duplicated()]['diag_id'].tolist()
            self.errors.append(f"Дублирующиеся diag_id: {duplicates[:5]}")
        
        # Проверка методов контроля
        invalid_methods = df[~df['method'].isin(self.VALID_METHODS)]['method'].unique()
        if len(invalid_methods) > 0:
            self.warnings.append(f"Неизвестные методы: {list(invalid_methods)}")
        
        # Проверка дат
        try:
            pd.to_datetime(df['date'], errors='coerce')
            invalid_dates = df['date'].isna().sum()
            if invalid_dates > 0:
                self.warnings.append(f"Некорректных дат: {invalid_dates}")
        except Exception:
            self.errors.append("Не удалось распознать формат дат")
        
        # Проверка качественной оценки
        if 'quality_grade' in df.columns:
            invalid_grades = df[~df['quality_grade'].isin(self.VALID_QUALITY_GRADES)]['quality_grade'].unique()
            if len(invalid_grades) > 0:
                self.warnings.append(f"Неизвестные оценки качества: {list(invalid_grades)}")
        
        # Проверка ml_label
        if 'ml_label' in df.columns:
            invalid_labels = df[~df['ml_label'].isin(self.VALID_ML_LABELS)]['ml_label'].unique()
            if len(invalid_labels) > 0:
                self.warnings.append(f"Неизвестные метки ML: {list(invalid_labels)}")
        
        # Проверка связи с объектами
        if objects_df is not None:
            valid_object_ids = set(objects_df['object_id'].values)
            invalid_refs = df[~df['object_id'].isin(valid_object_ids)]['object_id'].unique()
            if len(invalid_refs) > 0:
                self.errors.append(f"Ссылки на несуществующие object_id: {list(invalid_refs)[:10]}")
        
        # Проверка параметров дефектов
        if 'defect_found' in df.columns:
            defect_rows = df[df['defect_found'] == True]
            if len(defect_rows) > 0:
                if 'param1' in df.columns and defect_rows['param1'].isna().sum() > 0:
                    self.warnings.append(f"У дефектов отсутствует param1: {defect_rows['param1'].isna().sum()} записей")
        
        return len(self.errors) == 0, self.errors, self.warnings


class DataImporter:
    """Импортер данных из CSV/XLSX"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.validator = ImportValidator()
        self.import_log = []
    
    def read_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Чтение файла (CSV или XLSX)"""
        try:
            if filename.endswith('.csv'):
                # Пробуем разные кодировки и очищаем BOM
                for encoding in ['utf-8-sig', 'utf-8', 'cp1251', 'latin1']:
                    try:
                        df = pd.read_csv(io.BytesIO(file_content), encoding=encoding)
                        # Очищаем названия колонок от пробелов и невидимых символов
                        df.columns = df.columns.str.strip().str.replace('\ufeff', '').str.replace('\u200b', '')
                        return df
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue
                raise ValueError("Не удалось прочитать CSV файл. Проверьте кодировку.")
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(file_content))
                # Очищаем названия колонок
                df.columns = df.columns.str.strip().str.replace('\ufeff', '').str.replace('\u200b', '')
                return df
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {filename}")
        except Exception as e:
            raise ValueError(f"Ошибка чтения файла: {str(e)}")
    
    def import_objects(self, file_content: bytes, filename: str) -> Dict:
        """Импорт таблицы объектов"""
        result = {
            'success': False,
            'rows_imported': 0,
            'errors': [],
            'warnings': [],
            'preview': []
        }
        
        try:
            # Читаем файл
            df = self.read_file(file_content, filename)
            result['preview'] = df.head(10).to_dict('records')
            
            # Валидация
            is_valid, errors, warnings = self.validator.validate_objects(df)
            result['errors'] = errors
            result['warnings'] = warnings
            
            if not is_valid:
                self.import_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'file': filename,
                    'status': 'FAILED',
                    'errors': errors
                })
                return result
            
            # Сохраняем в data/
            output_path = os.path.join(self.data_dir, "Objects.csv")
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            result['success'] = True
            result['rows_imported'] = len(df)
            
            self.import_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': filename,
                'status': 'SUCCESS',
                'rows': len(df)
            })
            
        except Exception as e:
            result['errors'].append(f"Критическая ошибка: {str(e)}")
            self.import_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': filename,
                'status': 'ERROR',
                'error': str(e)
            })
        
        return result
    
    def import_diagnostics(self, file_content: bytes, filename: str) -> Dict:
        """Импорт таблицы диагностик"""
        result = {
            'success': False,
            'rows_imported': 0,
            'errors': [],
            'warnings': [],
            'preview': []
        }
        
        try:
            # Читаем файл
            df = self.read_file(file_content, filename)
            result['preview'] = df.head(10).to_dict('records')
            
            # Загружаем существующие объекты для проверки связей
            objects_path = os.path.join(self.data_dir, "Objects.csv")
            objects_df = None
            if os.path.exists(objects_path):
                objects_df = pd.read_csv(objects_path)
            
            # Валидация
            is_valid, errors, warnings = self.validator.validate_diagnostics(df, objects_df)
            result['errors'] = errors
            result['warnings'] = warnings
            
            if not is_valid:
                self.import_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'file': filename,
                    'status': 'FAILED',
                    'errors': errors
                })
                return result
            
            # Сохраняем в data/
            output_path = os.path.join(self.data_dir, "Diagnostics.csv")
            df.to_csv(output_path, index=False, encoding='utf-8')
            
            result['success'] = True
            result['rows_imported'] = len(df)
            
            self.import_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': filename,
                'status': 'SUCCESS',
                'rows': len(df)
            })
            
        except Exception as e:
            result['errors'].append(f"Критическая ошибка: {str(e)}")
            self.import_log.append({
                'timestamp': datetime.now().isoformat(),
                'file': filename,
                'status': 'ERROR',
                'error': str(e)
            })
        
        return result
    
    def get_import_log(self) -> List[Dict]:
        """Получить историю импорта"""
        return self.import_log
