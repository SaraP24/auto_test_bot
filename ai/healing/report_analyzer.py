import json
import xml.etree.ElementTree as ET
import re
from collections import Counter
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


def load_report(path: Optional[str] = None, report_data: Optional[Any] = None, loader: Optional[Callable[[str], Any]] = None):
    """Load a report from path or return already-parsed report_data.

    - If report_data is provided, it is returned as-is.
    - If loader is provided, it will be called with the path and should return parsed data.
    - Otherwise the function will try to infer format from extension (.json or .xml).
    """
    if report_data is not None:
        return report_data
    if path is None:
        raise ValueError("Either path or report_data must be provided")
    if loader:
        return loader(path)
    if path.lower().endswith('.json'):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    if path.lower().endswith(('.xml', '.junit')):
        tree = ET.parse(path)
        return tree.getroot()
    # Fallback: try json
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def default_playwright_extractor(report: Dict) -> Iterable[Tuple[str, str, List[str]]]:
    """Yield tuples of (suite_name, test_title, [error_messages]) from a Playwright JSON report.

    Compatible with the Playwright JSON reporter structure used in this repo.
    """
    for suite in report.get('suites', []):
        suite_name = suite.get('title') or 'suite'
        for spec in suite.get('specs', []):
            test_title = spec.get('title', 'unknown')
            errors = []
            for test in spec.get('tests', []):
                for result in test.get('results', []):
                    for error in result.get('errors', []):
                        # raw message
                        full_msg = error.get('message', '')
                        # strip ANSI sequences and split message vs stack
                        short_msg, stack = _split_message_and_stack(full_msg)
                        err_obj = {
                            'raw': full_msg,
                            'message': short_msg,
                        }
                        if stack:
                            err_obj['stack'] = stack
                        # include any explicit location fields if present
                        if isinstance(error, dict) and error.get('location'):
                            err_obj['location'] = error.get('location')
                        errors.append(err_obj)
            yield (suite_name, test_title, errors)


def junit_xml_extractor(root: ET.Element) -> Iterable[Tuple[str, str, List[str]]]:
    """Basic extractor for JUnit-style XML roots. Yields (suite, testcase, [messages])."""
    # junit xml: <testsuite> contains <testcase> with <failure> or <error>
    for testsuite in root.findall('.//testsuite'):
        suite_name = testsuite.get('name', 'testsuite')
        for testcase in testsuite.findall('testcase'):
            tc_name = testcase.get('name', 'testcase')
            messages = []
            for child in testcase:
                if child.tag in ('failure', 'error'):
                    text = child.text or ''
                    messages.append(text.strip())
            yield (suite_name, tc_name, messages)


DEFAULT_MATCHERS: List[Tuple[re.Pattern, str, str]] = [
    # Selector y localización de elementos
    (re.compile(r'strict mode violation', re.I), 'Broken selector',
     'Use role-based selectors (getByRole) or semantic locators (getByText/getByLabel). Avoid CSS/XPath selectors.'),
    (re.compile(r'(?:could not locate|unable to locate|cannot find|no element)', re.I), 'Element not found',
     'Use data-testid for dynamic elements, aria-labels for accessibility, or semantic locators like getByRole/getByText. Check element visibility state.'),
    (re.compile(r'selector\s+matched\s+(?:multiple|[0-9]+)', re.I), 'Ambiguous selector',
     'Make selectors more specific using getByRole with name/exact options or combine with filters like .filter({ hasText: ... }).'),
    
    # Timeouts y sincronización
    (re.compile(r'timeouterror', re.I), 'Timeout',
     'Add expect().toBeVisible() or expect().toBeEnabled() before interactions. Consider page load states with waitForLoadState().'),
    (re.compile(r'test timeout', re.I), 'Test timeout',
     'Add explicit expectations (expect) before actions. Use waitForLoadState() for navigation. Avoid sleep/fixed timeouts.'),
    (re.compile(r'element\s+not\s+visible', re.I), 'Element visibility',
     'Add expect().toBeVisible() check. For dynamic content, consider waitForSelector with state:"visible" option.'),
    
    # Errores de red y navegación
    (re.compile(r'protocol error', re.I), 'Invalid URL',
     'Configure baseURL in playwright.config.ts. Use relative paths in page.goto(). Consider environment-specific configs in .env correct usage.'),
    (re.compile(r'(?:net::ERR|network error|connection refused)', re.I), 'Network error',
     'Add retry logic for flaky APIs. Use test.fail() for known issues. Consider using API mocking for unstable endpoints.'),
    
    # Errores de estado y datos
    (re.compile(r'undefined', re.I), 'Undefined variable',
     'Use TypeScript for better type safety. Define page objects and interfaces. Consider test data factories.'),
    (re.compile(r'stale\s+element', re.I), 'Stale element',
     'Re-query elements after navigation/updates. Use page object pattern to encapsulate element queries. Add expect() or respective personalized assertions before actions.'),
    
    # Problemas de carga y rendimiento
    (re.compile(r'load\s+timeout', re.I), 'Page load timeout',
     'Use waitForLoadState("networkidle"). Consider lazy loading impact. Monitor network with page.route() for bottlenecks and optimize accordingly.'),
    (re.compile(r'(?:memory|heap|stack)\s+(?:limit|overflow)', re.I), 'Resource limit',
     'Close pages after tests. Use context.clearCookies(). Consider running tests in parallel with test.describe.configure({mode: "parallel"}).'),
    
    # Errores de iframe y contexto
    (re.compile(r'frame(?:detached|error)', re.I), 'Frame handling',
     'Use frameLocator() instead of frame.$(). Wait for frame load with expect(locator).toBeAttached(). Consider frame lifecycle.'),
]


