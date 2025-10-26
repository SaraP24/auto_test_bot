"""DOM analysis helpers.

Provide small, testable utilities to check whether a selector exists and
to return lightweight metadata about candidate elements. These helpers are
framework-agnostic and accept raw HTML or a BeautifulSoup object.
"""
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)


def to_soup(html_or_soup: Union[str, BeautifulSoup]) -> BeautifulSoup:
    if isinstance(html_or_soup, BeautifulSoup):
        return html_or_soup
    return BeautifulSoup(html_or_soup or "", 'html.parser')


def analyze_dom(html_content: Union[str, BeautifulSoup], expected_selector: str) -> Dict[str, Optional[Union[int, List[Dict[str, str]]]]]:
    """Return analysis for `expected_selector` in the provided HTML.

    Returns a dict with keys:
    - matches: number of matching elements
    - samples: small list of candidate element summaries (tag, text, id, classes)
    - selector: the selector queried
    """
    try:
        soup = to_soup(html_content)
        if not expected_selector:
            logging.info("No selector provided to analyze_dom")
            return {"selector": expected_selector, "matches": 0, "samples": []}

        candidates = soup.select(expected_selector)
        samples: List[Dict[str, str]] = []
        for el in candidates[:5]:
            samples.append({
                "tag": el.name or '',
                "text": (el.get_text(strip=True)[:120] if el.get_text() else ''),
                "id": el.get('id', ''),
                "class": ' '.join(el.get('class', [])) if el.get('class') else ''
            })

        logging.info(f"Found {len(candidates)} elements matching '{expected_selector}'")
        return {"selector": expected_selector, "matches": len(candidates), "samples": samples}
    except Exception as e:
        logging.exception(f"Error analyzing DOM: {e}")
        return {"selector": expected_selector, "matches": 0, "samples": []}