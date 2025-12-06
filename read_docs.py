# -*- coding: utf-8 -*-
import os
from docx import Document

data_path = r"c:\Users\tokmo\Integrity Хакатон\Данные"

docx_files = [f for f in os.listdir(data_path) if f.endswith('.docx')]

for docx_file in docx_files:
    filepath = os.path.join(data_path, docx_file)
    print(f"\n{'='*80}")
    print(f"FILE: {docx_file}")
    print('='*80)
    try:
        doc = Document(filepath)
        for i, para in enumerate(doc.paragraphs[:80]):
            if para.text.strip():
                print(para.text)
    except Exception as e:
        print(f"Error reading file: {e}")
