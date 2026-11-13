"""Acceptance checks for the sourced phase-three comparison release."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import arsiv


class ComparisonReleaseTest(unittest.TestCase):
    def test_real_sources_reach_closed_comparison_release(self):
        # Fail on the missing behaviour before paying for the archive copy and
        # immutable release audit; the remainder exercises the real pathway.
        self.assertTrue(callable(getattr(arsiv, 'load_comparison', None)),
                        'comparison package loading is required')
        original_data = arsiv.DATA
        package = Path(__file__).resolve().parents[1] / 'data/comparisons/03-tracer.json'
        with tempfile.TemporaryDirectory() as tmp:
            arsiv.DATA = Path(tmp) / 'data'
            try:
                shutil.copytree(original_data, arsiv.DATA)
                before = arsiv.current()
                base = arsiv.DATA / 'releases' / before
                hashes = {p.name: arsiv.sha(p) for p in base.iterdir() if p.is_file()}
                work = arsiv.open_workspace(tmp)
                arsiv.load_comparison(work, json.loads(package.read_text(encoding='utf-8')))
                release = arsiv.publish_release(work, refresh=True)
                self.assertNotEqual(before, release)
                folder = arsiv.DATA / 'releases' / release
                manifest = json.loads((folder / 'manifest.json').read_text())
                data = json.loads((folder / 'records.json').read_text())
                report = (folder / 'index.html').read_text(encoding='utf-8')
                self.assertEqual(manifest['data_schema_version'], 6)
                self.assertEqual(manifest['renderer_version'], 16)
                self.assertEqual(len(data['comparison_row']), 9)
                self.assertEqual(sum(row['state'] == 'not_researched' for row in data['comparison_row']), 7)
                for text in ('elli asıl', 'yirmi beş yedek', 'altmış asıl', 'otuz yedek',
                             'onda birinin', 'beşte birinin', 'Henüz incelenmedi'):
                    self.assertIn(text, report)
                self.assertEqual(hashes, {p.name: arsiv.sha(p) for p in base.iterdir() if p.is_file()})
                self.assertEqual(arsiv.audit_release(release), release)
            finally:
                arsiv.DATA = original_data


if __name__ == '__main__':
    unittest.main()
