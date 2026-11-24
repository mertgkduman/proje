import importlib.util,json,os,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('tracer',c/'tracer-validation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=c/'ankara-workshop-dem-draft.json';r=c/'ankara-workshop-dem-review-draft.json';assert m.sha(p)=='f33e33f8debe5f64bf1a1bf963a4bc859cb90faa4b7608d86958235f754dd47e' and m.sha(r)=='cdf7844f566de2c78947d68043178fbb9c7ab800065d7768776569a99d8d685e'
b=json.loads((root/'data/practices/04-dem.json').read_text());n=json.loads(p.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
m.main(p,r,'dem-ankara-workshop','0406-ankara-workshop-event','0406-iklim-group-final-relation','')
receipt=json.loads((c/f'dem-ankara-workshop-{job}.json').read_text());folder=Path(receipt['preview']);assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==84 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==12
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();q='0406-ankara-workshop'
assert db.execute('select event_id,actor_id from practice_contribution where id=?',(q+'-contribution',)).fetchone()==(q+'-event','0406-dem-institution')
assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'-candidate',)).fetchone()==('unmatched',None)
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-unmatched-{q}-candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}-finding"' in html[a:z]
db.close();print('EIGHTY_FOUR_EVENTS_BOTH_VIEWS_OK',flush=True)
