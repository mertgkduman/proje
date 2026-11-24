import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import practice_review_package_targets,validate_practice_source_review,validate_practices
c=Path(__file__).resolve().parent;root=c.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();enc=lambda x:json.dumps(x,ensure_ascii=False);q=lambda x:'0407-six-leaders-2022-'+x
base=root/'data/practices/04-iyi.json';rp=root/'data/practices/04-iyi-review.json';assert sha(base)=='5814587049d6af3f55d273eb8d2057af2cf2a22ae2ea3bc2051aac2453c148b1' and sha(rp)=='7eba5cdfb8a96ddd885d57450a06e01a64db5f27c991401c7dcea24d695fa028'
pkg,review=json.loads(base.read_text()),json.loads(rp.read_text());cap=json.loads((c/'six-leaders-2022-iyi-capture.json').read_text());when=datetime.datetime.now(datetime.timezone.utc).isoformat();scope='practice-9b28637c5a27901c18a5e7b6e92f1fc3fd3e84c85f73f38d858e8486d81aac44'
entries=[];records={k:[] for k in ('practice_scope_v2','practice_event','practice_event_evidence','practice_evidence_assessment','practice_contribution','practice_actor_period','practice_candidate','practice_scope_source','practice_attempt_v2')}
def add(category,**v):entries.append(dict(kind=category,values=v))
records['practice_scope_v2'].append(dict(id=scope,party_id='iyi',topic_id='demokrasi-katilim',taxonomy_version=4,period_start='2017-10-25',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='2 Ekim 2022 altı lider toplantısının dar aday zinciri; kapsam araştırması sürüyor.'))
anchors={
 'august':('2 Ekim 2022 Pazar günü saat 14.00’da CHP Genel Merkezinde','21 Ağustos ortak açıklamadaki duyuru'),
 'arrival':('Uysal’ın ardından sırasıyla saat 13.59’da Saadet Partisi Genel Başkanı Temel Karamollaoğlu, saat 14.02 Gelecek Partisi Ahmet Davutoğlu, saat 14.05’te DEVA Partisi Genel Başkanı Ahmet Babacan ve saat 14.10’da İYİ Parti Genel Başkanı Meral Akşener, CHP Genel Merkezi’ne ulaştı.','2 Ekim tarihli haber: katılım ve İYİ Parti başkanlığı'),
 'opening':("Saat 14.11’de başlayan görüşmenin CHP Genel Merkezi'nin, Genel Başkanlık katı olan 12. Katta yapıldığı öğrenildi.",'2 Ekim haberinde bildirilen fiilî başlangıç')}
for key in ('august','october'):
 x=cap[key];rawpath=root/'data/practices/sources/iyi'/x['original_path'];assert sha(rawpath)==x['sha256'];raw=html_source_text(rawpath.read_bytes());doc=q(key);vid=doc+'-v1'
 add('document',id=doc,party_id='iyi',title='21 Ağustos ortak açıklama ve katılım haberi' if key=='august' else '2 Ekim altı lider toplantısı haberi',source_kind='journalism')
 add('document_version',id=vid,document_id=doc,original_url=x['url'],final_url=x['url'],document_date=x['date'],date_precision='day',date_unknown_reason=None,version_label='Özgün haber HTML',accessed_at=x['accessed_at'],verified_at=when,mime='text/html',sha256=x['sha256'],original_path=x['original_path'],readable_path=x['readable_path'])
 add('archive_view',**x['view']);add('source_attribution',version_id=vid,publisher=x['publisher'],author=None,kind='journalism',published_at=x['date'],date_precision='day',social_handle=None,public_url=x['url'],basis='Karar ortak metni aktaran haber' if key=='august' else 'Independent Türkçe, ANKA imzalı toplantı haberi.')
 keys=('august',) if key=='august' else ('arrival','opening')
 for name in keys:
  exact,section=anchors[name];assert exact in raw,name;add('passage',id=q(name),version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=enc([anchors[n][1] for n in keys]),inspected_at=when))
 records['practice_attempt_v2'].append(dict(id=q(key+'-reading'),scope_id=scope,attempted_at=when,query='21 Ağustos duyurusu ve 2 Ekim 2022 altı lider İYİ Akşener CHP',url=x['url'],result='examined',reason='Önceki ortak duyuru, 2 Ekim Akşener parti sıfatı, varış ve fiilî başlangıç ayrı okundu.',source_version_id=vid))
