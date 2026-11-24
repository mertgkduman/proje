import hashlib,json,os,sqlite3
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
p=c/'iklim-komisyon-katilim-dem-draft.json';r=c/'iklim-komisyon-katilim-dem-review-draft.json';old=root/'data/practices/04-dem.json';oldr=root/'data/practices/04-dem-review.json'
assert sha(p)=='b6c2bcf6281edde82d810c891619a23345ae0f22d4a4e1a09a697ff43588f2d6' and sha(r)=='b533770946e85e460db56c4e2fba684648ad6c35111afcbd8aec6d2b7b6ef3da'
assert sha(old)=='666ba732e46b5a6bc9524fee2f4cb3c82774a0258fb44830094982f8a5c8549f' and sha(oldr)=='f749c62f4be4c1dc6f22638181c390735f981b5061cadc60f07489ac31361165'
b,n=json.loads(old.read_text()),json.loads(p.read_text())
for k in ('entries','scope_inventory'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
br,nr=json.loads(oldr.read_text()),json.loads(r.read_text())
for k,rows in br.items():assert {canon(x) for x in rows}<={canon(x) for x in nr[k]}
receipt=json.loads((c/f'dem-iklim-komisyon-katilim-{job}.json').read_text());folder=Path(receipt['preview']);assert folder.resolve().is_relative_to(Path(os.environ['GSD0404_PREVIEW_STAGING']).resolve());manifest=json.loads((folder/'manifest.json').read_text());assert manifest['renderer_version']==31
for name,h in manifest['files'].items():assert sha(folder/name)==h
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==83 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==12
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();q='0406-iklim-komisyon-katilim'
for event in events:assert db.execute('select 1 from practice_event where id=?',(event,)).fetchone()
row=db.execute('select actor_id,membership_passage_id,responsibility_limit from practice_contribution where id=?',(q+'-contribution',)).fetchone();assert row[:2]==('0406-iklim-final-koca-actor',q+'-membership') and 'kişisel oy' in row[2]
assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'-candidate',)).fetchone()==('unmatched',None)
for key in ('reply','heard'):assert db.execute('select stage from practice_event_evidence where event_id=? and passage_id=?',(q+'-event',q+'-'+key)).fetchone()==('result',)
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-unmatched-{q}-candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}-finding"' in html[a:z]
 a=html.index(f'id="{prefix}-practice-0406-iklim-group-final-relation"');z=html.index('</article>',a);assert 'data-finding-id="0406-iklim-group-final-explanation"' in html[a:z]
db.close();out=dict(job=job,checked_at=datetime.now(timezone.utc).isoformat(),package_sha256=sha(p),review_sha256=sha(r),preview=str(folder),manifest_sha256=sha(folder/'manifest.json'),renderer_version=31,event_count=83,relation_count=12,checks=['old records and review retained','manifest files','83 events SQLite and JSON','Koca request and prior relation in both HTML views'],status='passed');(c/f'dem-iklim-komisyon-katilim-{job}-independent.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
