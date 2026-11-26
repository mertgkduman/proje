"""Prepare two separate November events from shared, byte-checked sources."""
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, 'src')
import uygulamalar as rules
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(__file__).resolve().parent
shared = checks.parent / '04-11-checks'
working = Path('data/practices')
root = working / 'sources/demokrat'
case = '0412-six-leaders-2022-11-28'
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sha = lambda raw: hashlib.sha256(raw).hexdigest()
read = lambda p: json.loads(p.read_bytes())
pair = (working / '04-demokrat.json', working / '04-demokrat-review.json')
expected = ('486c4f736ab03cab9e7ee52e57339d56ce4c07deec5045719ca0d579383cfe1a', '3b6d03e6c7870b28e0f054c63e6c21f991008d70209cb829a032d881174b5fae')
assert tuple(sha(p.read_bytes()) for p in pair) == expected, 'live pair changed; rebase needed'
package, review = map(read, pair)
entries, records = package['entries'], package['practice_records']
assert [len(records[k]) for k in ('practice_event','practice_relation','practice_closure')] == [81,52,0]
insert = lambda kind, row: entries.append(dict(kind=kind, values=row))
def add(table, **row): records[table].append(row)
def vid(name): return f'{case}-{name}-v1'
def pid(name): return f'{case}-{name}-p'
sources = {
 'plan': ('six-leaders-2022-11-14-karar-original.html', 'https://www.karar.com/guncel-haberler/altili-masadan-mutabakat-metni-aciklamasi-28-kasimda-kamuoyuna-1705091', 'Karar', '2022-11-14', '2026-11-26T02:27:17.219775+00:00', '66eb93bd6f0af003e6043d0053105815f5adcdeb351bf09500386afa6f660f59'),
 'meeting': ('six-leaders-2022-11-28-meeting-original.html', 'https://www.sondakika.com/guncel/haber-altili-masa-nin-9-toplantisi-6-saat-surdu-15459327/', 'Son Dakika / İhlas Haber Ajansı', '2022-11-28', '2026-11-25T23:24:20.365561+00:00', '8b2d283fd2a306af8e7b97e11558b0737210021bad5c9bc886b47ece87870f39'),
 'presentation': ('six-leaders-2022-11-28-voa-original.html', 'https://www.voaturkce.com/a/altili-masa-anayasa-degisikligini-tanitti/6853087.html', 'VOA Türkçe', '2022-11-28', '2026-11-25T23:24:19.881559+00:00', '820cc3c0a298eeaea8606f82b32ab24b3fbf9210d6f28790932160cc39ef4a65'),
 'presentation-role': ('six-leaders-2022-11-28-haberimizvar-original.html', 'https://www.haberimizvar.net/iste-millet-ittifakinin-anayasa-taslagi-2544164', 'Haberimizvar', '2022-11-28', datetime.fromtimestamp((checks/'six-leaders-2022-11-28-haberimizvar-original.html').stat().st_mtime,timezone.utc).isoformat(), '636da081b4b76da903cc2f532500382753f0a5ca5ba6623cd11c5757fb4a8999')}
def store(path, raw):
 dest = root / path; dest.parent.mkdir(parents=True, exist_ok=True)
 if dest.exists(): assert dest.read_bytes() == raw
 else: dest.write_bytes(raw)
