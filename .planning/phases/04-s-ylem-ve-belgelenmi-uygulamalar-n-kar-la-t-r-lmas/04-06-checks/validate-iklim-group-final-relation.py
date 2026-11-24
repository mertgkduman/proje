import importlib.util,json,os,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID'];spec=importlib.util.spec_from_file_location('tracer',c/'tracer-validation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=c/'iklim-group-final-relation-dem-draft.json';r=c/'iklim-group-final-relation-dem-review-draft.json';assert m.sha(p)=='666ba732e46b5a6bc9524fee2f4cb3c82774a0258fb44830094982f8a5c8549f' and m.sha(r)=='f749c62f4be4c1dc6f22638181c390735f981b5061cadc60f07489ac31361165'
b=json.loads((root/'data/practices/04-dem.json').read_text());n=json.loads(p.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
m.main(p,r,'dem-iklim-group-final','0406-iklim-final-event','0406-iklim-group-final-relation','')
receipt=json.loads((c/f'dem-iklim-group-final-{job}.json').read_text());folder=Path(receipt['preview']);assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==82 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==12
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text();assert db.execute('select state,relation_id from practice_candidate_revision where id=?',('0406-iklim-group-final-eligible',)).fetchone()==('eligible','0406-iklim-group-final-relation');assert db.execute('select state,relation_id from practice_candidate where id=?',('0406-iklim-final-candidate',)).fetchone()==('unmatched',None)
assert db.execute('select result_finding_id from practice_relation where id=?',('0406-iklim-group-final-relation',)).fetchone()==(None,)
for prefix in ('party','comparison'):
 a=html.index(f'id="{prefix}-practice-0406-iklim-group-final-relation"');z=html.index('</article>',a)
 for fid in ('0406-iklim-group-final-explanation','0406-iklim-final-akin-finding','0406-iklim-final-koca-finding','0406-iklim-final-kordu-finding'):assert f'data-finding-id="{fid}"' in html[a:z]
db.close();print('EIGHTY_TWO_EVENTS_TWELVE_RELATIONS_BOTH_VIEWS_OK',flush=True)
