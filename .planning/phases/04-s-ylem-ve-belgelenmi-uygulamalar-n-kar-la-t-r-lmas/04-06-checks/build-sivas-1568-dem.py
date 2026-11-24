"""2024 10/1568 esasını ve 6131 grup gündemini ayrı olay olarak hazırla."""
import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:'0406-sivas-1568-'+x
base=root/'data/practices/04-dem.json';review_path=root/'data/practices/04-dem-review.json'
assert sha(base)=='1ad4fecb84494b3a47b478bd18834cb55e9712ff415fe1ba9a6746c0c1b7102b' and sha(review_path)=='93e8c132d2893c4df3377e0665f95889fa006bf68e44b8d7133bf20e3f750b8a'
pkg,review=json.loads(base.read_text()),json.loads(review_path.read_text());caps=json.loads((c/'sivas-1568-source-capture.json').read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat()
scope='practice-32598cee77548f2dce224908e63dc9005f9de70be0fff59b0b4990064ad650ae';s=next(x for x in pkg['practice_records']['practice_scope_v2'] if x['id']==scope)
s['boundary_reason']+=' Ayrıca 2 Temmuz 2024 10/1568 esas kaydı ve 6131 grup gündemi incelendi; aynı günkü açıklamanın saat sırası ve esas dosya sonucu açıktır.'
entries=[]; records={k:[] for k in ('practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**v):entries.append(dict(kind=category,values=v))
def passage(name,vid,exact,section):add('passage',id=q(name),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
for cap,suffix in zip(caps,('register','signed')):
 vid=q(suffix+'-v1');doc=q(suffix);path=root/'data/practices/sources/dem'/cap['original_path'];assert sha(path)==cap['sha256'];reg=suffix=='register'
 add('document',id=doc,party_id='dem',title='TBMM 10/1568 '+('esas kaydı' if reg else 'imzalı önerge'),source_kind='official')
 add('document_version',id=vid,document_id=doc,original_url=cap['source_url'],final_url=cap['source_url'],document_date=None if reg else '2024-07-02',date_precision='unknown' if reg else 'day',date_unknown_reason='Dinamik sicilin ilk yayın günü bilinmiyor.' if reg else None,version_label='TBMM özgün kaynak nüshası.',accessed_at=cap['accessed_at'],verified_at=when,mime='text/html' if reg else 'application/pdf',sha256=cap['sha256'],original_path=cap['original_path'],readable_path=cap['readable_path'])
 add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=cap['source_url'],basis='TBMM esas kaydı ve imzalı önerge dosyası.')
 if reg:
  view=dict(cap['view']);view['version_id']=vid;add('archive_view',**view);raw=html_source_text(path.read_bytes())
  for name,exact,section in [('number','10 / 1568','Esas numarası'),('date','02/07/2024','Başkanlığa geliş tarihi'),('sponsor','Halklar&#x131;n E&#x15F;itlik Ve Demokrasi Partisi','Önerge sahibi parti'),('status','G&#xFC;ndemde','Erişimde esas kaydının durumu')]:
   assert exact in raw;passage(name,vid,exact,section)
floorvid='0406-sivas-2024-tbmm-v1'; floor=root/'data/practices/sources/dem/objects/bb1eba84d477f1451d13a51b956f825e16cb7899381ea1c4ed3327f564045299/original.html.bin';raw=html_source_text(floor.read_bytes())
for name,exact,section in [('agenda','6131 grup numaralı','6131 numaralı aynı gün ön görüşme talebi'),('decision','Kabul edilmemiştir. Karar yeter sayısı vardır, öneri kabul edilmemiştir.','Başkanın takvim oylaması açıklaması'),('question','Karar yeter sayısı var mıdır?','Karar yeter sayısına ilişkin itiraz')]:
 assert exact in raw;passage(name,floorvid,exact,section)
event,finding,candidate,contribution=(q(x) for x in ('event','finding','candidate','contribution'));pids=[q(x) for x in ('number','date','sponsor','status','agenda','decision','question')];passages={x['values']['id']:x['values'] for x in entries if x['kind']=='passage'}
text='DEM Parti Grubunun 2 Temmuz 2024 tarihli Sivas araştırması 10/1568 esas ve 6131 grup numarasını taşıyordu. Genel Kurul aynı gün ön görüşme talebini kabul etmedi; başkan karar yeter sayısı olduğunu açıkladı, Sezai Temelli buna itiraz etti. Esas kaydı 24 Kasım 2026 erişiminde Gündemdeydi; araştırmanın açılışı ve sonucu bu takvim kararından ayrı kalır.'
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=text,provenance='summary',epistemic_type='claim')
records['practice_event'].append(dict(id=event,common_event_key='tbmm-28-2-97-10-1568-gundem',event_at='2024-07-02',date_precision='day',date_unknown_reason=None,title='10/1568 Sivas araştırmasının ön görüşme talebi',scope_context='DEM Parti Grubu 6131 grup numaralı 10/1568 Sivas araştırmasının 2 Temmuz 2024 birleşiminde ön görüşülmesini istedi; başkan talebin kabul edilmediğini açıkladı.',occurrence_basis='TBMM esas kaydı, 6131 numaralı imzalı önerge ve 97. birleşim tam tutanağı.'))
for pid in pids:
 stage='result' if pid in (q('status'),q('decision'),q('question')) else 'initiative';p=passages[pid]
 add('finding_evidence',finding_id=finding,passage_id=pid,role='support');add('verification',finding_id=finding,passage_id=pid,checked_at=when,result='confirmed',reason='TBMM sicili, imzalı dosya ve tutanak kesiti incelendi.')
 records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=p['section'],stage=stage,concrete_basis='TBMM sicili ve 97. birleşim tutanağı.',limitation='Gündem oylaması esas komisyonun kurulması veya sonucu değildir; yeter sayı itirazı korunur.',epistemic_type='claim'))
 records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Sicil, üç sayfalık imzalı önerge ve ayrı takvim oylaması okundu.')
