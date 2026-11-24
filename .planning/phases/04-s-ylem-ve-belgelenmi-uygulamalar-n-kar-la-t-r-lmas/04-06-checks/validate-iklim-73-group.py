import importlib.util,json,os,sqlite3
from pathlib import Path
c=Path(__file__).resolve().parent;root=c.parents[3];job=os.environ['SLURM_JOB_ID']; spec=importlib.util.spec_from_file_location('tracer',c/'tracer-validation.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=c/'iklim-73-group-dem-draft.json';r=c/'iklim-73-group-dem-review-draft.json';assert m.sha(p)=='6e98b8a1a312c439b9076602c704cf5b1661080fc98e3a76ff938981645d2c81' and m.sha(r)=='a8556fd440f59412b678e32b0864ba65eff66b96d50cfaefb61e672c2e4d6486'
b=json.loads((root/'data/practices/04-dem.json').read_text());n=json.loads(p.read_text());canon=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)
for k in ('entries','scope_inventory'):assert {canon(x) for x in b[k]}<={canon(x) for x in n[k]}
for k,rows in b['practice_records'].items():assert {canon(x) for x in rows}<={canon(x) for x in n['practice_records'][k]}
m.main(p,r,'dem-iklim-73-group','0406-iklim-73-group-event','0406-sivas-2024-2879-relation','')
receipt=json.loads((c/f'dem-iklim-73-group-{job}.json').read_text());folder=Path(receipt['preview']);assert json.loads((folder/'manifest.json').read_text())['renderer_version']==31
snap=json.loads((folder/'records.json').read_text());events={x['id'] for x in n['practice_records']['practice_event']};assert len(events)==82 and events<={x['id'] for x in snap['practice_event']};assert len([x for x in snap['practice_relation'] if x['party_id']=='dem'])==11
db=sqlite3.connect(f'file:{folder / "records.sqlite3"}?mode=ro',uri=True);html=(folder/'index.html').read_text()
for who in ('akin','koca'):
 row=db.execute('select event_id,contribution_kind,authority_passage_id from practice_contribution where id=?',(f'0406-iklim-73-group-{who}-contribution',)).fetchone();assert row==('0406-iklim-73-group-event','objection',f'0406-iklim-73-group-{who}-role')
 for prefix in ('party','comparison'):
  a=html.index(f'id="{prefix}-unmatched-0406-iklim-73-group-candidate"');z=html.index('</article>',a);assert f'data-finding-id="0406-iklim-73-group-{who}-finding"' in html[a:z]
db.close();print('EIGHTY_TWO_EVENTS_GROUP_SPEECHES_BOTH_VIEWS_OK',flush=True)
