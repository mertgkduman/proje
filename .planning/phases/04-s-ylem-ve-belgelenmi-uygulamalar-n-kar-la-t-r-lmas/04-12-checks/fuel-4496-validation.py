"""Verify the earlier filing and later lapse of the 2/4496 bill."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', checks.parent / '04-04-checks' / 'samsun-reply-validation.py',
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'demokrat'
case = 'fuel-4496'
stem = '0412-' + case
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert [harness.sha(p) for p in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (57, 46, 0)
receipt = harness.main(package, review, case, stem + '-lapse-event', stem + '-lapse-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
assert json.loads((folder / 'manifest.json').read_bytes())['renderer_version'] == 31
snapshot = json.loads((folder / 'records.json').read_bytes())
report = (folder / 'index.html').read_text()
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    rows = {
        'practice_statement': ('statement',),
        'practice_event': ('filing-event', 'lapse-event'),
        'practice_relation': ('lapse-relation',),
        'practice_candidate': ('filing-candidate', 'lapse-candidate'),
    }
    for table, suffixes in rows.items():
        for suffix in suffixes:
            ident = f'{stem}-{suffix}'
            row = next(item for item in records[table] if item['id'] == ident)
            result = db.execute(f'SELECT * FROM {table} WHERE id=?', (ident,)).fetchone()
            assert row in snapshot[table] and row == dict(result), ident
    assert tuple(db.execute('SELECT state, relation_id FROM practice_candidate WHERE id=?',
                            (stem + '-filing-candidate',)).fetchone()) == ('unmatched', None)
    assert db.execute('SELECT statement_at FROM practice_statement WHERE id=?',
                      (stem + '-statement',)).fetchone()[0] == '2022-06-22'
    for key, day in (('filing', '2022-06-16'), ('lapse', '2023-06-02')):
        assert db.execute('SELECT event_at FROM practice_event WHERE id=?',
                          (f'{stem}-{key}-event',)).fetchone()[0] == day
    assert db.execute('SELECT printed_page FROM passage WHERE id=?',
                      (stem + '-term-leaf-lapse-p',)).fetchone()[0] == '203'
for view in ('party', 'comparison'):
    anchors = {
        f'{view}-unmatched-{stem}-filing-candidate': ('2/4496', '16 Haziran', '17 Haziran'),
        f'{view}-practice-{stem}-lapse-relation': ('2/4496', '2 Haziran 2023', 'hükümsüz'),
    }
    for anchor, phrases in anchors.items():
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split('</article>', 1)[0].casefold()
        for phrase in phrases:
            assert phrase.casefold() in card, (view, phrase)
print('DEMOCRAT_FUEL_4496_BOTH_VIEWS_OK', folder, flush=True)
