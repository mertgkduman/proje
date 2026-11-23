"""Aynı 4114 toplantısındaki grup bağlamını ayrı taslakta delile bağlar."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import pdf_page_text
c=Path(__file__).resolve().parent; root=c.parents[3]
p=c/'4114-first-five-draft.json'; r=c/'4114-first-five-v2-review-draft.json'
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='22e0a4d6b0e9753b3b8ad397d0ab5a7e8d975b02767c3a6debe20463454b102c'
assert sha(r)=='c0366ac8dcaa65862c54830356fe2c90f404b1d7d6b295d11f5467585503a9c5'
pkg,review=json.loads(p.read_text()),json.loads(r.read_text()); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
h='977202aa2e935ac7038dbff7d26443ae314f0b9369d45a800594c46752b96826'; f=root/'data/practices/sources/dem/objects'/h/'original.pdf'; assert sha(f)==h
ver='0406-4114-iklim-v1'
specs=[('akin-dem',10,'İBRAHİM AKIN (İzmir) - Değerli Başkan','durumu DEM PARTİ olarak normal olarak kabul etmiyoruz','Akın’ın DEM Parti adına aynı toplantıdaki usul açıklaması'),('koca-grup',34,'PERİHAN KOCA (Mersin) - Gerekçelerimiz','gerekçelerimizi biz kendimiz okumak istiyoruz, kendi grubumuz adına.','Koca’nın grup adına gerekçeleri okuma açıklaması')]
ids=[]
for name,page,start,end,section in specs:
 text=pdf_page_text(f,page); i=text.index(start); j=text.index(end,i)+len(end); exact=text[i:j]; pid='0406-4114-'+name; ids.append(pid)
 pkg['entries'].append(dict(kind='passage',values=dict(id=pid,version_id=ver,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=str(page+1))))
for n in range(1,6):
 base=f'0406-4114-madde{n}'; event=base+'-event'; finding=base+'-finding'; candidate=base+'-candidate'
 for pid in ids:
  pkg['entries'].append(dict(kind='finding_evidence',values=dict(finding_id=finding,passage_id=pid,role='support')))
  pkg['entries'].append(dict(kind='verification',values=dict(finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='Aynı toplantıda grup bağlamına ilişkin ifade okundu.')))
  pkg['practice_records']['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point='Aynı toplantıda DEM ve grup adına konuşma bağlamı',stage='action',concrete_basis='26 Şubat 2025 Çevre Komisyonu tutanağı.',limitation='Genel oturum bağlamı; kişisel oy veya bütün partinin oyu değildir.',epistemic_type='claim'))
  pkg['practice_records']['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage='action',basis_kind='document'))
  review['practice_source_review'].append(dict(subject_kind='practice_event_evidence',subject_id=event+'|'+pid+'|action',reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps([ver]),passage_ids=json.dumps([pid]),inspected_sections=json.dumps([next(x[4] for x in specs if pid.endswith(x[0]))],ensure_ascii=False),supported_claim=f'{n}. madde önergesinin aynı toplantısında grup bağlamı okunmuştur.',limitations='Grup adına açıklama bireysel oy sonucu değildir.',result='reviewed',reason=f'{n}. madde olayı için toplantının ilgili grup açıklaması denetlendi.'))
 cand=next(x for x in pkg['practice_records']['practice_candidate'] if x['id']==candidate); cand['passage_ids']=json.dumps(json.loads(cand['passage_ids'])+ids)
 row=next(x for x in review['practice_source_review'] if x['subject_kind']=='practice_candidate' and x['subject_id']==candidate); row['passage_ids']=cand['passage_ids']; row['inspected_sections']=json.dumps([f'{n}. madde önergesi ve ret',specs[0][4],specs[1][4]],ensure_ascii=False)
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('4114-first-five-v3-draft.json',pkg),('4114-first-five-v3-review-draft.json',review)]:
 path=c/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(path))
