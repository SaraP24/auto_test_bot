import unittest
from ai.healing import dom_analyzer as da
from ai.healing import locator_recovery as lr


class TestHealingHelpers(unittest.TestCase):
    def test_analyze_dom_with_html(self):
        html = '<html><body><button id="btn" class="primary">Click me</button></body></html>'
        res = da.analyze_dom(html, 'button#btn')
        self.assertIsInstance(res, dict)
        self.assertEqual(res.get('matches'), 1)
        self.assertTrue(res.get('samples'))

    def test_suggest_alternative_locator(self):
        html = '<html><body><button id="btn" class="primary">Click me</button></body></html>'
        suggestions = lr.suggest_alternative_locator(html, broken_selector='.nonexistent')
        self.assertIsInstance(suggestions, list)
        self.assertGreaterEqual(len(suggestions), 1)


if __name__ == '__main__':
    unittest.main()
