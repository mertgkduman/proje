import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

job = Path('/tmp/gsd-03-lineage-integration-3ce46b890c2a4d8fac52855f34713ad1')
sys.path.insert(0, str(job / 'inputs/src'))
import arsiv

with tempfile.TemporaryDirectory(prefix='lineage-tamper-') as tmp:
    root = Path(tmp)
    shutil.copytree(job / 'inputs/data', root / 'data')
    arsiv.DATA = root / 'data'
    release = json.loads((job / 'proof/result.json').read_text())['release']
    folder = arsiv.DATA / 'releases' / release
    shutil.copytree(job / 'proof/release', folder)
    db = arsiv.connect(folder / 'records.sqlite3')
    try:
        row = db.execute('SELECT old_row_id,new_row_id FROM comparison_row_lineage LIMIT 1').fetchone()
        db.execute('DELETE FROM comparison_row_lineage WHERE old_row_id=? AND new_row_id=?', tuple(row))
        db.commit()
    finally: db.close()
    manifest = json.loads((folder / 'manifest.json').read_text())
    manifest['files']['records.sqlite3'] = hashlib.sha256((folder / 'records.sqlite3').read_bytes()).hexdigest()
    (folder / 'manifest.json').write_text(json.dumps(manifest))
    reasons = {}
    try: arsiv.audit_release(release)
    except ValueError as exc: reasons['audit'] = str(exc)
    else: raise AssertionError('Audit accepted missing lineage')
    work = root / 'work'; work.mkdir()
    shutil.copyfile(folder / 'records.sqlite3', work / 'records.sqlite3')
    (work / 'workspace.json').write_text(json.dumps({'token': 'isolated-tamper'}))
    (arsiv.DATA / '.write.lock').write_text(json.dumps({'token': 'isolated-tamper'}))
    before = arsiv.sha(work / 'records.sqlite3')
    try: arsiv.load_comparison(work, dict(contract_version=3, taxonomy_version=3, stage='partial', records=[]))
    except ValueError as exc: reasons['import'] = str(exc)
    else: raise AssertionError('Import accepted missing lineage')
    if arsiv.sha(work / 'records.sqlite3') != before: raise AssertionError('Failed import changed workspace')
    output = {'audit_rejected': True, 'import_rejected': True, 'workspace_unchanged': True, 'reasons': reasons}
    (job / 'proof/tamper-result.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(output, ensure_ascii=False))
