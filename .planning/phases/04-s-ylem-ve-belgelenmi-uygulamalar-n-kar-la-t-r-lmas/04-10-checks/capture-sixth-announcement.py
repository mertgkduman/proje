import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

capture=Path('/tmp/gsd0410-sixth-announcement.html');raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest()
exact='18 Aralık 2011 Pazar g&uuml;n&uuml; 6. Olağan Kongresi&rsquo;ni toplayacak olan Emek Partisi (EMEP)';assert exact in html_source_text(raw)
origin='https://www.evrensel.net/haber/19507/emep-6-genel-kongresini-topluyor';url='https://web.archive.org/web/20160926142806id_/https://www.evrensel.net/haber/19507/emep-6-genel-kongresini-topluyor'
root=Path('data/practices/sources/emep');obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    path=obj/name
    if path.exists(): assert path.read_bytes()==content
    else: path.write_bytes(content)
ident='0410-emep-2011-sixth-announcement';view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='emep',title='EMEP 6. Genel Kongresi duyurusu',source_kind='journalism')),
 ('document_version',dict(id=ident+'-v1',document_id=ident,original_url=origin,final_url=url,document_date='2011-12-17',version_label='17 Aralık 2011 Evrensel haberi; 2016 arşiv yakalaması',accessed_at=access,verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',date_precision='day',date_unknown_reason=None)),
 ('archive_view',view),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='18 Aralık için kongre duyurusu',pdf_page_index=None,printed_page=None)),
 ('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Evrensel',author=None,social_handle=None,published_at='2011-12-17',date_precision='day',public_url=url,basis='Arşiv sayfasındaki tarih 17 Aralık 2011; duyuruda 18 Aralık planı yazılıdır.'))]
out=Path(__file__).parent/'sixth-announcement-source-draft.json';assert not out.exists();out.write_text(json.dumps(dict(status='draft_unvalidated',entries=[dict(kind=k,values=v) for k,v in rows],note='Haber yalnız planlanan kongreyi bildirir; taramadaki 6. kongreye sunulan önerinin kabul edildiğini veya kongrenin bu günde gerçekleştiğini kanıtlamaz.'),ensure_ascii=False,indent=2)+'\n');print('SIXTH_SOURCE_VIEW_OK',sha,view['view_id'])
