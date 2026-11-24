import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text,pdf_page_text
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:'0406-tasimali-101783-'+x
base=root/'data/practices/04-dem.json';rp=root/'data/practices/04-dem-review.json';assert sha(base)=='edddf6d5326d82cab43d792d1d1c6845a43cde41495cc991f18d72110d1cf10a' and sha(rp)=='f460677b33bc2e56768e2c6cc930434397c98966874cc91df77a940321f05daa'
pkg,review=json.loads(base.read_text()),json.loads(rp.read_text());cap=json.loads((c/'tasimali-101783-capture.json').read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat();scope='practice-96f416de349c52eeef4f3821d1a6fea71b59dd6affde1ab82864670f6bcafb86'
entries=[];records={k:[] for k in ('practice_scope_v2','practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**v):entries.append(dict(kind=category,values=v))
records['practice_scope_v2'].append(dict(id=scope,party_id='dem',topic_id='egitime-erisim',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='10/1783 taşımalı eğitim araştırma önergesinin dar aday zinciri incelendi. Kapsam araştırması sürüyor.'))
anchors={
 'party-role':('Grup Başkanvekillerimiz Gülistan Kılıç Koçyiğit ve Sezai Temelli, taşımalı eğitimde yaşanan sorunlara çözüm üretilmesi için araştırma önergesi verdi.','DEM yayını ve grup sıfatı'),
 'party-scope':('Köy okullarının kapanmasının ve taşımalı eğitime geçilmesinin çok boyutlu tüm olumsuz sonuçlarının, taşımalı eğitimin sınırlandırılmasının gerekçelerinin ve mevcut taşımalı eğitim sistemin eksikliklerinin her yönüyle araştırılması','Araştırma konusu'),
 'party-date':('19 Eylül 2024','DEM yayınının tarihi'),
 'register-id':('10 / 1783','TBMM esas numarası'),
 'register-date':('20/09/2024','Başkanlığa geliş tarihi'),
 'register-status':('G&#xFC;ndemde','TBMM sicilinde erişim anı durumu'),
 'signed-id':('10/1783','İmzalı taramanın esas numarası')}
for key,kind in [('party','party'),('register','official'),('signed','official')]:
 x=cap[key];path=root/'data/practices/sources/dem'/x['original_path'];assert sha(path)==x['sha256'];raw=pdf_page_text(path,0) if key=='signed' else html_source_text(path.read_bytes());doc='0406-101783-'+key;vid=doc+'-v1'
 add('document',id=doc,party_id='dem',title={'party':'Taşımalı eğitimde yaşanan sorunlar','register':'TBMM 10/1783 esas kaydı','signed':'TBMM 10/1783 imzalı önerge'}[key],source_kind=kind)
 add('document_version',id=vid,document_id=doc,original_url=x['url'],final_url=x['url'],document_date=x['date'],date_precision='day' if x['date'] else 'unknown',date_unknown_reason=None if x['date'] else 'Sicil sayfasında yayın günü verilmemiştir.',version_label='Özgün parti yayını' if key=='party' else 'Özgün TBMM sicili' if key=='register' else 'İmzalı önerge taraması',accessed_at=x['accessed_at'],verified_at=when,mime=x['mime'],sha256=x['sha256'],original_path=x['original_path'],readable_path=x['readable_path'])
 if key!='signed':add('archive_view',**x['view'])
 add('source_attribution',version_id=vid,publisher='HALKLARIN EŞİTLİK VE DEMOKRASİ PARTİSİ' if key=='party' else 'TBMM',author=None,kind='party_publication' if key=='party' else 'official',published_at='2024-09-19' if key=='party' else None,date_precision='day' if key=='party' else 'unknown',social_handle=None,public_url=x['url'],basis='DEM yayınının 19 Eylül tarihli gövdesi' if key=='party' else 'TBMM sicili' if key=='register' else 'TBMM bağlantılı imzalı önerge taraması')
 keys=[k for k in anchors if k.startswith(key+'-')]
 for name in keys:
  exact,section=anchors[name];assert exact in raw,name;add('passage',id=q(name),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=0 if key=='signed' else None,printed_page=None)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=enc([anchors[n][1] for n in keys]),inspected_at=when));records['practice_attempt_v2'].append(dict(id=q(key+'-reading'),scope_id=scope,attempted_at=when,query='19 Eylül taşımalı eğitim 10/1783 önergesi ve 20 Eylül TBMM geliş kaydı',url=x['url'],result='examined',reason='Parti yayını, imzalı önergenin üç sayfa görüntüsü ve esas sicilindeki ayrı tarih ile durum okundu.',source_version_id=vid))
event=q('event');finding=q('finding');contribution=q('contribution');pids=[q(k) for k in ('party-role','party-scope','party-date','register-id','register-date','register-status','signed-id')]
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='DEM Parti grup başkanvekilleri Gülistan Kılıç Koçyiğit ile Sezai Temelli, köy okullarının kapanması ve taşımalı eğitime geçişin sonuçlarının araştırılmasını istedi. Parti yayını 19 Eylül 2024 tarihlidir. TBMM sicili 10/1783 önergesinin Başkanlığa gelişini 20 Eylül olarak kaydeder ve erişim tarihinde durumunu Gündemde gösterir.',provenance='summary',epistemic_type='claim')
records['practice_event'].append(dict(id=event,common_event_key='tbmm-28-2-10-1783-tasimali-egitim-arastirma',event_at='2024-09-20',date_precision='day',date_unknown_reason=None,title='10/1783 taşımalı eğitim araştırma önergesinin sunulması',scope_context='DEM Parti grup başkanvekillerinin köy okulları ve taşımalı eğitim hakkında araştırma talebi.',occurrence_basis='TBMM 10/1783 esas kaydı ve imzalı önerge. DEM Parti aynı metni 19 Eylül 2024 tarihli yayında aktardı.'))
for key,stage in [('party-role','initiative'),('party-scope','initiative'),('party-date','initiative'),('register-id','action'),('register-date','action'),('register-status','result'),('signed-id','initiative')]:
 pid=q(key);add('finding_evidence',finding_id=finding,passage_id=pid,role='support');add('verification',finding_id=finding,passage_id=pid,checked_at=when,result='confirmed',reason='Parti yayını ve TBMM sicili ile imzalı metin karşılaştırıldı.')
 records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=anchors[key][1],stage=stage,concrete_basis='DEM yayını' if key.startswith('party') else 'TBMM sicili' if key.startswith('register') else 'TBMM imzalı önerge taraması',limitation='19 Eylül grup belgesi ve yayın tarihi ile 20 Eylül Başkanlığa geliş tarihi ayrı kayıtlardır. Sicil durumu erişim anına aittir.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Parti yayımı, sicil tarihi ve imzalı belge ayrıldı.')
