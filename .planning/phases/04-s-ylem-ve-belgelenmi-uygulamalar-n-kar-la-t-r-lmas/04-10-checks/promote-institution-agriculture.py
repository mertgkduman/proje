import hashlib,json,shutil,sqlite3
from pathlib import Path
D=Path(__file__).parent;P=Path('data/practices/04-emep.json');R=Path('data/practices/04-emep-review.json')
pp=D/'institution-agriculture-union-draft.json';rr=D/'institution-agriculture-union-review-draft.json';release=Path('data/.staging/gsd-0410-instagri-62434031/preview/releases/5e70a2a5eb184bfe9b970d8d4676e96d')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(pp)=='4b83401a21314de59c17bf7210637026b019e8a765b20ef3ac96f8e3b86ebeae' and sha(rr)=='7ee6cef94304eb912c892295830a31559fa905d1aa709537dfad88955f2468e3'
a=json.loads(P.read_text());b=json.loads(pp.read_text());x=json.loads(R.read_text());y=json.loads(rr.read_text())
assert all(v in b['entries'] for v in a['entries'])
assert all(all(v in b['practice_records'][k] for v in rows) for k,rows in a['practice_records'].items())
old={(r['subject_kind'],r['subject_id']):r for r in x['practice_source_review']};new={(r['subject_kind'],r['subject_id']):r for r in y['practice_source_review']}
changed={('practice_event','0410-izmit-2020-congress-event'),('practice_relation','0410-izmit-2020-congress-relation')};proof=[]
for key,r in old.items():
 n=new[key]
 if key not in changed:assert n==r;continue
 for field in ('subject_kind','subject_id','reviewer_kind','reviewed_at','result'):assert n[field]==r[field]
 for field in ('passage_ids','source_version_ids','inspected_sections'):assert set(json.loads(r[field]))<=set(json.loads(n[field]))
 for field in ('supported_claim','limitations','reason'):assert n[field].startswith(r[field])
 proof.append(dict(subject=key,old_passage_ids=json.loads(r['passage_ids']),new_passage_ids=json.loads(n['passage_ids'])))
assert len(proof)==2 and not b['practice_records']['practice_closure']
assert len(b['practice_records']['practice_event'])==26 and len(b['practice_records']['practice_relation'])==27
log=(D/'institution-agriculture-union-62434031.log').read_text()
assert all(s in log for s in ['PRACTICE_INPUT_OK','PRACTICE_SOURCE_REVIEW_OK','PRACTICE_PREVIEW_OK','EMEP_PREVIEW_DB_JSON_BOTH_VIEWS_AND_INDEPENDENT_AUDIT_OK'])
canonical=sha(Path('data/current.json'));assert canonical=='5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7'
export=json.loads((release/'records.json').read_text());html=(release/'index.html').read_text()
with sqlite3.connect((release/'records.sqlite3').resolve().as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for table in ['practice_event','practice_relation']:
  for row in b['practice_records'][table]:assert row in export[table] and dict(db.execute('select * from '+table+' where id=?',(row['id'],)).fetchone())==row
for row in b['practice_records']['practice_relation']:
 for prefix in ['party','comparison']:
  anchor=prefix+'-practice-'+row['id'];assert html.count('id="'+anchor+'"')==1 and html.count('href="#'+anchor+'"')>=1
receipt=dict(job='62434031',status='COMPLETED 0:0; input/source/preview and independent audit pass',renderer=29,package_sha256=sha(pp),review_sha256=sha(rr),release=str(release),files_sha256={n:sha(release/n) for n in ['manifest.json','records.json','records.sqlite3','index.html']},canonical_current_sha256=canonical,event_count=26,relations=27,old_package_preserved=True,unchanged_reviews_exact=True,reread_reviews_prior_content_and_passages_preserved=proof,both_view_href_pass=True,scope_closures=0)
with (D/'institution-agriculture-union-62434031-receipt.json').open('x') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
shutil.copyfile(pp,P);shutil.copyfile(rr,R)
print('MONOTONIC_SQL_JSON_HTML_AND_REVIEW_SUBSET_PASS')