def _parse_location_from_text(text: str) -> Optional[Dict[str, int]]:
    """Try to extract file/line/col from an error text using common patterns.

    Returns a dict like {'file': str, 'line': int, 'col': int} or None.
    This handles typical Node/V8/Playwright stack frames such as:
      at Object.<anonymous> (C:/path/to/file.ts:17:23)
      at C:/repo/pages/HomePage.ts:45:12
      ../pages/BasePage.ts:17
    """
    if not text:
        return None
    # strip ANSI first
    text = _strip_ansi(text)

    # Try several regex patterns ordered from most-specific to fallback.
    patterns = [
        # (C:\path\to\file.ts:17:23) or (file:line:col) inside parentheses
        r'\((?P<file>[A-Za-z]:[^"()]+):(?P<line>\d+):(?P<col>\d+)\)',
        # absolute or relative paths with line and col: C:/path/to/file.ts:17:23 or ../pages/File.ts:17:23
        r'(?P<file>[\w\./\\-]+?):(?P<line>\d+):(?P<col>\d+)',
        # file:line (no col)
        r'(?P<file>[\w\./\\-]+?):(?P<line>\d+)'
    ]

    for pat in patterns:
        m = re.search(pat, text)
        if m:
            try:
                res: Dict[str, int] = {'file': m.group('file')}
                if m.groupdict().get('line'):
                    res['line'] = int(m.group('line'))
                if m.groupdict().get('col'):
                    res['col'] = int(m.group('col'))
                return res
            except Exception:
                return None

    # fallback for 'line X, column Y' patterns
    m2 = re.search(r"line\s+(?P<line>\d+)(?:[,\s]+col(?:umn)?\s+(?P<col>\d+))?", text, re.I)
    if m2:
        try:
            res = {'line': int(m2.group('line'))}
            if m2.group('col'):
                res['col'] = int(m2.group('col'))
            return res
        except Exception:
            return None
    return None


def _read_source_snippet(file: str, line: int, context: int = 3) -> Optional[Dict[str, Any]]:
    """Return a small source snippet around `line` from `file` if available.

    Returns dict with keys: file (resolved), line, snippet (string), start_line
    or None if file not found or cannot be read.
    """
    if not file or not line:
        return None
    from pathlib import Path
    p = Path(file)
    # Try as absolute
    if not p.exists():
        # Try relative to current working dir (project root)
        p = Path.cwd() / file
        if not p.exists():
            # Normalize backslashes and try again
            p = Path.cwd() / file.replace('\\', '/')
            if not p.exists():
                return None
    try:
        lines = p.read_text(encoding='utf-8', errors='ignore').splitlines()
    except Exception:
        return None

    idx = max(0, int(line) - 1)
    start = max(0, idx - context)
    end = min(len(lines), idx + context + 1)
    snippet_lines = lines[start:end]
    return {
        'file': str(p),
        'start_line': start + 1,
        'line': int(line),
        'snippet': '\n'.join(snippet_lines)
    }


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    if not text:
        return ''
    # ANSI escape sequence regex
    ansi_re = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_re.sub('', text)


