"""Verify the TBMM HTML source versions and signed answer in an isolated preview."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', checks.parent / '04-04-checks' / 'samsun-reply-validation.py'
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / 'practices/sources/saadet'
stem = '0411-saadet-mine-inquiry-35779'
compact = Path('/work/mg551/gsd0411-2020-miners/compact')
package = compact / 'candidate-draft.json'
review = compact / 'candidate-review-draft.json'
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
source_proof = json.loads((compact/'source-proof.json').read_bytes())
assert [source_proof['package_sha256'],source_proof['review_sha256']] == sys.argv[1:]
receipt = harness.main(package, review, 'mine-35779-official-html', f'{stem}-event',
                       f'{stem}-relation', None, expected_party='saadet', namespace='gsd-0411')
preview = Path(receipt['preview'])
manifest = json.loads((preview/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
rows = json.loads(package.read_bytes())['practice_records']
export = json.loads((preview/'records.json').read_bytes())
with sqlite3.connect((preview/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory=sqlite3.Row
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert not db.execute('PRAGMA foreign_key_check').fetchall()
    for table, count in (('practice_event',41),('practice_relation',37),('practice_closure',0)):
        by_id={row['id']:row for row in rows[table]}
        assert len(by_id)==count
        assert by_id=={row['id']:row for row in export[table] if row['id'] in by_id}
        assert by_id=={row['id']:dict(row) for row in db.execute(f'SELECT * FROM {table}') if row['id'] in by_id}
    for version in source_proof['substitutions']:
        record = db.execute('SELECT * FROM document_version WHERE id=?', (version['id'],)).fetchone()
        assert record['sha256']==version['sha256'] and record['final_url']==version['url']
        assert harness.sha(preview.parents[1]/record['original_path'])==version['sha256']
        view_path = preview.parents[1]/version['view']['manifest_path']
        view = json.loads(view_path.read_bytes())
        assert view['http_charset']==version['http_charset']
        assert harness.sha(view_path)==manifest['asset_files'][version['view']['manifest_path']]
    answer = db.execute('SELECT * FROM document_version WHERE id=?', ('0411-mine-inquiry-answer-v1',)).fetchone()
    assert harness.sha(preview.parents[1]/answer['original_path'])==answer['sha256']
report=(preview/'index.html').read_text()
for view in ('party','comparison'):
    anchor=f'{view}-practice-{stem}-relation'
    marker=f'id="{anchor}"'
    assert report.count(marker)==1 and f'href="#{anchor}"' in report
    summary=report.split(marker,1)[1].split('</article>',1)[0]
    assert all(fragment.casefold() in summary.casefold() for fragment in ('2020','2021','kıdem','Bakanlık')),view
print('SAADET_35779_OFFICIAL_HTML_BOTH_VIEWS_OK', preview, flush=True)