event=q('event');finding=q('finding');contribution=q('contribution');person=q('aksener-person');actor=q('aksener-actor');pids=[q(k) for k in ('august','arrival','opening')]
add('person',id=person,name='Meral Akşener');add('actor',id=actor,kind='authorized_representative',party_id='iyi',person_id=person,authorization_passage_id=q('arrival'))
add('finding',id=finding,party_id='iyi',heading='Belgelenmiş uygulamalar',pair_id=finding,text='Altı liderin 21 Ağustos ortak açıklamasında 2 Ekim için saat 14.00’te CHP Genel Merkezinde toplantı duyuruldu. 2 Ekim tarihli Independent Türkçe/ANKA haberine göre İYİ Parti Genel Başkanı Meral Akşener merkeze 14.10’da ulaştı ve görüşme 14.11’de başladı. Bu toplantı ve açıklama, olası siyasal önerilerin uygulandığını göstermez.',provenance='summary',epistemic_type='claim')
records['practice_event'].append(dict(id=event,common_event_key='six-leaders-2022-10-02-chp-second-round-meeting',event_at='2022-10-02',date_precision='day',date_unknown_reason=None,title='Altı liderin CHP Genel Merkezindeki ikinci tur ilk toplantısı',scope_context='Altı siyasi parti liderinin 2 Ekim 2022 tarihinde CHP Genel Merkezindeki ikinci tur ilk toplantısı.',occurrence_basis='2 Ekim 2022’de CHP’nin ev sahipliğinde yapılan ikinci turun ilk toplantısını 2 Ekim ortak açıklaması ve Independent Türkçe’nin tarihli haberi belgeliyor. Katılımcılar arasında Temel Karamollaoğlu, Gültekin Uysal ve Meral Akşener vardı.'))
for key,stage in [('august','initiative'),('arrival','action'),('opening','action')]:
 pid=q(key);add('finding_evidence',finding_id=finding,passage_id=pid,role='support');add('verification',finding_id=finding,passage_id=pid,checked_at=when,result='confirmed',reason='21 Ağustos açıklaması ve 2 Ekim haberindeki ayrı süreç aşamaları okundu.')
 records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,supported_point=anchors[key][1],stage=stage,concrete_basis='Karar ortak açıklama aktarımı' if key=='august' else 'Independent Türkçe / ANKA 2 Ekim haberi',limitation='Duyurulan saat, fiilî başlangıç ve siyasal hedeflerin uygulanması ayrı hususlardır.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind='document'))
add('review',id='review-'+finding,kind='finding',subject_id=finding,reviewer_kind='agent',reviewed_at=when,result='reviewed',reason='İYİ başkanı sıfatı ve önceki plan ile fiilî toplantı ayrıldı.')
records['practice_contribution'].append(dict(id=contribution,event_id=event,party_id='iyi',actor_id=actor,contribution_kind='task',finding_id=finding,authority_passage_id=q('arrival'),membership_passage_id=None,responsibility_limit='Meral Akşener’in İYİ Parti genel başkanı sıfatıyla katılımı; ortak politika uygulaması veya bireysel oy çıkarılmaz.'))
records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2022-10-02',valid_to='2022-10-02',identity_passage_id=q('arrival')))
records['practice_candidate'].append(dict(id=q('candidate'),scope_id=scope,event_id=event,relation_id=None,state='unmatched',reason='21 Ağustos ortak duyurusu toplantı planını destekler; İYİ parti yayımlı önceki özgül söylem ayrıca aranacak ve ortak politika uygulaması varsayılmayacak.',passage_ids=enc(pids)))
pkg['entries']+=entries
for k,v in records.items():pkg['practice_records'].setdefault(k,[]).extend(v)
snap=root/'data/.staging/gsd-0407-agenda-104-historic-62503516/releases/4420d5b841494b8eae48b5d0dbafccaf/records.json';data=json.loads(snap.read_text())
for e in entries:data.setdefault(e['kind'],[]).append(e['values'])
for k,v in records.items():data.setdefault(k,[]).extend(v)
validate_practices(data);print('SEMANTIC_PASS',flush=True)
newp=[e['values']['id'] for e in entries if e['kind']=='passage'];targets=practice_review_package_targets(data,records,newp,'iyi');allp={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']}
for (kind,ident),(refs,owners) in targets.items():
 assert (kind,ident) not in old;refs=sorted(refs);review['practice_source_review'].append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=when,source_version_ids=enc(sorted({allp[x]['version_id'] for x in refs})),passage_ids=enc(refs),inspected_sections=enc(sorted({allp[x]['section'] for x in refs})),supported_claim='Altı lider toplantısı ve Akşener sıfatı: '+kind+' / '+ident,limitations='Plan, başlangıç ve politika uygulaması ayrı; haber aktarımları kaynak olarak gösterilir.',result='reviewed',reason='21 Ağustos ortak metin ve 2 Ekim haberi tarih ve aktör açısından karşılaştırıldı.'))
validate_practice_source_review(data,[x for x in review['practice_source_review'] if (x['subject_kind'],x['subject_id']) in targets],target_keys=targets,party_id='iyi');review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']];pkg['source_review_refs']=review['source_review_refs'];print('SOURCE_REVIEW_PASS',len(targets),flush=True)
for name,obj in [('six-leaders-2022-iyi-draft.json',pkg),('six-leaders-2022-iyi-review-draft.json',review)]:
 f=c/name;f.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n');print(name,sha(f),flush=True)
