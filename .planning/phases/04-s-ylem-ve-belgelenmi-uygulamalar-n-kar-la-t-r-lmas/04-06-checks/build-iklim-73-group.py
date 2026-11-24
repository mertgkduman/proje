import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:'0406-iklim-73-group-'+x
base=root/'data/practices/04-dem.json';rp=root/'data/practices/04-dem-review.json'
assert sha(base)=='7dc82e7d70810259015b37ffb2cca472caf3615003ed4192276f7c4821c1baec' and sha(rp)=='65b2e90196b3c3cc469a168d8b90a047e9645add50d40568ac48ca4d4e1cbbca'
pkg,review=json.loads(base.read_text()),json.loads(rp.read_text());cap=json.loads((c/'iklim-73-source-capture.json').read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat()
scope='practice-1c5854aa8d8f94f0081a0ceb37427ff8b3ba45ab525d3b46b3e50beb15869a09';vid='0406-iklim-73-floor-v1';doc='0406-iklim-73-floor'
rawpath=root/'data/practices/sources/dem'/cap['original_path'];assert sha(rawpath)==cap['sha256'];raw=html_source_text(rawpath.read_bytes())
entries=[];records={k:[] for k in ('practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_actor_period','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**v):entries.append(dict(kind=category,values=v))
add('document',id=doc,party_id='dem',title='TBMM 8 Nisan 2025 73. birleşim tam tutanağı',source_kind='official')
add('document_version',id=vid,document_id=doc,original_url=cap['url'],final_url=cap['url'],document_date='2025-04-08',date_precision='day',date_unknown_reason=None,version_label='8 Nisan 2025 tam tutanak',accessed_at=cap['accessed_at'],verified_at=when,mime='text/html',sha256=cap['sha256'],original_path=cap['original_path'],readable_path=cap['readable_path'])
add('archive_view',**cap['view']);add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',published_at='2025-04-08',date_precision='day',social_handle=None,public_url=cap['url'],basis='TBMM Genel Kurul 73. birleşim tam tutanağı.')
anchors=[('date','8 Nisan 2025 Salı','73. birleşimin tarihi'),('bill','İklim Kanunu Teklifi (2/2927) ve Çevre Komisyonu Raporu (S. Sayısı: 198)','Görüşülen teklif'),('akin-role',"Halkların Eşitlik ve Demokrasi Partisi Grubu adına İzmir Milletvekili İbrahim Akın'a ait.",'Akın’a grup adına söz verilmesi'),('akin-call','biz bu yasanın çekilmesini istiyoruz; gerçek anlamda iklim kanununun çıkarılması için çalışma yapılmasını istiyoruz.','Akın’ın teklifin çekilmesi çağrısı'),('koca-role',"Halkların Eşitlik ve Demokrasi Partisi Grubu adına diğer söz talebi Mersin Milletvekili Perihan Koca'ya ait.",'Koca’ya grup adına söz verilmesi'),('koca-critique','bu kanunun adı olsa olsa emisyon ticaret kanunu olur','Koca’nın teklif eleştirisi')]
for key,exact,section in anchors:
 assert exact in raw,(key,exact);add('passage',id=q(key),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
event=q('event');pids=[q(x[0]) for x in anchors]
records['practice_event'].append(dict(id=event,common_event_key='tbmm-28-3-73-2-2927-dem-group-speeches',event_at='2025-04-08',date_precision='day',date_unknown_reason=None,title='İklim teklifi üzerine DEM grup konuşmaları',scope_context='TBMM 73. birleşimde 2/2927 sayılı İklim Kanunu Teklifi ve 198 sıra sayılı komisyon raporunun tümü görüşülürken DEM grubu adına iki konuşma yapıldı.',occurrence_basis='TBMM 28. Dönem 3. Yasama Yılı 73. birleşim tam tutanağı.'))
for key,exact,section in anchors:
 pid=q(key);stage='initiative' if key in ('date','bill') else 'action';records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=section,stage=stage,concrete_basis='8 Nisan 2025 TBMM tam tutanağı.',limitation='Grup konuşmaları, teklifin ve maddelerin oylamaları ayrı işlemlerdir.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
for who,name,text in [('akin','İbrahim Akın','İbrahim Akın, 8 Nisan 2025 Genel Kurulunda DEM Grubu adına 2/2927 İklim Kanunu Teklifi’nin geri çekilmesini ve gerçek bir iklim kanunu hazırlanması için çalışılmasını istedi.'),('koca','Perihan Koca','Perihan Koca, 8 Nisan 2025 Genel Kurulunda DEM Grubu adına 2/2927 İklim Kanunu Teklifi’ni eleştirerek metni emisyon ticareti düzenlemesi olarak niteledi.')]:
 actor=q(who+'-actor');finding=q(who+'-finding');contribution=q(who+'-contribution');role=q(who+'-role');refs=[q('date'),q('bill'),role,q(who+('-call' if who=='akin' else '-critique'))]
 add('actor',id=actor,kind='authorized_representative',party_id='dem',person_id='0406-iklim-final-'+who+'-person',authorization_passage_id=role)
 add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text=text+' Bu konuşma kişisel oy veya kanunun nihai sonucunu göstermez.',provenance='summary',epistemic_type='claim')
 for pid in refs:add('finding_evidence',finding_id=finding,passage_id=pid,role='support');add('verification',finding_id=finding,passage_id=pid,checked_at=when,result='confirmed',reason='Teklif, grup yetkisi ve konuşma ilgili tutanak bölümünde okundu.')
 add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Grup sıfatı ve konuşmacının kendi değerlendirmesi incelendi.')
 records['practice_contribution'].append(dict(id=contribution,event_id=event,party_id='dem',actor_id=actor,contribution_kind='objection',finding_id=finding,authority_passage_id=role,membership_passage_id=None,responsibility_limit=name+' tarafından DEM grubu adına yapılan bu konuşma; kişisel oy veya nihai sonuç çıkarılmaz.'))
 records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2025-04-08',valid_to='2025-04-08',identity_passage_id=role))
records['practice_candidate'].append(dict(id=q('candidate'),scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Daha önceki bağımsız parti söylemi ve dönemsel ilişki araştırması açık; aynı teklifin sonraki madde önergeleri farklı işlemlerdir.',passage_ids=enc(pids)))
records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=enc([x[2] for x in anchors]),inspected_at=when))
records['practice_attempt_v2'].append(dict(id=q('reading'),scope_id=scope,attempted_at=when,query='8 Nisan 2025 73. birleşim DEM 2/2927 grup konuşmaları',url=cap['url'],result='examined',reason='Teklif başlığı, grup sıfatları ve iki ilgili konuşma okundu.',source_version_id=vid))
pkg['entries']+=entries
for k,v in records.items():pkg['practice_records'].setdefault(k,[]).extend(v)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-iklim-74-motions-62579272/releases/4141c82a310a4a45a342679c9c7baf53/records.json');data=json.loads(snap.read_text())
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items():data.setdefault(k,[]).extend(v)
validate_practices(data);print('GROUP_73_SEMANTIC_PASS',flush=True)
newp=[e['values']['id'] for e in entries if e['kind']=='passage'];targets=practice_review_package_targets(data,records,newp,'dem');allp={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old;refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({allp[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({allp[x]['section'] for x in refs})),supported_claim='73. birleşimde iki ayrı grup konuşması: '+kind+' / '+ident,limitations='Konuşma kişisel veya grup oyu ya da nihai sonuç değildir.',result='reviewed',reason='Teklif, tarih, sıfat ve konuşma pasajları okundu.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem');review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('iklim-73-group-dem-draft.json',pkg),('iklim-73-group-dem-review-draft.json',review)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f),flush=True)
