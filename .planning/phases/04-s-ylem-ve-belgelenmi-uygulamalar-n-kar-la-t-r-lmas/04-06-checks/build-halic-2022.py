import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent; root=c.parents[3]; sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest(); enc=lambda x:json.dumps(x,ensure_ascii=False); q=lambda x:'0406-halic-2022-'+x
base=root/'data/practices/04-dem.json'; rp=root/'data/practices/04-dem-review.json'
assert sha(base)=='6dbdf8957464782f99860884841dffe7037f752f0d0d7e2f48026a53f9de20f5' and sha(rp)=='cc88060809d6915fe2af2ec37e7059e1b76fbaf504cc4256515d2a141e51e120'
pkg,review=json.loads(base.read_text()),json.loads(rp.read_text()); cap=json.loads((c/'halic-2022-capture.json').read_text()); when=datetime.datetime.now(datetime.timezone.utc).isoformat(); scope='practice-9a039f4f4e799b093a2abad214db0c890161e9e7cb97ca5374938d23ca99e93e'
entries=[]; records={k:[] for k in ('practice_scope_v2','practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_actor_period','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**v): entries.append(dict(kind=category,values=v))
records['practice_scope_v2'].append(dict(id=scope,party_id='dem',topic_id='siyasal-ittifaklar',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='24 Eylül 2022 Haliç buluşmasında Yeşil Sol temsilcilerinin katılımı incelendi. Kapsam araştırması sürüyor.'))
raw=html_source_text((root/'data/practices/sources/dem'/cap['original_path']).read_bytes()); assert sha(root/'data/practices/sources/dem'/cap['original_path'])==cap['sha256']
add('document',id=q('bianet'),party_id='dem',title='Emek ve Özgürlük İttifakı halkla buluştu',source_kind='journalism')
add('document_version',id=q('bianet-v1'),document_id=q('bianet'),original_url=cap['url'],final_url=cap['final_url'],document_date='2022-09-24',date_precision='day',date_unknown_reason=None,version_label='Bianet özgün haber',accessed_at=cap['accessed_at'],verified_at=when,mime='text/html',sha256=cap['sha256'],original_path=cap['original_path'],readable_path=cap['readable_path'])
add('archive_view',**cap['view'])
add('source_attribution',version_id=q('bianet-v1'),publisher='Bianet',author=None,kind='journalism',published_at='2022-09-24',date_precision='day',social_handle=None,public_url=cap['url'],basis='24 Eylül 2022 tarihli Bianet haber gövdesi')
anchors={'occurrence':('oluşturduğu "Emek ve Özgürlük İttifakı", Haliç Kongre Merkezi\'nde yol haritasını açıklamak üzere toplandı.','Haliç buluşması'),'presence':('Yeşil Sol Parti Eş Genel Başkanları İbrahim Akın ve Ayşe Erdem, Devrimci Parti Genel Başkanı Elif Torun Öneren, Sosyalist Yeniden Kuruluş Partisi (SYKP) Eş Genel Başkanları Canan Yüce ve Cavit Uğur, Sosyalist Dayanışma Platformu (SODAP) Eşsözcüleri Kezban Konukçu ve Sezgin Kartal ile ittifakın bileşen partilerinin milletvekilleri ile temsilcileri de yer aldı.','Yeşil Sol temsilcilerinin katılımı')}
for key,(exact,section) in anchors.items():
 assert exact in raw,key
 add('passage',id=q(key),version_id=q('bianet-v1'),exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
records['practice_scope_source'].append(dict(scope_id=scope,version_id=q('bianet-v1'),inspected_sections=enc([x[1] for x in anchors.values()]),inspected_at=when))
records['practice_attempt_v2'].append(dict(id=q('reading'),scope_id=scope,attempted_at=when,query='24 Eylül 2022 Haliç buluşması Yeşil Sol katılımı',url=cap['url'],result='examined',reason='Bianet haber gövdesi ve ayrıca HDP özgün yayını okundu. Kurucu imza ile katılım ayrıldı.',source_version_id=q('bianet-v1')))
event=q('event'); finding=q('finding')
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='Bianet’in 24 Eylül tarihli haberine göre Yeşil Sol Parti temsilcileri Ayşe Erdem ve İbrahim Akın Haliç buluşmasında bulundu. Haber katılımı bildiriyor, kurucu imzayı veya deklarasyonu hazırlama görevini göstermiyor.',provenance='summary',epistemic_type='claim')
records['practice_event'].append(dict(id=event,common_event_key='halic-emek-ozgurluk-2022-09-24',event_at='2022-09-24',date_precision='day',date_unknown_reason=None,title='Emek ve Özgürlük İttifakı’nın Haliç halk buluşması',scope_context='24 Eylül 2022’de İstanbul Haliç Kongre Merkezi’nde düzenlenen Emek ve Özgürlük İttifakı halk buluşması ve deklarasyonun açıklanması.',occurrence_basis='24 Eylül 2022 tarihli Bianet haberi ve HDP yayını, Haliç Kongre Merkezi’ndeki halk buluşmasını ve deklarasyonun açıklanmasını bildiriyor.'))
for key,(_,section) in anchors.items():
 pid=q(key); add('finding_evidence',finding_id=finding,passage_id=pid,role='support'); add('verification',finding_id=finding,passage_id=pid,checked_at=when,result='confirmed',reason='Özgün haber gövdesi okundu.')
 records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=section,stage='action',concrete_basis='Bianet haber gövdesi',limitation='Haberin güncellenme zamanı aynı gün 23.08 olarak gösterilir. Katılım kurucu imza sayılmaz.',epistemic_type='claim')); records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage='action',basis_kind='document'))
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Katılım ile kurucu imza ve ayrı parti kimlikleri ayrıldı.')
add('person',id=q('erdem-person'),name='Ayşe Erdem')
for name,person in [('erdem',q('erdem-person')),('akin','0406-iklim-final-akin-person')]:
 actor=q(name+'-actor'); contribution=q(name+'-contribution')
 add('actor',id=actor,kind='authorized_representative',party_id='dem',person_id=person,authorization_passage_id=q('presence'))
 records['practice_contribution'].append(dict(id=contribution,event_id=event,party_id='dem',actor_id=actor,contribution_kind='unknown',finding_id=finding,authority_passage_id=q('presence'),membership_passage_id=None,responsibility_limit='Haberin bildirdiği bireysel katılım. Kurucu imza, metin hazırlığı veya politika uygulaması sonucu çıkarılmaz.'))
 records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2022-09-24',valid_to='2022-09-24',identity_passage_id=q('presence')))
