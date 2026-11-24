import importlib.util,json,os,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('tracer',c/'tracer-validation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=c/'van-2024-dem-draft.json';r=c/'van-2024-dem-review-draft.json';assert m.sha(p)=='06f92639c132bb92389aa8109d2eb21af01aa4c0c6cb8141042933ee3cf53b43' and m.sha(r)=='1c8514fa09acb88021b25ca81460dfbe8aa5061f3ac093edf994062f7ad10231'
b=json.loads((root/'data/practices/04-dem.json').read_text());n=json.loads(p.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory','source_review_refs'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
m.main(p,r,'dem-van-2024','0406-van-2024-event','0406-van-2024-relation','')
receipt=json.loads((c/f'dem-van-2024-{job}.json').read_text());folder=Path(receipt['preview']);assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==87 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==13
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();q='0406-van-2024'

assert db.execute('select event_id,statement_id from practice_relation where id=?',(q+'-relation',)).fetchone()==(q+'-event',q+'-statement')
assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'-candidate',)).fetchone()==('eligible',q+'-relation')
for prefix in ('party','comparison'):
 a=html.index(f'id=\"{prefix}-practice-{q}-relation\"');z=html.index('</article>',a);assert f'data-finding-id=\"{q}-explanation\"' in html[a:z]
db.close();print('EIGHTY_SEVEN_EVENTS_THIRTEEN_RELATIONS_BOTH_VIEWS_OK',flush=True)
