"""Verify the group agenda and the separate written response in both reader views."""

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
case='textile-2881'
stem='0408-textile-2881'
package=checks/f'{case}-draft.json'
review=checks/f'{case}-review-draft.json'
assert harness.sha(package)=='157bb81f42eacf833157aaad22e678302924288a6b8a3820a1b4015f67c89fff'
assert harness.sha(review)=='fe6419877162c9d2cfb75cc56c58fee38bb3847728a85fe734450c5bb3b7bc02'
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
    assert db.execute('SELECT count(*) FROM practice_dispute_evidence WHERE dispute_id=?',
                      (stem+'-export-dispute',)).fetchone()[0]==3
    assert db.execute('SELECT count(*) FROM practice_contribution WHERE event_id=?',
                      (stem+'-29149-event',)).fetchone()[0]==0
page=(folder/'index.html').read_text()
phrases={
    '-candidate':('10/2881','Mehmet Emin Ekmen','Gündemde','19,2 milyar','19,3 milyar'),
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
print('YENI_YOL_TEXTILE_BOTH_VIEWS_OK',folder,flush=True)
