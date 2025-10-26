"""Healing engine orchestration.

Expose a small, framework-agnostic `heal` function that accepts either a
trace path or already-parsed trace data. Returns a structured dict with
diagnosis and suggestions.
"""
from typing import Any, Dict, Optional
from .trace_parser import extract_trace_data
from .dom_analyzer import analyze_dom
from .locator_recovery import suggest_alternative_locator


def heal(trace_path: Optional[str] = None, trace_data: Optional[Any] = None) -> Dict[str, Any]:
    """Attempt to heal from a trace file or trace data.

    Returns a dict with keys: ok (bool), reason (str), selector (opt), suggestions (list)
    """
    trace = trace_data or (extract_trace_data(trace_path) if trace_path else None)
    if not trace:
        return {"ok": False, "reason": "No trace data found", "suggestions": []}

    # Try to extract a broken selector and the DOM snapshot in a defensive way
    broken_selector = None
    html = None
    try:
        # common keys used by Playwright traces / custom traces
        error = trace.get('error') if isinstance(trace, dict) else None
        if error:
            broken_selector = error.get('selector') or error.get('locator')
        snapshot = trace.get('snapshot') if isinstance(trace, dict) else None
        if snapshot:
            html = snapshot.get('dom') or snapshot.get('html')
    except Exception:
        # fallback: try shallow access
        broken_selector = trace.get('error', {}).get('selector') if isinstance(trace, dict) else None
        html = (trace.get('snapshot') or {}).get('dom') if isinstance(trace, dict) else None

    if not html:
        return {"ok": False, "reason": "No DOM snapshot found in trace", "suggestions": []}

    analysis = analyze_dom(html, broken_selector)
    if analysis.get('matches', 0) > 0:
        return {"ok": True, "reason": "Selector found", "selector": broken_selector, "matches": analysis.get('matches'), "samples": analysis.get('samples', [])}

    # propose alternatives
    suggestions = suggest_alternative_locator(html, broken_selector)
    return {"ok": False, "reason": "Selector not found", "selector": broken_selector, "suggestions": suggestions, "analysis": analysis}