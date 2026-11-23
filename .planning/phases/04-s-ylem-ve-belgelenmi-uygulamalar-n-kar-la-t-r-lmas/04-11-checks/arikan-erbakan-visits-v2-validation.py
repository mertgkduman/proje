"""Verify the two documented meetings and the narrowly linked visit statement."""

import importlib.util
import json
from pathlib import Path
import sqlite3

here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
    'practice_validation',here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness=importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE=here
harness.SOURCE=harness.DATA/'practices'/'sources'/'saadet'
scope='arikan-erbakan-visits-v2'
draft_path=here/f'{scope}-draft.json'
review=here/f'{scope}-review-draft.json'
assert harness.sha(draft_path)=='7ac56d371f684a068d5a7f0710739eac8ba64e05fa7c257f3683073a34a34736'
assert harness.sha(review)=='c0793f3394a829343dcf492eca79dadcd0a6c8254cfffb35e16a0d70686b9602'
draft=json.loads(draft_path.read_bytes())['practice_records']
assert (len(draft['practice_event']),len(draft['practice_relation']),len(draft['practice_closure']))==(16,13,0)
jan='0411-arikan-erbakan-2026-01-28'
aug='0411-arikan-erbakan-2026-08-11'
eid=aug+'-event'
rid=aug+'-relation'
receipt=harness.main(draft_path,review,scope,eid,rid,None,expected_party='saadet',namespace='gsd-0411')
folder=Path(receipt['preview'])
manifest=json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version']==31
export=json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for table,ids in [('practice_event',(jan+'-event',eid)),('practice_relation',(rid,)),
                      ('practice_candidate',(jan+'-unmatched',aug+'-candidate'))]:
        for identity in ids:
            row=next(r for r in draft[table] if r['id']==identity)
            assert row in export[table]
            assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(identity,)).fetchone())
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(jan+'-unmatched',)).fetchone()[0]=='unmatched'
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(aug+'-candidate',)).fetchone()[0]=='eligible'
    assert db.execute("SELECT occurrence_basis FROM practice_event WHERE id='0411-saadet-2026-kocasinan-kongre-event'").fetchone()[0].startswith('28 Ağustos tarihli Kayseri Haber')
report=(folder/'index.html').read_text()
for view in ('party','comparison'):
    for kind,identity,terms in [
        ('unmatched',jan+'-unmatched',('28 Ocak','DHA','imzalı toplantı tutanağı')),
        ('practice',rid,('11 Ağustos','karşılıklı ziyaret','İmzalı ittifak protokolü')),
    ]:
        anchor=f'{view}-{kind}-{identity}'
        tag=f'id="{anchor}"'
        assert report.count(tag)==1 and f'href="#{anchor}"' in report,tag
        card=report.split(tag,1)[1].split('</article>',1)[0]
        for term in terms:
            assert term.casefold().replace('i̇','i') in card.casefold().replace('i̇','i'),(view,identity,term)
print('SAADET_FOLLOWUP_VISITS_BOTH_VIEWS_OK',folder,flush=True)
