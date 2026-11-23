"""Öğretmen adayı kesin geçerse onu temel alarak ayrı 2026 kongre adayını hazırlar."""
import datetime,hashlib,json
from pathlib import Path
c=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p,r=c/'teacher-4314-dem-draft.json',c/'teacher-4314-dem-review-draft.json'
assert sha(p)=='af249fce72f3d37a197b087d725a2a8094ef3bf6ef9c94c5c6c8c4b5574d652d'
assert sha(r)=='8888877de623335b07f47d6b6be109cdddb54ed7c88a0bf155a3b5496c534bce'
pkg,rev=json.loads(p.read_text()),json.loads(r.read_text())
entries=json.loads((c/'2026-congress-records.json').read_text())['entries']
passages={x['values']['id']:x['values'] for x in entries if x['kind']=='passage'}
versions={x['values']['id']:x['values'] for x in entries if x['kind']=='document_version'}
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
q=lambda x:'0406-2026-congress-'+x
event,finding,contribution,candidate=(q(x) for x in ('event','finding','contribution','candidate'))
scope='practice-a433ea5fa3150ee0f0b832989d2c0ca7c9ff2925ed20fec91567a684719d2d83'
points=[('dw-result','result'),('jin-result','action'),('jin-count','result')]
ids=[q(n) for n,_ in points]
def add(table,**values):pkg['practice_records'].setdefault(table,[]).append(values)
entries.append(dict(kind='finding',values=dict(id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='6 Eylül 2026’da DEM Parti’nin 5. Olağan Büyük Kongresi’nde Tülay Hatimoğulları ve Tuncer Bakırhan yeniden eş genel başkan seçildi. DW Türkçe, geçerli 535 oyun tamamının iki adaya verildiğini; JINNEWS ise tek listeli kapalı oylamada 538 oy kullanıldığını, 535 oyun geçerli ve üçünün geçersiz olduğunu bildirdi. Seçim tutanağı bu kaynaklarda sunulmadı.',provenance='summary',epistemic_type='claim')))
for suffix,stage in points:
 pid=q(suffix); passage=passages[pid]
 entries.extend([dict(kind='finding_evidence',values=dict(finding_id=finding,passage_id=pid,role='support')),dict(kind='verification',values=dict(finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='Parti biyografisi ve iki ayrı haber ilgili bölümleri okundu.'))])
 add('practice_event_evidence',event_id=event,passage_id=pid,supported_point=passage['section'],stage=stage,concrete_basis='Parti biyografisi ile DW Türkçe ve JINNEWS kongre haberleri.',limitation='Oy sayıları haber kaynaklarına atfedilir; seçim tutanağı elde edilmedi.',epistemic_type='claim')
 add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
entries.append(dict(kind='review',values=dict(id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Kongre günü, parti ve haberlerin bildirdiği seçim sonucu kontrol edildi.')))
add('practice_event',id=event,common_event_key='dem-2026-09-06-5-olagan-kongre-es-baskan-secimi',event_at='2026-09-06',date_precision='day',date_unknown_reason=None,title='5. Olağan Kongrede eş genel başkanların yeniden seçilmesi',scope_context='DEM Parti’nin Ankara’da düzenlediği 5. Olağan Büyük Kongrede eş genel başkanlar yeniden seçildi.',occurrence_basis='Parti biyografisi ve 6 Eylül 2026 tarihli kongre haberleri; seçim tutanağı alınmadı.')
add('practice_contribution',id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Partinin büyük kongrede yaptığı seçim; oy sayıları ilgili haberlerin aktarımıdır.')
add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Eş genel başkan seçimi ve 2023 tarihsel tüzük arasındaki ilişki, tüzük nüshasının dönemsel yürürlüğü ayrı doğrulanana dek açık tutuluyor.',passage_ids=json.dumps(ids,ensure_ascii=False))
targets=[('practice_event_evidence',event+'|'+q(n)+'|'+stage,[q(n)],passages[q(n)]['section']) for n,stage in points]
targets += [('practice_event',event,ids,'2026 kongresi ve seçim sonucu.'),('practice_contribution',contribution,ids,'Büyük kongre seçimi.'),('practice_contribution.finding_id',contribution,ids,'Seçim sonucu ve kaynak sınırı.'),('practice_candidate',candidate,ids,'Tüzük dönemsel geçerliliği açık.')]
for typ,ident,refs,description in targets:
 rev['practice_source_review'].append(dict(subject_kind=typ,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(passages[x]['version_id'] for x in refs)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(passages[x]['section'] for x in refs)),ensure_ascii=False),supported_claim=description,limitations='Kongre oy tutanağı ve tüzük nüshasının dönemsel yürürlüğü henüz incelenmedi.',result='reviewed',reason='Parti biyografisi ve bağımsız haberlerin ilgili bölümleri okundu.'))
for suffix in ('party-v1','dw-v1','jin-v1'):
 vid=q(suffix);refs=[x for x in ids if passages[x]['version_id']==vid]
 add('practice_scope_source',scope_id=scope,version_id=vid,inspected_sections=json.dumps([passages[x]['section'] for x in refs] or ['Parti biyografisinde 2026 seçimi'],ensure_ascii=False),inspected_at=now)
 add('practice_attempt_v2',id=q(suffix+'-reading'),scope_id=scope,attempted_at=now,query='DEM 6 Eylül 2026 5. olağan kongre eş genel başkan seçimi',url=versions[vid]['original_url'],result='examined',reason='Parti biyografisi veya bağımsız kongre haberi okundu; seçim tutanağı henüz elde edilmedi.',source_version_id=vid)
pkg['entries']+=entries
rev['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name,obj in [('2026-congress-dem-draft.json',pkg),('2026-congress-dem-review-draft.json',rev)]:
 path=c/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(path))
