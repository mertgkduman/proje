"""Audit real closed releases without retaining descendant snapshots on descent."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import arsiv


RELEASE = '7d5f78dde79a4b0bb48f64a16fd263c1'
SECOND = 'e0467880febd44068d476a448e09608f'
ANCESTOR = 'b14c96c54e4b420686c46e5cfb1071a3'


class AuditMemoryTest(unittest.TestCase):
    def test_closed_release_descent_does_not_hold_descendant_exports(self):
        observations = []

        def profile(frame, event, arg):
            if event == 'call' and frame.f_code is arsiv.export_db.__code__:
                parent = frame.f_back
                frames = []
                while parent:
                    if parent.f_code is arsiv.audit_release.__code__:
                        frames.append(any(
                            isinstance(value, dict)
                            and {'schema_version', 'party', 'finding'} <= value.keys()
                            for value in parent.f_locals.values()
                        ))
                    parent = parent.f_back
                observations.append(frames)

        previous = sys.getprofile()
        try:
            sys.setprofile(profile)
            self.assertEqual(arsiv.audit_release(RELEASE), RELEASE)
        finally:
            sys.setprofile(previous)
        self.assertGreaterEqual(len(observations), 7)
        self.assertFalse(any(any(frames) for frames in observations), observations)

    def test_rejects_tampered_ancestor_and_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'data'
            root.mkdir()
            shutil.copytree(arsiv.DATA / 'objects', root / 'objects')
            (root / 'releases').mkdir()
            release = RELEASE
            while release:
                src = arsiv.DATA / 'releases' / release
                shutil.copytree(src, root / 'releases' / release)
                release = json.loads((src / 'manifest.json').read_text()).get('base_release')
            old = arsiv.DATA
            arsiv.DATA = root
            try:
                html = root / 'releases' / ANCESTOR / 'index.html'
                original = html.read_bytes()
                html.write_bytes(original + b'corrupt')
                with self.assertRaisesRegex(ValueError, 'Manifest'):
                    arsiv.audit_release(RELEASE)
                html.write_bytes(original)
                manifest = root / 'releases' / SECOND / 'manifest.json'
                data = json.loads(manifest.read_text())
                data['base_release'] = RELEASE
                manifest.write_text(json.dumps(data))
                with self.assertRaisesRegex(ValueError, 'döngü'):
                    arsiv.audit_release(RELEASE)
            finally:
                arsiv.DATA = old
