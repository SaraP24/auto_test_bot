"""Locator recovery helpers.

Provide functions that, given an HTML snapshot (or soup) and a broken selector,
try to propose alternative locators (css selectors or textual heuristics).
"""
from bs4 import BeautifulSoup
from typing import List, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)


def to_soup(html_or_soup: Union[str, BeautifulSoup]) -> BeautifulSoup:
    if isinstance(html_or_soup, BeautifulSoup):
        return html_or_soup
    return BeautifulSoup(html_or_soup or "", 'html.parser')


def suggest_alternative_locator(html_or_soup: Union[str, BeautifulSoup], broken_selector: Optional[str] = None, max_suggestions: int = 5) -> List[str]:
    """Return a list of suggested locators.

    Strategies:
    - suggest elements with similar attributes (id, name, class)
    - suggest by visible text for buttons/links
    - suggest positional selectors as a last resort
    """
    soup = to_soup(html_or_soup)
    suggestions: List[str] = []

    # 1) If broken_selector is provided, try to find nearby elements by tag
    try:
        if broken_selector:
            # try to find elements whose id or class partially matches
            tokens = [t for t in (broken_selector or '').split() if t]
            for token in tokens:
                token = token.strip('.#')
                # id match
                el = soup.find(id=lambda i: i and token in i)
                if el:
                    sel = f"#{el.get('id')}"
                    suggestions.append(sel)
                # class match
                elc = soup.find(class_=lambda c: c and token in ' '.join(c))
                if elc:
                    cls = ' '.join(elc.get('class', [])).split()[0]
                    suggestions.append(f".{cls}")

    except Exception:
        logging.debug("Error searching by broken_selector heuristics", exc_info=True)

    # 2) Suggest by visible text for common tags
    for tag in soup.find_all(['button', 'a', 'input']):
        text = (tag.get_text(strip=True) or tag.get('value') or '').strip()
        if text:
            sel = f"{tag.name}:has-text('{text[:80]}')"
            if sel not in suggestions:
                suggestions.append(sel)
        if len(suggestions) >= max_suggestions:
            break

    # 3) As fallback, give nth-of-type suggestions for first few elements of a tag
    if not suggestions:
        for tag_name in ['button', 'a', 'input', 'div', 'span']:
            els = soup.find_all(tag_name)
            for idx, el in enumerate(els[:3], start=1):
                suggestions.append(f"{tag_name}:nth-of-type({idx})")
            if suggestions:
                break

    return suggestions[:max_suggestions]