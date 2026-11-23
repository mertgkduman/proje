"""7 Ekim adayını gerçek kapılar ve iki görünümle doğrula."""
import importlib.util,json,os,sqlite3
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('dem_tracer_validation',here/'tracer-validation.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
package=here/'oct08-two-events-draft.json';review=here/'oct08-two-events-review-draft.json'
assert mod.sha(package)=='09a12448a4d727b21f9734d71aed688e8d2d7698b6602291cc18df269a00e8bf' and mod.sha(review)=='190f924b8665c292dff6826fa738fa341f4b9f12237363540f3b8e84faeefa89'
before=json.loads((root/'data/practices/04-dem.json').read_text());candidate=json.loads(package.read_text());canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory'):assert {canonical(x) for x in before[k]} <= {canonical(x) for x in candidate[k]},k
for k,rows in before['practice_records'].items():assert {canonical(x) for x in rows} <= {canonical(x) for x in candidate['practice_records'].get(k,[])},k
mod.main(package,review,'dem-oct08-two-events','0406-dem-5472-cebir-event','0406-2025-224-relation','')
receipt=json.loads((here/f'dem-oct08-two-events-{job}.json').read_text());folder=Path(receipt['preview']);snapshot=json.loads((folder/'records.json').read_text());report=(folder/'index.html').read_text();db=sqlite3.connect(f'file:{folder/"records.sqlite3"}?mode=ro',uri=True)
assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
for event in [x['id'] for x in before['practice_records']['practice_event']]+['0406-fund-4830-event','0406-fund-4918-event']:
 assert any(x['id']==event for x in snapshot['practice_event']) and db.execute('select 1 from practice_event where id=?',(event,)).fetchone(),event
for prefix in ('party','comparison'):
 for c,f in [('0406-fund-4830-unmatched','0406-fund-4830-f'),('0406-fund-4918-unmatched','0406-fund-4918-f'),('0406-fund-july-4343-unmatched','0406-fund-july-4343-f'),('0406-2026-fund-1007-unmatched','0406-2026-fund-1007-dispute-f'),('0406-2026-mdkd-dem-unmatched','0406-2026-mdkd-tally-f'),('0406-2026-23464-kaya-unmatched','0406-2026-23464-kaya-f')]:
  a=report.index('id="'+prefix+'-unmatched-'+c+'"');b=report.index('</article>',a);assert 'data-finding-id="'+f+'"' in report[a:b]
 for relation,f in [('0406-hakkari-selection-relation','0406-hakkari-dispute-finding'),('0406-101831-relation','0406-101831-debate-f')]:
  a=report.index('id="'+prefix+'-practice-'+relation+'"');b=report.index('</article>',a);assert 'data-finding-id="'+f+'"' in report[a:b]
 for relation in ('0406-silopi-dem-relation','0406-silopi-hedep-relation'):
  assert db.execute('select result_finding_id from practice_relation where id=?',(relation,)).fetchone()==(None,) and 'id="'+prefix+'-practice-'+relation+'"' in report
for key in ('cebir','hisse'):
 event='0406-dem-5472-'+key+'-event'; cand='0406-dem-5472-'+key+'-candidate'; finding='0406-dem-5472-'+key+'-finding'
 assert any(x['id']==event for x in snapshot['practice_event']) and db.execute('select 1 from practice_event where id=?',(event,)).fetchone()
 for prefix in ('party','comparison'):
  a=report.index('id=\"'+prefix+'-unmatched-'+cand+'\"'); b=report.index('</article>',a); assert 'data-finding-id=\"'+finding+'\"' in report[a:b]
for key in ('yeniyol','dem'):
 event='0406-oct08-'+key+'-event'; cand='0406-oct08-'+key+'-candidate'; finding='0406-oct08-'+key+'-finding'
 assert any(x['id']==event for x in snapshot['practice_event']) and db.execute('select 1 from practice_event where id=?',(event,)).fetchone()
 for prefix in ('party','comparison'):
  a=report.index('id=\"'+prefix+'-unmatched-'+cand+'\"'); b=report.index('</article>',a); assert 'data-finding-id=\"'+finding+'\"' in report[a:b]
db.close();print('SEVENTEEN_EVENTS_AND_DISPUTES_BOTH_VIEWS_OK',flush=True)
