"""Verify that the 2021 party statement and the TBMM decision reach both reader views."""

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', checks.parent / '04-04-checks' / 'samsun-reply-validation.py',
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'emep'
case = 'tezkere-1310'
stem = '0410-' + case
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert [harness.sha(p) for p in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (73, 72, 0)
receipt = harness.main(package, review, case, stem + '-event', stem + '-relation',
                       None, expected_party='emep', namespace='gsd-0410')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
report = (folder / 'index.html').read_text()
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, suffix in (
        ('practice_statement', 'statement'), ('practice_event', 'event'),
        ('practice_relation', 'relation'), ('practice_candidate', 'candidate'),
    ):
        ident = stem + '-' + suffix
        row = next(row for row in records[table] if row['id'] == ident)
        result = db.execute(f'SELECT * FROM {table} WHERE id=?', (ident,)).fetchone()
        assert row in export[table] and row == dict(result), ident
    assert db.execute('SELECT statement_at FROM practice_statement WHERE id=?',
                      (stem + '-statement',)).fetchone()[0] == '2021-10-26T09:22:20+03:00'
    assert db.execute('SELECT event_at FROM practice_event WHERE id=?',
                      (stem + '-event',)).fetchone()[0] == '2021-10-26'
    assert db.execute('SELECT document_date FROM document_version WHERE id=?',
                      (stem + '-gazette-v1',)).fetchone()[0] == '2021-10-28'
    assert db.execute('SELECT pdf_page_index FROM passage WHERE id=?',
                      (stem + '-gazette-term-p',)).fetchone()[0] == 1
    assert len(db.execute('SELECT passage_id FROM manual_passage WHERE passage_id LIKE ?',
                          (stem + '-%',)).fetchall()) == 1
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    start = f'id="{anchor}"'
    assert report.count(start) == 1 and f'href="#{anchor}"' in report
    card = report.split(start, 1)[1].split('</article>', 1)[0]
    for phrase in ('3/1704', '1310', '26 Ekim', '28 Ekim', '30 Ekim', '09.22', '15.00'):
        assert phrase in card, (view, phrase)
print('EMEP_TEZKERE_1310_BOTH_VIEWS_OK', folder, flush=True)
