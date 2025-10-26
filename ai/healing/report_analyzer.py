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
                        msg = error.get('message', '')
                        errors.append(msg)
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
    (re.compile(r'strict mode violation', re.I), 'Broken selector', 'Use getByRole() or getByText()'),
    (re.compile(r'timeouterror', re.I), 'Timeout', 'Increase timeout or check visibility of elements'),
    (re.compile(r'protocol error', re.I), 'Invalid URL', 'Verify path or baseURL'),
    (re.compile(r'undefined', re.I), 'Undefined variable', 'Check for typos or missing imports'),
    (re.compile(r'test timeout', re.I), 'Test timeout', 'Check locators or increase test timeout; add explicit waits'),
]


def analyze_report(path: Optional[str] = None,
                   report: Optional[Any] = None,
                   loader: Optional[Callable[[str], Any]] = None,
                   extractor: Optional[Callable[[Any], Iterable[Tuple[str, str, List[str]]]]] = None,
                   matchers: Optional[List[Tuple[re.Pattern, str, str]]] = None,
                   dedupe: bool = True) -> List[Tuple[str, str, str]]:
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
    for suite_name, test_title, messages in extractor(parsed):
        for msg in messages:
            norm = (msg or '').strip()
            for pattern, err_type, suggestion in matchers:
                if pattern.search(norm):
                    key = (test_title, err_type)
                    if dedupe and key in seen:
                        continue
                    suggestions.append((test_title, err_type, suggestion))
                    seen.add(key)
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