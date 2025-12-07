# -*- coding: utf-8 -*-
"""
Генератор HTML отчетов
"""

import pandas as pd
from datetime import datetime


def generate_html_report(pipelines_df, objects_df, diagnostics_df, pipeline_id=None):
    """Генерация HTML отчета"""
    
    # Фильтрация по трубопроводу если указан
    if pipeline_id:
        obj_ids = objects_df[objects_df["pipeline_id"] == pipeline_id]["object_id"].tolist()
        diags = diagnostics_df[diagnostics_df["object_id"].isin(obj_ids)].copy()
        pipeline_name = pipelines_df[pipelines_df["pipeline_id"] == pipeline_id]["name"].values[0]
        title = f"Отчет по трубопроводу {pipeline_name} ({pipeline_id})"
    else:
        diags = diagnostics_df.copy()
        title = "Общий отчет по системе IntegrityOS"
    
    # Статистика
    total_inspections = len(diags)
    total_defects = int(diags["defect_found"].sum())
    defect_rate = round(total_defects / total_inspections * 100, 2) if total_inspections > 0 else 0
    
    # Распределение по критичности
    risk_normal = int((diags["ml_label"] == "normal").sum())
    risk_medium = int((diags["ml_label"] == "medium").sum())
    risk_high = int((diags["ml_label"] == "high").sum())
    
    # Таблица дефектов с высоким риском
    high_risk_defects = diags[diags["ml_label"] == "high"].copy()
    high_risk_defects = high_risk_defects.merge(
        objects_df[["object_id", "object_name", "pipeline_id"]], 
        on="object_id", 
        how="left"
    )
    high_risk_defects = high_risk_defects.sort_values("date", ascending=False).head(20)
    
    # Топ объектов по количеству дефектов
    defects_by_object = diags[diags["defect_found"] == True].groupby("object_id").size().reset_index(name="defect_count")
    defects_by_object = defects_by_object.sort_values("defect_count", ascending=False).head(10)
    defects_by_object = defects_by_object.merge(
        objects_df[["object_id", "object_name", "object_type", "pipeline_id"]], 
        on="object_id"
    )
    
    # Распределение по методам
    methods_stats = diags["method"].value_counts()
    
    # HTML шаблон
    html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
        }}
        
        .header h1 {{
            color: #2c3e50;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .header .date {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-card.green {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        
        .stat-card.yellow {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}
        
        .stat-card.red {{
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }}
        
        .stat-card h3 {{
            font-size: 2.5em;
            margin-bottom: 5px;
        }}
        
        .stat-card p {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .section {{
            margin: 40px 0;
        }}
        
        .section h2 {{
            color: #2c3e50;
            font-size: 1.5em;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
            padding-left: 15px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        thead {{
            background: #1e3a8a;
            color: white;
        }}
        
        th {{
            padding: 14px 12px;
            text-align: left;
            border-bottom: 2px solid #ddd;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-size: 0.9em;
        }}
        
        td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
            color: #1e293b;
            font-weight: 500;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .badge.high {{
            background: #e74c3c;
            color: white;
        }}
        
        .badge.medium {{
            background: #f39c12;
            color: white;
        }}
        
        .badge.normal {{
            background: #2ecc71;
            color: white;
        }}
        
        .methods-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .method-card {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .method-card strong {{
            display: block;
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .recommendation {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        
        .recommendation h3 {{
            color: #856404;
            margin-bottom: 10px;
        }}
        
        @media print {{
            body {{
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p class="date">Дата формирования: {datetime.now().strftime("%d.%m.%Y %H:%M")}</p>
        </div>
        
        <div class="section">
            <h2>📊 Общая статистика</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{total_inspections}</h3>
                    <p>Всего обследований</p>
                </div>
                <div class="stat-card">
                    <h3>{total_defects}</h3>
                    <p>Обнаружено дефектов</p>
                </div>
                <div class="stat-card green">
                    <h3>{risk_normal}</h3>
                    <p>Низкий риск</p>
                </div>
                <div class="stat-card yellow">
                    <h3>{risk_medium}</h3>
                    <p>Средний риск</p>
                </div>
                <div class="stat-card red">
                    <h3>{risk_high}</h3>
                    <p>Высокий риск</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Распределение по методам контроля</h2>
            <div class="methods-grid">
    """
    
    for method, count in methods_stats.items():
        html += f"""
                <div class="method-card">
                    <strong>{count}</strong>
                    <span>{method}</span>
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>⚠️ Дефекты высокого риска</h2>
    """
    
    if len(high_risk_defects) > 0:
        html += """
            <table>
                <thead>
                    <tr>
                        <th>Дата</th>
                        <th>Объект</th>
                        <th>Трубопровод</th>
                        <th>Метод</th>
                        <th>Описание</th>
                        <th>Оценка</th>
                        <th>Риск</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for _, row in high_risk_defects.iterrows():
            html += f"""
                    <tr>
                        <td>{row['date']}</td>
                        <td>{row['object_name']}</td>
                        <td>{row['pipeline_id']}</td>
                        <td>{row['method']}</td>
                        <td>{row['defect_description']}</td>
                        <td>{row['quality_grade']}</td>
                        <td><span class="badge high">HIGH</span></td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        """
    else:
        html += "<p>Дефектов высокого риска не обнаружено.</p>"
    
    html += """
        </div>
        
        <div class="section">
            <h2>📍 Топ-10 объектов по количеству дефектов</h2>
            <table>
                <thead>
                    <tr>
                        <th>Объект</th>
                        <th>Тип</th>
                        <th>Трубопровод</th>
                        <th>Количество дефектов</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for _, row in defects_by_object.iterrows():
        html += f"""
                    <tr>
                        <td>{row['object_name']}</td>
                        <td>{row['object_type']}</td>
                        <td>{row['pipeline_id']}</td>
                        <td><strong>{row['defect_count']}</strong></td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="recommendation">
                <h3>💡 Рекомендации</h3>
                <ul>
    """
    
    if risk_high > 0:
        html += f"<li>Требуется немедленное внимание к {risk_high} объектам с высоким риском</li>"
    
    if risk_medium > 10:
        html += f"<li>Необходим план мероприятий для {risk_medium} объектов со средним риском</li>"
    
    if defect_rate > 50:
        html += f"<li>Высокий процент дефектности ({defect_rate}%) требует системного анализа</li>"
    
    html += """
                    <li>Продолжить регулярные обследования согласно графику</li>
                    <li>Рассмотреть применение дополнительных методов контроля для критичных участков</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Сгенерировано системой IntegrityOS | © 2025</p>
            <p>Все данные являются синтетическими и предназначены для демонстрационных целей</p>
        </div>
    </div>
</body>
</html>
    """
    
    return html
