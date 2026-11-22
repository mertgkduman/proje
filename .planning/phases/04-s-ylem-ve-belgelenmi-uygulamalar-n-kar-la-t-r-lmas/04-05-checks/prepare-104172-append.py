import hashlib,json,sqlite3,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text,pdf_page_exists
from uygulamalar import practice_review_targets
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks');root=Path('data/practices/sources/tip')
live=Path('data/practices/04-tip.json');rev=Path('data/practices/04-tip-review.json')
assert hashlib.sha256(live.read_bytes()).hexdigest()=='9320401d2e28485806487f798a278b56a6ce068c04d516a5abcb5fdec809ef41'
assert hashlib.sha256(rev.read_bytes()).hexdigest()=='dd52918493f7ec09198d854cb7548f9970b6b2cfbf85c49de80a2e9f34427915'
pkg=json.loads(live.read_text());review=json.loads(rev.read_text());now=datetime.now(timezone.utc).isoformat();entries=[];records={}
def add(k,v):entries.append(dict(kind=k,values=v))
def rec(k,v):records.setdefault(k,[]).append(v)
def html_doc(doc,title,date,quote,section,publisher):
 cap=json.loads((p/(doc+'-v1-capture.json')).read_text());h=cap['sha256'];url=cap['url'];raw=(root/'objects'/h/'original.html.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==h and quote in html_source_text(raw)
 add('document',dict(id=doc,party_id='tip',title=title,source_kind='official'))
 add('document_version',dict(id=doc+'-v1',document_id=doc,original_url=url,final_url=url,document_date=date,version_label='Özgün kaynak',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='text/html',sha256=h,original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',date_precision='day',date_unknown_reason=None))
 add('archive_view',cap['view']);add('source_attribution',dict(version_id=doc+'-v1',kind='official',publisher=publisher,author=None,social_handle=None,published_at=date,date_precision='day',public_url=url,basis='Tarihli özgün açıklama ve ilgili metin incelendi.'))
 add('passage',dict(id=doc+'-p',version_id=doc+'-v1',exact=quote,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))
html_doc('0405-tip-aliaga-2022','Ülkemiz Dünyanın Çöplüğü Değildir','2022-07-28','Gemi sökümünde çalışan işçilerin kendilerinin, ailelerinin rutin akciğer kontrolleri yapılmalıdır.','TİP bürolarının iş sağlığı istemi','Türkiye İşçi Partisi')
html_doc('0405-tip-bas-20260430','30 Nisan 2026 TİP basın toplantısı','2026-04-30','Türkiye İşçi Partisi (TİP) Genel Başkanı Erkan Baş','Tarihli genel başkan unvanı','Türkiye İşçi Partisi')
doc='0405-tip-104172';cap=json.loads((p/(doc+'-v1-capture.json')).read_text());h=cap['sha256'];url=cap['url'];pdf=root/'objects'/h/'original.pdf';assert hashlib.sha256(pdf.read_bytes()).hexdigest()==h
add('document',dict(id=doc,party_id='tip',title='10/4172 Aliağa ağır sanayide iş sağlığı araştırma önergesi',source_kind='official'))
add('document_version',dict(id=doc+'-v1',document_id=doc,original_url=url,final_url=url,document_date='2026-05-07',version_label='TBMM özgün imzalı tarama',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='application/pdf',sha256=h,original_path=f'objects/{h}/original.pdf',readable_path=f'objects/{h}/readable.html',date_precision='day',date_unknown_reason=None))
add('source_attribution',dict(version_id=doc+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Sekiz tarama sayfası görsel okundu; son sayfa cümle ortasında kesilir. Tarih ayrıca resmî ayrıntı kaydından kontrol edildi.'))
for suffix,index,exact,section in [('signature',1,'Erkan Baş','İmza cetvelinde TİP milletvekili'),('kadigil',1,'Saliha Sera Kadıgil','İmza cetvelinde TİP milletvekili'),('sik',1,'Ahmet Şık','İmza cetvelinde TİP milletvekili')]:
 assert pdf_page_exists(pdf,index) and pdf_page_text(pdf,index).strip() in ('','10/4172');pid=doc+'-'+suffix+'-p'
 add('passage',dict(id=pid,version_id=doc+'-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=index,printed_page=None));add('manual_passage',dict(passage_id=pid,checked_at=now,method='Özgün tarama sayfası Poppler ile görsel okundu.',reason='Belirtilen metin özgün sayfa görüntüsünden okundu; metin katmanı boştur.'))
doc2='0405-tip-104172-detail';cap=json.loads((p/(doc2+'-v1-capture.json')).read_text());h=cap['sha256'];url=cap['url'];raw=(root/'objects'/h/'original.html.bin').read_bytes();assert '07/05/2026' in html_source_text(raw)
add('document',dict(id=doc2,party_id='tip',title='TBMM 10/4172 işlem ayrıntısı',source_kind='official'))
add('document_version',dict(id=doc2+'-v1',document_id=doc2,original_url=url,final_url=url,document_date=None,version_label='TBMM işlem kaydı',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='text/html',sha256=h,original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',date_precision='unknown',date_unknown_reason='İşlem tarihi kayıttadır; sayfa yayın tarihi belirtilmemiştir.'))
add('archive_view',cap['view']);add('source_attribution',dict(version_id=doc2+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Başkanlığa geliş 7 Mayıs 2026; güncel aşama geçmiş kesim tarihine taşınmaz.'))
add('passage',dict(id=doc2+'-date-p',version_id=doc2+'-v1',exact='07/05/2026',prefix=None,suffix=None,article=None,section='Başkanlığa geliş tarihi',pdf_page_index=None,printed_page=None))
import re
source=html_source_text(raw)
purpose_text=re.search(r'Önergenin Özeti</b></td>\s*<td>(.*?)</td>',source,re.S).group(1)
bayhan_text=re.search(r'&#x130;skender BAYHAN</a></td>.*?İlk İmza Sahibi',source,re.S).group(0)
for suffix,exact,section in [('purpose',purpose_text,'Önergenin resmî özeti'),('bayhan',bayhan_text,'İlk imza sahibi')]:
 add('passage',dict(id=doc2+'-'+suffix+'-p',version_id=doc2+'-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))
prefix='0405-tip-aliaga';ev=prefix+'-104172-event';statement=prefix+'-statement';rel=prefix+'-relation';a='0405-tip-bas-20260430-p';q='0405-tip-aliaga-2022-p';purpose=doc2+'-purpose-p';sign=doc+'-signature-p';stamp=doc2+'-date-p'
add('actor',dict(id=prefix+'-bas',kind='authorized_representative',party_id='tip',person_id='0405-tip-erkan-bas',authorization_passage_id=a))
fs=[(prefix+'-summary','TİP, Aliağa gemi sökümünde çalışanların ve ailelerinin düzenli akciğer kontrollerini istedi.','summary',[q]),(prefix+'-quote','Gemi sökümünde çalışan işçilerin kendilerinin, ailelerinin rutin akciğer kontrolleri yapılmalıdır.','quote',[q]),(prefix+'-initiative','İskender Bayhan’ın ilk imzacısı olduğu 10/4172 çok partili Meclis araştırması önergesini Erkan Baş, Saliha Sera Kadıgil ve Ahmet Şık da imzaladı. Önerge, Aliağa ağır sanayisinde iş sağlığı ve güvenliği eksikliklerinin araştırılmasını istedi.','summary',[purpose,sign,doc+'-kadigil-p',doc+'-sik-p',doc2+'-bayhan-p',stamp]),(prefix+'-explanation','2022 açıklaması ile 2026 ortak araştırma önergesi Aliağa gemi sökümünde iş sağlığı sorunlarıyla ilişkilidir. Önerge, daha önce istenen sağlık kontrollerinin yapıldığını veya Meclis araştırmasının kabul edildiğini göstermez.','summary',[q,purpose,sign,stamp])]
for fid,value,prov,refs in fs:
 add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=statement if fid in (prefix+'-summary',prefix+'-quote') else fid,text=value,provenance=prov,epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='quotation' if prov=='quote' else 'support'));add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Kaynak ve olay kapsamı doğrudan incelendi.'))
 add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Ortak girişim ile sonuç ve önceki istem ayrıldı.'))
inv=json.loads(Path('data/practices/04-inventory.json').read_text())
for kind in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='tip' and x['topic_id']=='is-sagligi' and x['research_kind']==kind)
 rec('practice_scope_v2',dict(id=cell['cell_id'],party_id='tip',topic_id='is-sagligi',taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='Seçili Aliağa kaynakları okundu; diğer dönem ve uçlar açıktır.'))
 if kind=='event':scope=cell['cell_id']
rec('practice_event',dict(id=ev,common_event_key='tbmm-28-4-10-4172-aliaga-is-sagligi',event_at='2026-05-07',date_precision='day',date_unknown_reason=None,scope_context='28. dönem çok partili araştırma önergesi',title='Aliağa iş sağlığı araştırma önergesi',occurrence_basis='TBMM imzalı önerge ve geliş kaydı.'))
for pid,point in [(purpose,'Araştırma talebi'),(sign,'Erkan Baş ortak imzası'),(stamp,'Başkanlığa geliş tarihi')]:
 rec('practice_event_evidence',dict(event_id=ev,passage_id=pid,supported_point=point,stage='initiative',concrete_basis='TBMM resmî özgün belgesi.',limitation='Önergenin kabulü veya araştırma sonucu gösterilmemiştir.',epistemic_type='claim'));rec('practice_evidence_assessment',dict(event_id=ev,passage_id=pid,stage='initiative',basis_kind='document'))
con=prefix+'-contribution';rec('practice_contribution',dict(id=con,event_id=ev,party_id='tip',actor_id=prefix+'-bas',contribution_kind='task',finding_id=prefix+'-initiative',authority_passage_id=a,membership_passage_id=None,responsibility_limit='Baş ortak imzacıdır; ilk imzacı Bayhan, karar mercii TBMM’dir.'))
rec('practice_actor_period',dict(contribution_id=con,valid_from='2026-04-30',valid_to='2026-05-07',identity_passage_id=a))
rec('practice_statement',dict(id=statement,party_id='tip',topic_id='is-sagligi',taxonomy_version=4,summary_finding_id=prefix+'-summary',quote_finding_id=prefix+'-quote',statement_at='2022-07-28',date_precision='day',version_id='0405-tip-aliaga-2022-v1',period_basis='TİP’in 28 Temmuz 2022 tarihli açıklaması.',uncertainty_reason='Tek bir açıklama incelendi.',comparison_row_id='04-03-v3-0304-tip-program-issagligi-baglam-row'))
rec('practice_relation',dict(id=rel,statement_id=statement,event_id=ev,party_id='tip',topic_id='is-sagligi',scope_id=scope,comparability_reason='Her iki kaynak Aliağa gemi sökümü ve iş sağlığını ele alır; somut talepler birebir aynı değildir.',target_finding_id=prefix+'-summary',result_finding_id=None,explanation_finding_id=prefix+'-explanation',temporal_context='2022 büro açıklaması ve 2026 çok partili girişim ayrı tarihlidir.',authority_context='Meclis araştırması kararı TBMM yetkisindedir.',uncertainty_reason='Kesim anında önergenin aşaması ve sonucu gösterilmedi.'))
pkg['entries'].extend(entries)
for k,rows in records.items():pkg['practice_records'].setdefault(k,[]).extend(rows)
data={k:list(v) for k,v in pkg['practice_records'].items()}
for entry in pkg['entries']:data.setdefault(entry['kind'],[]).append(entry['values'])
db=sqlite3.connect('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.sqlite3');db.row_factory=sqlite3.Row
for name in ('finding_evidence','passage'):data.setdefault(name,[]).extend(dict(x) for x in db.execute('SELECT * FROM '+name))
versions={x['id']:x['version_id'] for x in data['passage']};targets=practice_review_targets(data,records)
for (kind,identity),(refs,parties) in targets.items():
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({versions[x] for x in refs})),passage_ids=json.dumps(sorted(refs)),inspected_sections=json.dumps(['2022 TİP açıklaması','2026 yetki açıklaması','10/4172 sayfa 0–7 taraması ve tarihli geliş kaydı'],ensure_ascii=False),supported_claim='Söylem ve araştırma girişiminin kaynak sınırları incelendi: '+identity,limitations='İmzalı PDF son cümlesi kesiktir; kabul ve sonuç gösterilmemiştir.',result='reviewed',reason='Bağlı özgün pasajlar doğrudan okundu: '+kind+' '+identity));review['source_review_refs'].append(dict(subject_kind=kind,subject_id=identity))
for name,obj in [('104172-append-draft.json',pkg),('104172-review-draft.json',review)]:(p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries),len(targets))
