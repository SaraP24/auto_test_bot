"""Trace parsing helpers.

Provide utilities to extract trace data from Playwright trace zip files or
from other archive formats. Return a structured dict (or None).
"""
import zipfile
import json
import logging
from typing import Optional, Any

logging.basicConfig(level=logging.INFO)


def extract_trace_data(trace_path: str) -> Optional[Any]:
    """Try to extract and parse JSON-like trace content from a trace zip file.

    Returns parsed JSON-like object or None if nothing found.
    """
    try:
        with zipfile.ZipFile(trace_path, 'r') as zip_ref:
            # Search for likely JSON files inside the trace archive
            for name in zip_ref.namelist():
                lower = name.lower()
                if lower.endswith('.json') or lower.endswith('trace.trace') or 'metadata' in lower:
                    try:
                        with zip_ref.open(name) as f:
                            data = f.read()
                        # try decode as utf-8 and json parse
                        try:
                            text = data.decode('utf-8')
                            return json.loads(text)
                        except Exception:
                            # not JSON text, skip
                            continue
                    except Exception as e:
                        logging.debug(f"Failed to open or read {name}: {e}")
                        continue
            logging.info('No JSON-like trace found in archive')
    except Exception as e:
        logging.exception(f'Error reading trace archive: {e}')
    return None