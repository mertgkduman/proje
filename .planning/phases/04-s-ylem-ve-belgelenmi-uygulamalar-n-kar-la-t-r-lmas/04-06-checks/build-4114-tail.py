"""4114 tutanağının 18–20. madde önergelerini canlı çifte ayrı ekler."""
import datetime, hashlib, json, re
from pathlib import Path
from arsiv import pdf_page_text
c=Path(__file__).resolve().parent;root=c.parents[3]
p=c/'4114-eighteen-twenty-draft.json';r=c/'4114-eighteen-twenty-review-draft.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(p)=='a42c3c272e0a3b8b125185ed781517c50ba117a1b203146e4cdd95cfed50555c'
assert sha(r)=='9715d19970725e1458e69b6f71e204c05106b297e2f84e995ac06cb754009ff3'
pkg,review=json.loads(p.read_text()),json.loads(r.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat()
h='977202aa2e935ac7038dbff7d26443ae314f0b9369d45a800594c46752b96826';f=root/'data/practices/sources/dem/objects'/h/'original.pdf';assert sha(f)==h
ver='0406-4114-iklim-v1';scope='practice-1c5854aa8d8f94f0081a0ceb37427ff8b3ba45ab525d3b46b3e50beb15869a09'
roles=['0406-4114-akin-dem','0406-4114-koca-grup']
sections={x['values']['id']:x['values']['section'] for x in pkg['entries'] if x['kind']=='passage'}
def add(kind,**v):pkg['practice_records'].setdefault(kind,[]).append(v)
def entry(entry_kind,**v):pkg['entries'].append(dict(kind=entry_kind,values=v))
def reading(kind,identity,refs,claim,reason):
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,
  source_version_ids=json.dumps([ver]),passage_ids=json.dumps(refs),inspected_sections=json.dumps([sections[x] for x in refs],ensure_ascii=False),
  supported_claim=claim,limitations='Tekil komisyon önergesi ve ret; Genel Kurul sonucu ve isimli oy ayrıdır.',result='reviewed',reason=reason))