def _split_message_and_stack(full_text: str) -> Tuple[str, Optional[str]]:
    """Split a possibly multi-line error text into a short message and a stack trace.

    Heuristic: first non-empty line is the message; subsequent lines that look like stack
    entries (start with whitespace + 'at' or contain file:line:col) are considered stack.
    """
    if not full_text:
        return ('', None)
    text = _strip_ansi(full_text)
    lines = [ln for ln in text.splitlines()]
    if not lines:
        return (text.strip(), None)

    # find split point where stack-like lines start
    stack_start = None
    for i, ln in enumerate(lines[1:], start=1):
        if re.search(r"\bat\b", ln) or re.search(r"[A-Za-z]:\\|/", ln) and re.search(r":\d+", ln):
            stack_start = i
            break

    if stack_start is None:
        # no obvious stack, return the first line as message and the rest as additional info
        msg = lines[0].strip()
        rest = '\n'.join(lines[1:]).strip()
        return (msg, rest if rest else None)

    msg = lines[0].strip()
    stack = '\n'.join(lines[stack_start:]).strip()
    return (msg, stack if stack else None)


def _suggest_from_trace(detail: Dict[str, Any]) -> Optional[str]:
    """Generate a short actionable suggestion using stack/raw/parsed_location info."""
    if not detail:
        return None
    raw = detail.get('raw') or ''
    stack = detail.get('stack') or ''
    loc = detail.get('parsed_location') or {}

    suggestions = []

    text = ' '.join([raw, stack]).lower()
    # If call log or getByRole appears, suggest checking role/text
    if 'getbyrole' in text or "getByRole" in (raw or ''):
        suggestions.append("Check the getByRole selector and its 'name' argument; try getByText or check the visible text.")
    # If locator.* appears, suggest checking locator resolution and add explicit waits
    if 'locator.' in text or 'locator(' in text or 'locator.click' in text:
        suggestions.append("Ensure the locator resolves before clicking: add explicit wait or check selector in the referenced page file.")
    # Timeouts
    if 'timeout' in text:
        suggestions.append("Increase test timeout or add explicit waits around the action.")
    # If parsed location points to a page file, suggest inspecting it
    file = loc.get('file') if isinstance(loc, dict) else None
    if file:
        suggestions.append(f"Inspect {file} at line {loc.get('line', '?')} to find the locator or action causing the error.")

    if suggestions:
        # return the most specific-looking suggestion (prefer locator-related)
        for s in suggestions:
            if 'locator' in s or 'getbyrole' in s.lower():
                return s
        return suggestions[0]
    return None


