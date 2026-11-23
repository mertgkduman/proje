"""Verify four distinct stages of the small-ruminant program in both views."""

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
case = 'kucukbas'
stem = '0412-kucukbas-2026'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == '70208713c098518739b79ea8024c1e17c4cdacc863e6a2d8e8e9c8d740a7848c'
assert harness.sha(review) == '1f3659ef136a782903e8c97ea64729f478be4bb05693190052baeba918a73fe9'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (25, 23, 0)
labels = ('apply', 'first', 'duzce', 'yozgat')
receipt = harness.main(package, review, case, stem + '-apply-event', stem + '-apply-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ('practice_statement', (stem + '-statement',)),
        ('practice_event', tuple(f'{stem}-{label}-event' for label in labels)),
        ('practice_relation', tuple(f'{stem}-{label}-relation' for label in labels)),
    ):
        for identity in identities:
            row = next(row for row in records[table] if row['id'] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    matched = db.execute('SELECT id FROM practice_relation WHERE statement_id=?', (stem + '-statement',))
    assert {row[0] for row in matched} == {f'{stem}-{label}-relation' for label in labels}
    dates = db.execute('SELECT event_at FROM practice_event WHERE id LIKE ? ORDER BY event_at', (stem + '-%',))
    assert [row[0] for row in dates] == ['2026-04-01', '2026-06-11', '2026-09-16', '2026-09-24']
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    for label, terms in (
        ('apply', ('1–30 Nisan', '45 bin TL', '150 bin', 'peşin veya kredi')),
        ('first', ('asil ve yedek', 'SMS')),
        ('duzce', ('Halilbey', '95 dişi ve 5 erkek', 'teslimin kesin günü')),
        ('yozgat', ('2.381', '14 asil ve 42 yedek', 'beş yetiştiriciye teslim')),
    ):
        anchor = f'{view}-practice-{stem}-{label}-relation'
        tag = f'id="{anchor}"'
        assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
        card = report.split(tag, 1)[1].split('</article>', 1)[0]
        for term in terms:
            assert term.casefold() in card.casefold(), (view, label, term)
print('DEMOKRAT_KUCUKBAS_BOTH_VIEWS_OK', folder, flush=True)
