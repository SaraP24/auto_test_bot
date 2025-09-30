#Extrae información de los archivos .zip de trazas de Playwright.

import zipfile
import json

def extract_trace_data(trace_path):
    with zipfile.ZipFile(trace_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('trace.trace'):
                with zip_ref.open(file) as f:
                    return json.load(f)
    return None