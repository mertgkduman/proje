"""Verify the 2/4471 votes and separate AYM record in both reader views."""

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
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'demokrat'
case = 'law-7418'
stem = '0412-' + case
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert [harness.sha(p) for p in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (55, 45, 0)
receipt = harness.main(package, review, case, stem + '-article29-event', stem + '-article29-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
report = (folder / 'index.html').read_text()
events = {'article29': '2022-10-13', 'bill': '2022-10-13', 'court': '2023-11-08'}
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, ids in (
        ('practice_statement', (stem + '-statement',)),
        ('practice_event', tuple(f'{stem}-{key}-event' for key in events)),
        ('practice_relation', tuple(f'{stem}-{key}-relation' for key in ('article29', 'bill'))),
        ('practice_candidate', tuple(f'{stem}-{key}-candidate' for key in events)),
    ):
        for ident in ids:
            row = next(item for item in records[table] if item['id'] == ident)
            result = db.execute(f'SELECT * FROM {table} WHERE id=?', (ident,)).fetchone()
            assert row in export[table] and row == dict(result), ident
    for key, day in events.items():
        assert db.execute('SELECT event_at FROM practice_event WHERE id=?',
                          (f'{stem}-{key}-event',)).fetchone()[0] == day
    assert tuple(db.execute('SELECT state, relation_id FROM practice_candidate WHERE id=?',
                            (stem + '-court-candidate',)).fetchone()) == ('unmatched', None)
    for role, day in (('party', '2022-10-06'), ('law', '2022-10-18'), ('court', '2024-02-23')):
        assert db.execute('SELECT document_date FROM document_version WHERE id=?',
                          (f'{stem}-{role}-v1',)).fetchone()[0] == day
    assert db.execute('SELECT count(*) FROM manual_passage WHERE passage_id LIKE ?',
                      (stem + '-court-%',)).fetchone()[0] == 2
for view in ('party', 'comparison'):
    anchors = {
        f'{view}-practice-{stem}-article29-relation': ('13 Ekim', '217/A'),
        f'{view}-practice-{stem}-bill-relation': ('13 Ekim', '18 Ekim', '7418'),
        f'{view}-unmatched-{stem}-court-candidate': ('AYM', '217/A', '2023/189'),
    }
    for anchor, phrases in anchors.items():
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split('</article>', 1)[0]
        for phrase in phrases:
            assert phrase in card, (view, phrase)
print('DEMOCRAT_LAW_7418_BOTH_VIEWS_OK', folder, flush=True)
