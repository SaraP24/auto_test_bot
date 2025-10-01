import json
from collections import Counter

def analyze_report(path='reports/report.json'):
    with open(path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    suggestions = []
    seen = set()
    for suite in report.get('suites', []):
        for spec in suite.get('specs', []):
            test_title = spec["title"]
            for test in spec.get('tests', []):
                if test_title in seen:
                    continue
                seen.add(test_title)
                for result in test.get('results', []):
                    for error in result.get('errors', []):
                        msg = error.get('message', '')
                        if 'strict mode violation' in msg:
                            suggestions.append((test_title, 'Broken selector', 'Use getByRole() or getByText()'))
                        elif 'TimeoutError' in msg:
                            suggestions.append((test_title, 'Timeout', 'Increase timeout or check visibility of elements'))
                        elif 'Protocol error' in msg:
                            suggestions.append((test_title, 'Invalid URL', 'Varify that path is relative if using baseURL or check the full URL'))
                        elif 'undefined' in msg:
                            suggestions.append((test_title, 'Undefined variable', 'Check for typos or missing imports'))
                        elif 'Test timeout' in msg:
                            suggestions.append((test_title, 'Test timeout', 'You should check if locators are correct or increase test timeout, priorize checking locators and adding explicit waits'))
    return suggestions


# Get statistics of error types for visualization
def get_error_stats(path='reports/report.json'):
    with open(path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    error_types = []
    seen = set()
    for suite in report.get('suites', []):
        for spec in suite.get('specs', []):
            test_title = spec["title"]
            for test in spec.get('tests', []):
                if test_title in seen:
                    continue
                seen.add(test_title)
                for result in test.get('results', []):
                    for error in result.get('errors', []):
                        msg = error.get('message', '')
                        if 'strict mode violation' in msg:
                            error_types.append('Broken selector')
                        elif 'TimeoutError' in msg:
                            error_types.append('Timeout')
                        elif 'Protocol error' in msg:
                            error_types.append('Invalid URL')
                        elif 'Test timeout' in msg:
                            error_types.append('Test timeout')
                        else:
                            error_types.append('Others')

    return Counter(error_types)