pids=[q(x) for x in anchors]; records['practice_candidate'].append(dict(id=q('candidate'),scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Daha önceki bağımsız parti söylemi ayrıca araştırılacak. Katılım kurucu imza sayılmaz.',passage_ids=enc(pids)))
pkg['entries']+=entries
for k,v in records.items(): pkg['practice_records'].setdefault(k,[]).extend(v)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-tasimali-101783-62618221/releases/4776b5d4a08949c8a87b3a830cc24bfe/records.json'); data=json.loads(snap.read_text())
for e in entries: data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items(): data.setdefault(k,[]).extend(v)
validate_practices(data); print('SEMANTIC_PASS',flush=True)
targets=practice_review_package_targets(data,records,pids,'dem'); allp={x['id']:x for x in data['passage']}; old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old; refs=sorted(refs)
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({allp[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({allp[x]['section'] for x in refs})),supported_claim='Haliç buluşmasında Yeşil Sol katılımı '+kind+' '+ident,limitations='Katılım ile kurucu imza ayrıdır. Haberin aynı gün güncellendiği belirtiliyor.',result='reviewed',reason='Bianet gövdesi ve HDP özgün yayını karşılaştırıldı.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem'); review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]; pkg['source_review_refs']=review['source_review_refs']; print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('halic-2022-dem-draft.json',pkg),('halic-2022-dem-review-draft.json',review)]:
 f=c/name; f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n'); print(name,sha(f),flush=True)
