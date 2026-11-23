import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

D=Path(__file__).parent; root=Path('data/practices/sources/emep'); now=datetime.now(timezone.utc).isoformat(timespec='seconds'); entries=[]
sources=[
 ('36753','register','html','https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/18dc2193-ff58-4569-b507-019ab49a28ef',None,None),
 ('36753','question','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T7/WebOnergeMetni/aab4f655-0b72-46de-82aa-35aa79adf0aa.pdf','2025-11-21',None),
 ('36753','answer','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T7/WebOnergeMetni/49541f06-4ba7-4080-897f-107895823c62.pdf',None,'Çalışma ve Sosyal Güvenlik Bakanlığı'),
 ('36769','register','html','https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/e50baefc-ce0f-4c09-a80e-019ab49289c5',None,None),
 ('36769','question','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T7/WebOnergeMetni/15e33f02-3c34-46e6-a6d0-c8d05641fddf.pdf','2025-11-21',None),
 ('36769','answer','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T7/WebOnergeMetni/a7b3cae9-b240-4fcc-86ab-6f5cb5299a37.pdf','2025-12-19','Enerji ve Tabii Kaynaklar Bakanlığı'),
]
for num,role,typ,url,date,author in sources:
    raw=(D/('tupras-'+num+'-'+role+('.html' if typ=='html' else '.pdf'))).read_bytes(); digest=hashlib.sha256(raw).hexdigest(); obj=root/'objects'/digest;obj.mkdir(parents=True,exist_ok=True)
    original='original.html.bin' if typ=='html' else 'original.pdf'
    for name,content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
        path=obj/name
        if path.exists(): assert path.read_bytes()==content
        else: path.write_bytes(content)
    doc='0410-emep-tupras-'+num+'-'+role; v=doc+'-v1'
    entries.append(dict(kind='document',values=dict(id=doc,party_id='emep',title='TBMM 7/'+num+' '+{'register':'kayıt','question':'soru','answer':'bakanlık yanıtı'}[role],source_kind='official')))
    entries.append(dict(kind='document_version',values=dict(id=v,document_id=doc,original_url=url,final_url=url,document_date=date,date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Yayım veya belge günü doğrulanmadı.',version_label='TBMM özgün kaydı; taranmış PDF sayfaları görsel okundu' if typ=='pdf' else 'TBMM kayıt ekranı',accessed_at=now,verified_at=now,mime='text/html' if typ=='html' else 'application/pdf',sha256=digest,original_path='objects/'+digest+'/'+original,readable_path='objects/'+digest+'/readable.html')))
    if typ=='html':
        view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=v;validate_view(root,view);entries.append(dict(kind='archive_view',values=view))
        for key,exact in [('number','7 / '+num),('date','21.11.2025'),('reply', '07.09.2026' if num=='36753' else '22.12.2025')]:
            assert exact in html_source_text(raw)
            entries.append(dict(kind='passage',values=dict(id=doc+'-'+key+'-p',version_id=v,exact=exact,prefix=None,suffix=None,article=None,section='Soru ve yanıt bildirim kaydı',pdf_page_index=None,printed_page=None)))
    entries.append(dict(kind='source_attribution',values=dict(version_id=v,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=author,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM özgün kaydı; belge ve bildirim günleri ayrıdır. Taranmış cevaplar sayfa sayfa görsel okundu; yayın günü çıkarılmadı.')))
    print(num,role,digest)
with (D/'tupras-norm-source-draft.json').open('x') as f:
    json.dump(dict(status='source_read_package_pending',entries=entries,note='İki 21 Kasım 2025 soru; Enerji cevabı 19 Aralık 2025 ve bildirimi 22 Aralık, Çalışma cevabı bildirimi 7 Eylül 2026. Her iki cevap görsel okundu, sonuç veya önlem varsayılmaz.'),f,ensure_ascii=False,indent=2);f.write('\n')
