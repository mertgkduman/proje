"""Canlı sıra korunumu, gerçek kapılar ve iki alternatif/sonuç açığı denetimi."""
import importlib.util,json,os,sqlite3
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('dem_tracer_validation',here/'tracer-validation.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
code_root=os.environ.get('GSD04_RENDERER_CHECKOUT')
if code_root:
 mod.ROOT=Path(code_root);mod.DATA=mod.ROOT/'data';mod.INVENTORY=mod.DATA/'practices/04-inventory.json';mod.SOURCE=mod.DATA/'practices/sources/dem'
package=here/'two-2025-combined-draft.json';review=here/'two-2025-combined-review-draft.json';before=json.loads((root/'data/practices/04-dem.json').read_text());candidate=json.loads(package.read_text());canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
assert mod.sha(package)=='602ab586d51b7b94b66c3ca35723b3c46882807e92995c71c83c3ebe5f201a0e' and mod.sha(review)=='4de45c11170f1cc2e4b35774dcf92c246f0d1aff2d2843d00ba0ba67ddae27bb'
for k in ('entries','scope_inventory'):assert {canonical(x) for x in before[k]} <= {canonical(x) for x in candidate[k]},k
for k,rows in before['practice_records'].items():assert {canonical(x) for x in rows} <= {canonical(x) for x in candidate['practice_records'].get(k,[])},k
mod.main(package,review,'dem-two2025','0406-2025-103465-gundem','0406-2025-103465-relation','')
receipt=json.loads((here/f'dem-two2025-{job}.json').read_text());folder=Path(receipt['preview']);snapshot=json.loads((folder/'records.json').read_text());report=(folder/'index.html').read_text();db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True)
assert json.loads((folder/'manifest.json').read_text())['renderer_version']==(31 if code_root else 30)
for event in ['0406-2023-congress','0406-2159','0406-hakkari-2024-selection','0406-101831-commission','0406-2026-3961-vote','0406-silopi-2025-discipline','0406-2025-103465-gundem','0406-2025-103464-gundem']:
 assert any(x['id']==event for x in snapshot['practice_event']) and db.execute('SELECT 1 FROM practice_event WHERE id=?',(event,)).fetchone(),event
for relation in ['0406-silopi-dem-relation','0406-silopi-hedep-relation']:
 row=db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?',(relation,)).fetchone();assert row is not None and row[0] is None
 assert any(x['id']==relation and x['result_finding_id'] is None for x in snapshot['practice_relation'])
 for prefix in ('party','comparison'):assert f'id="{prefix}-practice-{relation}"' in report
for relation,finding in [('0406-hakkari-selection-relation','0406-hakkari-dispute-finding'),('0406-101831-relation','0406-101831-debate-f')]:
 for prefix in ('party','comparison'):
  start=report.index(f'id="{prefix}-practice-{relation}"');end=report.index('</article>',start);assert f'data-finding-id="{finding}"' in report[start:end]
assert db.execute("SELECT state FROM practice_candidate WHERE id='0406-2025-103464-unmatched'").fetchone()==('unmatched',)
for prefix in ('party','comparison'):
 start=report.index('id="'+prefix+'-unmatched-0406-2025-103464-unmatched"'); end=report.index('</article>',start); assert 'data-finding-id="0406-103464-contribution-f"' in report[start:end]
assert db.execute('SELECT 1 FROM practice_relation WHERE id=?',('0406-2025-103465-relation',)).fetchone(); assert all(f'id="{prefix}-practice-0406-2025-103465-relation"' in report for prefix in ('party','comparison')); db.close();receipt.update(verified_eight_events=True,verified_alternative_relations=['0406-silopi-dem-relation','0406-silopi-hedep-relation'],independent_result_missing=True,live_entries_preserved=len(before['entries']));mod.receipt(here/f'dem-two2025-full-{job}.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print('NEW_EVENT_AND_PRIOR_ALTERNATIVES_BOTH_VIEWS_OK',flush=True)
