import importlib.util,json,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];spec=importlib.util.spec_from_file_location('harness',c.parent/'04-04-checks'/'samsun-reply-validation.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.HERE=c;h.SOURCE=h.DATA/'practices/sources/iyi'
p=c/'akbelen-iyi-draft.json';r=c/'akbelen-iyi-review-draft.json';assert h.sha(p)=='1a0960a4d5eac4c029cfad9e985bc13c1c46ae05a3834cd887e5ccb0e66835bf' and h.sha(r)=='e10e4e42084be8a82108dd93b13a0c7a30cd92e68de84f80e11d3962121ff0ad'
b=json.loads((root/'data/practices/04-iyi.json').read_text());n=json.loads(p.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory','source_review_refs'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
records=n['practice_records'];assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(21,13,0)
receipt=h.main(p,r,'akbelen-iyi','0407-akbelen-2023-event','0407-akbelen-2023-relation',None,expected_party='iyi',namespace='gsd-0407')
folder=Path(receipt['preview']);assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 q='0407-akbelen-2023-';assert db.execute('select common_event_key,event_at from practice_event where id=?',(q+'event',)).fetchone()==('tbmm-28-1-18-akbelen-8-14-on-gorusme','2023-08-08')
 assert db.execute('select actor_id,authority_passage_id from practice_contribution where id=?',(q+'contribution',)).fetchone()==(q+'ergun-actor',q+'floor-role')
 assert db.execute('select statement_at from practice_statement where id=?',(q+'statement',)).fetchone()==('2023-08-07',)
 assert db.execute('select stage from practice_event_evidence where event_id=? and passage_id=?',(q+'event',q+'floor-result')).fetchone()==('result',)
html=(folder/'index.html').read_text()
for v in ('party','comparison'):
 a=html.index(f'id="{v}-practice-0407-akbelen-2023-relation"');z=html.index('</article>',a);assert 'data-finding-id="0407-akbelen-2023-explanation"' in html[a:z]
print('IYI_AKBELEN_TWENTY_ONE_EVENTS_BOTH_VIEWS_OK',flush=True)
