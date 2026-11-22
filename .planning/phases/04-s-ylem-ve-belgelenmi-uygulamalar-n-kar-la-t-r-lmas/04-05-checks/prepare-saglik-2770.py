import hashlib,json,sqlite3,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text
from uygulamalar import practice_review_targets
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks');root=Path('data/practices/sources/tip');live=Path('data/practices/04-tip.json');rev=Path('data/practices/04-tip-review.json')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(live)=='84d54e77d0199ec190708ff7693d58c83799e7f081ceff483c902824ffcd08e9' and sha(rev)=='f8db09da39c34de0df5f83ffbb08955ee0bc48b85ec0cbe422be2639a4c7ccd4'
pkg=json.loads(live.read_text());review=json.loads(rev.read_text());now=datetime.now(timezone.utc).isoformat();entries=[];records={}
def add(k,v):entries.append(dict(kind=k,values=v))
def rec(k,v):records.setdefault(k,[]).append(v)
for filename,doc,title,date,kind,publisher in [('saglik-anka-capture.json','0405-tip-saglik-20241023-anka','ANKA Baş basın açıklaması','2024-10-23','journalism','ANKA Haber Ajansı'),('saglik-2770-detail-capture.json','0405-tip-2770-detail','TBMM 2/2770 teklif ayrıntısı',None,'official','Türkiye Büyük Millet Meclisi')]:
 cap=json.loads((p/filename).read_text());h=cap['sha256'];url=cap['url'];vid=doc+'-v1';raw=(root/'objects'/h/'original.html.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==h;t=html_source_text(raw)
 add('document',dict(id=doc,party_id='tip',title=title,source_kind=kind));add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,version_label=title,accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='text/html',sha256=h,original_path=f'objects/{h}/original.html.bin',readable_path=f'objects/{h}/readable.html',date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Dinamik TBMM ayrıntısının yayın tarihi belirtilmemiştir.'))
 add('archive_view',cap['view']);add('source_attribution',dict(version_id=vid,kind=kind,publisher=publisher,author='Çağatan Akyol' if kind=='journalism' else None,social_handle=None,published_at=date,date_precision='day' if date else 'unknown',public_url=url,basis='Ajans haberinin tarihi, atıflı söz ve görev bilgisi okundu; sayfa 3 Haziran 2026 güncellemesi taşır.' if kind=='journalism' else 'TBMM numara, tarih ve ilk imzacı tablosu okundu; güncel durum kesim anına taşınmadı.'))
 pieces=[('authority','Türkiye İşçi Partisi (TİP) Genel Başkanı Erkan Baş'),('quote','hastaneler derhal kamulaştırılmalı')] if kind=='journalism' else [('signature','Saliha Sera KADIG&#x130;L'),('number','2 / 2770'),('date','11/12/2024')]
 for suffix,exact in pieces:
  assert exact in t
  add('passage',dict(id=doc+'-'+suffix+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section='Atıflı açıklama ve temsil görevi' if kind=='journalism' else 'Teklif ayrıntı tablosu',pdf_page_index=None,printed_page=None))
cap=json.loads((p/'saglik-2770-capture.json').read_text());h=cap['sha256'];url=cap['url'];f=root/'objects'/h/'original.pdf';assert sha(f)==h;doc='0405-tip-saglik-2770';vid=doc+'-v1'
add('document',dict(id=doc,party_id='tip',title='28. dönem 2/2770 özel sağlık kurumları teklifi',source_kind='official'))
add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date='2024-12-11',version_label='TBMM imzalı teklif',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='application/pdf',sha256=h,original_path=f'objects/{h}/original.pdf',readable_path=f'objects/{h}/readable.html',date_precision='day',date_unknown_reason=None))
add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Yedi sayfa, gerekçe ve teklifin son sayfası okundu.'))
t=pdf_page_text(f,6); start=t.index('olan özel sağlık kurum ve kuruluşları');end=t.index('devletleştirilir.',start)+len('devletleştirilir.');exact=t[start:end];add('passage',dict(id=doc+'-measure-p',version_id=vid,exact=exact,prefix=None,suffix=None,article='MADDE 2',section='Bir yıl içinde devletleştirme önerisi',pdf_page_index=6,printed_page=None))
prefix='0405-tip-saglik';statement=prefix+'-statement';event=prefix+'-2770-event';relation=prefix+'-relation';contribution=prefix+'-contribution';a='0405-tip-saglik-20241023-anka-authority-p';q='0405-tip-saglik-20241023-anka-quote-p';measure=doc+'-measure-p';sign='0405-tip-2770-detail-signature-p';number='0405-tip-2770-detail-number-p';date='0405-tip-2770-detail-date-p';auth='0405-tip-kadigil-bio-authority-p'
add('actor',dict(id=prefix+'-kadigil',kind='authorized_representative',party_id='tip',person_id='0405-tip-sera-kadigil',authorization_passage_id=auth))
findings=[(prefix+'-summary','ANKA, TİP Genel Başkanı Baş’ın özel hastanelerin kamulaştırılmasını istediğini aktardı.','summary',[a,q]),(prefix+'-quote','hastaneler derhal kamulaştırılmalı','quote',[q]),(prefix+'-initiative','Sera Kadıgil, mevcut özel sağlık kurum ve kuruluşlarının bir yıl içinde devletleştirilmesini öngören 2/2770 teklifini sundu.','summary',[auth,sign,number,date,measure]),(prefix+'-explanation','Baş’ın Ekim 2024 çağrısı ile Kadıgil’in Aralık 2024 tarihli farklı kapsamlı özel sağlık kurumları teklifi sağlıkta kamu mülkiyeti bakımından ilişkilidir; teklif kabul edilmiş sayılmaz.','summary',[a,q,sign,number,date,measure])]
for fid,text,prov,refs in findings:
 add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=statement if fid in (prefix+'-summary',prefix+'-quote') else fid,text=text,provenance=prov,epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='quotation' if prov=='quote' else 'support'));add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Haberin atfı, teklifin kaydı ve madde metni karşılaştırıldı.'))
 add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Haber, aktör ve öneri sınırı okundu.'))
