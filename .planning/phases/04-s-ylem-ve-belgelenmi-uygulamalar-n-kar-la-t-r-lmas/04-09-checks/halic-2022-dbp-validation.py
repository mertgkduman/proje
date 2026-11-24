import importlib.util,json,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('harness',c.parent/'04-04-checks'/'samsun-reply-validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.HERE=c;h.SOURCE=h.DATA/'practices'/'sources'/'dbp';case='halic-2022-dbp';stem='0409-halic-2022-dbp';p=c/(case+'-draft.json');r=c/(case+'-review-draft.json')
assert h.sha(p)=='3e1e0bd7bc3f05adf2cf8ca32a5d3fe0544c9f810faf15af076098bb8a86e134';assert h.sha(r)=='b5b55ae18b0851ac620adc1cfe56b774c416ae86c8623ae986e107e9b856f8fe'
draft=json.loads(p.read_bytes())['practice_records'];assert (len(draft['practice_event']),len(draft['practice_relation']),len(draft['practice_closure']))==(67,7,0)
receipt=h.main(p,r,case,stem+'-event','0409-dbp-baglar-2015-cemr-relation',None,expected_party='dbp',namespace='gsd-0409');folder=Path(receipt['preview']);saved=json.loads((folder/'records.json').read_text());page=(folder/'index.html').read_text()
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
 for text in ('Haliç','Keskin Bayındır'):assert text in card,(view,text)
print('HALIC2022_DBP_BOTH_VIEWS_OK',folder,flush=True)
