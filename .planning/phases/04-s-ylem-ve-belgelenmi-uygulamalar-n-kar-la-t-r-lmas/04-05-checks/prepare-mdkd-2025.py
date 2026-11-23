import hashlib, json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import pdf_page_text
from uygulamalar import practice_review_targets

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
root = Path('data/practices/sources/tip')
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
live, rev = Path('data/practices/04-tip.json'), Path('data/practices/04-tip-review.json')
assert sha(live) == '1ced429d942264dc591e78dc50dc4df31141b32740e10f173da0a7cb2a03fe99'
assert sha(rev) == '5d6450239cc992a580e124d2dab0c61543d148fca562978b08f235fd52681a93'
pkg, review = json.loads(live.read_text()), json.loads(rev.read_text())
now = datetime.now(timezone.utc).isoformat()
entries, records = [], {}
def add(kind, values): entries.append(dict(kind=kind, values=values))
def rec(kind, values): records.setdefault(kind, []).append(values)
cap = json.loads((p/'mdkd-5242-capture.json').read_text())
h, url = cap['sha256'], cap['url']
f = root/'objects'/h/'original.pdf'
assert h == '81cc3eb06e5703779c9d3e290b1db379e1edca5d0e6419e573beab6e589f1755' and sha(f) == h
doc = '0405-tip-mdkd-20250805'; vid = doc+'-v1'; prefix = '0405-tip-mdkd-usul'
add('document', dict(id=doc, party_id='tip', title='TBMM MDKD Komisyonu ilk toplantı incelenmemiş tutanağı', source_kind='official'))
add('document_version', dict(id=vid, document_id=doc, original_url=url, final_url=url, document_date='2025-08-05', version_label='İlk toplantı incelenmemiş tutanağı', accessed_at=cap['accessed_at'], verified_at=cap['accessed_at'], mime='application/pdf', sha256=h, original_path=f'objects/{h}/original.pdf', readable_path=f'objects/{h}/readable.html', date_precision='day', date_unknown_reason=None))
add('source_attribution', dict(version_id=vid, kind='official', publisher='Türkiye Büyük Millet Meclisi', author=None, social_handle=None, published_at=None, date_precision='unknown', public_url=url, basis='95 sayfanın metni, 85 ve 93. indeksin görseli okundu; incelenmemiş tutanaktaki yinelenen konuşma bölümü ayrıca kaydedildi.'))
pieces=[('proposal',85,'3’te 2 karar mekanizmas ı yla'),('change',92,'üye tam say ı s ı n ı n be ş te 3’ü'),('decision',93,'Oy\nbirli ğ iyle kabul edilmi ş tir.')]
for suffix,index,exact in pieces:
 assert exact in pdf_page_text(f,index), suffix
 add('passage',dict(id=doc+'-'+suffix+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section='Şık önerisi veya başkanın komisyon kararı',pdf_page_index=index,printed_page=None))
prop,change,decision=[doc+'-'+x+'-p' for x in ('proposal','change','decision')]
oldname='0405-tip-mdkd-anka-20250805-identity-p'; oldcontext='0405-tip-mdkd-anka-20250805-context-p'
for suffix,text,refs in [('action','Şık, komisyon gündeminin üyelerce ve üçte iki karar mekanizmasıyla belirlenmesini istedi.',[prop,oldname]),('result','Başkan değişikliklerden sonra komisyon çalışma usul ve esaslarının oy birliğiyle kabul edildiğini duyurdu.',[change,decision]),('explanation','Şık’ın ad ve üçte iki önerileriyle, kabul duyurusu yapılan komisyon usul metni ayrı tutulur; tutanak incelenmemiştir ve kabul Genel Kurul yasası değildir.',[prop,change,decision,oldcontext])]:
 fid=prefix+'-'+suffix
 add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=fid,text=text,provenance='summary',epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='support'))
  add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='İncelenmemiş tutanak ve önerinin kaynak bağlamı ayrı değerlendirildi.'))
 add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Öneri ile kararın konusu ve kayıt sınırları ayrıldı.'))
