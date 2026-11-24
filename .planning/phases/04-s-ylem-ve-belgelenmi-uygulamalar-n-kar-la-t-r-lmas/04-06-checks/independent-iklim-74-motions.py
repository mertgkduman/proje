import hashlib,json,os,sqlite3
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent; root=c.parents[3]; job=os.environ['SLURM_JOB_ID']; sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
p=c/'iklim-74-motions-dem-draft.json'; r=c/'iklim-74-motions-dem-review-draft.json'; old=root/'data/practices/04-dem.json'; oldr=root/'data/practices/04-dem-review.json'
assert sha(p)=='7dc82e7d70810259015b37ffb2cca472caf3615003ed4192276f7c4821c1baec' and sha(r)=='65b2e90196b3c3cc469a168d8b90a047e9645add50d40568ac48ca4d4e1cbbca'
assert sha(old)=='a69ef44ead1395255f616827b1423d8326e7f46f1898dfa9993f27f041bb8827' and sha(oldr)=='a12e3613feb8199388f0f8672f1d67bcd7ddc1c5c8604abc35dac1702484ccaf'
b,n=json.loads(old.read_text()),json.loads(p.read_text())
for k in ('entries','scope_inventory'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
br,nr=json.loads(oldr.read_text()),json.loads(r.read_text())
for k,rows in br.items():assert {canon(x) for x in rows}<={canon(x) for x in nr[k]}
receipt=json.loads((c/f'dem-iklim-74-motions-{job}.json').read_text()); folder=Path(receipt['preview']); assert folder.resolve().is_relative_to(Path(os.environ['GSD0404_PREVIEW_STAGING']).resolve())
manifest=json.loads((folder/'manifest.json').read_text()); assert manifest['renderer_version']==31
for name,h in manifest['files'].items():assert sha(folder/name)==h
snap=json.loads((folder/'records.json').read_text()); events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==81 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==11
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True); html=(folder/'index.html').read_text()
for event in events: assert db.execute('select 1 from practice_event where id=?',(event,)).fetchone()
for number in range(1,5):
 q=f'0406-iklim-74-motions-{number}'; row=db.execute('select event_id,actor_id,membership_passage_id,responsibility_limit from practice_contribution where id=?',(q+'-contribution',)).fetchone(); assert row[:3]==(q+'-event','0406-iklim-74-motions-actor','0406-iklim-74-motions-membership') and 'oyu çıkarılmaz' in row[3]
 assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'-candidate',)).fetchone()==('unmatched',None)
 for prefix in ('party','comparison'):
  a=html.index(f'id="{prefix}-unmatched-{q}-candidate"'); z=html.index('</article>',a); assert f'data-finding-id="{q}-finding"' in html[a:z]
for num in ('2879','2880'): assert db.execute('select 1 from practice_relation where id=?',(f'0406-sivas-2024-{num}-relation',)).fetchone()
db.close(); out=dict(job=job,checked_at=datetime.now(timezone.utc).isoformat(),package_sha256=sha(p),review_sha256=sha(r),preview=str(folder),manifest_sha256=sha(folder/'manifest.json'),renderer_version=31,event_count=81,relation_count=11,checks=['old records and review retained','manifest files','81 events SQLite and JSON','four signed amendments in both HTML views'],status='passed')
(c/f'dem-iklim-74-motions-{job}-independent.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(out,ensure_ascii=False,indent=2))
