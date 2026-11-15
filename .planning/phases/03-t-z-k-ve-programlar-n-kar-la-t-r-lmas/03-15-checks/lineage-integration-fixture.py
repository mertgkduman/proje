import json
import os
from pathlib import Path
import sys
import unittest

root = Path(os.environ.get('LINEAGE_INPUT', '/hpc/group/pfisterlab/mg551/storage/proje'))
sys.path[:0] = [str(root / 'src'), str(root / 'tests')]
test_path = root / 'tests/test_comparison_content.py'
source = test_path.read_text()
source = source.replace('        before_pointer = arsiv.current()\n', '        before_pointer = source.parent.name\n', 1)
needle = "            arsiv.DATA.mkdir()\n            try:\n"
setup = """            arsiv.DATA.mkdir()
            for directory in ('objects', 'views', 'releases'):
                shutil.copytree(original_data / directory, arsiv.DATA / directory)
            try:
"""
if source.count(needle) < 1: raise RuntimeError('fixture setup hook missing')
source = source.replace(needle, setup, 1)
needle = "                    db = arsiv.connect_readonly(cross_work / 'records.sqlite3')\n"
addition = """                    arsiv.export_db = original_export
                    real_export = original_export(cross_work / 'records.sqlite3', 'lineage-test', strict_identity=True)
                    self.assertEqual(real_export['comparison_contract'][0]['version'], 3)
                    self.assertEqual(real_export['comparison_lineage_contract'][0]['version'], 1)
                    self.assertTrue(arsiv.validate_changed_topic_reviews(real_export))
                    release = arsiv.publish_release(cross_work, refresh=True)
                    folder = arsiv.DATA / 'releases' / release
                    manifest = json.loads((folder / 'manifest.json').read_text())
                    self.assertEqual((manifest['comparison_validation_version'], manifest['comparison_synthesis_contract_version'], manifest['comparison_lineage_version']), (3, 2, 1))
                    self.assertEqual(arsiv.audit_release(release), release)
                    damaged = dict(manifest, comparison_lineage_version=0)
                    (folder / 'manifest.json').write_text(json.dumps(damaged))
                    with self.assertRaisesRegex(ValueError, 'soyu manifesti'):
                        arsiv.audit_release(release)
                    (folder / 'manifest.json').write_text(json.dumps(manifest))
                    proof = Path(os.environ['LINEAGE_PROOF'])
                    shutil.copytree(folder, proof / 'release')
                    (proof / 'result.json').write_text(json.dumps({'release': release, 'manifest': manifest, 'base': before_pointer, 'tampered_manifest_rejected': True}, indent=2) + '\\n')
                    arsiv.export_db = lambda *args, **kwargs: {}
                    (arsiv.DATA / 'current.json').write_text(json.dumps({'release_id': before_pointer}))
                    (arsiv.DATA / '.write.lock').write_text(json.dumps({'token': 'test-token'}))
"""
if source.count(needle) != 1: raise RuntimeError('fixture integration hook mismatch')
source = source.replace(needle, addition + needle)
module = {'__file__': str(test_path), '__name__': 'temporary_lineage_integration_test', 'os': os}
exec(compile(source, str(test_path), 'exec'), module)
suite = unittest.TestSuite([module['ComparisonContentTest']('test_reconcile_rolls_back_after_complete_mapping_loader_failure')])
sys.exit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
