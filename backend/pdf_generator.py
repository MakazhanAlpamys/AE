# -*- coding: utf-8 -*-
"""
Генератор PDF отчетов с использованием ReportLab
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Frame, PageTemplate, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
from datetime import datetime
from io import BytesIO


def transliterate(text):
    """Транслитерация кириллицы в латиницу для PDF"""
    translit_map = {
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya',
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        '№': 'No.', '—': '-', '–': '-'
    }
    result = ''
    for char in str(text):
        result += translit_map.get(char, char)
    return result

def register_fonts():
    """Регистрация шрифтов для поддержки кириллицы"""
    # Используем стандартные шрифты с транслитерацией
    return 'Helvetica'


def generate_pdf_report(pipelines_df, objects_df, diagnostics_df, pipeline_id=None):
    """Генерация PDF отчета"""
    
    # Создаем буфер для PDF
    buffer = BytesIO()
    
    # Настройка документа
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Регистрация шрифтов
    font_name = register_fonts()
    
    # Стили
    styles = getSampleStyleSheet()
    
    # Заголовок
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name if font_name != 'Helvetica' else 'Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        leading=28
    )
    
    # Подзаголовок
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    # Заголовок секции
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName=font_name if font_name != 'Helvetica' else 'Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        spaceBefore=20,
        leading=20
    )
    
    # Обычный текст
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14
    )
    
    # Фильтрация данных
    if pipeline_id:
        obj_ids = objects_df[objects_df["pipeline_id"] == pipeline_id]["object_id"].tolist()
        diags = diagnostics_df[diagnostics_df["object_id"].isin(obj_ids)].copy()
        pipeline_name = pipelines_df[pipelines_df["pipeline_id"] == pipeline_id]["name"].values[0]
        title_text = f"Report: {transliterate(pipeline_name)} ({pipeline_id})"
    else:
        diags = diagnostics_df.copy()
        title_text = "IntegrityOS General Report"
    
    # Статистика
    total_inspections = len(diags)
    total_defects = int(diags["defect_found"].sum())
    defect_rate = round(total_defects / total_inspections * 100, 2) if total_inspections > 0 else 0
    
    risk_normal = int((diags["ml_label"] == "normal").sum())
    risk_medium = int((diags["ml_label"] == "medium").sum())
    risk_high = int((diags["ml_label"] == "high").sum())
    
    # Содержимое документа
    story = []
    
    # Заголовок
    story.append(Paragraph(title_text, title_style))
    story.append(Paragraph(f"Data sozdaniya: {datetime.now().strftime('%d.%m.%Y %H:%M')}", subtitle_style))
    story.append(Spacer(1, 10*mm))
    
    # Ключевые показатели
    story.append(Paragraph("Key Metrics", section_style))
    
    stats_data = [
        ['Metric', 'Value'],
        ['Total Inspections', str(total_inspections)],
        ['Defects Found', str(total_defects)],
        ['Defect Rate', f"{defect_rate}%"],
        ['Low Risk', str(risk_normal)],
        ['Medium Risk', str(risk_medium)],
        ['High Risk', str(risk_high)]
    ]
    
    stats_table = Table(stats_data, colWidths=[80*mm, 80*mm])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), font_name if font_name != 'Helvetica' else 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 10*mm))
    
    # Дефекты высокого риска
    high_risk_defects = diags[diags["ml_label"] == "high"].copy()
    high_risk_defects = high_risk_defects.merge(
        objects_df[["object_id", "object_name", "pipeline_id"]], 
        on="object_id", 
        how="left"
    )
    high_risk_defects = high_risk_defects.sort_values("date", ascending=False).head(20)
    
    if len(high_risk_defects) > 0:
        story.append(Paragraph(f"High Risk Defects (TOP-{len(high_risk_defects)})", section_style))
        
        defects_data = [['Date', 'Object', 'Method', 'Description']]
        
        for _, row in high_risk_defects.iterrows():
            defects_data.append([
                str(row.get('date', '-'))[:10],
                transliterate(str(row.get('object_name', '-')))[:35],
                str(row.get('method', '-')),
                transliterate(str(row.get('defect_description', '-')))[:45]
            ])
        
        defects_table = Table(defects_data, colWidths=[28*mm, 55*mm, 22*mm, 65*mm])
        defects_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), font_name if font_name != 'Helvetica' else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')])
        ]))
        
        story.append(defects_table)
        story.append(Spacer(1, 10*mm))
    
    # Топ объектов по дефектам
    defects_by_object = diags[diags["defect_found"] == True].groupby("object_id").size().reset_index(name="defect_count")
    defects_by_object = defects_by_object.sort_values("defect_count", ascending=False).head(10)
    defects_by_object = defects_by_object.merge(
        objects_df[["object_id", "object_name", "object_type", "pipeline_id"]], 
        on="object_id"
    )
    
    if len(defects_by_object) > 0:
        story.append(PageBreak())
        story.append(Paragraph("TOP-10 Objects by Defect Count", section_style))
        
        objects_data = [['Object', 'Type', 'Pipeline', 'Defects']]
        
        for _, row in defects_by_object.iterrows():
            object_type_map = {
                'crane': 'Crane',
                'compressor': 'Compressor',
                'pipeline_section': 'Pipeline Section'
            }
            objects_data.append([
                transliterate(str(row.get('object_name', '-')))[:40],
                object_type_map.get(str(row.get('object_type', '-')), str(row.get('object_type', '-'))),
                str(row.get('pipeline_id', '-')),
                str(row.get('defect_count', 0))
            ])
        
        objects_table = Table(objects_data, colWidths=[75*mm, 35*mm, 30*mm, 25*mm])
        objects_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 0), (3, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), font_name if font_name != 'Helvetica' else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), font_name),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        
        story.append(objects_table)
    
    # Footer
    story.append(Spacer(1, 15*mm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"IntegrityOS - Pipeline Monitoring System | {datetime.now().year}", footer_style))
    
    # Генерация PDF
    doc.build(story)
    
    # Возвращаем буфер
    buffer.seek(0)
    return buffer
