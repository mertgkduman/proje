"""Verify both archival edition rows in the 10/2881 dispute."""

import importlib.util
import json
from pathlib import Path
import sqlite3

checks=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
    'practice_validation',checks.parent/'04-04-checks'/'samsun-reply-validation.py')
harness=importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE=checks
harness.SOURCE=harness.DATA/'practices'/'sources'/'yeni-yol'
case='textile-series'
stem='0408-textile-2881'
package=checks/f'{case}-draft.json'
review=checks/f'{case}-review-draft.json'
assert harness.sha(package)=='07a7acdd87ff461abe7fd3f75f1e4e60ef4805c6cbdf2eab7f60756b703d9f6a'
assert harness.sha(review)=='1b89ab0381dad5fc48a00a603c5624ed34489205d60d6bde83a5c7f298c79115'
records=json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(23,12,0)
receipt=harness.main(package,review,case,stem+'-event','0408-chair-rotation-relation',None,
                     expected_party='yeni-yol',namespace='gsd-0408')
folder=Path(receipt['preview'])
manifest=json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version']==31
export=json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    expected={
        'practice_event':('-event','-29149-event'),
        'practice_contribution':('-contribution',),
        'practice_dispute':('-export-dispute',),
        'practice_candidate':('-candidate','-29149-candidate'),
    }
    for table,suffixes in expected.items():
        for suffix in suffixes:
            identity=stem+suffix
            row=next(row for row in records[table] if row['id']==identity)
            assert row in export[table]
            assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(identity,)).fetchone())
    assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id IN (?,?)',
                          (stem+'-event',stem+'-29149-event')).fetchone()
    dispute_rows = [dict(row) for row in db.execute(
        'SELECT * FROM practice_dispute_evidence WHERE dispute_id=?', (stem+'-export-dispute',))]
    assert len(dispute_rows)==5 and all(row in export['practice_dispute_evidence'] for row in dispute_rows)
    assert {r['passage_id'] for r in dispute_rows if 'textile-series' in r['passage_id']} == {
        '0408-textile-series-2023-value', '0408-textile-series-2024-value'}
    assert db.execute('SELECT count(*) FROM practice_contribution WHERE event_id=?',
                      (stem+'-29149-event',)).fetchone()[0]==0
page=(folder/'index.html').read_text()
phrases={
    '-candidate':('10/2881','Mehmet Emin Ekmen','Gündemde','19,2 milyar','19,3 milyar','19.316.151','19.242.984','73.167.000'),
    '-29149-candidate':('7/29149','9 Temmuz','2.500 TL','konkordato','sektör kırılımı'),
}
for view in ('party','comparison'):
    for suffix,terms in phrases.items():
        anchor=f'{view}-unmatched-{stem}{suffix}'
        tag=f'id="{anchor}"'
        assert page.count(tag)==1 and f'href="#{anchor}"' in page,anchor
        card=page.split(tag,1)[1].split('</article>',1)[0]
        for term in terms:
            assert term.casefold() in card.casefold(),(view,suffix,term)
print('YENI_YOL_TEXTILE_SERIES_BOTH_VIEWS_OK',folder,flush=True)
