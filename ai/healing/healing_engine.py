# Orquesta todo: recibe la traza, analiza el DOM, propone fixes

from bs4 import BeautifulSoup
from .trace_parser import extract_trace_data
from .dom_analyzer import analyze_dom
from .locator_recovery import suggest_alternative_locator

def heal(trace_path):
    trace = extract_trace_data(trace_path)
    if not trace:
        return "No trace data found."

    broken_selector = trace.get('error', {}).get('selector')
    html = trace.get('snapshot', {}).get('dom')

    if not analyze_dom(html, broken_selector):
        soup = BeautifulSoup(html, 'html.parser')
        suggestion = suggest_alternative_locator(soup, broken_selector)
        return f"Selector roto: {broken_selector}\nSugerencia: {suggestion}"
    return "No se detectaron problemas con el selector."