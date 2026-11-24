import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:'0406-ankara-workshop-'+x
base=root/'data/practices/04-dem.json';rp=root/'data/practices/04-dem-review.json'
assert sha(base)=='b6c2bcf6281edde82d810c891619a23345ae0f22d4a4e1a09a697ff43588f2d6' and sha(rp)=='b533770946e85e460db56c4e2fba684648ad6c35111afcbd8aec6d2b7b6ef3da'
pkg,review=json.loads(base.read_text()),json.loads(rp.read_text());cap=json.loads((c/'ankara-workshop-capture.json').read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat();scope='practice-b30bb606ba0f24e6b147112b2daadcd0a9123126b317c2ea638087212545e08a'
entries=[];records={k:[] for k in ('practice_scope_v2','practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**values):entries.append(dict(kind=category,values=values))
records['practice_scope_v2'].append(dict(id=scope,party_id='dem',topic_id='demokrasi-katilim',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='1–2 Kasım 2025 Ankara çalıştayı aday zinciri; kapsam araştırması sürüyor.'))
anchors={
 'dem':('DEM Parti, EHP, EMEP, SMF, TİP ve TÖP olarak 1-2 Kasım tarihlerinde Ankara\'da düzenlediğimiz “Demokrasi ve Barış İçin Buluşuyoruz, Mücadelenin Olanaklarını Konuşuyoruz” başlıklı çalıştayın sonuç metni:','Ortak düzenleme ve sonuç metni'),
 'ilke':('Halkların Eşitlik ve Demokrasi Partisi (DEM Parti), Emekçi Hareket Partisi (EHP), Toplumsal Özgürlük Partisi (TÖP), Emek Partisi (EMEP), Türkiye İşçi Partisi (TİP) ve Sosyalist Meclisler Federasyonu’nun (SMF) ortak düzenlediği “Demokrasi ve Barış İçin Buluşuyoruz, Mücadelenin Olanaklarını Konuşuyoruz” başlıklı çalıştay, Ankara Makine Mühendisleri Odası Eğitim ve Kültür Merkezi’nde ikinci gününde devam etti.','İkinci gün ve altı düzenleyici')}
for key,publisher,kind in [('dem','DEM Parti','party'),('ilke','İlke TV','news')]:
 x=cap[key];rawpath=root/'data/practices/sources/dem'/x['original_path'];assert sha(rawpath)==x['sha256'];raw=html_source_text(rawpath.read_bytes());exact,section=anchors[key];assert exact in raw
 doc=q(key);vid=doc+'-v1';pid=q(key+'-passage')
 add('document',id=doc,party_id='dem',title=('Demokrasi ve Barış çalıştayı sonuç metni' if key=='dem' else 'Ankara Demokrasi ve Barış çalıştayı ikinci gün haberi'),source_kind=kind)
 add('document_version',id=vid,document_id=doc,original_url=x['url'],final_url=x['url'],document_date=x['date'],date_precision='day',date_unknown_reason=None,version_label='Özgün yayımlanan HTML',accessed_at=x['accessed_at'],verified_at=when,mime='text/html',sha256=x['sha256'],original_path=x['original_path'],readable_path=x['readable_path'])
 add('archive_view',**x['view']);add('source_attribution',version_id=vid,publisher=publisher,author=None,kind=kind,published_at=x['date'],date_precision='day',social_handle=None,public_url=x['url'],basis='Özgün yayın gövdesi; tarih ve yayıncı sayfada incelendi.')
 add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=enc([section]),inspected_at=when))
 records['practice_attempt_v2'].append(dict(id=q(key+'-reading'),scope_id=scope,attempted_at=when,query='1–2 Kasım 2025 Ankara demokrasi barış çalıştayı altı düzenleyici',url=x['url'],result='examined',reason='Ortak düzenleme ve iki gün incelendi; 3 Kasım parti sayfasının yayın tarihidir, ilk açıklanma veya politika uygulaması sonucu değildir.',source_version_id=vid))
event=q('event');finding=q('finding');contribution=q('contribution');pids=[q('dem-passage'),q('ilke-passage')]
add('finding',id=finding,party_id='dem',heading='Belgelenmiş uygulamalar',pair_id=finding,text='DEM Parti, EHP, EMEP, SMF, TİP ve TÖP 1–2 Kasım 2025’te Ankara’da Demokrasi ve Barış çalıştayını ortak düzenledi. 2 Kasım tarihli haber toplantının ikinci gününde sürdüğünü bildirdi; DEM Parti 3 Kasım’da ortak sonuç metnini yayımladı. Metnin yayımlanması önerilerin uygulandığını göstermez.',provenance='summary',epistemic_type='claim')
records['practice_event'].append(dict(id=event,common_event_key='ankara-2025-11-01-02-demokrasi-baris-calistayi',event_at='2025-11-01',date_precision='day',date_unknown_reason=None,title='Ankara Demokrasi ve Barış Çalıştayı',scope_context='DEM Parti, EHP, EMEP, SMF, TİP ve TÖP tarafından Ankara’da 1–2 Kasım 2025’te düzenlenen ortak çalıştay.',occurrence_basis='DEM 3 Kasım ortak metni ve İlke TV 2 Kasım ikinci gün haberi.'))
for key,stage in [('dem','initiative'),('ilke','action')]:
 pid=q(key+'-passage');add('finding_evidence',finding_id=finding,passage_id=pid,role='support');add('verification',finding_id=finding,passage_id=pid,checked_at=when,result='confirmed',reason='Ortak düzenleme ve ikinci gün farklı yayınlarda kontrol edildi.')
 records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=anchors[key][1],stage=stage,concrete_basis='DEM ortak sonuç metni' if key=='dem' else '2 Kasım İlke TV haber gövdesi',limitation='Ortak sonuç metni uygulamanın gerçekleştiğini göstermez; ilk açıklanma tarihi 3 Kasım olarak varsayılmaz.',epistemic_type='claim'))
 records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='İki günlük ortak olay, 3 Kasım parti yayını ve uygulama sonucu ayrı tutuldu.')
records['practice_contribution'].append(dict(id=contribution,event_id=event,party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM’in altı düzenleyiciden biri olarak kurumsal katkısı; ortak metin gerçekleşmiş politika sayılmaz.'))
records['practice_candidate'].append(dict(id=q('candidate'),scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='Önceki bağımsız DEM söylemiyle özgül eşleşme ayrıca araştırılmalı; sonuç metni politika uygulaması değildir.',passage_ids=enc(pids)))
pkg['entries']+=entries
for k,v in records.items():pkg['practice_records'].setdefault(k,[]).extend(v)
snap=Path('/work/mg551/gsd-phase04-previews.sgFrq4/gsd-0406-dem-iklim-komisyon-katilim-62587929/releases/89e2ca8fd5364ceab8b52ac8c5551ca9/records.json');data=json.loads(snap.read_text())
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items():data.setdefault(k,[]).extend(v)
validate_practices(data);print('SEMANTIC_PASS',flush=True)
newp=[e['values']['id'] for e in entries if e['kind']=='passage'];targets=practice_review_package_targets(data,records,newp,'dem');allp={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old;refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({allp[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({allp[x]['section'] for x in refs})),supported_claim='Ankara iki günlük ortak çalıştay: '+kind+' / '+ident,limitations='3 Kasım yayımdır; ortak metin uygulama değildir.',result='reviewed',reason='Parti sonuç metni ve 2 Kasım haber gövdesi okundu.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='dem');review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('ankara-workshop-dem-draft.json',pkg),('ankara-workshop-dem-review-draft.json',review)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f),flush=True)
