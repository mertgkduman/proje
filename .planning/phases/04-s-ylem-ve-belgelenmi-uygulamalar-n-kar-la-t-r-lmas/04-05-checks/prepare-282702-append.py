import hashlib, json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from uygulamalar import practice_review_targets

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); root=Path('data/practices/sources/tip')
live=Path('data/practices/04-tip.json'); rev=Path('data/practices/04-tip-review.json')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(live)=='080069555877b7a970dc54f6e7fda4079b8c7e0f1fa32c33126869b669820899'
assert sha(rev)=='104e86b8ebe5a2cb6fb0f7ec90ee8b23f13d09589926a26aa9dd089145dbf710'
pkg=json.loads(live.read_text()); review=json.loads(rev.read_text()); now=datetime.now(timezone.utc).isoformat(); entries=[]; records={}
def add(k,v): entries.append({'kind':k,'values':v})
def rec(k,v): records.setdefault(k,[]).append(v)

cap=json.loads((p/'20241106-bas-capture.json').read_text()); h=cap['sha256']; raw=(root/'objects'/h/'original.html.bin').read_bytes(); text=html_source_text(raw); doc='0405-tip-20241106-bas'; vid=doc+'-v1'; url=cap['url']
assert sha(root/'objects'/h/'original.html.bin')==h
add('document',dict(id=doc,party_id='tip',title='TİP Genel Başkanı Baş’ın basın toplantısı',source_kind='official'))
add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date='2024-11-06',version_label='TBMM haberi',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='text/html',sha256=h,original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',date_precision='day',date_unknown_reason=None))
add('archive_view',cap['view']); add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at='2024-11-06',date_precision='day',public_url=url,basis='TBMM haberinin tarih, unvan ve aktarılmış konuşma bölümü okundu.'))
authority='Türkiye İşçi Partisi (TİP) Genel Başkanı Erkan Baş'
quote="Mardin'de, Esenyurt'ta, Batman'da, Halfeti'de halkın iradesi yok mu?"
for suf,exact,section in [('authority',authority,'Tarihli kişi ve temsil görevi'),('quote',quote,'Baş’ın aktarılan sorusu')]:
 assert exact in text
 add('passage',dict(id=doc+'-'+suf+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))

cap=json.loads((p/'tbmm-282702-capture.json').read_text()); h=cap['sha256']; pdf=root/'objects'/h/'original.pdf'; raw=pdf.read_bytes(); assert sha(pdf)==h
readable=pdf.parent/'readable.html'; rb=readable_bytes(raw,'pdf',legacy=False)
if readable.exists(): assert readable.read_bytes()==rb
else: readable.write_bytes(rb)
doc='0405-tip-282702'; vid=doc+'-v1'; url=cap['url']
add('document',dict(id=doc,party_id='tip',title='28. dönem 2/2702 ortak belediye kanunu teklifi',source_kind='official'))
add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date='2024-11-21',version_label='TBMM ortak imzalı teklif',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='application/pdf',sha256=h,original_path=f'objects/{h}/original.pdf',readable_path=f'objects/{h}/readable.html',date_precision='day',date_unknown_reason=None))
add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='On dokuz sayfa: CHP grup sunuşu, farklı parti imzaları, gerekçe ve teklif maddeleri okundu.'))
for suf,index,exact,section in [('presenter',0,'CUMHURİYET HALK PARTİSİ\nGrup Başkanlığı','CHP grup sunuşu'),('signatures',11,'Erkan BAŞ\nTürkiye İşçi Partisi\nİstanbuİ Milletvekili\nSallha Sera KADİGİL\nAhmet ŞIK\nTürkiye İşçi Partisi Türkiye İşçi Partisi','TİP ortak imzacıları; metin katmanında Saliha adı Sallha okunmuş'),('measure',18,'3/7/2005 tarihli ve 5393 sayılı Belediye Kanununun 45 inci maddesinin ikinci\nfıkrası yürürlükten kaldırılmıştır.','Birinci madde'),('date',1,'Tarih; 21-11-2024 Esas No:2/2702','TBMM kayıt kaşesi')]:
 assert exact in pdf_page_text(pdf,index)
 add('passage',dict(id=doc+'-'+suf+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=index,printed_page=None))

prefix='0405-tip-kayyum'; ev=prefix+'-282702-event'; statement=prefix+'-statement'; relation=prefix+'-relation'; contribution=prefix+'-contribution'; a='0405-tip-20241106-bas-authority-p'; q='0405-tip-20241106-bas-quote-p'; presenter=doc+'-presenter-p'; sign=doc+'-signatures-p'; measure=doc+'-measure-p'; stamp=doc+'-date-p'
add('actor',dict(id=prefix+'-bas',kind='authorized_representative',party_id='tip',person_id='0405-tip-erkan-bas',authorization_passage_id=a))
findings=[(prefix+'-summary','TBMM haberine göre TİP Genel Başkanı Baş, görevden uzaklaştırılan belediye başkanları bağlamında seçmen iradesini sorguladı.','summary',[q,a]),(prefix+'-quote',quote,'quote',[q]),(prefix+'-initiative','Baş, Kadıgil ve Şık, CHP Grup Başkanlığınca sunulan ve başka partilerden imzacılar da içeren 2/2702 ortak teklifini imzaladı; teklif 5393 sayılı Kanunun 45. maddesinin ikinci fıkrasının kaldırılmasını öngördü.','summary',[presenter,sign,measure,stamp]),(prefix+'-explanation','Baş’ın Kasım başında aktarılan belediye başkanlarının uzaklaştırılması ve halk iradesine ilişkin sorusu ile daha sonra ortak imzalanan 45/2 teklifi yerel temsil konusuyla ilişkilidir. Söz belirli madde değişikliği sözü değildir; teklifin kabulü gösterilmemiştir.','summary',[a,q,presenter,sign,measure,stamp])]
for fid,value,prov,refs in findings:
 add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=statement if fid in (prefix+'-summary',prefix+'-quote') else fid,text=value,provenance=prov,epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='quotation' if prov=='quote' else 'support'))
  add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Tarihli metin, imza ve kapsam bağlamı kaynaktan okundu.'))
 add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Ortak imza, atıflı söz ve teklif kapsamı ayrıldı.'))
