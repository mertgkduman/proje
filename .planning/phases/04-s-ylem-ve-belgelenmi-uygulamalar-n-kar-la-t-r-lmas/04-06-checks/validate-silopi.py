"""Canlı sıra korunumu, gerçek kapılar ve iki alternatif/sonuç açığı denetimi."""
import importlib.util,json,os,sqlite3
from pathlib import Path
here=Path(__file__).resolve().parent;root=here.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('dem_tracer_validation',here/'tracer-validation.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
package=here/'silopi-combined-draft.json';review=here/'silopi-combined-review-draft.json';before=json.loads((root/'data/practices/04-dem.json').read_text());candidate=json.loads(package.read_text());canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory'):assert {canonical(x) for x in before[k]} <= {canonical(x) for x in candidate[k]},k
for k,rows in before['practice_records'].items():assert {canonical(x) for x in rows} <= {canonical(x) for x in candidate['practice_records'].get(k,[])},k
mod.main(package,review,'dem-silopi','0406-silopi-2025-discipline','0406-silopi-dem-relation','')
receipt=json.loads((here/f'dem-silopi-{job}.json').read_text());folder=Path(receipt['preview']);snapshot=json.loads((folder/'records.json').read_text());report=(folder/'index.html').read_text();db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True)
for event in ['0406-2023-congress','0406-2159','0406-hakkari-2024-selection','0406-101831-commission','0406-2026-3961-vote','0406-silopi-2025-discipline']:
 assert any(x['id']==event for x in snapshot['practice_event']) and db.execute('SELECT 1 FROM practice_event WHERE id=?',(event,)).fetchone(),event
for relation in ['0406-silopi-dem-relation','0406-silopi-hedep-relation']:
 row=db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?',(relation,)).fetchone();assert row is not None and row[0] is None
 assert any(x['id']==relation and x['result_finding_id'] is None for x in snapshot['practice_relation'])
 for prefix in ('party','comparison'):assert f'id="{prefix}-practice-{relation}"' in report
for relation,finding in [('0406-hakkari-selection-relation','0406-hakkari-dispute-finding'),('0406-101831-relation','0406-101831-debate-f')]:
 for prefix in ('party','comparison'):
  start=report.index(f'id="{prefix}-practice-{relation}"');end=report.index('</article>',start);assert f'data-finding-id="{finding}"' in report[start:end]
db.close();receipt.update(verified_six_events=True,verified_alternative_relations=['0406-silopi-dem-relation','0406-silopi-hedep-relation'],independent_result_missing=True,live_entries_preserved=len(before['entries']));mod.receipt(here/f'dem-silopi-full-{job}.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print('SILOPI_ALTERNATIVES_RESULT_GAP_BOTH_VIEWS_OK',flush=True)
