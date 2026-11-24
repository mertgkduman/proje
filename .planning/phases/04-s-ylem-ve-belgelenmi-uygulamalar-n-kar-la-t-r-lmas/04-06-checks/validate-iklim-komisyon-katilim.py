import importlib.util,json,os,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('tracer',c/'tracer-validation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=c/'iklim-komisyon-katilim-dem-draft.json';r=c/'iklim-komisyon-katilim-dem-review-draft.json';assert m.sha(p)=='b6c2bcf6281edde82d810c891619a23345ae0f22d4a4e1a09a697ff43588f2d6' and m.sha(r)=='b533770946e85e460db56c4e2fba684648ad6c35111afcbd8aec6d2b7b6ef3da'
b=json.loads((root/'data/practices/04-dem.json').read_text());n=json.loads(p.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
m.main(p,r,'dem-iklim-komisyon-katilim','0406-iklim-komisyon-katilim-event','0406-iklim-group-final-relation','')
receipt=json.loads((c/f'dem-iklim-komisyon-katilim-{job}.json').read_text());folder=Path(receipt['preview']);assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==83 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==12
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();q='0406-iklim-komisyon-katilim'
assert db.execute('select event_id,actor_id,membership_passage_id from practice_contribution where id=?',(q+'-contribution',)).fetchone()==(q+'-event','0406-iklim-final-koca-actor',q+'-membership')
assert db.execute('select valid_from,valid_to from practice_actor_period where contribution_id=?',(q+'-contribution',)).fetchone()==('2025-02-26','2025-02-26')
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-unmatched-{q}-candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}-finding"' in html[a:z]
db.close();print('EIGHTY_THREE_EVENTS_KOCA_BOTH_VIEWS_OK',flush=True)
