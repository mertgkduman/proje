import importlib.util,json,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('harness',c.parent/'04-04-checks'/'samsun-reply-validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.HERE=c;h.SOURCE=h.DATA/'practices'/'sources'/'emep';case='joint-2020-emep-v2';stem='0410-joint-2020-emep';p=c/(case+'-draft.json');r=c/(case+'-review-draft.json')
assert h.sha(p)=='a54cbfcd727547b1bb9133f6564d92fe5edd278a7f08662162c96e8c998bdc67';assert h.sha(r)=='f730e495aa9df23b253265cdc06c4cdb13a560940508e6c62ba317c2d1911c95'
draft=json.loads(p.read_bytes())['practice_records'];assert (len(draft['practice_event']),len(draft['practice_relation']),len(draft['practice_closure']))==(84,79,0)
receipt=h.main(p,r,case,stem+'-event','0410-2023-kongre-relation',None,expected_party='emep',namespace='gsd-0410');folder=Path(receipt['preview']);saved=json.loads((folder/'records.json').read_text());page=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table in ('practice_event','practice_relation','practice_candidate','practice_contribution','practice_actor_period'):
  for row in draft[table]:
   assert row in saved[table];key='contribution_id' if table=='practice_actor_period' else 'id';assert row==dict(db.execute('SELECT * FROM '+table+' WHERE '+key+'=?',(row[key],)).fetchone())
 assert db.execute('SELECT contribution_kind FROM practice_contribution WHERE id=?',(stem+'-contribution',)).fetchone()[0]=='support'
 assert not db.execute('SELECT 1 FROM practice_relation WHERE event_id=?',(stem+'-event',)).fetchone()
for view in ('party','comparison'):
 anchor=view+'-unmatched-'+stem+'-unmatched';tag='id="'+anchor+'"';assert page.count(tag)==1 and 'href="#'+anchor+'"' in page
 card=page.split(tag,1)[1].split('</article>',1)[0]
 for text in ('18 Mayıs 2020','EMEP'):assert text in card,(view,text)
print('JOINT2020_EMEP_BOTH_VIEWS_OK',folder,flush=True)
