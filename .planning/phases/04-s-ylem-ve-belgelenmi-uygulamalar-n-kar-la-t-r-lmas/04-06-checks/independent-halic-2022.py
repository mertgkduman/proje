import hashlib,json,os,sqlite3
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
p=c/'halic-2022-dem-draft.json';r=c/'halic-2022-dem-review-draft.json';old=root/'data/practices/04-dem.json';oldr=root/'data/practices/04-dem-review.json'
assert sha(p)=='0f861578ff8e556d09e693cda410663d2a932a6b83d2dc1a98d01c30b3fccefc' and sha(r)=='564da8c8b14818a1b4be591dd513564e926eaf0229366207f7fdfce91161de33'
assert sha(old)=='6dbdf8957464782f99860884841dffe7037f752f0d0d7e2f48026a53f9de20f5' and sha(oldr)=='cc88060809d6915fe2af2ec37e7059e1b76fbaf504cc4256515d2a141e51e120'
b,n=json.loads(old.read_text()),json.loads(p.read_text())
for k in ('entries','scope_inventory','source_review_refs'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
br,nr=json.loads(oldr.read_text()),json.loads(r.read_text())
for k,rows in br.items():assert {canon(x) for x in rows}<={canon(x) for x in nr[k]}
receipt=json.loads((c/f'dem-halic-2022-{job}.json').read_text());folder=Path(receipt['preview']);assert folder.resolve().is_relative_to(Path(os.environ['GSD0404_PREVIEW_STAGING']).resolve());manifest=json.loads((folder/'manifest.json').read_text());assert manifest['renderer_version']==31
for name,h in manifest['files'].items():assert sha(folder/name)==h
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==86 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==12
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();q='0406-halic-2022'
for event in events:assert db.execute('select 1 from practice_event where id=?',(event,)).fetchone()
for person in ('erdem','akin'):
 row=db.execute('select actor_id,responsibility_limit from practice_contribution where id=?',(q+'-'+person+'-contribution',)).fetchone(); assert row[0]==q+'-'+person+'-actor' and 'Kurucu imza' in row[1]
assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'-candidate',)).fetchone()==('unmatched',None)
event=db.execute('select common_event_key,scope_context from practice_event where id=?',(q+'-event',)).fetchone(); assert event[0]=='halic-emek-ozgurluk-2022-09-24' and 'Haliç' in event[1]
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-unmatched-{q}-candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}-finding"' in html[a:z]
db.close();out=dict(job=job,checked_at=datetime.now(timezone.utc).isoformat(),package_sha256=sha(p),review_sha256=sha(r),preview=str(folder),manifest_sha256=sha(folder/'manifest.json'),renderer_version=31,event_count=86,relation_count=12,checks=['old records and reviews retained','manifest files','86 events SQLite and JSON','Yeşil Sol attendance and two individual contributions','candidate in both HTML views'],status='passed');(c/f'dem-halic-2022-{job}-independent.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
