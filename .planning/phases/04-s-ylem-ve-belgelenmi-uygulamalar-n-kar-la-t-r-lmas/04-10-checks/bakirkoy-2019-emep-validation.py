import importlib.util,json,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('harness',c.parent/'04-04-checks'/'samsun-reply-validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.HERE=c;h.SOURCE=h.DATA/'practices'/'sources'/'emep';case='bakirkoy-2019-emep';stem='0410-bakirkoy-2019-emep';p=c/(case+'-draft.json');r=c/(case+'-review-draft.json')
assert h.sha(p)=='570fd88c8aba0e216dd9e6568f0775421317b210bc6cc6bfbb7fa3be011cfec2';assert h.sha(r)=='8ac039468285698df17517d11d0dcd2613d1b97d63084a6bd739f4f465754645'
draft=json.loads(p.read_bytes())['practice_records'];assert (len(draft['practice_event']),len(draft['practice_relation']),len(draft['practice_closure']))==(85,79,0)
receipt=h.main(p,r,case,stem+'-event','0410-2023-kongre-relation',None,expected_party='emep',namespace='gsd-0410');folder=Path(receipt['preview']);saved=json.loads((folder/'records.json').read_text());page=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table in ('practice_event','practice_relation','practice_candidate','practice_contribution','practice_actor_period'):
  for row in draft[table]:
   assert row in saved[table];key='contribution_id' if table=='practice_actor_period' else 'id';assert row==dict(db.execute('SELECT * FROM '+table+' WHERE '+key+'=?',(row[key],)).fetchone())
 assert db.execute('SELECT contribution_kind FROM practice_contribution WHERE id=?',(stem+'-contribution',)).fetchone()[0]=='unknown'
 assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(stem+'-event',)).fetchone()
for view in ('party','comparison'):
 anchor=view+'-unmatched-'+stem+'-unmatched';tag='id="'+anchor+'"';assert page.count(tag)==1 and 'href="#'+anchor+'"' in page
 card=page.split(tag,1)[1].split('</article>',1)[0]
 for text in ('Bakırköy','EMEP'):assert text in card,(view,text)
print('BAKIRKOY2019_EMEP_BOTH_VIEWS_OK',folder,flush=True)
