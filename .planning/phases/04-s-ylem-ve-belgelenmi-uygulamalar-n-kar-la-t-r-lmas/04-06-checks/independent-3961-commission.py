import hashlib,json,os,sqlite3
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
p=c/'3961-commission-dem-draft.json';r=c/'3961-commission-dem-review-draft.json';old=root/'data/practices/04-dem.json';oldr=root/'data/practices/04-dem-review.json'
assert sha(p)=='da836b07b4cb4ac61bcaefe6eaf744ce66c1effcdf714df1ea97ec946818c9df' and sha(r)=='02db365953f11836672a19ef088ede88ac970d075cfbaa2f6dd835a5f1195891'
assert sha(old)=='eecb16315fbf1990c664601e4591e7718e66858e8fedc948b8041064e4e5c4cd' and sha(oldr)=='2f7df55e18057a6c9060e578a47bb3424e4260f631b54c6cebe5291adeac9bb8'
b,n=json.loads(old.read_text()),json.loads(p.read_text())
for k in ('entries','scope_inventory','source_review_refs'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
br,nr=json.loads(oldr.read_text()),json.loads(r.read_text())
for k,rows in br.items():assert {canon(x) for x in rows}<={canon(x) for x in nr[k]}
receipt=json.loads((c/f'dem-3961-commission-{job}.json').read_text());folder=Path(receipt['preview']);assert folder.resolve().is_relative_to(Path(os.environ['GSD0404_PREVIEW_STAGING']).resolve());manifest=json.loads((folder/'manifest.json').read_text());assert manifest['renderer_version']==31
for name,h in manifest['files'].items():assert sha(folder/name)==h
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==89 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==13
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();q='0406-3961-commission'
for event in events:assert db.execute('select 1 from practice_event where id=?',(event,)).fetchone()
row=db.execute('select actor_id,contribution_kind,responsibility_limit from practice_contribution where id=?',(q+'-contribution',)).fetchone();assert row[0]==q+'-cupolo-actor' and row[1]=='objection' and 'isimli oy' in row[2]
assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'-candidate',)).fetchone()==('unmatched',None)
event=db.execute('select common_event_key,scope_context from practice_event where id=?',(q+'-event',)).fetchone();assert event[0]=='tbmm-28-5-disisleri-2026-10-27-2-3961' and '2/3961' in event[1]
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-unmatched-{q}-candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}-finding"' in html[a:z]
db.close();out=dict(job=job,checked_at=datetime.now(timezone.utc).isoformat(),package_sha256=sha(p),review_sha256=sha(r),preview=str(folder),manifest_sha256=sha(folder/'manifest.json'),renderer_version=31,event_count=89,relation_count=13,checks=['old records and reviews retained','manifest files','89 events SQLite and JSON','Cupolo individual speech and committee majority','candidate in both HTML views'],status='passed');(c/f'dem-3961-commission-{job}-independent.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
