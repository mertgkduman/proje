"""Gerçek kapalı raporda karşılaştırma bağlantısının odağını denetle."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from browser_probe import browser

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'data/releases/b513965558094e338a941be90a1960a4/index.html'


class ComparisonNavigation(unittest.TestCase):
    def test_direct_hash_reveals_and_focuses_same_row(self):
        executable = browser()
        self.assertIsNotNone(executable, 'Chromium bulunamadı')
        source = REPORT.read_text(encoding='utf-8')
        marker = '''<script>setTimeout(()=>{const e=document.getElementById('comparison-03-iyi-merkez');document.body.dataset.focusCheck=String(e===document.activeElement && !e.closest('[role=tabpanel]').hidden)},200)</script>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'index.html'
            path.write_text(source.replace('</html>', marker + '</html>'), encoding='utf-8')
            result = subprocess.run([executable, '--headless', '--no-sandbox', '--disable-gpu', '--virtual-time-budget=1000', '--dump-dom', path.as_uri() + '#comparison-03-iyi-merkez'], capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr[-1000:])
        self.assertTrue('data-focus-check="true"' in result.stdout, 'Doğrudan hedef odaklanmadı')


if __name__ == '__main__':
    unittest.main()
