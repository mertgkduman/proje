"""Canlı sıra korunumu, gerçek kapılar ve iki alternatif/sonuç açığı denetimi."""
import importlib.util,json,os,sqlite3
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('dem_tracer_validation',here/'tracer-validation.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
code_root=os.environ.get('GSD04_RENDERER_CHECKOUT')
if code_root:
 mod.ROOT=Path(code_root);mod.DATA=mod.ROOT/'data';mod.INVENTORY=mod.DATA/'practices/04-inventory.json';mod.SOURCE=mod.DATA/'practices/sources/dem'
package=here/'10437-combined-draft.json';review=here/'10437-combined-review-draft.json';before=json.loads((root/'data/practices/04-dem.json').read_text());candidate=json.loads(package.read_text());canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
assert mod.sha(package)=='f36124bd5bb4981cf0f6052da6c1bd4095414320d7b3cbca38ff731310ba577c' and mod.sha(review)=='ab00cb4fe7626e82bfcf771c90ea81065579e609dded0325c2b11a2b45830437'
for k in ('entries','scope_inventory'):assert {canonical(x) for x in before[k]} <= {canonical(x) for x in candidate[k]},k
for k,rows in before['practice_records'].items():assert {canonical(x) for x in rows} <= {canonical(x) for x in candidate['practice_records'].get(k,[])},k
mod.main(package,review,'dem-10437','0406-2024-10437-gundem','0406-2025-224-relation','')
receipt=json.loads((here/f'dem-10437-{job}.json').read_text());folder=Path(receipt['preview']);snapshot=json.loads((folder/'records.json').read_text());report=(folder/'index.html').read_text();db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True)
assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
for event in ['0406-2023-congress','0406-2159','0406-hakkari-2024-selection','0406-101831-commission','0406-2026-3961-vote','0406-silopi-2025-discipline','0406-2025-103465-gundem','0406-2025-103464-gundem','0406-2025-224-report']:
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
for prefix in ('party','comparison'):
 start=report.index('id="'+prefix+'-practice-0406-2025-224-relation"'); end=report.index('</article>',start)
 for finding in ('0406-224-result-f','0406-224-contribution-f','0406-224-link-f'): assert 'data-finding-id="'+finding+'"' in report[start:end]
assert db.execute("SELECT event_at FROM practice_event WHERE id='0406-2025-224-report'").fetchone()==('2025-07-03',)
assert db.execute('SELECT 1 FROM practice_relation WHERE id=?',('0406-2025-103465-relation',)).fetchone(); assert all(f'id="{prefix}-practice-0406-2025-103465-relation"' in report for prefix in ('party','comparison'))
assert db.execute("SELECT event_at FROM practice_event WHERE id='0406-2024-10437-gundem'").fetchone()==('2024-01-17',)
assert db.execute("SELECT state FROM practice_candidate WHERE id='0406-2024-10437-unmatched'").fetchone()==('unmatched',)
db.close()

assert any(x['id']=='0406-2024-10437-gundem' for x in snapshot['practice_event'])
assert any(x['id']=='0406-2024-10437-unmatched' and x['state']=='unmatched' for x in snapshot['practice_candidate'])
for prefix in ('party','comparison'):
 start=report.index('id="'+prefix+'-unmatched-0406-2024-10437-unmatched"');end=report.index('</article>',start);assert 'data-finding-id="0406-2024-10437-f"' in report[start:end]
print('TEN_EVENT_UNMATCHED_BOTH_VIEWS_OK',flush=True)
receipt.update(verified_ten_events=True,verified_alternative_relations=['0406-silopi-dem-relation','0406-silopi-hedep-relation'],independent_result_missing=True,live_entries_preserved=len(before['entries']))
mod.receipt(here/f'dem-10437-full-{job}.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
