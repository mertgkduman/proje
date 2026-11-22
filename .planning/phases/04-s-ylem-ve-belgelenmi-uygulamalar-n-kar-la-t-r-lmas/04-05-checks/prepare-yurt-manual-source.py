import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_exists, pdf_page_text, readable_bytes

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
capture=json.loads((p/'yurt-3833-capture.json').read_text()); sha=capture['sha256']; url=capture['url']; f=Path('data/practices/sources/tip/objects')/sha/'original.pdf'; raw=f.read_bytes()
assert hashlib.sha256(raw).hexdigest()==sha and pdf_page_exists(f,5) and not pdf_page_text(f,5).strip()
readable=f.parent/'readable.html'; content=readable_bytes(raw,'pdf',legacy=False)
if readable.exists(): assert readable.read_bytes()==content
else: readable.write_bytes(content)
doc='0405-tip-yurt-273833'; vid=doc+'-v1'; passage=doc+'-free-dorm-p'; now=datetime.now(timezone.utc).isoformat()
entries=[
 dict(kind='document',values=dict(id=doc,party_id='tip',title='27. dönem 2/3833 öğrenci yurtları kanun teklifi',source_kind='official')),
 dict(kind='document_version',values=dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date='2021-09-23',version_label='TBMM özgün taranmış teklif',accessed_at=capture['accessed_at'],verified_at=capture['accessed_at'],mime='application/pdf',sha256=sha,original_path=f'objects/{sha}/original.pdf',readable_path=f'objects/{sha}/readable.html',date_precision='day',date_unknown_reason=None)),
 dict(kind='source_attribution',values=dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM imzalı taramasının altı sayfası görüntülenerek okundu.')),
 dict(kind='passage',values=dict(id=passage,version_id=vid,exact='Gençlik ve Spor Bakanlığı Kredi ve Yurtlar Genel Müdürlüğü ve Yükseköğretim Kurumlarına ait tüm yurtlar ücretsiz olarak barınma hizmeti sunar.',prefix=None,suffix=None,article='MADDE 1',section='Öğrencilere barınma hizmeti ve desteği ile yurt inşası',pdf_page_index=5,printed_page=None)),
 dict(kind='manual_passage',values=dict(passage_id=passage,checked_at=now,method='Özgün tarama sayfası Poppler ile görsel olarak okundu.',reason='Teklif 1. maddesindeki ücretsiz kamu yurdu cümlesi 5 indeksli sayfa görüntüsüyle doğrudan karşılaştırıldı; metin katmanı boştur.'))]
assert pdf_page_exists(f,0) and not pdf_page_text(f,0).strip()
entries.extend([
 dict(kind='passage',values=dict(id=doc+'-authority-p',version_id=vid,exact='Erkan Baş\nTİP Genel Başkanı',prefix=None,suffix=None,article=None,section='23 Eylül 2021 imzalı sunuş',pdf_page_index=0,printed_page=None)),
 dict(kind='manual_passage',values=dict(passage_id=doc+'-authority-p',checked_at=now,method='Özgün tarama sayfası Poppler ile görsel olarak okundu.',reason='Kapakta ilk imza sahibinin adı ve hemen altındaki TİP Genel Başkanı unvanı doğrudan görüntüden okundu.'))])
(p/'yurt-manual-source-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries),ensure_ascii=False,indent=2)+'\n')
print('MANUAL_SOURCE_DRAFT_ONLY',len(entries))
