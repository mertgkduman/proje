"""Verify eight decisions and three changes to the active report topic."""

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
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'dbp'
case = 'baglar-march-reports-v2'
stem = '0409-baglar-march-reports-'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == 'ed8ce1205c3ec0baac700d2be712402441814c4688972ba21d77f727a41aae8f'
assert harness.sha(review) == '6af83d6895837fd2a34d45b78887e545163ed47c1a2b401065fea40f081988a4'
cases = {
    '42': ('2015-02-05', 'Fatih Mahallesi', 'komisyona sevk', '2015/56'),
    '43': ('2015-02-06', 'Kaynartepe', 'komisyona sevk', '2015/57'),
    '51': ('2015-03-04', '18.420.000 TL', '14.060.244,50 TL', '4.359.755,50 TL'),
    '52': ('2015-03-04', 'kız öğrencilere', 'psikoloji eğitimi', 'Program, katılım'),
    '54': ('2015-03-04', 'çocuk bakımı', 'sosyal etkinlik', 'kişi sayısı'),
    '56': ('2015-03-05', 'konteyner', 'kaldırımlar', '2015/42'),
    '57': ('2015-03-05', '17 fırın', 'eksik gramaj', '2015/43'),
    '58': ('2015-03-05', 'Sakarya Caddesi', 'aydınlatma', 'iki komisyona sevk'),
}
draft = json.loads(package.read_bytes())['practice_records']
assert (len(draft['practice_event']), len(draft['practice_relation']), len(draft['practice_closure'])) == (44, 7, 0)
receipt = harness.main(package, review, case, stem + '51-event', '0409-dbp-baglar-2015-cemr-relation',
                       None, expected_party='dbp', namespace='gsd-0409')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for number, (day, *_) in cases.items():
        event, candidate = stem + number + '-event', stem + number + '-unmatched'
        for table, identity in (('practice_event', event), ('practice_candidate', candidate)):
            row = next(row for row in draft[table] if row['id'] == identity)
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
        assert db.execute('SELECT event_at FROM practice_event WHERE id=?', (event,)).fetchone()[0] == day
        assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?', (event,)).fetchone()
    for number in ('49', '99', '161'):
        old = '0409-baglar-2015-' + number + '-unmatched'
        event, state = db.execute(
            'SELECT event_id,state FROM practice_candidate_revision WHERE candidate_id=? ORDER BY recorded_at DESC LIMIT 1',
            (old,)).fetchone()
        new = db.execute(
            'SELECT c.event_id,s.topic_id,c.state FROM practice_candidate c JOIN practice_scope_v2 s ON s.id=c.scope_id WHERE c.id=?',
            (stem + number + '-public-finance',)).fetchone()
        assert state == 'excluded'
        assert tuple(new) == (event, 'kamu-hesap-verebilirlik', 'unmatched')
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    for number, (_, *terms) in cases.items():
        anchor = f'{view}-unmatched-{stem}{number}-unmatched'
        tag = f'id="{anchor}"'
        assert report.count(tag) == 1 and f'href="#{anchor}"' in report, anchor
        card = report.split(tag, 1)[1].split('</article>', 1)[0]
        for term in terms:
            assert term.casefold().replace('i̇', 'i') in card.casefold().replace('i̇', 'i'), (view, number, term)
    for number in ('49', '99', '161'):
        assert f'id="{view}-unmatched-0409-baglar-2015-{number}-unmatched"' not in report
        tag = f'id="{view}-unmatched-{stem}{number}-public-finance"'
        assert report.count(tag) == 1, (view, number)
print('DBP_BAGLAR_MARCH_REPORTS_BOTH_VIEWS_OK', folder, flush=True)
