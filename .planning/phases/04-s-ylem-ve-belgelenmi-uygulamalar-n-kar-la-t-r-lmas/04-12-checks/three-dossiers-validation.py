"""Verify two separate legislative proposals and one written-question case."""

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
case = 'three-dossiers'
stem = '0412-three-dossiers'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == '788da75156f75abaed4308410a233206243520239f2a254c78091c06284c9a95'
assert harness.sha(review) == 'eeab9f54985611823d2a83b40cb8a8897b29fa342128fc2a1d1a4600de6af1dc'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']),
        len(records['practice_closure'])) == (38, 32, 0)
receipt = harness.main(package, review, case, stem + '-city-event', stem + '-city-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
report = (folder / 'index.html').read_text()
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ('practice_statement', tuple(f'{stem}-{label}-statement' for label in ('city', 'penal'))),
        ('practice_event', tuple(f'{stem}-{label}-event' for label in ('city', 'penal', 'drug'))),
        ('practice_relation', tuple(f'{stem}-{label}-relation' for label in ('city', 'penal'))),
        ('practice_candidate', (stem + '-drug-candidate',)),
        ('practice_dispute', (stem + '-city-article-dispute',)),
    ):
        for identity in identities:
            row = next(row for row in records[table] if row['id'] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    evidence = db.execute(
        'SELECT p.pdf_page_index FROM practice_dispute_evidence e JOIN passage p ON p.id=e.passage_id '
        'WHERE e.dispute_id=? ORDER BY p.pdf_page_index', (stem + '-city-article-dispute',))
    assert [r[0] for r in evidence] == [4, 5]
    assert tuple(db.execute('SELECT state,relation_id FROM practice_candidate WHERE id=?',
                            (stem + '-drug-candidate',)).fetchone()) == ('unmatched', None)
for view in ('party', 'comparison'):
    for case_key, expected in (
        (f'practice-{stem}-city-relation', ('2/3139', '23 Mayıs', 'aynı 45. maddeyi kaldırıyor')),
        (f'practice-{stem}-penal-relation', ('2/3144', '28 Mayıs', 'dörtte üç')),
        (f'unmatched-{stem}-drug-candidate', ('7/20085', '7 Ocak', 'süresinde cevaplanmayanlar')),
    ):
        anchor = f'{view}-{case_key}'
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split('</article>', 1)[0]
        for phrase in expected:
            assert escape(phrase).casefold() in card.casefold(), (view, case_key, phrase)
print('DEMOCRAT_THREE_DOSSIERS_BOTH_VIEWS_OK', folder, flush=True)
