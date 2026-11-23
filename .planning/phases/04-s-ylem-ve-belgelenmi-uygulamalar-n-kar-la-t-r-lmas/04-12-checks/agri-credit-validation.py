"""Verify the separate 2/3485, 2/3970 and institutional notice records."""

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
harness.SOURCE=harness.DATA/'practices'/'sources'/'demokrat'
case='agri-credit'
stem='0412-agri-credit-'
package=checks/f'{case}-draft.json'
review=checks/f'{case}-review-draft.json'
assert harness.sha(package)=='53d65b9d18651e55c91dfc7477517e984e5c1666efb445711d33568895d62700'
assert harness.sha(review)=='c63786406af1d4d83d98f7177c42c316efc40ff96c8df741f9950ab2abfd8845'
records=json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(31,28,0)
receipt=harness.main(package,review,case,stem+'3485-event',stem+'3485-relation',None,
                     expected_party='demokrat',namespace='gsd-0412')
folder=Path(receipt['preview'])
manifest=json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version']==31
export=json.loads((folder/'records.json').read_bytes())
labels=('3485','ministry','3970')
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for table,kind in (('practice_event','event'),('practice_relation','relation'),('practice_candidate','candidate')):
        for label in labels:
            identity=stem+label+'-'+kind
            row=next(row for row in records[table] if row['id']==identity)
            assert row in export[table],identity
            assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(identity,)).fetchone()),identity
    for label in ('3485','3970'):
        assert not db.execute("SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'",
                              (stem+label+'-event',)).fetchone()
    assert db.execute("SELECT count(*) FROM practice_event_evidence WHERE event_id=? AND stage='result'",
                      (stem+'ministry-event',)).fetchone()[0]==4
page=(folder/'index.html').read_text()
phrases={
    '3485':('2/3485','faizsiz uzun vadeye','Komisyonda'),
    'ministry':('400.000 TL','300.000 TL','Ardahan','fiilî kredi'),
    '3970':('2/3970','GSYİH','avans','gayrisafi millî hasıla'),
}
for view in ('party','comparison'):
    for label,terms in phrases.items():
        anchor=f'{view}-practice-{stem}{label}-relation'
        tag=f'id="{anchor}"'
        assert page.count(tag)==1 and f'href="#{anchor}"' in page,anchor
        card=page.split(tag,1)[1].split('</article>',1)[0]
        for term in terms:
            assert term.casefold() in card.casefold(),(view,label,term)
print('DEMOKRAT_AGRI_CREDIT_BOTH_VIEWS_OK',folder,flush=True)
