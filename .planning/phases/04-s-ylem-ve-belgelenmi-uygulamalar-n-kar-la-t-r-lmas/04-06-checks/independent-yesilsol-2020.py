import hashlib,json,os,sqlite3
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
p=c/'yesilsol-2020-dem-draft.json';r=c/'yesilsol-2020-dem-review-draft.json';old=root/'data/practices/04-dem.json';oldr=root/'data/practices/04-dem-review.json'
assert sha(p)=='35f7eeb6bdca9a5c3ea79d21ff081259aad8e457ab24b94015b1b5735afb9192' and sha(r)=='00fdeac8e4d9db509b0b6c2cd2a0824a6545b4ca1ece79bf2f53879bfa7e4fa4'
assert sha(old)=='06f92639c132bb92389aa8109d2eb21af01aa4c0c6cb8141042933ee3cf53b43' and sha(oldr)=='1c8514fa09acb88021b25ca81460dfbe8aa5061f3ac093edf994062f7ad10231'
b,n=json.loads(old.read_text()),json.loads(p.read_text())
for k in ('entries','scope_inventory','source_review_refs'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
br,nr=json.loads(oldr.read_text()),json.loads(r.read_text())
for k,rows in br.items():assert {canon(x) for x in rows}<={canon(x) for x in nr[k]}
receipt=json.loads((c/f'dem-yesilsol-2020-{job}.json').read_text());folder=Path(receipt['preview']);assert folder.resolve().is_relative_to(Path(os.environ['GSD0404_PREVIEW_STAGING']).resolve());manifest=json.loads((folder/'manifest.json').read_text());assert manifest['renderer_version']==31
for name,h in manifest['files'].items():assert sha(folder/name)==h
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==88 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==13
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();q='0406-yesilsol-2020'
for event in events:assert db.execute('select 1 from practice_event where id=?',(event,)).fetchone()
row=db.execute('select actor_id,contribution_kind,responsibility_limit from practice_contribution where id=?',(q+'-contribution',)).fetchone();assert row[0]=='0406-dem-institution' and row[1]=='unknown' and 'HDP ayrı partidir' in row[2]
assert db.execute('select state,relation_id from practice_candidate where id=?',(q+'-candidate',)).fetchone()==('unmatched',None)
event=db.execute('select common_event_key,scope_context from practice_event where id=?',(q+'-event',)).fetchone();assert event[0]=='yerel-yonetimler-2020-05-18-ortak-bildiri' and 'ortak bildirinin' in event[1]
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-unmatched-{q}-candidate"');z=html.index('</article>',a);assert f'data-finding-id="{q}-finding"' in html[a:z]
db.close();out=dict(job=job,checked_at=datetime.now(timezone.utc).isoformat(),package_sha256=sha(p),review_sha256=sha(r),preview=str(folder),manifest_sha256=sha(folder/'manifest.json'),renderer_version=31,event_count=88,relation_count=13,checks=['old records and reviews retained','manifest files','88 events SQLite and JSON','historical Yeşil Sol signatory and unknown authority','candidate in both HTML views'],status='passed');(c/f'dem-yesilsol-2020-{job}-independent.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
