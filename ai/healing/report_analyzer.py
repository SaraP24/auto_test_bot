import json

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
                            suggestions.append((test['title'], 'Selector roto', 'Usá getByRole() o getByText()'))
                        elif 'TimeoutError' in msg:
                            suggestions.append((test['title'], 'Timeout', 'Aumentá el timeout o revisá visibilidad'))
                        elif 'Protocol error' in msg:
                            suggestions.append((test['title'], 'URL inválida', 'Verificá que sea relativa si usás baseURL'))
    return suggestions


    ##      npm run test
#       python ai/healing/report_analyzer.py