import unittest
import os
import json

from ai.healing import report_analyzer as ra


class TestReportAnalyzer(unittest.TestCase):
    def setUp(self):
        here = os.path.dirname(__file__)
        self.sample_path = os.path.abspath(os.path.join(here, '..', 'data', 'sample_report.json'))
        with open(self.sample_path, 'r', encoding='utf-8') as f:
            self.sample = json.load(f)

    def test_load_report_from_path(self):
        parsed = ra.load_report(path=self.sample_path)
        self.assertIsInstance(parsed, dict)
        self.assertIn('suites', parsed)

    def test_load_report_from_data(self):
        parsed = ra.load_report(report_data=self.sample)
        self.assertIs(parsed, self.sample)

    def test_analyze_report_default(self):
        suggestions = ra.analyze_report(report=self.sample)
        # Expect at least one timeout and one broken selector suggestion
        types = {t for (_, t, _) in suggestions}
        self.assertIn('Test timeout', types)
        self.assertIn('Broken selector', types)

    def test_get_error_stats(self):
        stats = ra.get_error_stats(report=self.sample)
        self.assertGreaterEqual(stats.get('Test timeout', 0), 1)
        self.assertGreaterEqual(stats.get('Broken selector', 0), 1)


if __name__ == '__main__':
    unittest.main()
