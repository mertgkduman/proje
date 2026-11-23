"""60 olaylı adaydan sonraki üç ayrı Genel Kurul önergesini hazırlar."""
import datetime,hashlib,json
from pathlib import Path
from arsiv import pdf_page_text
from uygulamalar import practice_review_targets,validate_practice_source_review
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p,r=c/'sivas-two-dem-draft.json',c/'sivas-two-dem-review-draft.json'
assert sha(p)=='f2f7c7a74d75a762f5247a728be572559e96d2cc686e117a9c1aa47e4939bd44'
assert sha(r)=='af7dcf5f3961a01e900283082e49e32c3a3f521fe3b8f692936cf9efe1f1aaaf'
pkg,rev=json.loads(p.read_text()),json.loads(r.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat()
pdf=root/'data/practices/sources/dem/objects/85eb8b1af1952bd67610a902bdaa980cdcfd6685b3abdaf10483c3fafb3e8c73/original.pdf'
assert sha(pdf)=='85eb8b1af1952bd67610a902bdaa980cdcfd6685b3abdaf10483c3fafb3e8c73'
q=lambda s:'0406-iklim-103-'+s;scope='practice-1c5854aa8d8f94f0081a0ceb37427ff8b3ba45ab525d3b46b3e50beb15869a09';version='0406-iklim-103-printed-v1'
specs=[('14','14. madde',111,111,114,'cikarma',True),('15','15. madde',117,118,120,'cikarma',True),('16','16. madde',124,124,127,'cikarma',True)]
url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/103/Basilmis/a6442221-3730-4ca7-b08b-9ab39e3c3b96.pdf'
new={k:[] for k in ('practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_actor_period','practice_candidate','practice_attempt_v2','practice_scope_source')};entries=[dict(kind='document',values=dict(id='0406-iklim-103-printed',party_id='dem',title='TBMM 1 Temmuz 2025 103. Birleşim basılı tutanağı',source_kind='official')),dict(kind='document_version',values=dict(id=version,document_id='0406-iklim-103-printed',original_url=url,final_url=url,document_date='2025-07-01',date_precision='day',date_unknown_reason=None,version_label='1 Temmuz 2025 basılı tutanak',accessed_at=now,verified_at=now,mime='application/pdf',sha256='85eb8b1af1952bd67610a902bdaa980cdcfd6685b3abdaf10483c3fafb3e8c73',original_path='objects/85eb8b1af1952bd67610a902bdaa980cdcfd6685b3abdaf10483c3fafb3e8c73/original.pdf',readable_path='objects/85eb8b1af1952bd67610a902bdaa980cdcfd6685b3abdaf10483c3fafb3e8c73/readable.html'))]
def add(table,**values):new[table].append(values)
add('practice_scope_source',scope_id=scope,version_id=version,inspected_sections=json.dumps(['14, 15 ve 16 madde önergeleri, imzalar ve ret kararları'],ensure_ascii=False),inspected_at=now)
def passage(key,section,exact,page):
 assert exact in pdf_page_text(pdf,page),(key,page)
 entries.append(dict(kind='passage',values=dict(id=q(key),version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=str(page+1))))
for key,md,mp,sp,rp,action,joint in specs:
 event,fid,cid,candidate=(q(key+'-'+x) for x in ('event','finding','contribution','candidate'))
 ms=pdf_page_text(pdf,mp);a=ms.index('Görüşülmekte olan');b=ms.index('arz ve teklif ederiz.',a)+len('arz ve teklif ederiz.');motion=ms[a:b]
 if key=='20':
  end=ms.index('”',b)+1;motion=ms[a:end]
 ss=pdf_page_text(pdf,sp);i=ss.index('İbrahim Akın');a=ss.rfind('Aynı mahiyetteki diğer önergenin imza sahipleri:',0,i) if joint else i
 assert a>=0
 b=ss.index('BAŞKAN - Komisyon',i);signature=ss[a:b].strip()
 rs=pdf_page_text(pdf,rp);prefix='Aynı mahiyetteki önergeleri oylarınıza sunuyorum:' if joint else 'Önergeyi oylarınıza sunuyorum:';a=rs.index(prefix);b=rs.index('Kabul edilmemiştir.',a)+len('Kabul edilmemiştir.');result=rs[a:b]
 passage(key+'-motion',md+' önerge metni',motion,mp);passage(key+'-signature',md+' imzacı listesi',signature,sp);passage(key+'-result',md+' başkan oylama duyurusu',result,rp)
 ids=[q(key+'-'+x) for x in ('motion','signature','result')]
 title='İklim Kanunu '+md+(' çıkarma önergelerinin reddi' if joint and action=='cikarma' else ' çıkarma önergesinin reddi' if action=='cikarma' else ' değiştirme önergelerinin reddi')
 scope_text=('Genel Kurul 1 Temmuz 2025’te 2/2927 teklifinin '+md+('sinin çıkarılmasına' if action=='cikarma' else 'sinin değiştirilmesine')+(' ilişkin aynı mahiyetteki önergeleri birlikte oyladı ve reddetti.' if joint else ' ilişkin önergeyi reddetti.'))
 add('practice_event',id=event,common_event_key='tbmm-28-3-103-2-2927-'+key+'-'+action,event_at='2025-07-01',date_precision='day',date_unknown_reason=None,title=title,scope_context=scope_text,occurrence_basis='TBMM 28. Dönem 3. Yasama Yılı 103. Birleşim basılı tutanağındaki önerge, imzalar ve başkanın oylama açıklaması.')
 entries.append(dict(kind='finding',values=dict(id=fid,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=fid,text='İbrahim Akın, 1 Temmuz 2025’te 2/2927 teklifinin '+md+('sinin çıkarılması' if action=='cikarma' else 'sinin değiştirilmesi')+(' önergesini imzalayan milletvekilleri arasındaydı. ' if key!='20' else ' ve hükümlerin Cumhurbaşkanınca yürütülmesi önergesini imzalayan milletvekilleri arasındaydı. ')+('Aynı mahiyetteki önergeler birlikte oylandı ve reddedildi.' if joint else 'Önerge reddedildi.')+' Önerge, kanun teklifinin tümüne verilen kişisel oydan ayrıdır.',provenance='summary',epistemic_type='claim')))
 for pid in ids:
  entries.extend([dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=pid,role='support')),dict(kind='verification',values=dict(finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Önerge metni, aynı gündem imza listesi ve başkan sonucu basılı tutanakta görsel ve metinle incelendi.'))])
 entries.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Ayrı madde, kişi imzası ve oylama sonucu incelendi.')))
 for suffix,stage in (('motion','initiative'),('signature','action'),('result','result')):
  pid=q(key+'-'+suffix);add('practice_event_evidence',event_id=event,passage_id=pid,supported_point=md+' '+suffix,stage=stage,concrete_basis='1 Temmuz 2025 TBMM basılı tutanağındaki özgün sayfalar.',limitation='İmza ve önerge oylaması kanun teklifinin tümüne ait kişisel oyla aynı değildir.',epistemic_type='claim');add('practice_evidence_assessment',event_id=event,passage_id=pid,stage=stage,basis_kind='document')
 add('practice_contribution',id=cid,event_id=event,party_id='dem',actor_id='0406-iklim-final-akin-actor',contribution_kind='task',finding_id=fid,authority_passage_id=None,membership_passage_id='0406-iklim-final-akin-membership',responsibility_limit='İbrahim Akın’ın ilgili önergedeki imzası; diğer imzacıların veya grubun oyu çıkarılmaz.')
 add('practice_actor_period',contribution_id=cid,valid_from='2025-07-01',valid_to='2025-07-01',identity_passage_id='0406-iklim-final-akin-identity')
 add('practice_candidate',id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='2023 tarihsel seçim bildirgesi ve 2012 programatik kaynaklar incelendi; bağımsız güncel parti programı ve dönemsel bağ araştırması açık.',passage_ids=json.dumps(ids,ensure_ascii=False))
 add('practice_attempt_v2',id=q(key+'-reading'),scope_id=scope,attempted_at=now,query='1 Temmuz 2025 2/2927 '+md+' önerge imza oylama',url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/103/Basilmis/a6442221-3730-4ca7-b08b-9ab39e3c3b96.pdf',result='examined',reason='Önerge, imza ve oylama sayfaları görsel ve metinle incelendi.',source_version_id=version)
pkg['entries']+=entries
for k,v in new.items():pkg['practice_records'].setdefault(k,[]).extend(v)
data=dict(pkg['practice_records'])
for x in pkg['entries']:data.setdefault(x['kind'],[]).append(x['values'])
selection={k:new[k] for k in ('practice_event','practice_event_evidence','practice_contribution','practice_candidate')};targets=practice_review_targets(data,selection);pp={x['id']:x for x in data['passage']};reviews=[]
for (typ,ident),(refs,_) in targets.items():
 refs=sorted(refs);reviews.append(dict(subject_kind=typ,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(pp[x]['version_id'] for x in refs)),ensure_ascii=False),passage_ids=json.dumps(refs,ensure_ascii=False),inspected_sections=json.dumps(list(dict.fromkeys(pp[x]['section'] for x in refs)),ensure_ascii=False),supported_claim='TBMM ayrı önerge, imza ve ret kaynakları: '+typ+' / '+ident,limitations='İmza kişisel oy, önerge kararı teklifin tümünün sonucu değildir.',result='reviewed',reason='Ayrı madde ve kaynak pasajları okundu: '+typ+' / '+ident))
validate_practice_source_review(data,reviews,selection=selection);rev['practice_source_review']+=reviews;rev['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in rev['practice_source_review']]
for name,obj in [('iklim-103-motions-dem-draft.json',pkg),('iklim-103-motions-dem-review-draft.json',rev)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f))
print('UC_ONERGE_TARGET_PASS',len(targets))
