"""Verify the bill, personal vote and conflicting totals in both report views."""

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
case = 'framework-7595'
stem = '0412-framework-7595'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == 'be1d7bcba72ce25c35cc28ac7cbd412b39c2884fbecdfab4ce297d8266e4dbe3'
assert harness.sha(review) == 'e9cb5b948ca843250fba1b2194f8a7a7f62bd484c23bff6eaf66504685f0cde8'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (21, 19, 0)
receipt = harness.main(package, review, case, stem + '-event', stem + '-relation',
                       None, expected_party='demokrat', namespace='gsd-0412')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, key, suffix in (
        ('practice_statement', 'id', '-statement'),
        ('practice_event', 'id', '-event'),
        ('practice_relation', 'id', '-relation'),
        ('practice_contribution', 'id', '-contribution'),
        ('practice_actor_period', 'contribution_id', '-contribution'),
        ('practice_dispute', 'id', '-vote-dispute'),
        ('practice_dispute_evidence', 'dispute_id', '-vote-dispute'),
    ):
        identity = stem + suffix
        expected = [row for row in records[table] if row[key] == identity]
        exported = [row for row in export[table] if row[key] == identity]
        persisted = [dict(row) for row in db.execute(f'SELECT * FROM {table} WHERE {key}=?', (identity,))]
        assert len(expected) == (3 if table == 'practice_dispute_evidence' else 1)
        sort_rows = lambda rows: sorted(json.dumps(row, sort_keys=True) for row in rows)
        assert sort_rows(expected) == sort_rows(exported) == sort_rows(persisted), table
    actor = db.execute('SELECT kind FROM actor WHERE id=?', (stem + '-actor',)).fetchone()
    assert actor[0] == 'individual_mp'
    evidence = db.execute('SELECT passage_id,role FROM practice_dispute_evidence WHERE dispute_id=?',
                          (stem + '-vote-dispute',)).fetchall()
    assert {tuple(row) for row in evidence} == {
        (stem + '-minutes-announced', 'conflict'),
        (stem + '-minutes-official-count', 'support'),
        (stem + '-minutes-duplicates', 'support'),
    }
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
    card = report.split(tag, 1)[1].split('</article>', 1)[0]
    for term in ('Bireysel milletvekili faaliyeti', '468 kabul, 88 ret ve 6 çekimser',
                 '467 kabul, 87 ret, 7 çekimser', '2 mükerrer', 'tümüne ret oyu verdi',
                 'MGK teyidinin yayımlanması', '18 Ağustos'):
        assert term.casefold() in card.casefold(), (view, term)
    for suffix in ('-minutes-nominal', '-minutes-official-count', '-identity-speaker', '-membership-party'):
        assert f'href="#source-{stem}{suffix}"' in card, (view, suffix)
print('DEMOKRAT_FRAMEWORK_7595_BOTH_VIEWS_OK', folder, flush=True)
