# -*- coding: utf-8 -*-
import pandas as pd
import os

path = r"c:\Users\tokmo\Integrity Хакатон\Данные"
xlsx_files = [f for f in os.listdir(path) if f.endswith('.xlsx')]

if xlsx_files:
    filepath = os.path.join(path, xlsx_files[0])
    xls = pd.ExcelFile(filepath)
    
    # Read each sheet
    for sheet in xls.sheet_names:
        print(f"\n{'='*60}")
        print(f"SHEET: {sheet}")
        print('='*60)
        df = pd.read_excel(filepath, sheet_name=sheet)
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()[:10]}...")
        print(df.head(10).to_string())
