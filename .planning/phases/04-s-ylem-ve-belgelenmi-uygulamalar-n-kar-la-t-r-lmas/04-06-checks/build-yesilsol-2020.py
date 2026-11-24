import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text,pdf_page_text
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:'0406-yesilsol-2020-'+x
base=root/'data/practices/04-dem.json';rp=root/'data/practices/04-dem-review.json'
assert sha(base)=='06f92639c132bb92389aa8109d2eb21af01aa4c0c6cb8141042933ee3cf53b43' and sha(rp)=='1c8514fa09acb88021b25ca81460dfbe8aa5061f3ac093edf994062f7ad10231'
pkg,review=json.loads(base.read_text()),json.loads(rp.read_text());cap=json.loads((c/'yesilsol-2020-capture.json').read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat();scope='practice-e65794f6bf91077b14af9defd5619d256b99c44fc728f28f5fa36402c2e5d2ff'
assert next(x for x in pkg['practice_records']['practice_scope_v2'] if x['id']==scope)['boundary_reason']=='2024 Van mazbata itirazı ve YSK sonucu incelendi. Kapsam araştırması sürüyor.'
entries=[];records={k:[] for k in ('practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**v):entries.append(dict(kind=category,values=v))
anchors={'hdp-sign':('hdp','Yeşiller ve Sol Gelecek Partisi imzasıyla yayınlanan “Gasp edilen halkın iradesidir; sessiz kalmayacağız!”','HDP yayını ve tarihsel imzacı'), 'hdp-date':('hdp','<strong>18 Mayıs 2020</strong>','Ortak bildirinin tarihi'), 'birgun-title':('birgun','Sessiz kalmayacağız','Bağımsız gazete ortak bildiri haberi'), 'birgun-sign':('birgun','Partisi (TKP) ve Yeşiller ve Sol Gele-\nyok edilmeye çalışılmasına sessiz\ncek Partisi.','Basılı sayfada Yeşil Sol imzası')}
for key in ('hdp','birgun'):
 x=cap[key];path=root/'data/practices/sources/dem'/x['original_path'];assert sha(path)==x['sha256'];raw=html_source_text(path.read_bytes()) if key=='hdp' else pdf_page_text(path,7);doc=q(key);vid=doc+'-v1';date='2020-05-18' if key=='hdp' else '2020-05-19'
 add('document',id=doc,party_id='dem',title='18 Mayıs ortak bildirisi HDP yayını' if key=='hdp' else 'BirGün 19 Mayıs 2020 basılı sayı',source_kind='news')
 add('document_version',id=vid,document_id=doc,original_url=x['url'],final_url=x['url'],document_date=date,date_precision='day',date_unknown_reason=None,version_label='Özgün HDP yayını' if key=='hdp' else 'Özgün basılı gazete PDF',accessed_at=x['accessed_at'],verified_at=when,mime='text/html' if key=='hdp' else 'application/pdf',sha256=x['sha256'],original_path=x['original_path'],readable_path=x['readable_path'])
 if key=='hdp':add('archive_view',**x['view'])
 add('source_attribution',version_id=vid,publisher='Halkların Demokratik Partisi' if key=='hdp' else 'BirGün',author=None,kind='other' if key=='hdp' else 'journalism',published_at=date,date_precision='day',social_handle=None,public_url=x['url'],basis='HDP ayrı parti ve ortak imzacı yayıncıdır.' if key=='hdp' else '19 Mayıs basılı gazete sayfa 8 haberi.')
 keys=[k for k,v in anchors.items() if v[0]==key]
 for k in keys:
  _,exact,section=anchors[k];assert exact in raw,k;add('passage',id=q(k),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=7 if key=='birgun' else None,printed_page='8' if key=='birgun' else None)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=enc([anchors[k][2] for k in keys]),inspected_at=when));records['practice_attempt_v2'].append(dict(id=q(key+'-reading'),scope_id=scope,attempted_at=when,query='18 Mayıs 2020 ortak bildiride Yeşiller ve Sol Gelecek Partisi imzası',url=x['url'],result='examined',reason='HDP yayını ve bağımsız gazete basılı sayfası okundu. Bildiri tarihi ile belediye işlemleri ayrı.',source_version_id=vid))
event=q('event');finding=q('finding');pids=[q(x) for x in anchors]
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='Yeşiller ve Sol Gelecek Partisi, yerel yönetimlere ilişkin 18 Mayıs 2020 ortak bildirisinin imzacıları arasında yer aldı. Ortak metin HDP tarafından yayımlandı ve 19 Mayıs tarihli BirGün haberinde de imzacılar arasında sayıldı. Bireysel imza yetkilisi bu kaynaklarda belirlenmedi.',provenance='summary',epistemic_type='claim')
records['practice_event'].append(dict(id=event,common_event_key='yerel-yonetimler-2020-05-18-ortak-bildiri',event_at='2020-05-18',date_precision='day',date_unknown_reason=None,title='Yerel yönetimlere ilişkin 18 Mayıs 2020 ortak bildirisi',scope_context='18 Mayıs 2020 tarihli ortak bildirinin yayımlanması.',occurrence_basis='18 Mayıs tarihli ortak açıklama ve 19 Mayıs BirGün basılı sayı, sayfa 8.'))
for key,stage in [('hdp-sign','action'),('hdp-date','action'),('birgun-title','action'),('birgun-sign','action')]:
 pid=q(key);add('finding_evidence',finding_id=finding,passage_id=pid,role='support');add('verification',finding_id=finding,passage_id=pid,checked_at=when,result='confirmed',reason='Ortak imza ve basılı haber kaynakta incelendi.')
 records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=anchors[key][2],stage=stage,concrete_basis='HDP ortak imzacı yayını' if key.startswith('hdp') else 'BirGün 19 Mayıs basılı sayı sayfa 8',limitation='HDP yayıncı ve ayrı imzacıdır. BirGün metin çıkarımında iki gazete sütunu karışır. Bireysel imza yetkilisi bilinmiyor.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='HDP yayıncısı ile tarihsel Yeşil Sol imzası ve bağımsız gazete ayrıldı.')
records['practice_contribution'].append(dict(id=q('contribution'),event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='unknown',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='Kaynaklar tarihsel Yeşiller ve Sol Gelecek Partisini imzacı sayıyor. Yetkili kişi ve fiziksel imza belgesi belirlenmedi. HDP ayrı partidir.'))
records['practice_candidate'].append(dict(id=q('candidate'),scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Önceki bağımsız parti söylemi ayrıca araştırılacak. Ortak bildiri belediye işlemi değildir.',passage_ids=enc(pids)))
pkg['entries']+=entries
for k,v in records.items():pkg['practice_records'].setdefault(k,[]).extend(v)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-van-2024-62625356/releases/c71707dd841e467a84bf1e56b314cff2/records.json');data=json.loads(snap.read_text())
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items():data.setdefault(k,[]).extend(v)
validate_practices(data);print('SEMANTIC_PASS',flush=True)
targets=practice_review_package_targets(data,records,pids,'dem');allp={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old;refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({allp[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({allp[x]['section'] for x in refs})),supported_claim='2020 yerel yönetimler ortak bildirisi '+kind+' '+ident,limitations='HDP yayıncıdır, bireysel imza yetkilisi açık. Gazete sayfa metni sütunları karıştırır.',result='reviewed',reason='HDP yayını ve bağımsız BirGün sayfası okundu.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem');review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];pkg['source_review_refs']=review['source_review_refs'];print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('yesilsol-2020-dem-draft.json',pkg),('yesilsol-2020-dem-review-draft.json',review)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f),flush=True)