def analyze_report(path: Optional[str] = None,
                   report: Optional[Any] = None,
                   loader: Optional[Callable[[str], Any]] = None,
                   extractor: Optional[Callable[[Any], Iterable[Tuple[str, str, List[str]]]]] = None,
                   matchers: Optional[List[Tuple[re.Pattern, str, str]]] = None,
                   dedupe: bool = True,
                   return_details: bool = False) -> List[Tuple[str, str, str]]:
    """Analyze a test report and return suggestions.

    Parameters:
    - path: path to the report file (if report is not passed)
    - report: already-parsed report object (JSON dict or XML Element)
    - loader: optional function(path) -> parsed report
    - extractor: function(parsed_report) -> iterable of (suite, test_title, [messages])
    - matchers: list of tuples (compiled_regex, error_type, suggestion)
    - dedupe: if True, only one suggestion per (test_title, error_type) is returned
    """
    parsed = load_report(path=path, report_data=report, loader=loader)
    if matchers is None:
        matchers = DEFAULT_MATCHERS
    if extractor is None:
        # choose extractor by type
        if isinstance(parsed, dict):
            extractor = default_playwright_extractor
        else:
            extractor = junit_xml_extractor

    suggestions: List[Tuple[str, str, str]] = []
    seen = set()
    # When return_details=True and dedupe=True we prefer entries that include stack traces
    best: Dict[Tuple[str, str], Tuple[str, str, str, Dict]] = {}
    for suite_name, test_title, messages in extractor(parsed):
        for msg in messages:
            # msg may be a dict (normalized) or a raw string
            if isinstance(msg, dict):
                text = (msg.get('message') or '').strip()
            else:
                text = (msg or '').strip()

            for pattern, err_type, suggestion in matchers:
                if pattern.search(text):
                    key = (test_title, err_type)
                    # Build detail dict if requested
                    if return_details:
                        detail = {
                            'message': text,
                        }
                        if isinstance(msg, dict):
                            if 'location' in msg:
                                detail['location'] = msg.get('location')
                            if 'stack' in msg:
                                detail['stack'] = msg.get('stack')
                            if 'raw' in msg:
                                detail['raw'] = msg.get('raw')

                        # Try to parse a location from the short message first
                        loc = _parse_location_from_text(text)
                        if loc:
                            detail.setdefault('parsed_location', loc)

                        # If we didn't find a location yet, try parsing the stack or raw text
                        if not detail.get('parsed_location'):
                            loc2 = _parse_location_from_text(detail.get('stack') or detail.get('raw') or '')
                            if loc2:
                                detail.setdefault('parsed_location', loc2)

                        # Add a trace-based suggestion derived from stack/parsed location
                        trace_sugg = _suggest_from_trace(detail)
                        if trace_sugg:
                            detail['trace_suggestion'] = trace_sugg

                        # If we have a parsed location with file and line, attempt to read a small snippet
                        ploc = detail.get('parsed_location') or {}
                        if ploc.get('file') and ploc.get('line'):
                            try:
                                snippet = _read_source_snippet(ploc.get('file'), ploc.get('line'))
                                if snippet:
                                    detail['source_snippet'] = snippet
                            except Exception:
                                # non-fatal: don't block analysis if reading file fails
                                pass

                        if dedupe:
                            # prefer entries that include a stack trace
                            existing = best.get(key)
                            has_stack = bool(detail.get('stack'))
                            if existing is None:
                                best[key] = (test_title, err_type, suggestion, detail)
                            else:
                                _, _, _, ex_detail = existing
                                ex_has_stack = bool(ex_detail.get('stack'))
                                # replace only if new one has stack and existing doesn't
                                if has_stack and not ex_has_stack:
                                    best[key] = (test_title, err_type, suggestion, detail)
                        else:
                            suggestions.append((test_title, err_type, suggestion, detail))
                    else:
                        if dedupe and key in seen:
                            # already seen; skip
                            pass
                        else:
                            suggestions.append((test_title, err_type, suggestion))
                    seen.add(key)
    # if we collected best detailed suggestions, return them
    if return_details and dedupe:
        return list(best.values())
    return suggestions


def get_error_stats(path: Optional[str] = None,
                    report: Optional[Any] = None,
                    loader: Optional[Callable[[str], Any]] = None,
                    extractor: Optional[Callable[[Any], Iterable[Tuple[str, str, List[str]]]]] = None,
                    matchers: Optional[List[Tuple[re.Pattern, str, str]]] = None,
                    dedupe: bool = True) -> Counter:
    """Return a Counter of error types found in the report. Uses same parameters as analyze_report."""
    parsed = load_report(path=path, report_data=report, loader=loader)
    if matchers is None:
        matchers = DEFAULT_MATCHERS
    if extractor is None:
        extractor = default_playwright_extractor if isinstance(parsed, dict) else junit_xml_extractor

    counts: List[str] = []
    seen = set()
    for suite_name, test_title, messages in extractor(parsed):
        for msg in messages:
            # msg may be a dict (normalized) or a raw string
            if isinstance(msg, dict):
                norm = (msg.get('message') or '').strip()
            else:
                norm = (msg or '').strip()

            matched = False
            for pattern, err_type, _ in matchers:
                if pattern.search(norm):
                    key = (test_title, err_type)
                    if dedupe and key in seen:
                        matched = True
                        break
                    counts.append(err_type)
                    seen.add(key)
                    matched = True
                    break
            if not matched:
                key = (test_title, 'Others')
                if not (dedupe and key in seen):
                    counts.append('Others')
                    seen.add(key)
    return Counter(counts)