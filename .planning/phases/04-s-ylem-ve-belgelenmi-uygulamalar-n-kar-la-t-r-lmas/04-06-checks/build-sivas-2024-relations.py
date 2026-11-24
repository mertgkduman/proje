"""2024 parti talebini iki ayrı 2025 işlemiyle, eski adayları koruyarak karşılaştır."""
import datetime, hashlib, json
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import practice_review_package_targets, validate_practice_source_review, validate_practices

c=Path(__file__).resolve().parent; root=c.parents[3]; sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=root/'data/practices/04-dem.json'; revfile=root/'data/practices/04-dem-review.json'
assert sha(base)=='ee7b2a10cee56b2c8ee4babf59fb8f2589597eab1103a8337a93e47593a18ee2'
assert sha(revfile)=='d2eac1dbbaa3fd198644cc3443afff90cdeb729e840fcfb1493261a0b6cbc39d'
pkg,review=json.loads(base.read_text()),json.loads(revfile.read_text())
capture=json.loads((c/'sivas-2024-antecedents-capture.json').read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat()
enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:'0406-sivas-2024-'+x
entries=[]; records={k:[] for k in ('practice_statement','practice_relation','practice_candidate_revision','practice_scope_source','practice_attempt_v2')}
def add(category,**v):entries.append({'kind':category,'values':v})
for cap,kind in zip(capture,('party','tbmm')):
 doc=q(kind);vid=q(kind+'-v1');path=root/'data/practices/sources/dem'/cap['original_path'];assert sha(path)==cap['sha256']; raw=html_source_text(path.read_bytes())
 add('document',id=doc,party_id='dem',title='DEM 2024 Madımak araştırma talebi' if kind=='party' else 'TBMM 2024 97. birleşim tam tutanağı',source_kind='party' if kind=='party' else 'official')
 add('document_version',id=vid,document_id=doc,original_url=cap['original_url'],final_url=cap['final_url'],document_date='2024-07-02',date_precision='day',date_unknown_reason=None,version_label='2 Temmuz 2024',accessed_at=cap['accessed_at'],verified_at=when,mime='text/html',sha256=cap['sha256'],original_path=cap['original_path'],readable_path=cap['readable_path'])
 view=dict(cap['view']);view['version_id']=vid;add('archive_view',**view)
 add('source_attribution',version_id=vid,publisher='HALKLARIN EŞİTLİK VE DEMOKRASİ PARTİSİ' if kind=='party' else 'TBMM',author=None,kind='party_publication' if kind=='party' else 'official',published_at='2024-07-02',date_precision='day',social_handle=None,public_url=cap['original_url'],basis='Parti yayını ve aynı ana makinede tam hukuki adı taşıyan arşivli parti yayını.' if kind=='party' else 'TBMM 97. birleşim tutanağı.')
 anchors=[('commission','bir araştırma komisyonunun kurulması elzemdir.','2024 parti araştırma komisyonu talebi')] if kind=='party' else [('motion','6131 grup numaralı','2024 grup gündem önergesi numarası'),('speaker','DEM PARTİ GRUBU ADINA İBRAHİM AKIN (İzmir)','2024 grup adına konuşmacı')]
 for suffix,exact,section in anchors:
  assert exact in raw;add('passage',id=q(suffix),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)

target,quote,statement=q('target'),q('quote'),q('statement'); targetp=q('commission');support=[targetp,q('motion'),q('speaker')]
def finding(ident,text,refs,provenance='summary',pair=None):
 add('finding',id=ident,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=pair or ident,text=text,provenance=provenance,epistemic_type='claim')
 for pid in refs:
  add('finding_evidence',finding_id=ident,passage_id=pid,role='support');add('verification',finding_id=ident,passage_id=pid,checked_at=when,result='confirmed',reason='Tarihli özgün kaynak ve bağlam okundu.')
 add('review',id='review-'+ident,kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='Önceki talep, işlemlerin tarihi ve aktör sınırları ayrıldı.')
finding(target,'DEM Parti 2 Temmuz 2024 tarihli yayında Sivas Madımak olaylarının tüm yönleriyle incelenmesi için Meclis araştırma komisyonu kurulmasını istedi.',support)
finding(quote,'bir araştırma komisyonunun kurulması elzemdir.',[targetp],'quote',target)
records['practice_statement'].append(dict(id=statement,party_id='dem',topic_id='inanc-mezhep-esitligi',taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2024-07-02',date_precision='day',version_id=q('party-v1'),period_basis='DEM Parti 2 Temmuz 2024 tarihli açıklaması ve TBMM 97. birleşimindeki grup önerisi.',uncertainty_reason=None,comparison_row_id='04-03-v3-0305-dem-program-inanc-row'))
scope='practice-32598cee77548f2dce224908e63dc9005f9de70be0fff59b0b4990064ad650ae'
for cap,kind in zip(capture,('party','tbmm')):
 vid=q(kind+'-v1');pids=[e['values'] for e in entries if e['kind']=='passage' and e['values']['version_id']==vid]
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=enc([p['section'] for p in pids]),inspected_at=when))
 records['practice_attempt_v2'].append(dict(id=q(kind+'-reading'),scope_id=scope,attempted_at=when,query='2024 DEM Sivas Madımak araştırma talebi',url=cap['original_url'],result='examined',reason='Tarihli parti metni ve TBMM grup gündemi okundu.',source_version_id=vid))
for number in ('2879','2880'):
 candidate=next(x for x in pkg['practice_records']['practice_candidate'] if x['id']==f'0406-sivas-{number}-candidate');event=candidate['event_id']; refs=json.loads(candidate['passage_ids'])
 relation=q(number+'-relation');explanation=q(number+'-explanation'); result=None
 if number=='2879':
  erefs=['0406-sivas-2879-number','0406-sivas-2879-date','0406-sivas-2879-sponsor','0406-sivas-2879-status']
  reason='2024 komisyon talebi ile 1 Temmuz 2025 kişisel araştırma başvurusu aynı Madımak olaylarını araştırma konusundadır.'
  text='2024 tarihli DEM komisyon talebi ile Meral Danış Beştaş ve 20 milletvekilinin 1 Temmuz 2025 başvurusu aynı olayların araştırılmasına yöneliktir. Bireysel başvuru parti grubu görevlendirmesi değildir; esas araştırmanın açılması ve sonucu açık kalır.'
  authority='2024 parti yayını ve grup gündemi; 2025 sicili milletvekillerinin bireysel başvurusunu gösterir.'
  uncertainty='10/2879 bireysel başvurudur; araştırma komisyonunun açılması ve sonucu bilinmiyor. 10/2880 takvim oyu bu dosyaya aktarılmaz.'
 else:
  erefs=['0406-sivas-2880-floor-call','0406-sivas-2880-floor-no-quorum','0406-sivas-2880-floor-retry']
  reason='2024 komisyon talebi ile 2 Temmuz 2025 DEM grup araştırmasının ön görüşme önerisi aynı Madımak olaylarını araştırma konusundadır.'
  text='2024 tarihli DEM komisyon talebi ile Koçyiğit ve Temelli’nin 2025 grup araştırma önergesi aynı olayların araştırılmasına yöneliktir. 2 Temmuz 2025 ön görüşme takvimi ikinci oylamada reddedildi; bu karar araştırma esasının sonucu veya kişisel oy değildir.'
  authority='2024 parti yayını ve grup gündemi ile 2025 grup başkanvekillerinin ayrı grup önerisi ve başkanın takvim açıklaması ayrıdır.'
  uncertainty='Takvim oylamasının reddi araştırma esasının reddi veya açılması değildir; kişisel oy ve araştırma sonucu bilinmiyor.'
  result=q('2880-calendar-result');finding(result,'2 Temmuz 2025 Genel Kurulunda 10/2880 araştırmasının aynı gün ön görüşülmesi önerisi, ilk oylamada karar yeter sayısı bulunmaması ardından ikinci oylamada kabul edilmedi.',['0406-sivas-2880-floor-no-quorum','0406-sivas-2880-floor-retry'])
 finding(explanation,text,support+erefs)
 records['practice_relation'].append(dict(id=relation,statement_id=statement,event_id=event,party_id='dem',topic_id='inanc-mezhep-esitligi',scope_id=scope,comparability_reason=reason,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='2 Temmuz 2024 parti açıklaması; '+('1 Temmuz 2025 bireysel başvuru.' if number=='2879' else '2 Temmuz 2025 grup gündemi.'),authority_context=authority,uncertainty_reason=uncertainty))
 records['practice_candidate_revision'].append(dict(id=q(number+'-eligible'),candidate_id=candidate['id'],recorded_at=when,event_id=event,relation_id=relation,state='eligible',reason=reason,passage_ids=enc(refs)))
pkg['entries']+=entries
for k,rows in records.items():pkg['practice_records'].setdefault(k,[]).extend(rows)
snapshot_path=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-sivas-2879-62566333/releases/50390a6a114740c49450dcea2115f470/records.json')
snapshot=json.loads(snapshot_path.read_text())
for e in entries:
 rows=snapshot.setdefault(e['kind'],[])
 if e['values'] not in rows:rows.append(e['values'])
for kind,rows in records.items():snapshot.setdefault(kind,[]).extend(x for x in rows if x not in snapshot[kind])
validate_practices(snapshot);print('SIVAS_2024_RELATIONS_SEMANTIC_PASS',flush=True)
passages={p['id']:p for p in snapshot['passage']};newp=[x['values']['id'] for x in entries if x['kind']=='passage']
targets=practice_review_package_targets(snapshot,records,newp,'dem');existing={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 if (kind,ident) in existing: raise ValueError('Beklenmeyen eski inceleme hedefi '+repr((kind,ident)))
 refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({passages[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({passages[x]['section'] for x in refs})),supported_claim='2024 araştırma talebi ile ayrı 2025 işlemlerinin sınırlı karşılaştırması: '+kind+' / '+ident,limitations='2879 bireysel başvuru; 2880 grup takvim kararı; esas araştırma sonucu ve isimli oy açık.',result='reviewed',reason='Özgün parti yayını, 2024 tutanak kesiti ve ayrı 2025 işlem kanıtları okundu.'))
validate_practice_source_review(snapshot,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem');print('SOURCE_REVIEW_PASS',len(targets),flush=True)
refs=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];review['source_review_refs']=refs
for name,obj in [('sivas-2024-relations-dem-draft.json',pkg),('sivas-2024-relations-dem-review-draft.json',review)]:
 p=c/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(name,sha(p),flush=True)
