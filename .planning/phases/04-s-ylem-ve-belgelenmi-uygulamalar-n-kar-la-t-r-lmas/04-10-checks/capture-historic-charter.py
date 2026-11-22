import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

capture=Path('/tmp/gsd0410-snapshot-20230516202909.html')
raw=capture.read_bytes()
sha=hashlib.sha256(raw).hexdigest()
assert sha=='b85f649ee487d2a364352d1decb62ccd8140119a35b97a0cbee270699260cd6b'
exact='Genel Başkan’ı, GYK ve MDK’yi seçer.'
assert exact in html_source_text(raw)
url='https://web.archive.org/web/20230516202909id_/https://www.emep.org/emek-partisi-program-ve-tuzugu'
root=Path('data/practices/sources/emep'); obj=root/'objects'/sha
obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    p=obj/name
    if p.exists(): assert p.read_bytes()==content
    else: p.write_bytes(content)
v='0410-emep-charter-202305-v1'
view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8')
view['version_id']=v
validate_view(root,view)
access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds')
now=datetime.now(timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id='0410-emep-charter-202305',party_id='emep',title='EMEP program ve tüzüğü — 16 Mayıs 2023 arşiv yakalaması',source_kind='party')),
('document_version',dict(id=v,document_id='0410-emep-charter-202305',original_url='https://www.emep.org/emek-partisi-program-ve-tuzugu',final_url=url,document_date=None,version_label='16 Mayıs 2023 Internet Archive yakalaması; kabul ve yürürlük günü belirsiz',accessed_at=access,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',date_precision='unknown',date_unknown_reason='Arşiv yakalama zamanı metnin kabul veya yürürlük günü değildir.')),
('archive_view',view),('passage',dict(id='0410-emep-charter-202305-congress-p',version_id=v,exact=exact,prefix=None,suffix=None,article='Madde 31/e',section='Genel Kongre görevleri',pdf_page_index=None,printed_page=None)),
('source_attribution',dict(version_id=v,kind='party_publication',publisher='Emek Partisi',author='Mustafa Mayda (site metadata)',social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Partinin program/tüzük sayfasının 16 Mayıs 2023 tarihli arşiv görüntüsü; yakalama tarihi yayımlanma veya kabul tarihi sayılmaz.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/historic-charter-source-draft.json')
out.write_text(json.dumps(dict(status='draft_unvalidated',snapshot_at='2023-05-16T20:29:09Z',entries=[dict(kind=k,values=v) for k,v in rows]),ensure_ascii=False,indent=2)+'\n')
print(sha,view['view_id'])