inv=json.loads(Path('data/practices/04-inventory.json').read_text())
for kind in ('statement','event'):
 c=next(x for x in inv['cells'] if x['party_id']=='tip' and x['topic_id']=='sagliga-erisim' and x['research_kind']==kind);rec('practice_scope_v2',dict(id=c['cell_id'],party_id='tip',topic_id='sagliga-erisim',taxonomy_version=c['taxonomy_version'],period_start=c['period_start'],cutoff_at=c['cutoff_at'],research_kind=kind,boundary_reason='Seçili haber ve teklif okundu; diğer dönem ve kaynaklar açık.'))
 if kind=='event':scope=c['cell_id']
rec('practice_event',dict(id=event,common_event_key='tbmm-28-3-2-2770-ozel-saglik',event_at='2024-12-11',date_precision='day',date_unknown_reason=None,scope_context='28. dönem 2/2770',title='Özel sağlık kurumları devletleştirme teklifi',occurrence_basis='TBMM özgün teklif ve ayrıntı kaydı.'))
for pid,point in [(sign,'Kadıgil ilk imzacı'),(number,'Teklif numarası'),(date,'Başkanlığa geliş tarihi'),(measure,'Bir yıl içinde devletleştirme önerisi')]:
 rec('practice_event_evidence',dict(event_id=event,passage_id=pid,supported_point=point,stage='initiative',concrete_basis='TBMM özgün belge veya ayrıntı kaydı.',limitation='Teklifin sunulması kabul veya fiilî devletleştirme değildir.',epistemic_type='claim'));rec('practice_evidence_assessment',dict(event_id=event,passage_id=pid,stage='initiative',basis_kind='document'))
rec('practice_contribution',dict(id=contribution,event_id=event,party_id='tip',actor_id=prefix+'-kadigil',contribution_kind='task',finding_id=prefix+'-initiative',authority_passage_id=auth,membership_passage_id=None,responsibility_limit='Kadıgil teklif sunar; kabul yetkisi TBMM’dedir.'));rec('practice_actor_period',dict(contribution_id=contribution,valid_from='2024-12-11',valid_to='2024-12-11',identity_passage_id='0405-tip-kadigil-bio-identity-p'))
rec('practice_statement',dict(id=statement,party_id='tip',topic_id='sagliga-erisim',taxonomy_version=4,summary_finding_id=prefix+'-summary',quote_finding_id=prefix+'-quote',statement_at='2024-10-23',date_precision='day',version_id='0405-tip-saglik-20241023-anka-v1',period_basis='ANKA haberinin 23 Ekim 2024 tarihli aktarımı.',uncertainty_reason='Aktarım 3 Haziran 2026 güncellemesi taşıyor; tam konuşma kaydı ayrıca incelenmedi.',comparison_row_id='04-03-v3-0304-tip-program-saglik-row'))
rec('practice_relation',dict(id=relation,statement_id=statement,event_id=event,party_id='tip',topic_id='sagliga-erisim',scope_id=scope,comparability_reason='Baş’ın özel hastaneler çağrısı ve Kadıgil’in özel sağlık kurumları teklifinin kapsamları farklıdır.',target_finding_id=prefix+'-summary',result_finding_id=None,explanation_finding_id=prefix+'-explanation',temporal_context='23 Ekim haberini 11 Aralık 2024 teklif sunumu izler.',authority_context='Parti başkanı çağrı yaptı; milletvekili teklif sundu; kanunu kabul yetkisi TBMM’dedir.',uncertainty_reason='Teklifin kesim aşaması ve somut sonuç gösterilmedi; haber güncellemesi kesim öncesindedir.'))
pkg['entries'].extend(entries)
for k,rows in records.items():pkg['practice_records'].setdefault(k,[]).extend(rows)
data={k:list(v) for k,v in pkg['practice_records'].items()}
for e in pkg['entries']:data.setdefault(e['kind'],[]).append(e['values'])
db=sqlite3.connect('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.sqlite3');db.row_factory=sqlite3.Row
for k in ('finding_evidence','passage'):data.setdefault(k,[]).extend(dict(x) for x in db.execute('SELECT * FROM '+k))
versions={x['id']:x['version_id'] for x in data['passage']};targets=practice_review_targets(data,records)
for (kind,identity),(refs,parties) in targets.items():
 row=dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({versions[x] for x in refs})),passage_ids=json.dumps(sorted(refs)),inspected_sections=json.dumps(['23 Ekim ANKA haberindeki Baş çağrısı','2/2770 TBMM ayrıntısı ve 2. madde'],ensure_ascii=False),supported_claim='Kayda bağlı sağlık çağrısı ve teklif kapsamı ayrı incelendi: '+identity,limitations='Haber 2026 güncellemesi taşıyor; teklifin kabulü veya uygulama sonucu gösterilmiyor.',result='reviewed',reason='Bu hedefin özgün pasajları incelendi: '+kind+' '+identity);review['practice_source_review'].append(row);review['source_review_refs'].append(dict(subject_kind=kind,subject_id=identity))
for name,obj in [('saglik-2770-append-draft.json',pkg),('saglik-2770-review-draft.json',review)]:(p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries),len(targets))
