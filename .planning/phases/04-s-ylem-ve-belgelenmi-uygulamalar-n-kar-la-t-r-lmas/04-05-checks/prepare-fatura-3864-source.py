import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_exists,pdf_page_text
P=Path(__file__).parent; root=Path('data/practices/sources/tip'); now=datetime.now(timezone.utc).isoformat()
cap=json.loads((P/'fatura-3864-capture.json').read_text()); sha=cap['sha256']; pdf=root/'objects'/sha/'original.pdf'; assert hashlib.sha256(pdf.read_bytes()).hexdigest()==sha
doc='0405-tip-fatura-3864'; vid=doc+'-v1'; url=cap['url']
entries=[dict(kind='document',values=dict(id=doc,party_id='tip',title='27. dönem 2/3864 fatura desteği kanun teklifi',source_kind='official')),
 dict(kind='document_version',values=dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date='2021-10-08',version_label='TBMM özgün imzalı tarama',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='application/pdf',sha256=sha,original_path=f'objects/{sha}/original.pdf',readable_path=f'objects/{sha}/readable.html',date_precision='day',date_unknown_reason=None)),
 dict(kind='source_attribution',values=dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Özgün teklif taramasının dokuz sayfası görsel okundu.'))]
for suffix,page,exact,section in [
 ('authority',0,'Erkan Baş\nTİP Genel Başkanı','İmzalı teklifin sunuş sayfası'),
 ('measure',8,'Hane geliri net asgari ücretin 2 katı veya altında ise belirlenen ortalama tüketim miktarının altında elektrik tüketilmesi hâlinde, hane gelirine göre belirlenmesi suretiyle fatura bedellerinin tamamı Hazine tarafından karşılanır.','Teklif 10. madde, elektrik tarifesi')]:
 assert pdf_page_exists(pdf,page) and not pdf_page_text(pdf,page).strip()
 pid=doc+'-'+suffix+'-p'
 entries.append(dict(kind='passage',values=dict(id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article='MADDE 10' if page==8 else None,section=section,pdf_page_index=page,printed_page=None)))
 entries.append(dict(kind='manual_passage',values=dict(passage_id=pid,checked_at=now,method='Özgün tarama sayfası Poppler ile görsel olarak okundu.',reason='İlgili pasaj doğrudan tarama görüntüsüyle karşılaştırıldı; metin katmanı boştur.')))
cap=json.loads((P/'fatura-3864-detail-capture.json').read_text()); sha=cap['sha256']; url=cap['url']; raw=(root/'objects'/sha/'original.html.bin').read_bytes(); assert hashlib.sha256(raw).hexdigest()==sha
doc='0405-tip-fatura-3864-detail'; vid=doc+'-v1'; t=html_source_text(raw)
entries += [dict(kind='document',values=dict(id=doc,party_id='tip',title='TBMM 2/3864 teklif kayıt ekranı',source_kind='official')),
 dict(kind='document_version',values=dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date=None,version_label='TBMM teklif ayrıntısı',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='text/html',sha256=sha,original_path=f'objects/{sha}/original.html.bin',readable_path=f'objects/{sha}/readable.html',date_precision='unknown',date_unknown_reason='Dinamik kayıt ekranının yayın tarihi belirtilmemiştir.')),
 dict(kind='archive_view',values=cap['view']),dict(kind='source_attribution',values=dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Teklif numarası, geliş tarihi, özeti ve güncel sonuç alanı okundu.'))]
for suffix,exact in [('number','2 / 3864'),('date','08/10/2021'),('status','H&#xDC;K&#xDC;MS&#xDC;Z (G)')]:
 assert exact in t
 entries.append(dict(kind='passage',values=dict(id=doc+'-'+suffix+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section='Teklif numarası, geliş veya sonuç alanı',pdf_page_index=None,printed_page=None)))
(P/'fatura-3864-source-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries),ensure_ascii=False,indent=2)+'\n')
print('3864_SOURCE_DRAFT',len(entries))
