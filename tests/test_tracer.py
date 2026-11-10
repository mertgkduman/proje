import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class TracerTest(unittest.TestCase):
    def test_real_evidence_chain(self):
        result = subprocess.run([sys.executable, str(ROOT / 'src/arsiv.py'), 'audit', '--release', 'current'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('AUDIT_OK', result.stdout)
        report = (ROOT / 'data/current.json').read_text(encoding='utf-8')
        self.assertIn('release_id', report)