for n,page in [('gecici1',54),('gecici2',55),('14-anayasa',51)]:
 text=pdf_page_text(f,page);starts=[m.start() for m in re.finditer('Çevre Komisyonu Başkanlığına',text)]
 if n=='14-anayasa': matches=[i for i in starts if 'Anayasa' in text[i:i+300] and 'durdurularak' in text[i:i+350]]
 else:
  digit=n[-1];matches=[i for i in starts if re.search(rf'geçici {digit}[\x27’]',text[i:i+230],re.I) and 'çıkarılmasını' in text[i:i+270]]
 assert len(matches)==1,(n,matches);start=matches[0];following=next((i for i in starts if i>start),len(text));chunk=text[start:following]
 split=n=='14-anayasa'
 if split: chunks=[(page,chunk,'initiative'),(page+1,pdf_page_text(f,page+1),'result')]
 else: chunks=[(page,chunk,'result')]
 assert all(x in ' '.join(y[1] for y in chunks) for x in ('Ayten Kordu','İbrahim Akın','Perihan Koca'))
 label={'gecici1':'geçici 1. madde','gecici2':'geçici 2. madde','14-anayasa':'14. madde anayasal uygunluk'}[n]
 base=f'0406-4114-madde{n}';event=base+'-event';finding=base+'-finding';candidate=base+'-candidate';contrib=base+'-contribution'
 new=[]
 for ix,(page_no,chunk,stage) in enumerate(chunks):
  if stage=='result':
   m=re.search(r'(?:kabul\s+)?edilmemiştir\.',chunk,re.I);assert m,(n,page_no)
   chunk=chunk[:m.end()]
  pid=base+('-passage' if len(chunks)==1 else ('-proposal' if ix==0 else '-result'));new.append((pid,stage))
  section=f'{label} '+('önergesi ve ret' if len(chunks)==1 else ('önergesi ve gerekçesi' if ix==0 else 'ayrı ret duyurusu'))
  sections[pid]=section;entry('passage',id=pid,version_id=ver,exact=chunk,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page_no,printed_page=str(page_no+1))
 title={'gecici1':'DEM’in 2/2927 geçici 1. madde çıkarma önergesi','gecici2':'DEM’in 2/2927 geçici 2. madde çıkarma önergesi','14-anayasa':'DEM’in 2/2927 14. madde anayasal uygunluk incelemesi önergesi'}[n]
 if n=='14-anayasa': context='Ayten Kordu, İbrahim Akın ve Perihan Koca, 14. madde için görüşmelerin durdurulup anayasal uygunluğun incelenmesini önerdi; Çevre Komisyonu önergeyi kabul etmedi.'
 else: context=f'Ayten Kordu, İbrahim Akın ve Perihan Koca, İklim Kanunu Teklifi’nin {label}nin çıkarılmasını önerdi; Çevre Komisyonu önergeyi kabul etmedi.'
 reasons={'gecici1':'Önerge sahipleri ETS kurulum süresinin gerçekçi olmadığını savundu.','gecici2':'Önerge sahipleri uyum eylem planlarının kapsamı ve kentsel altyapı eksikliğine dikkat çekti.','14-anayasa':'Önerge sahipleri faaliyetin durdurulması için verilen sürenin Anayasa 56 ile bağdaşmadığını savundu; bu bir yargı kararı değildir.'}
 entry('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=context+' '+reasons[n]+' Bu işlem Genel Kurul sonucu veya isimli oy değildir.',provenance='summary',epistemic_type='claim')
 for pid in [x[0] for x in new]+roles:
  entry('finding_evidence',finding_id=finding,passage_id=pid,role='support')
  entry('verification',finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason=f'{label} ve aynı toplantı grup bağlamı okundu.')
 entry('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason=f'{label} önergesi, ayrı ret ve grup bağlamı kontrol edildi.')
 add('practice_event',id=event,common_event_key=f'tbmm-komisyon-4114-2-2927-madde{n}-dem-onerge',event_at='2025-02-26',date_precision='day',date_unknown_reason=None,title=title,scope_context=context,occurrence_basis='TBMM Çevre Komisyonu tutanağı.')
 refs=[x[0] for x in new]+roles
 for pid,stage in new+[(x,'action') for x in roles]:
  add('practice_event_evidence',event_id=event,passage_id=pid,supported_point=sections[pid],stage=stage,concrete_basis='26 Şubat 2025 komisyon tutanağı.',limitation='Grup bağlamı ve tekil ret; isimli oy veya Genel Kurul kararı değildir.',epistemic_type='claim')
  add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
  reading('practice_event_evidence',event+'|'+pid+'|'+stage,[pid],f'{label} için {sections[pid]} belirlendi.',f'Bu olayın {stage} aşamasındaki özgün pasajı incelendi.')
 add('practice_contribution',id=contrib,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Üç milletvekilinin ayrı önergesi ve komisyon reddi; Genel Kurul kararı değil.')
 add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Bu madde için önceki bağımsız parti söylemiyle somut eşleştirme araştırması açık; sonraki 198 raporu öncül değildir.',passage_ids=json.dumps(refs))
 for typ,ident,detail in [('practice_event',event,'Olayın önerge ve ret sırası'),('practice_contribution',contrib,'Üç imzacı ve toplantı grup bağlamı'),('practice_contribution.finding_id',contrib,'Bulgunun ret ve sorumluluk sınırı'),('practice_candidate',candidate,'Önceki söylem araştırmasının açık durumu')]:
  reading(typ,ident,refs,context,detail+f' {label} için incelendi.')
add('practice_attempt_v2',id='0406-4114-gecici-anayasa-reading',scope_id=scope,attempted_at=now,query='26 Şubat 2025 2/2927 DEM geçici 1–2 çıkarma ve 14 anayasal inceleme önergeleri',url='https://tbmm.gov.tr/Tutanaklar/TutanakGoster/4114',result='examined',reason='Tutanak ilgili sayfaları ve ayrı retler görsel okundu; kalan önergeler ile konu kapsamı açık.',source_version_id=ver)
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
for name,obj in [('4114-tail-draft.json',pkg),('4114-tail-review-draft.json',review)]:
 path=c/name;path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(path))