records['practice_contribution'].append(dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM grup başkanvekillerinin araştırma önergesi. Komisyon kurulması veya uygulanan eğitim politikası sonucu çıkarılmaz.'))
records['practice_candidate'].append(dict(id=q('candidate'),scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Daha önceki bağımsız parti söylemi araştırılacak. 7/15029 kişisel yazılı soru ayrı işlemdir.',passage_ids=enc(pids)))
pkg['entries']+=entries
for k,v in records.items():pkg['practice_records'].setdefault(k,[]).extend(v)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-ankara-workshop-62602872/releases/fc9734ddf2ed4955aee3e9efad62bea5/records.json');data=json.loads(snap.read_text())
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items():data.setdefault(k,[]).extend(v)
validate_practices(data);print('SEMANTIC_PASS',flush=True)
newp=[e['values']['id'] for e in entries if e['kind']=='passage'];targets=practice_review_package_targets(data,records,newp,'dem');allp={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old;refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({allp[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({allp[x]['section'] for x in refs})),supported_claim='Taşımalı eğitim araştırma önergesi '+kind+' '+ident,limitations='Başkanlığa geliş tarihi, parti yayın tarihi ve sicil durumu ayrı tutuldu.',result='reviewed',reason='Yayın gövdesi, sicil ve imzalı belgenin görüntüleri okundu.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem');review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];pkg['source_review_refs']=review['source_review_refs'];print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('tasimali-101783-dem-draft.json',pkg),('tasimali-101783-dem-review-draft.json',review)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f),flush=True)
