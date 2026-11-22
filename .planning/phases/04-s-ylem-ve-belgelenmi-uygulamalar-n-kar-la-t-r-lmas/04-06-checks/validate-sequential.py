"""İki yeni ihtilaflı ilişki için izole üç CLI ve DB/JSON/iki görünüm denetimi."""
import importlib.util,json,os,sqlite3
from pathlib import Path

here=Path(__file__).resolve().parent;root=here.parents[3];job=os.environ['SLURM_JOB_ID']
spec=importlib.util.spec_from_file_location('dem_tracer_validation',here/'tracer-validation.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
package=here/'101831-combined-draft.json';review=here/'101831-combined-review-draft.json';live=root/'data/practices/04-dem.json'
before=json.loads(live.read_text());candidate=json.loads(package.read_text());canonical=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for kind in ('entries','scope_inventory'):
 assert {canonical(x) for x in before[kind]} <= {canonical(x) for x in candidate[kind]},kind
for kind,rows in before['practice_records'].items():
 assert {canonical(x) for x in rows} <= {canonical(x) for x in candidate['practice_records'].get(kind,[])},kind
mod.main(package,review,'dem-sequence','0406-hakkari-2024-selection','0406-hakkari-selection-relation','')
receipt=json.loads((here/f'dem-sequence-{job}.json').read_text());folder=Path(receipt['preview']);snapshot=json.loads((folder/'records.json').read_text());report=(folder/'index.html').read_text();db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True)
cases=[('0406-hakkari-2024-selection','0406-hakkari-selection-relation','0406-hakkari-selection-dispute','0406-hakkari-dispute-finding'),('0406-101831-commission','0406-101831-relation','0406-101831-debate','0406-101831-debate-f')]
for event,relation,dispute,finding in cases:
 for table,identity in [('practice_event',event),('practice_relation',relation),('practice_dispute',dispute)]:
  assert any(row['id']==identity for row in snapshot[table]),(table,identity,'json')
  assert db.execute(f'SELECT 1 FROM {table} WHERE id=?',(identity,)).fetchone(),(table,identity,'db')
 assert db.execute('SELECT summary_finding_id FROM practice_dispute WHERE id=?',(dispute,)).fetchone()[0]==finding
 for prefix in ('party','comparison'):
  start=report.index(f'id="{prefix}-practice-{relation}"');end=report.index('</article>',start);article=report[start:end]
  assert f'data-finding-id="{finding}"' in article,(prefix,relation,finding)
db.close();receipt['verified_cases']=[dict(event=e,relation=r,dispute=d,summary_finding=f) for e,r,d,f in cases];receipt['live_entries_preserved']=len(before['entries']);receipt['live_record_tables_preserved']=len(before['practice_records'])
mod.receipt(here/f'dem-sequence-full-{job}.json',json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print('SEQUENTIAL_DB_JSON_BOTH_DISPUTES_OK',flush=True)
