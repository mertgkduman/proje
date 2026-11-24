import hashlib,json,os,sqlite3
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
p=c/'iklim-group-final-relation-dem-draft.json';r=c/'iklim-group-final-relation-dem-review-draft.json';old=root/'data/practices/04-dem.json';oldr=root/'data/practices/04-dem-review.json'
assert sha(p)=='666ba732e46b5a6bc9524fee2f4cb3c82774a0258fb44830094982f8a5c8549f' and sha(r)=='f749c62f4be4c1dc6f22638181c390735f981b5061cadc60f07489ac31361165'
assert sha(old)=='6e98b8a1a312c439b9076602c704cf5b1661080fc98e3a76ff938981645d2c81' and sha(oldr)=='a8556fd440f59412b678e32b0864ba65eff66b96d50cfaefb61e672c2e4d6486'
b,n=json.loads(old.read_text()),json.loads(p.read_text())
for k in ('entries','scope_inventory'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
br,nr=json.loads(oldr.read_text()),json.loads(r.read_text())
for k,rows in br.items():assert {canon(x) for x in rows}<={canon(x) for x in nr[k]}
receipt=json.loads((c/f'dem-iklim-group-final-{job}.json').read_text());folder=Path(receipt['preview']);assert folder.resolve().is_relative_to(Path(os.environ['GSD0404_PREVIEW_STAGING']).resolve());manifest=json.loads((folder/'manifest.json').read_text());assert manifest['renderer_version']==31
for name,h in manifest['files'].items():assert sha(folder/name)==h
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==82 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==12
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text()
for event in events:assert db.execute('select 1 from practice_event where id=?',(event,)).fetchone()
assert db.execute('select state,relation_id from practice_candidate where id=?',('0406-iklim-final-candidate',)).fetchone()==('unmatched',None)
assert db.execute('select state,relation_id from practice_candidate_revision where id=?',('0406-iklim-group-final-eligible',)).fetchone()==('eligible','0406-iklim-group-final-relation')
assert db.execute('select event_id,statement_id,result_finding_id from practice_relation where id=?',('0406-iklim-group-final-relation',)).fetchone()==('0406-iklim-final-event','0406-iklim-group-final-statement',None)
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-practice-0406-iklim-group-final-relation"');z=html.index('</article>',a)
 for fid in ('0406-iklim-group-final-explanation','0406-iklim-73-group-akin-finding','0406-iklim-final-akin-finding','0406-iklim-final-koca-finding','0406-iklim-final-kordu-finding'):assert f'data-finding-id="{fid}"' in html[a:z]
db.close();out=dict(job=job,checked_at=datetime.now(timezone.utc).isoformat(),package_sha256=sha(p),review_sha256=sha(r),preview=str(folder),manifest_sha256=sha(folder/'manifest.json'),renderer_version=31,event_count=82,relation_count=12,checks=['old records and review retained','manifest files','82 events SQLite and JSON','limited relation and all three individual votes in both HTML views'],status='passed');(c/f'dem-iklim-group-final-{job}-independent.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
