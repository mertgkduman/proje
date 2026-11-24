"""Verify the distinct motion and final vote against both reader views."""

from html import escape
import importlib.util
import json
from pathlib import Path
import sqlite3

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', checks.parent / '04-04-checks' / 'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'demokrat'
case = 'siber-7545'
stem = '0412-siber-7545'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == 'b34d00127a035ca541e9d8144ea2f6eeb841ee45c4beab97115b683be4e7dcff'
assert harness.sha(review) == '029f631fb9347fbe39dbd616f7c9743302c3b5c527fe3882264da6aea05fc9ff'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (35, 30, 0)
receipt = harness.main(package, review, case, stem + '-motion-event', '0412-izmir-tis-izelman-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
report = (folder / 'index.html').read_text()
labels = ('motion', 'final')
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ('practice_event', tuple(f'{stem}-{label}-event' for label in labels)),
        ('practice_candidate', tuple(f'{stem}-{label}-candidate' for label in labels)),
        ('practice_contribution', tuple(f'{stem}-{label}-contribution' for label in labels)),
        ('practice_dispute', (stem + '-vote-count-dispute',)),
    ):
        for identity in identities:
            row = next(row for row in records[table] if row['id'] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    assert [tuple(row) for row in db.execute(
        'SELECT state,relation_id FROM practice_candidate WHERE id LIKE ? ORDER BY id',
        (stem + '%',))] == [('unmatched', None), ('unmatched', None)]
    assert db.execute('SELECT count(*) FROM practice_dispute_evidence WHERE dispute_id=?',
                      (stem + '-vote-count-dispute',)).fetchone()[0] == 4
    assert db.execute('SELECT event_id FROM practice_dispute WHERE id=?',
                      (stem + '-vote-count-dispute',)).fetchone()[0] == stem + '-final-event'
for view in ('party', 'comparison'):
    for label, expected in (
        ('motion', ('geçici 1. madde', 'ilk önergenin yedi imzacısından biri', 'Önergeler')),
        ('final', ('Katılmadı', '246 kabul', '245 kabul', 'iki mükerrer')),
    ):
        anchor = f'{view}-unmatched-{stem}-{label}-candidate'
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split('</article>', 1)[0]
        for phrase in expected:
            assert escape(phrase).casefold() in card.casefold(), (view, label, phrase)
print('DEMOCRAT_SIBER_7545_BOTH_VIEWS_OK', folder, flush=True)
