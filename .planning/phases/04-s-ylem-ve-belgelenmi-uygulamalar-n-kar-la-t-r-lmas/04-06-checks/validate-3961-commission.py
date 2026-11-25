import importlib.util,json,os,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('tracer',c/'tracer-validation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=c/'3961-commission-dem-draft.json';r=c/'3961-commission-dem-review-draft.json';assert m.sha(p)=='da836b07b4cb4ac61bcaefe6eaf744ce66c1effcdf714df1ea97ec946818c9df' and m.sha(r)=='02db365953f11836672a19ef088ede88ac970d075cfbaa2f6dd835a5f1195891'
b=json.loads((root/'data/practices/04-dem.json').read_text());n=json.loads(p.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory','source_review_refs'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
m.main(p,r,'dem-3961-commission','0406-3961-commission-event','0406-iklim-group-final-relation','')
receipt=json.loads((c/f'dem-3961-commission-{job}.json').read_text());folder=Path(receipt['preview']);assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==89 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==13
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();q='0406-3961-commission'
assert db.execute('select event_id,actor_id,contribution_kind from practice_contribution where id=?',(q+'-contribution',)).fetchone()==(q+'-event',q+'-cupolo-actor','objection')
assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'-candidate',)).fetchone()==('unmatched',None)
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-unmatched-{q}-candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}-finding"' in html[a:z]
db.close();print('EIGHTY_NINE_EVENTS_BOTH_VIEWS_OK',flush=True)
