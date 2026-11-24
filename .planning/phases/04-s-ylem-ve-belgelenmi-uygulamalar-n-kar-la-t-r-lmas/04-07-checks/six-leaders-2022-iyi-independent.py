import hashlib,json,os,sqlite3
from pathlib import Path
from datetime import datetime,timezone
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
p=c/'six-leaders-2022-iyi-draft.json';r=c/'six-leaders-2022-iyi-review-draft.json';old=root/'data/practices/04-iyi.json';oldr=root/'data/practices/04-iyi-review.json'
assert sha(p)=='f63197aab0d8acb54fb11d4477837f6e49c1c04d008165aeda445895abf7c0ff' and sha(r)=='e7a920753b3381200d79c8f39851f6e197ee816fe114b5032761f81fe2535237'
assert sha(old)=='5814587049d6af3f55d273eb8d2057af2cf2a22ae2ea3bc2051aac2453c148b1' and sha(oldr)=='7eba5cdfb8a96ddd885d57450a06e01a64db5f27c991401c7dcea24d695fa028'
b,n=json.loads(old.read_text()),json.loads(p.read_text())
for k in ('entries','scope_inventory','source_review_refs'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
br,nr=json.loads(oldr.read_text()),json.loads(r.read_text())
for k,rows in br.items():assert {canon(x) for x in rows}<={canon(x) for x in nr[k]}
receipt=json.loads((c/f'six-leaders-2022-iyi-{job}.json').read_text());folder=Path(receipt['preview']);assert folder.resolve().is_relative_to(Path(os.environ['GSD0404_PREVIEW_STAGING']).resolve());m=json.loads((folder/'manifest.json').read_text());assert m['renderer_version']==31
for name,h in m['files'].items():assert sha(folder/name)==h
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==20 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='iyi'])==12
db=sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True);q='0407-six-leaders-2022-'
for eid in events:assert db.execute('select 1 from practice_event where id=?',(eid,)).fetchone()
assert db.execute('select common_event_key,date_precision from practice_event where id=?',(q+'event',)).fetchone()==('six-leaders-2022-10-02-chp-second-round-meeting','day')
assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'candidate',)).fetchone()==('unmatched',None)
assert db.execute('select actor_id,authority_passage_id from practice_contribution where id=?',(q+'contribution',)).fetchone()==(q+'aksener-actor',q+'arrival');db.close()
html=(folder/'index.html').read_text()
for v in ('party','comparison'):
 a=html.index(f'id="{v}-unmatched-{q}candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}finding"' in html[a:z]
out=dict(job=job,checked_at=datetime.now(timezone.utc).isoformat(),package_sha256=sha(p),review_sha256=sha(r),preview=str(folder),manifest_sha256=sha(folder/'manifest.json'),renderer_version=31,event_count=20,relation_count=12,checks=['append-only records and reviews','manifest files','20 events in SQLite and JSON','Akşener capacity and candidate in both views'],status='passed');(c/f'six-leaders-2022-iyi-{job}-independent.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