inv=json.loads(Path('data/practices/04-inventory.json').read_text())
for kind in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='tip' and x['topic_id']=='yerel-demokrasi' and x['research_kind']==kind)
 rec('practice_scope_v2',dict(id=cell['cell_id'],party_id='tip',topic_id='yerel-demokrasi',taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='Seçili iki kaynak incelendi; diğer dönem ve uçlar açık.'))
 if kind=='event': scope=cell['cell_id']
rec('practice_event',dict(id=ev,common_event_key='tbmm-28-3-2-2702-belediye-45',event_at='2024-11-21',date_precision='day',date_unknown_reason=None,scope_context='28. dönem ortak belediye kanunu teklifi',title='Belediye görevlendirme hükmüne ortak teklif',occurrence_basis='TBMM 2/2702 imzalı teklif ve kayıt kaşesi.'))
for pid,point in [(sign,'TİP imzacılarının adı ve parti kimliği'),(measure,'5393/45 ikinci fıkranın kaldırılması önerisi'),(stamp,'21 Kasım 2024 başkanlık kaydı')]:
 rec('practice_event_evidence',dict(event_id=ev,passage_id=pid,supported_point=point,stage='initiative',concrete_basis='TBMM özgün teklifinin ilgili sayfası.',limitation='Ortak teklifin sunulması kabul veya belediyelerde gerçekleşmiş sonuç değildir.',epistemic_type='claim'))
 rec('practice_evidence_assessment',dict(event_id=ev,passage_id=pid,stage='initiative',basis_kind='document'))
rec('practice_contribution',dict(id=contribution,event_id=ev,party_id='tip',actor_id=prefix+'-bas',contribution_kind='task',finding_id=prefix+'-initiative',authority_passage_id=a,membership_passage_id=None,responsibility_limit='Baş çok partili teklifin TİP ortak imzacılarındandır; sunuş CHP grubu adına ve kabul yetkisi TBMM’dedir.'))
rec('practice_actor_period',dict(contribution_id=contribution,valid_from='2024-11-06',valid_to='2024-11-21',identity_passage_id=a))
rec('practice_statement',dict(id=statement,party_id='tip',topic_id='yerel-demokrasi',taxonomy_version=4,summary_finding_id=prefix+'-summary',quote_finding_id=prefix+'-quote',statement_at='2024-11-06',date_precision='day',version_id='0405-tip-20241106-bas-v1',period_basis='TBMM haberinin 6 Kasım tarihli basın toplantısı.',uncertainty_reason='Haber aktarımıdır; tam toplantı dökümü değildir.',comparison_row_id='04-03-v3-0304-tip-program-yerel-demokrasi-row'))
rec('practice_relation',dict(id=relation,statement_id=statement,event_id=ev,party_id='tip',topic_id='yerel-demokrasi',scope_id=scope,comparability_reason='Her iki kaynak yerel seçilmişlerin görevden uzaklaştırılmasıyla ilgilidir; söz ve 45/2 somut teklifi aynı kapsamda değildir.',target_finding_id=prefix+'-summary',result_finding_id=None,explanation_finding_id=prefix+'-explanation',temporal_context='6 Kasım haberindeki söz ve 21 Kasım ortak teklif ayrı tarihlerdedir.',authority_context='Milletvekilleri teklif sunar; kanun kabulü TBMM yetkisindedir.',uncertainty_reason='Teklifin kesim anındaki aşaması ve sonucu ayrıca araştırılmalıdır.'))
pkg['entries'].extend(entries)
for k,rows in records.items():pkg['practice_records'].setdefault(k,[]).extend(rows)
data={k:list(v) for k,v in pkg['practice_records'].items()}
for entry in pkg['entries']: data.setdefault(entry['kind'],[]).append(entry['values'])
db=sqlite3.connect('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.sqlite3');db.row_factory=sqlite3.Row
for name in ('finding_evidence','passage'):data.setdefault(name,[]).extend(dict(x) for x in db.execute('SELECT * FROM '+name))
versions={x['id']:x['version_id'] for x in data['passage']}; targets=practice_review_targets(data,records)
for (kind,identity),(refs,parties) in targets.items():
 row=dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({versions[x] for x in refs})),passage_ids=json.dumps(sorted(refs)),inspected_sections=json.dumps(['6 Kasım TBMM haberinde atıflı açıklama ve unvan','2/2702 imzaları, kaşe ve birinci madde'],ensure_ascii=False),supported_claim='İlgili söylem, ortak imza ve madde önerisi tarih ve görev bağlamıyla incelendi: '+identity,limitations='İlk söz özel 45/2 hükmü için taahhüt değildir; teklif kabulü ve kesim aşaması gösterilmedi.',result='reviewed',reason='Bu hedefe bağlı özgün pasajlar incelendi: '+kind+' '+identity)
 review['practice_source_review'].append(row);review['source_review_refs'].append(dict(subject_kind=kind,subject_id=identity))
for name,obj in [('282702-append-draft.json',pkg),('282702-review-draft.json',review)]:(p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries),len(targets))