records['practice_contribution'].append(dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM grup gündemi; bireysel oy ve esas araştırma sonucu çıkarılmaz.'))
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='2 Temmuz 2024 parti açıklamasıyla aynı gün saat sırası bilinmiyor; daha önceki bağımsız söylem ve esas araştırma sonucu açık.',passage_ids=enc(pids)))
sources=[(caps[0]['source_url'],q('register-v1'),['Esas numarası','Başkanlığa geliş tarihi','Önerge sahibi parti','Erişimde esas kaydının durumu']),(caps[1]['source_url'],q('signed-v1'),['Üç sayfalık imzalı önergenin görsel okuması'] ),('https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/97/Tam/ea0a7bcb-b641-4f4d-9f3d-7f8d14dae6a7.html',floorvid,['6131 numaralı aynı gün ön görüşme talebi','Başkanın takvim oylaması açıklaması','Karar yeter sayısına ilişkin itiraz'])]
for i,(url,vid,sections) in enumerate(sources):
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=enc(sections),inspected_at=when));records['practice_attempt_v2'].append(dict(id=q('reading-'+str(i)),scope_id=scope,attempted_at=when,query='2024 Sivas 6131 / 10/1568',url=url,result='examined',reason='Sicil, üç görsel sayfa ve 97. birleşim işlemi okundu.',source_version_id=vid))
pkg['entries']+=entries
for k,rows in records.items():pkg['practice_records'].setdefault(k,[]).extend(rows)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-sivas-2024-relations-62569027/releases/304b78a6f09d43f2a4dd3118da576fc0/records.json');data=json.loads(snap.read_text())
oldscope=next(x for x in data['practice_scope_v2'] if x['id']==scope);oldscope['boundary_reason']=s['boundary_reason']
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,rows in records.items():data.setdefault(k,[]).extend(rows)
validate_practices(data);print('SIVAS_1568_SEMANTIC_PASS',flush=True)
newp=[e['values']['id'] for e in entries if e['kind']=='passage'];targets=practice_review_package_targets(data,records,newp,'dem');passages={x['id']:x for x in data['passage']};prior={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in prior;refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({passages[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({passages[x]['section'] for x in refs})),supported_claim='10/1568 esas ve 6131 takvim işlemi: '+kind+' / '+ident,limitations='Ön görüşme oylaması esas komisyon sonucu değildir; karar yeter sayısı itirazı vardır.',result='reviewed',reason='Sicil, imzalı dosya ve birleşim tutanağının ilgili kesiti okundu.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem');review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('sivas-1568-dem-draft.json',pkg),('sivas-1568-dem-review-draft.json',review)]:
 p=c/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(p),flush=True)
