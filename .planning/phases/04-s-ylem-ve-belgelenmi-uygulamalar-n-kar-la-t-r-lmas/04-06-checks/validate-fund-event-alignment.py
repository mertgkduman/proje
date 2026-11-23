"""7 Ekim adayını gerçek kapılar ve iki görünümle doğrula."""
import importlib.util,json,os,sqlite3
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('dem_tracer_validation',here/'tracer-validation.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
package=here/'fund-event-alignment-draft.json';review=here/'fund-event-alignment-review.json'
assert mod.sha(package)=='f537c6246f655f10608c82797eb9c4ac5554cc675d0b1e4c177f629b3d343d77' and mod.sha(review)=='b1dba2674a0ce8c1c901b80b5a638d0ddc49df59531810e36ab9bc8d9f72601d'
before=json.loads((root/'data/practices/04-dem.json').read_text());candidate=json.loads(package.read_text());canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory'):assert {canonical(x) for x in before[k]} <= {canonical(x) for x in candidate[k]},k
for k,rows in before['practice_records'].items():
 old=[x for x in rows if not (k=='practice_event' and x['id']=='0406-2026-fund-1007')]
 assert {canonical(x) for x in old} <= {canonical(x) for x in candidate['practice_records'].get(k,[])},k
a=next(x for x in before['practice_records']['practice_event'] if x['id']=='0406-2026-fund-1007'); b=next(x for x in candidate['practice_records']['practice_event'] if x['id']==a['id']);assert {k:v for k,v in a.items() if k not in ('title','scope_context','occurrence_basis')}=={k:v for k,v in b.items() if k not in ('title','scope_context','occurrence_basis')}
oldrev=json.loads((root/'data/practices/04-dem-review.json').read_text());newrev=json.loads(review.read_text());nr={(x['subject_kind'],x['subject_id']):x for x in newrev['practice_source_review']}
for x in oldrev['practice_source_review']:
 y=nr[(x['subject_kind'],x['subject_id'])];assert {k:v for k,v in x.items() if k not in ('passage_ids','inspected_sections')}=={k:v for k,v in y.items() if k not in ('passage_ids','inspected_sections')};assert set(json.loads(x['passage_ids']))<=set(json.loads(y['passage_ids']))
mod.main(package,review,'dem-fund-align','0406-fund-july-4343-event','0406-2025-224-relation','')
receipt=json.loads((here/f'dem-fund-align-{job}.json').read_text());folder=Path(receipt['preview']);snapshot=json.loads((folder/'records.json').read_text());report=(folder/'index.html').read_text();db=sqlite3.connect(f'file:{folder/"records.sqlite3"}?mode=ro',uri=True)
assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
for event in [x['id'] for x in before['practice_records']['practice_event']]+['0406-fund-july-4343-event']:
 assert any(x['id']==event for x in snapshot['practice_event']) and db.execute('select 1 from practice_event where id=?',(event,)).fetchone(),event
for prefix in ('party','comparison'):
 for c,f in [('0406-fund-july-4343-unmatched','0406-fund-july-4343-f'),('0406-2026-fund-1007-unmatched','0406-2026-fund-1007-dispute-f'),('0406-2026-mdkd-dem-unmatched','0406-2026-mdkd-tally-f'),('0406-2026-23464-kaya-unmatched','0406-2026-23464-kaya-f')]:
  a=report.index('id="'+prefix+'-unmatched-'+c+'"');b=report.index('</article>',a);assert 'data-finding-id="'+f+'"' in report[a:b]
 for relation,f in [('0406-hakkari-selection-relation','0406-hakkari-dispute-finding'),('0406-101831-relation','0406-101831-debate-f')]:
  a=report.index('id="'+prefix+'-practice-'+relation+'"');b=report.index('</article>',a);assert 'data-finding-id="'+f+'"' in report[a:b]
 for relation in ('0406-silopi-dem-relation','0406-silopi-hedep-relation'):
  assert db.execute('select result_finding_id from practice_relation where id=?',(relation,)).fetchone()==(None,) and 'id="'+prefix+'-practice-'+relation+'"' in report
db.close();print('ALIGNED_FIFTEEN_EVENTS_AND_DISPUTES_BOTH_VIEWS_OK',flush=True)
