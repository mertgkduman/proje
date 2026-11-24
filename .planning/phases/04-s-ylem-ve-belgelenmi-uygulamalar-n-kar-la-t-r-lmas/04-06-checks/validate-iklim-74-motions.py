import importlib.util, json, os, sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent; root=c.parents[3]; job=os.environ['SLURM_JOB_ID']
spec=importlib.util.spec_from_file_location('tracer',c/'tracer-validation.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=c/'iklim-74-motions-dem-draft.json'; r=c/'iklim-74-motions-dem-review-draft.json'
assert m.sha(p)=='7dc82e7d70810259015b37ffb2cca472caf3615003ed4192276f7c4821c1baec'
assert m.sha(r)=='65b2e90196b3c3cc469a168d8b90a047e9645add50d40568ac48ca4d4e1cbbca'
before=json.loads((root/'data/practices/04-dem.json').read_text()); after=json.loads(p.read_text()); canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory'): assert {canon(x) for x in before[k]} <= {canon(x) for x in after[k]}
for k,rows in before['practice_records'].items(): assert {canon(x) for x in rows} <= {canon(x) for x in after['practice_records'][k]}
m.main(p,r,'dem-iklim-74-motions','0406-iklim-74-motions-1-event','0406-sivas-2024-2879-relation','')
receipt=json.loads((c/f'dem-iklim-74-motions-{job}.json').read_text()); folder=Path(receipt['preview'])
assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
snap=json.loads((folder/'records.json').read_text()); events={x['id'] for x in after['practice_records']['practice_event']}; assert len(events)==81 and events<={x['id'] for x in snap['practice_event']}
assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==11
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True); html=(folder/'index.html').read_text()
for n in range(1,5):
 q=f'0406-iklim-74-motions-{n}'
 assert db.execute('select event_id, contribution_kind, membership_passage_id from practice_contribution where id=?',(q+'-contribution',)).fetchone()==(q+'-event','task','0406-iklim-74-motions-membership')
 assert db.execute('select valid_from,valid_to from practice_actor_period where contribution_id=?',(q+'-contribution',)).fetchone()==('2025-04-09','2025-04-09')
 for prefix in ('party','comparison'):
  a=html.index(f'id="{prefix}-unmatched-{q}-candidate"'); b=html.index('</article>',a); assert f'data-finding-id="{q}-finding"' in html[a:b]
db.close(); print('EIGHTY_ONE_EVENTS_FOUR_MOTIONS_BOTH_VIEWS_OK',flush=True)
