"""9 Nisan 2025 grup konuşmasını ayrı bir olay olarak doğrulama için hazırlar."""
import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:'0406-iklim-74-kordu-'+x
base=root/'data/practices/04-dem.json';rp=root/'data/practices/04-dem-review.json'
assert sha(base)=='78a74803dcde3d0f24c8b546f9f5fb5b41994da1f25126818a5e522fa48a18f7' and sha(rp)=='94234dad20e2b4402819ed834f907872040fd3d03ba614fe47cd0640f0966a1d'
pkg,review=json.loads(base.read_text()),json.loads(rp.read_text());cap=json.loads((c/'iklim-74-source-capture.json').read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat()
scope='practice-1c5854aa8d8f94f0081a0ceb37427ff8b3ba45ab525d3b46b3e50beb15869a09';sc=next(x for x in pkg['practice_records']['practice_scope_v2'] if x['id']==scope)
sc['boundary_reason']+=' Ayrıca 9 Nisan 2025 DEM grup konuşması incelendi; önceki bağımsız söylem ve kapsam araştırması açıktır.'
vid='0406-iklim-74-floor-v1';doc='0406-iklim-74-floor';rawpath=root/'data/practices/sources/dem'/cap['original_path'];assert sha(rawpath)==cap['sha256'];raw=html_source_text(rawpath.read_bytes())
entries=[];records={k:[] for k in ('practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_actor_period','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**v):entries.append(dict(kind=category,values=v))
add('document',id=doc,party_id='dem',title='TBMM 9 Nisan 2025 74. birleşim tam tutanağı',source_kind='official')
add('document_version',id=vid,document_id=doc,original_url=cap['url'],final_url=cap['url'],document_date='2025-04-09',date_precision='day',date_unknown_reason=None,version_label='9 Nisan 2025 tam tutanak',accessed_at=cap['accessed_at'],verified_at=when,mime='text/html',sha256=cap['sha256'],original_path=cap['original_path'],readable_path=cap['readable_path'])
view=dict(cap['view']);view['version_id']=vid;add('archive_view',**view)
add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',published_at='2025-04-09',date_precision='day',social_handle=None,public_url=cap['url'],basis='TBMM Genel Kurul 74. birleşim tam tutanağı.')
anchors=[('date','9 Nisan 2025 Çarşamba','74. birleşimin tarihi'),('bill','İklim Kanunu Teklifi (2/2927) ve Çevre Komisyonu Raporu (S. Sayısı: 198)','Görüşülen teklif ve komisyon raporu'),('role',"Halkların Eşitlik ve Demokrasi Partisi Grubu adına Tunceli Milletvekili Ayten Kordu'ya ait.",'Korduya DEM grubu adına söz verilmesi'),('objection','Bu teklif kabul edilmemelidir.','Teklifin kabul edilmemesi çağrısı'),('withdraw',"Bu yasa geri çekilmeli, ilgili tüm kurumlar ve STK'ler, odalar, çevre örgütleriyle gerçek bir iklim kanunu hazırlanmalı",'Geri çekilme ve katılımcı hazırlık çağrısı')]
for n,exact,section in anchors:
 assert exact in raw,(n,exact);add('passage',id=q(n),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
event,finding,candidate,contribution,actor=(q(x) for x in ('event','finding','candidate','contribution','actor'));pids=[q(x[0]) for x in anchors];passages={x['values']['id']:x['values'] for x in entries if x['kind']=='passage'}
add('actor',id=actor,kind='authorized_representative',party_id='dem',person_id='0406-iklim-final-kordu-person',authorization_passage_id=q('role'))
text='9 Nisan 2025 Genel Kurulunda DEM Parti Grubu adına Ayten Kordu, 2/2927 İklim Kanunu Teklifi’nin kabul edilmemesini ve geri çekilerek ilgili kurumlarla çevre örgütlerinin katılımıyla yeniden hazırlanmasını istedi. Bu konuşma, kişisel oy veya kanunun nihai oylama sonucunu göstermez.'
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=text,provenance='summary',epistemic_type='claim')
records['practice_event'].append(dict(id=event,common_event_key='tbmm-28-3-74-2-2927-dem-group-speech',event_at='2025-04-09',date_precision='day',date_unknown_reason=None,title='İklim teklifi üzerine DEM grup konuşması',scope_context='TBMM 74. birleşimde 2/2927 sayılı İklim Kanunu Teklifi ve 198 sıra sayılı komisyon raporu görüşülürken DEM grubu adına konuşma yapıldı.',occurrence_basis='TBMM 28. Dönem 3. Yasama Yılı 74. birleşim tam tutanağı.'))
for n,_,_ in anchors:
 pid=q(n);stage='initiative' if n in ('date','bill') else 'action';p=passages[pid]
 add('finding_evidence',finding_id=finding,passage_id=pid,role='support');add('verification',finding_id=finding,passage_id=pid,checked_at=when,result='confirmed',reason='74. birleşim grup konuşması ve teklif bağlamı özgün tutanakta okundu.')
 records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=p['section'],stage=stage,concrete_basis='9 Nisan 2025 TBMM tam tutanağı.',limitation='Grup konuşması, bireysel oy, madde önergeleri ve kanunun nihai sonucu ayrı işlemlerdir.',epistemic_type='claim'))
 records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Grup sıfatı, konuşma ve 2/2927 bağlamı okundu; oy veya sonuç atfedilmedi.')
records['practice_contribution'].append(dict(id=contribution,event_id=event,party_id='dem',actor_id=actor,contribution_kind='objection',finding_id=finding,authority_passage_id=q('role'),membership_passage_id=None,responsibility_limit='Ayten Kordu’nun DEM grubu adına bu birleşimdeki konuşması; kişisel veya grup oyu ve nihai sonuç çıkarılmaz.'))
records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2025-04-09',valid_to='2025-04-09',identity_passage_id=q('role')))
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='İlgili bağımsız önceki parti söylemi ve dönemsellik ayrıca değerlendirilmeli; grup konuşması nihai oy değildir.',passage_ids=enc(pids)))
records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=enc([x[2] for x in anchors]),inspected_at=when))
records['practice_attempt_v2'].append(dict(id=q('reading'),scope_id=scope,attempted_at=when,query='9 Nisan 2025 74. birleşim DEM iklim grup konuşması',url=cap['url'],result='examined',reason='Teklif başlığı, grup sıfatı ve Kordu konuşmasının ilgili bölümü okundu.',source_version_id=vid))
pkg['entries']+=entries
for k,rows in records.items():pkg['practice_records'].setdefault(k,[]).extend(rows)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-sivas-1568-62571175/releases/1f3b717e6dc9420da75bec75d2d69b34/records.json');data=json.loads(snap.read_text());next(x for x in data['practice_scope_v2'] if x['id']==scope)['boundary_reason']=sc['boundary_reason']
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,rows in records.items():data.setdefault(k,[]).extend(rows)
validate_practices(data);print('IKLIM_74_SEMANTIC_PASS',flush=True)
newp=[e['values']['id'] for e in entries if e['kind']=='passage'];targets=practice_review_package_targets(data,records,newp,'dem');allp={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old;refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({allp[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({allp[x]['section'] for x in refs})),supported_claim='74. birleşim grup konuşması ve teklif: '+kind+' / '+ident,limitations='Grup konuşması, bireysel oy ve teklifin nihai sonucu ayrı işlemlerdir.',result='reviewed',reason='Teklif başlığı, tarih, grup sıfatı ve ilgili konuşma bölümü okundu.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem');review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('iklim-74-kordu-dem-draft.json',pkg),('iklim-74-kordu-dem-review-draft.json',review)]:
 p=c/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(p),flush=True)