for name, (filename, url, publisher, day, accessed, digest) in sources.items():
 path=checks/filename if name=='presentation-role' else shared/filename
 raw = path.read_bytes(); assert sha(raw) == digest
 folder = Path('objects') / digest; original = folder / 'original.html.bin'; readable = folder / 'readable.html'
 store(original,raw); store(readable,readable_bytes(raw,'html'))
 document = f'{case}-{name}'
 kind='journalism'
 insert('document', dict(id=document, party_id='demokrat', title=f'{day} {publisher} yayımı', source_kind=kind))
 insert('document_version', dict(id=vid(name), document_id=document, original_url=url, final_url=url, document_date=day, date_precision='day', date_unknown_reason=None, version_label=f'{day} {publisher} haberi', accessed_at=accessed, verified_at=now, mime='text/html', sha256=digest, original_path=str(original), readable_path=str(readable)))
 insert('source_attribution', dict(version_id=vid(name), kind='party_publication' if kind=='party' else 'journalism', publisher=publisher, author='Yıldız Yazıcıoğlu ve Murat Karabulut' if name == 'presentation' else None, social_handle=None, published_at=day, date_precision='day', public_url=url, basis='Tarihli yayımın ilgili olay ve ortak açıklama pasajları.'))
 view=build_view(raw,url,root,fetch_assets=False); validate_view(root,view); insert('archive_view',dict(view,version_id=vid(name)))
specs = {
 'meeting-plan': ('plan', 'Altılı Masanın bir sonraki liderler buluşması 28 Kasım 2022 tarihinde Demokrat Parti’nin ev sahipliğinde gerçekleştirilecektir.', '14 Kasım ortak açıklamasında DP ev sahipliği planı'),
 'presentation-plan': ('plan', 'bu çalışmayı 28 Kasım tarihinde kamuoyuyla paylaşma kararı aldık.', '14 Kasım ortak açıklamasında anayasa önerisinin paylaşılması planı'),
 'meeting-role': ('meeting', "Gültekin Uysal</a>'ın ev sahipliğinde Demokrat Parti Genel Merkezi'nde gerçekleştirildi.", 'İHA haberinde Uysal ev sahipliğinde DP genel merkezi toplantısı'),
 'presentation-role': ('presentation-role', 'Demokrat Parti Genel Başkanı&nbsp;Gültekin Uysal<strong>, </strong>Saadet Partisi Genel Başkanı<strong>&nbsp;</strong>Temel Karamollaoğlu<strong>,</strong> DEVA Partisi Genel Başkanı<strong>&nbsp;</strong>Ali Babacan&nbsp;ve Gelecek Partisi Genel Başkanı&nbsp;Ahmet Davutoğlu&nbsp;katıldı', 'Haberimizvar haberinde Uysal’ın katılımı'),
 'presentation-independent': ('presentation', 'teklif metni tanıtım toplantısı Bilkent Oteli’nde yapıldı.', 'VOA haberinde Bilkent tanıtımı')}
