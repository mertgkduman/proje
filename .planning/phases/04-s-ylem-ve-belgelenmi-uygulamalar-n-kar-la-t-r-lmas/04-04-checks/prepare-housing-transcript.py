import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd()/'src'))
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root=Path('data/practices/sources/yeni-parti')
url='https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/122/Ham/824e2a72-561f-4031-a097-138f2f468abb.html'
raw=Path('/tmp/gsd-0404-tbmm-122.html').read_bytes()
digest=hashlib.sha256(raw).hexdigest()
assert digest=='38d374df7534834cb6fae4b8937f225bcf055c094859881ebea38a416810be78'
source=html_source_text(raw)
exact='Sakarya Milletvekili Ayça Taşkent ve arkadaşları tarafından, ülkemizde giderek derinleşen barınma krizinin nedenlerinin ekonomik ve sosyal sonuçları ile çözüm önerilerinin belirlenmesi amacıyla 5/8/2026 tarihinde Türkiye Büyük Millet Meclisi Başkanlığına verilmiş olan (25 sıra no.lu) Meclis araştırması önergesinin diğer önergelerin önüne alınarak görüşmelerinin 7/8/2026 Cuma günkü birleşimde yapılması önerilmiştir.'
result='BAŞKAN - Önergeyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Önerge kabul edilmemiştir.'
start=source.index(exact); end=source.index(result,start)
assert 37000 < end-start < 37300
folder=root/'objects'/digest; folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
 target=folder/name
 if target.exists(): assert target.read_bytes()==content
 else: target.write_bytes(content)
view=build_view(raw,url,root,fetch_assets=False); view['version_id']='0404-tbmm-barinma-tutanak-v1'; validate_view(root,view)
version=dict(id='0404-tbmm-barinma-tutanak-v1',document_id='0404-tbmm-barinma-tutanak',original_url=url,final_url=url,document_date=None,version_label='7 Ağustos TBMM 122. birleşim ham tutanağı; yakalanan HTML',accessed_at='2026-11-21T20:46:19+00:00',verified_at='2026-11-21T20:46:19+00:00',mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Birleşme tarihi 7 Ağustos 2026; tutanak sayfasının yayım tarihi belirtilmemiştir.')
def passage(id, text, section):
 return dict(id=id,version_id=version['id'],exact=text,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
entries=[('document',dict(id='0404-tbmm-barinma-tutanak',party_id='yeni-parti',title='TBMM 122. birleşim barınma grup önerisi',source_kind='official')),('document_version',version),('archive_view',view),('passage',passage('0404-barinma-grup-oneri-p',exact,'Yeni Parti grubunun 25 sıra sayılı araştırma önergesini öne alma talebi')),('passage',passage('0404-barinma-grup-oylama-p',result,'Aynı görüşmenin ardından grup önerisinin oylanması')),('source_attribution',dict(version_id=version['id'],kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM Tutanak Hizmetleri Başkanlığı 28. dönem 4. yasama yılı 122. birleşim metni.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/housing-transcript-records-draft.json')
out.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=[dict(kind=k,values=v) for k,v in entries]),ensure_ascii=False,indent=2)+'\n')
print('PREPARED',digest,view['view_id'])