ev=prefix+'-event'; rel=prefix+'-relation'; con=prefix+'-contribution'
rec('practice_event',dict(id=ev,common_event_key='tbmm-mdkd-komisyon-usul-2025-08-05',event_at='2025-08-05',date_precision='day',date_unknown_reason=None,scope_context='MDKD Komisyonu ilk toplantısı dördüncü ve beşinci oturumlar',title='Komisyonun çalışma usullerine Şık’ın önerisi ve kabul',occurrence_basis='TBMM ilk toplantı incelenmemiş tutanağı.'))
for pid,stage,point in [(prop,'action','Şık üçte iki karar mekanizmasını önerdi'),(change,'result','Revize metinde kanun teklifi için üye tam sayısının beşte üçü okundu'),(decision,'result','Başkan usul ve esasların oy birliğiyle kabul edildiğini duyurdu')]:
 rec('practice_event_evidence',dict(event_id=ev,passage_id=pid,supported_point=point,stage=stage,concrete_basis='TBMM incelenmemiş tutanağının ilgili sayfası.',limitation='İncelenmemiş tutanakta yinelenen konuşma bölümü vardır; komisyon kararı Genel Kurul yasası değildir.',epistemic_type='claim'))
 rec('practice_evidence_assessment',dict(event_id=ev,passage_id=pid,stage=stage,basis_kind='document'))
rec('practice_contribution',dict(id=con,event_id=ev,party_id='tip',actor_id='0405-tip-mdkd-sik',contribution_kind='objection',finding_id=prefix+'-action',authority_passage_id=oldname,membership_passage_id=None,responsibility_limit='Şık’ın taslağa itirazı, sözlü önerisi ve komisyonun kolektif kararı ayrı tutuldu.'))
rec('practice_actor_period',dict(contribution_id=con,valid_from='2025-08-05',valid_to='2025-08-05',identity_passage_id=oldname))
rec('practice_relation',dict(id=rel,statement_id='0405-tip-mdkd-statement',event_id=ev,party_id='tip',topic_id='kurt-sorunu',scope_id='practice-4127192b5dc84c207ff4a641151a75949a272089d63a8ecdb70fdaf09751dcd2',comparability_reason='Aynı toplantıda önce ad önerisi ardından usul itirazı ve komisyon kararı yer alır; ad ve karar mekanizması farklı unsurlardır.',target_finding_id='0405-tip-mdkd-summary',result_finding_id=prefix+'-result',explanation_finding_id=prefix+'-explanation',temporal_context='5 Ağustos 2025 ilk toplantısında ilk ad önerisi sonra usul görüşmesi ve oylama gerçekleşti.',authority_context='Şık TİP adına öneride bulundu; usul kabulü komisyonun ortak kararıdır.',uncertainty_reason='Tutanak incelenmemiştir; indeks 86–88 bölümünde tekrar ve konuşmacı etiketi sorunu bulunur.'))
pkg['entries'].extend(entries)
for k,rows in records.items(): pkg['practice_records'].setdefault(k,[]).extend(rows)
data={k:list(v) for k,v in pkg['practice_records'].items()}
for e in pkg['entries']: data.setdefault(e['kind'],[]).append(e['values'])
db=sqlite3.connect('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.sqlite3'); db.row_factory=sqlite3.Row
for k in ('finding_evidence','passage'): data.setdefault(k,[]).extend(dict(x) for x in db.execute('SELECT * FROM '+k))
versions={x['id']:x['version_id'] for x in data['passage']}
targets=practice_review_targets(data,records)
for (kind,identity),(ps,parties) in targets.items():
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({versions[x] for x in ps})),passage_ids=json.dumps(sorted(ps)),inspected_sections=json.dumps(['2025 ilk toplantı öneri ve usul kabulü','ANKA temsil ve ad önerisi'],ensure_ascii=False),supported_claim='Kaynaklarda ayrı öneri ve karar incelendi: '+identity,limitations='İncelenmemiş tutanakta tekrar var; Şık’ın bütün önerileri kabul edilmiş sayılmaz.',result='reviewed',reason='Hedefe bağlı özgün pasajlar okundu: '+kind+' '+identity))
 review['source_review_refs'].append(dict(subject_kind=kind,subject_id=identity))
for name,obj in [('mdkd-2025-append-draft.json',pkg),('mdkd-2025-review-draft.json',review)]: (p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries),len(targets))
