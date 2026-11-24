"""Append four floor-amendment candidates based on same-day identified signer."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import practice_review_package_targets, validate_practice_source_review, validate_practices

c=Path(__file__).resolve().parent; root=c.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
enc=lambda x:json.dumps(x,ensure_ascii=False)
q=lambda x:'0406-iklim-74-motions-'+x
p=root/'data/practices/04-dem.json'; r=root/'data/practices/04-dem-review.json'
assert sha(p)=='a69ef44ead1395255f616827b1423d8326e7f46f1898dfa9993f27f041bb8827'
assert sha(r)=='a12e3613feb8199388f0f8672f1d67bcd7ddc1c5c8604abc35dac1702484ccaf'
pkg,review=json.loads(p.read_text()),json.loads(r.read_text())
when=datetime.datetime.now(datetime.timezone.utc).isoformat()
vid='0406-iklim-74-floor-v1'; scope='practice-1c5854aa8d8f94f0081a0ceb37427ff8b3ba45ab525d3b46b3e50beb15869a09'
src=root/'data/practices/sources/dem/objects/489decab3ae68c7d1e77936d0e13f593e5bcb692a038cd2a2f4740b946fa042b/original.html.bin'
assert sha(src)=='489decab3ae68c7d1e77936d0e13f593e5bcb692a038cd2a2f4740b946fa042b'
raw=html_source_text(src.read_bytes()); entries=[]
records={k:[] for k in ('practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_actor_period','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**values): entries.append(dict(kind=category,values=values))
def passage(name,exact,section):
 assert exact in raw,(name,exact[:100])
 add('passage',id=q(name),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
role="Halkların Eşitlik ve Demokrasi Partisi Grubu adına İstanbul Milletvekili Celal Fırat'a ait."
passage('membership',role,'Aynı gün Celal Fırat’a DEM grubu adına söz verilmesi')
passage('identity','Celal Fırat','Aynı gün Celal Fırat imzacı kimliği')
add('person',id=q('person'),name='Celal Fırat')
add('actor',id=q('actor'),kind='individual_mp',party_id='dem',person_id=q('person'),authorization_passage_id=None)
ords=['1\'inci','2\'nci','3\'üncü','4\'üncü']
starts=[raw.index(s+' madde üzerinde 4 önerge',raw.index('X.- KANUN TEKLİFLERİ')) for s in ords]
for n,(ordinal,start) in enumerate(zip(ords,starts),1):
 end=starts[n] if n<4 else raw.index('BEŞİNCİ OTURUM',start)
 chunk=raw[start:end]
 a=chunk.index('Görüşülmekte olan 198 sıra sayılı'); b=chunk.index('arz ve teklif ederiz.',a)+len('arz ve teklif ederiz.')
 motion=chunk[a:b]; assert str(n)+"'" in motion and 'çıkarılmasını' in motion
 a=chunk.index('Aynı mahiyetteki diğer önergenin imza sahipleri:'); b=chunk.index('BAŞKAN - Komisyon',a)
 sig=chunk[a:b]; assert 'Celal Fırat' in sig and 'İstanbul' in sig
 if n==1:
  a=chunk.index('Divanda uyum yok.'); b=chunk.index('aynı mahiyetteki önergeler reddedilmiştir.',a)+len('aynı mahiyetteki önergeler reddedilmiştir.')
  result=chunk[a:b]
 else:
  a=chunk.index('Aynı mahiyetteki önergeleri oylarınıza sunuyorum:',b); b=chunk.index('kabul edilmemiştir.',a)+len('kabul edilmemiştir.'); result=chunk[a:b]
 for name,exact,section in [('motion',motion,f'{n}. madde çıkarma metni'),('signature',sig,f'{n}. madde diğer önergenin imzacıları'),('result',result,f'{n}. madde ortak önerge oylaması')]: passage(str(n)+'-'+name,exact,section)
 ev=q(str(n)+'-event'); finding=q(str(n)+'-finding'); contribution=q(str(n)+'-contribution'); ids=[q(str(n)+'-'+x) for x in ('motion','signature','result')]
 records['practice_event'].append(dict(id=ev,common_event_key=f'tbmm-28-3-74-2-2927-{n}-cikarma',event_at='2025-04-09',date_precision='day',date_unknown_reason=None,title=f'İklim Kanunu {n}. madde çıkarma önergelerinin reddi',scope_context=f'Genel Kurul 9 Nisan 2025’te 2/2927 teklifinin {n}. maddesinin çıkarılmasına ilişkin aynı mahiyetteki iki önergeyi birlikte oyladı ve reddetti.',occurrence_basis='TBMM 74. birleşim tam tutanağında önerge, imzalar ve başkanın oylama açıklaması.'))
 add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=f'Celal Fırat, 9 Nisan 2025’te 2/2927 teklifinin {n}. maddesinin çıkarılması önergesini imzalayan milletvekilleri arasındaydı. Aynı mahiyetteki önergeler birlikte oylandı ve reddedildi. Bu işlem, maddenin kendisine veya kanunun tümüne verilen kişisel oydan ayrıdır.',provenance='summary',epistemic_type='claim')
 for suffix,stage in [('motion','initiative'),('signature','action'),('result','result')]:
  pid=q(str(n)+'-'+suffix); add('finding_evidence',finding_id=finding,passage_id=pid,role='support'); add('verification',finding_id=finding,passage_id=pid,checked_at=when,result='confirmed',reason='İlgili önerge, imzalar ve ortak oylama tutanakta ayrı okundu.')
  records['practice_event_evidence'].append(dict(event_id=ev,passage_id=pid,supported_point=f'{n}. madde {suffix}',stage=stage,concrete_basis='9 Nisan 2025 TBMM tam tutanağı.',limitation='İmza, maddenin ve kanunun tümünün kişisel oyu değildir.',epistemic_type='claim'))
  records['practice_evidence_assessment'].append(dict(event_id=ev,passage_id=pid,stage=stage,basis_kind='document'))
 add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Ayrı madde, imza ve önerge sonucu okundu.')
 records['practice_contribution'].append(dict(id=contribution,event_id=ev,party_id='dem',actor_id=q('actor'),contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=q('membership'),responsibility_limit='Celal Fırat’ın ilgili önergedeki imzası; diğer imzacıların veya grubun oyu çıkarılmaz.'))
 records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2025-04-09',valid_to='2025-04-09',identity_passage_id=q('identity')))
 records['practice_candidate'].append(dict(id=q(str(n)+'-candidate'),scope_id=scope,event_id=ev,relation_id=None,state='unmatched',reason='Önceki bağımsız parti söylemi ve dönemsel bağ araştırması açıktır.',passage_ids=enc(ids)))
 records['practice_attempt_v2'].append(dict(id=q(str(n)+'-reading'),scope_id=scope,attempted_at=when,query=f'9 Nisan 2025 2/2927 {n}. madde önergesi',url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/74/Tam/0fb55943-1a03-46cc-8bb2-3c59a2fb8af2.html',result='examined',reason='Önerge, imza ve ortak oylama ayrı incelendi.',source_version_id=vid))
pkg['entries']+=entries
for k,v in records.items(): pkg['practice_records'].setdefault(k,[]).extend(v)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-iklim-74-kordu-62576233/releases/cba09ec0dc8b43968d415cd52d43cf66/records.json')
data=json.loads(snap.read_text())
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items():data.setdefault(k,[]).extend(v)
validate_practices(data); print('FOUR_MOTIONS_SEMANTIC_PASS',flush=True)
newp=[e['values']['id'] for e in entries if e['kind']=='passage']; targets=practice_review_package_targets(data,records,newp,'dem'); allp={x['id']:x for x in data['passage']}; old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old; refs=sorted(refs); review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({allp[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({allp[x]['section'] for x in refs})),supported_claim='74. birleşim ayrı madde önergesi: '+kind+' / '+ident,limitations='İmza, madde oyu ve teklifin nihai sonucu ayrı işlemlerdir.',result='reviewed',reason='Teklif, imzacı, aynı gün grup sıfatı ve ilgili önerge sonucu okundu.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem')
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('iklim-74-motions-dem-draft.json',pkg),('iklim-74-motions-dem-review-draft.json',review)]:
 f=c/name; f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n'); print(name,sha(f),flush=True)