passages={}
for name,(source,exact,section) in specs.items():
 path=checks/sources[source][0] if source=='presentation-role' else shared/sources[source][0]
 raw=path.read_bytes(); assert exact in html_source_text(raw), name
 row=dict(id=pid(name),version_id=vid(source),exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
 insert('passage',row); passages[name]=row
scopes={r['research_kind']:r['cell_id'] for r in read(working/'04-inventory.json')['cells'] if (r['party_id'],r['topic_id']) == ('demokrat','siyasal-ittifaklar')}
assert set(scopes)=={'event','statement'}
for name,(_,url,_,_,_,_) in sources.items():
 scope=scopes['statement' if name=='plan' else 'event']; v=vid(name)
 sections=[r['section'] for r in passages.values() if r['version_id']==v]; attempt=f'{v}-reading'
 add('practice_scope_source',scope_id=scope,version_id=v,inspected_at=now,inspected_sections=json.dumps(sections,ensure_ascii=False))
 add('practice_attempt_v2',id=attempt,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='İlgili olay ve ortak açıklama pasajları incelendi.',source_version_id=v)
 add('practice_lead',id=f'lead-{attempt}',scope_id=scope,url=url,relevance_reason='14 ve 28 Kasım ortak plan ve ayrı toplantılar.',state='examined',attempt_ids=json.dumps([attempt]))
bounds='Ortak açıklama ve haberler sınırlı bağlamda okunmuştur. Tanıtım kabul edilmiş anayasa değişikliği değildir; kapalı toplantıdaki tekil konuşmalar ve imzaların bireysel kimliği belirlenmemiştir.'
def finding(suffix, text, ref, quote=False, pair_id=None):
 ident=f'{case}-{suffix}'
 refs=ref if isinstance(ref,tuple) else (ref,)
 insert('finding',dict(id=ident,party_id='demokrat',heading='Belgelenmiş uygulamalar',pair_id=pair_id or ident,text=text,provenance='quote' if quote else 'summary',epistemic_type='claim'))
 insert('review',dict(id=f'review-{ident}',kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='İlgili pasajlar incelendi.'))
 for ref in refs:
  insert('finding_evidence',dict(finding_id=ident,passage_id=pid(ref),role='quotation' if quote else 'support'))
  insert('verification',dict(finding_id=ident,passage_id=pid(ref),checked_at=now,result='confirmed',reason=passages[ref]['section']))
 return ident
events=[
 ('meeting','six-leaders-2022-11-28-dp-meeting','Altı liderin Demokrat Parti ev sahipliğindeki toplantısı','Altı siyasi parti liderinin 28 Kasım 2022 tarihinde Demokrat Parti Genel Merkezindeki toplantısı.','28 Kasım 2022’de Demokrat Parti Genel Merkezinde altı liderin yaptığı toplantıyı DEVA Partisinin 28. sayı bültenindeki ortak açıklama ve İHA haberi belgeliyor.','14 Kasım ortak açıklamasında 28 Kasım liderler toplantısına Demokrat Parti’nin ev sahipliği yapacağı duyuruldu.','28 Kasım’da altı lider Demokrat Parti Genel Merkezinde Gültekin Uysal’ın ev sahipliğinde toplandı.'),
 ('presentation','six-party-2022-11-28-constitutional-proposal-presentation','Altı partinin anayasa değişikliği önerisini kamuoyuna tanıtması','Altı siyasi partinin 28 Kasım 2022 tarihinde Ankara Bilkent Otel’de anayasa değişikliği önerisini tanıtması.','28 Kasım 2022’de Ankara Bilkent Otel’de altı liderin katıldığı tanıtım toplantısını CHP yayımı ve VOA Türkçe haberi belgeliyor. DEVA Partisinin 28. sayı bültenindeki ortak açıklama, önerinin liderler toplantısından önce tanıtıldığını doğruluyor.','14 Kasım ortak açıklamasında anayasa çalışmasının 28 Kasım’da kamuoyuyla paylaşılacağı belirtildi.','28 Kasım’da altı partinin anayasa önerisi Bilkent Otel’de tanıtıldı; Gültekin Uysal toplantıya katıldı.')]
for name,key,title,context,basis,announced,result_text in events:
 plan=f'{name}-plan'; role=f'{name}-role'; statement_summary=finding(f'{name}-statement-summary',announced,plan); quote=finding(f'{name}-statement-quote',passages[plan]['exact'],plan,True,statement_summary)
 statement=f'{case}-{name}-statement'
 add('practice_statement',id=statement,party_id='demokrat',topic_id='siyasal-ittifaklar',taxonomy_version=4,summary_finding_id=statement_summary,quote_finding_id=quote,statement_at='2022-11-14',date_precision='day',version_id=vid('plan'),period_basis='14 Kasım altı genel başkan ortak açıklamasının Karar haberindeki aktarımı.',comparison_row_id='04-03-v3-0313-demokrat-siyasal-ittifaklar',uncertainty_reason=bounds)
 event=f'{case}-{name}-event'; relation=f'{case}-{name}-relation'
 add('practice_event',id=event,common_event_key=key,event_at='2022-11-28',date_precision='day',date_unknown_reason=None,title=title,scope_context=context,occurrence_basis=basis)
 occurrence='presentation-independent' if name=='presentation' else role
 outcome='Bilkent Otel’de anayasa önerisi tanıtıldı.' if name=='presentation' else result_text
 for stage in ('action','result'):
  add('practice_event_evidence',event_id=event,passage_id=pid(occurrence),stage=stage,supported_point=outcome,concrete_basis=passages[occurrence]['section'],limitation=bounds,epistemic_type='claim')
  add('practice_evidence_assessment',event_id=event,passage_id=pid(occurrence),stage=stage,basis_kind='independent_report')
 result=finding(f'{name}-result',result_text,(role,occurrence) if role!=occurrence else role); explanation=finding(f'{name}-comparison',announced+' '+result_text,(plan,role,occurrence) if role!=occurrence else (plan,role))
 add('practice_relation',id=relation,party_id='demokrat',topic_id='siyasal-ittifaklar',scope_id=scopes['event'],statement_id=statement,event_id=event,target_finding_id=statement_summary,result_finding_id=result,explanation_finding_id=explanation,comparability_reason='14 Kasım ortak açıklaması ile 28 Kasım haberi aynı ayrı etkinliği gösterir.',temporal_context='14 Kasım plan, 28 Kasım gerçekleşme.',authority_context='Altı parti ortak çalışma yürüttü; Demokrat Parti Uysal ile temsil edildi.',uncertainty_reason=bounds)
 add('practice_candidate',id=f'{case}-{name}-candidate',scope_id=scopes['event'],event_id=event,relation_id=relation,state='eligible',reason='Tarihli ortak plan ve gerçekleşme haberi mevcut.',passage_ids=json.dumps([pid(occurrence)]))
 actor='0412-six-leaders-2022-dp-uysal-actor'; contribution=f'{case}-{name}-uysal-contribution'; rolefinding=finding(f'{name}-uysal-role',result_text,(role,occurrence) if role!=occurrence else role)
 add('practice_contribution',id=contribution,event_id=event,party_id='demokrat',actor_id=actor,contribution_kind='task',finding_id=rolefinding,authority_passage_id='0412-six-leaders-2022-dp-uysal-p',membership_passage_id=None,responsibility_limit=bounds)
 add('practice_actor_period',contribution_id=contribution,valid_from='2022-11-28',valid_to='2022-11-28',identity_passage_id=pid(role))
snapshot=read(Path('data/releases')/package['base_release']/'records.json')
for entry in entries:
 rows=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in rows: rows.append(entry['values'])
snapshot['practice_contract']=records['practice_contract']
for table,rows in records.items():
 target=snapshot.setdefault(table,[]); target.extend(row for row in rows if row not in target)
rules.validate_practices(snapshot)
targets=rules.practice_review_package_targets(snapshot,records,{r['values']['id'] for r in entries if r['kind']=='passage'},party_id='demokrat')
by_id={r['id']:r for r in snapshot['passage']}; reviews=review['practice_source_review']; existing={(r['subject_kind'],r['subject_id']) for r in reviews}; assert existing <= targets.keys()
for kind,ident in sorted(targets.keys()-existing):
 refs,_=targets[kind,ident]; inspected=[by_id[r] for r in sorted(refs)]
 reviews.append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({r['version_id'] for r in inspected})),passage_ids=json.dumps([r['id'] for r in inspected]),inspected_sections=json.dumps(sorted({r['section'] for r in inspected}),ensure_ascii=False),supported_claim=f'{kind} {ident}: '+' '.join(r['section'] for r in inspected),limitations=bounds,result='reviewed',reason='İlgili dar kapsamlı haber ve ortak açıklama pasajları okundu.'))
rules.validate_practice_source_review(snapshot,reviews,party_id='demokrat',target_keys=set(targets))
references=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
for payload in (package,review): payload['source_review_refs']=references
for suffix,payload in (('draft',package),('review-draft',review)):
 with (checks/f'six-leaders-november-dp-v2-{suffix}.json').open('x') as f: json.dump(payload,f,ensure_ascii=False,indent=2); f.write('\n')
print('DEMOCRAT_NOVEMBER_SEMANTIC_OK',len(records['practice_event']),len(records['practice_relation']))
