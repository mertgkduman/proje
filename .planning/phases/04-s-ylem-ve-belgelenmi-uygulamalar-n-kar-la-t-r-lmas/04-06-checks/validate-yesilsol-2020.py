import importlib.util,json,os,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('tracer',c/'tracer-validation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=c/'yesilsol-2020-dem-draft.json';r=c/'yesilsol-2020-dem-review-draft.json';assert m.sha(p)=='eecb16315fbf1990c664601e4591e7718e66858e8fedc948b8041064e4e5c4cd' and m.sha(r)=='2f7df55e18057a6c9060e578a47bb3424e4260f631b54c6cebe5291adeac9bb8'
b=json.loads((root/'data/practices/04-dem.json').read_text());n=json.loads(p.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory','source_review_refs'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
m.main(p,r,'dem-yesilsol-2020','0406-yesilsol-2020-event','0406-iklim-group-final-relation','')
receipt=json.loads((c/f'dem-yesilsol-2020-{job}.json').read_text());folder=Path(receipt['preview']);assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==88 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==13
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();q='0406-yesilsol-2020'
assert db.execute('select event_id,actor_id,contribution_kind from practice_contribution where id=?',(q+'-contribution',)).fetchone()==(q+'-event','0406-dem-institution','unknown')
assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'-candidate',)).fetchone()==('unmatched',None)
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-unmatched-{q}-candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}-finding"' in html[a:z]
db.close();print('EIGHTY_EIGHT_EVENTS_BOTH_VIEWS_OK',flush=True)
