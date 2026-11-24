import hashlib,json,os,sqlite3
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
p=c/'iklim-73-group-dem-draft.json';r=c/'iklim-73-group-dem-review-draft.json';old=root/'data/practices/04-dem.json';oldr=root/'data/practices/04-dem-review.json'
assert sha(p)=='6e98b8a1a312c439b9076602c704cf5b1661080fc98e3a76ff938981645d2c81' and sha(r)=='a8556fd440f59412b678e32b0864ba65eff66b96d50cfaefb61e672c2e4d6486'
assert sha(old)=='7dc82e7d70810259015b37ffb2cca472caf3615003ed4192276f7c4821c1baec' and sha(oldr)=='65b2e90196b3c3cc469a168d8b90a047e9645add50d40568ac48ca4d4e1cbbca'
b,n=json.loads(old.read_text()),json.loads(p.read_text())
for k in ('entries','scope_inventory'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
br,nr=json.loads(oldr.read_text()),json.loads(r.read_text())
for k,rows in br.items():assert {canon(x) for x in rows}<={canon(x) for x in nr[k]}
receipt=json.loads((c/f'dem-iklim-73-group-{job}.json').read_text());folder=Path(receipt['preview']);assert folder.resolve().is_relative_to(Path(os.environ['GSD0404_PREVIEW_STAGING']).resolve());manifest=json.loads((folder/'manifest.json').read_text());assert manifest['renderer_version']==31
for name,h in manifest['files'].items():assert sha(folder/name)==h
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==82 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==11
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text()
for event in events:assert db.execute('select 1 from practice_event where id=?',(event,)).fetchone()
for who in ('akin','koca'):
 q='0406-iklim-73-group-'+who;row=db.execute('select event_id,authority_passage_id,responsibility_limit from practice_contribution where id=?',(q+'-contribution',)).fetchone();assert row[:2]==('0406-iklim-73-group-event',q+'-role') and 'nihai sonuç çıkarılmaz' in row[2]
 assert db.execute('select valid_from,valid_to from practice_actor_period where contribution_id=?',(q+'-contribution',)).fetchone()==('2025-04-08','2025-04-08')
 for prefix in ('party','comparison'):
  a=html.index(f'id="{prefix}-unmatched-0406-iklim-73-group-candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}-finding"' in html[a:z]
for num in range(1,5):assert db.execute('select 1 from practice_event where id=?',(f'0406-iklim-74-motions-{num}-event',)).fetchone()
assert db.execute('select state,relation_id from practice_candidate where id=?',('0406-iklim-73-group-candidate',)).fetchone()==('unmatched',None);db.close()
out=dict(job=job,checked_at=datetime.now(timezone.utc).isoformat(),package_sha256=sha(p),review_sha256=sha(r),preview=str(folder),manifest_sha256=sha(folder/'manifest.json'),renderer_version=31,event_count=82,relation_count=11,checks=['old records and review retained','manifest files','82 events SQLite and JSON','two authorized speakers in both HTML views'],status='passed');(c/f'dem-iklim-73-group-{job}-independent.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
