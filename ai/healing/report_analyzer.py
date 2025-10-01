import json
from collections import Counter

def analyze_report(path='reports/report.json'):
    with open(path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    suggestions = []
    for suite in report.get('suites', []):
        for spec in suite.get('specs', []):
            for test in spec.get('tests', []):
                for result in test.get('results', []):
                    for error in result.get('errors', []):
                        msg = error.get('message', '')
                        if 'strict mode violation' in msg:
                            suggestions.append((test['title'], 'Broken selector', 'Use getByRole() or getByText()'))
                        elif 'TimeoutError' in msg:
                            suggestions.append((test['title'], 'Timeout', 'Increase timeout or check visibility of elements'))
                        elif 'Protocol error' in msg:
                            suggestions.append((test['title'], 'Invalid URL', 'Varify that path is relative if using baseURL or check the full URL'))
    return suggestions


# Get statistics of error types for visualization
def get_error_stats(path='reports/report.json'):
    with open(path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    error_types = []
    for suite in report.get('suites', []):
        for spec in suite.get('specs', []):
            for test in spec.get('tests', []):
                for result in test.get('results', []):
                    for error in result.get('errors', []):
                        msg = error.get('message', '')
                        if 'strict mode violation' in msg:
                            error_types.append('Selector roto')
                        elif 'TimeoutError' in msg:
                            error_types.append('Timeout')
                        elif 'Protocol error' in msg:
                            error_types.append('URL inválida')
                        else:
                            error_types.append('Otro')

    return Counter(error_types)