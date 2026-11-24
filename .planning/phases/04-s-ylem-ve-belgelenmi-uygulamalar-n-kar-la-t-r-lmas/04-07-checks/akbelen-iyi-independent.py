import hashlib,json,os,sqlite3
from pathlib import Path
from datetime import datetime,timezone
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
p=c/'akbelen-iyi-draft.json';r=c/'akbelen-iyi-review-draft.json';old=root/'data/practices/04-iyi.json';oldr=root/'data/practices/04-iyi-review.json'
assert sha(p)=='1a0960a4d5eac4c029cfad9e985bc13c1c46ae05a3834cd887e5ccb0e66835bf' and sha(r)=='e10e4e42084be8a82108dd93b13a0c7a30cd92e68de84f80e11d3962121ff0ad'
assert sha(old)=='f63197aab0d8acb54fb11d4477837f6e49c1c04d008165aeda445895abf7c0ff' and sha(oldr)=='e7a920753b3381200d79c8f39851f6e197ee816fe114b5032761f81fe2535237'
b,n=json.loads(old.read_text()),json.loads(p.read_text())
for k in ('entries','scope_inventory','source_review_refs'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
br,nr=json.loads(oldr.read_text()),json.loads(r.read_text())
for k,rows in br.items():assert {canon(x) for x in rows}<={canon(x) for x in nr[k]}
receipt=json.loads((c/f'akbelen-iyi-{job}.json').read_text());folder=Path(receipt['preview']);assert folder.resolve().is_relative_to(Path(os.environ['GSD0404_PREVIEW_STAGING']).resolve());m=json.loads((folder/'manifest.json').read_text());assert m['renderer_version']==31
for name,digest in m['files'].items():assert sha(folder/name)==digest
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==21 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='iyi'])==13
q='0407-akbelen-2023-';db=sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True)
for eid in events:assert db.execute('select 1 from practice_event where id=?',(eid,)).fetchone()
assert db.execute('select statement_at,version_id from practice_statement where id=?',(q+'statement',)).fetchone()==('2023-08-07',q+'news-v1')
assert db.execute('select actor_id,authority_passage_id from practice_contribution where id=?',(q+'contribution',)).fetchone()==(q+'ergun-actor',q+'floor-role')
assert db.execute('select result_finding_id from practice_relation where id=?',(q+'relation',)).fetchone()==(None,)
assert db.execute('select stage from practice_event_evidence where event_id=? and passage_id=?',(q+'event',q+'floor-result')).fetchone()==('result',);db.close()
html=(folder/'index.html').read_text()
for v in ('party','comparison'):
 a=html.index(f'id="{v}-practice-{q}relation"');z=html.index('</article>',a);assert f'data-finding-id="{q}explanation"' in html[a:z]
out=dict(job=job,checked_at=datetime.now(timezone.utc).isoformat(),package_sha256=sha(p),review_sha256=sha(r),preview=str(folder),manifest_sha256=sha(folder/'manifest.json'),renderer_version=31,event_count=21,relation_count=13,checks=['append-only records and reviews','manifest files','21 events in SQLite and JSON','dated spokesperson statement and Ergun group authority','both HTML views'],status='passed');(c/f'akbelen-iyi-{job}-independent.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
