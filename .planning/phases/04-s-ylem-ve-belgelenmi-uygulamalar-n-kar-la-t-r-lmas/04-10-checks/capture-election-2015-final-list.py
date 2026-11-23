import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text,readable_bytes
root=Path('data/practices/sources/emep');path=Path('/tmp/gsd0410-election2015/final-candidates.pdf');raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
url='https://www.ysk.gov.tr/doc/dosyalar/docs/Milletvekili/1Kasim2015/2015MVES-KesinAdayListesi.pdf';final='https://ysk.gov.tr/doc/dosyalar/docs/Milletvekili/1Kasim2015/2015MVES-KesinAdayListesi.pdf';ident='0410-emep-election-2015-final-list';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
exact='MİLLETVEKİLİ SEÇİMLERİ KESİN ADAY LİSTESİ';assert exact in pdf_page_text(path,0)
entries=[dict(kind='document',values=dict(id=ident,party_id='emep',title='YSK 1 Kasım 2015 milletvekili kesin aday listeleri',source_kind='official')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=final,document_date=None,date_precision='unknown',date_unknown_reason='Listenin kesin yayın günü ayrıca doğrulanmadı.',version_label='26. dönem kesin aday listesi; 289 sayfa',accessed_at=now,verified_at=now,mime='application/pdf',sha256=sha,original_path='objects/'+sha+'/original.pdf',readable_path='objects/'+sha+'/readable.html')),dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='Yüksek Seçim Kurulu',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='YSK kesin aday listesi; yayım günü ayrı bilinmiyor. www TLS kesildi, ysk.gov.tr özgün bayt sağladı.')),dict(kind='passage',values=dict(id=ident+'-title-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Kesin aday listesi başlığı',pdf_page_index=0,printed_page=None))]
out=Path(__file__).parent/'election-2015-final-list-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_partial',note='289 sayfanın tümünde metin çıkarıldı ve EMEK PARTİSİ tam başlığı makineyle arandı; eşleşme yok. Bu işlem insanın her sayfayı okuması, başka listelerde aday kimliklerinin saptanması veya hukuki sonuç değildir.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('ELECTION2015_FINAL_LIST_CAPTURE_OK',sha)
