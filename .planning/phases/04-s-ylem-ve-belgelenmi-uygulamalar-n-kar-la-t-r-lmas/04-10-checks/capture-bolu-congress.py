import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
capture=Path('/tmp/gsd0410-bolu-2020.html');raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest()
exacts=['Ahmet Özkan seçildi','Süreyya Demir, Burakcan Akpınar, Hasan Metin Taşkıran'];assert all(x in html_source_text(raw) for x in exacts)
url='https://www.koroglugazetesi.com/emek-partisi-bolu-il-kongresi-yapildi';root=Path('data/practices/sources/emep');obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    p=obj/name
    if p.exists():assert p.read_bytes()==content
    else:p.write_bytes(content)
ident='0410-emep-2020-bolu';view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='emep',title='EMEP Bolu il kongresi ve organları',source_kind='journalism')),
('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date='2020-12-24',version_label='24 Aralık 2020 tarihli haber; kongrenin kesin günü belirtilmiyor',accessed_at=access,verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',date_precision='day',date_unknown_reason=None)),('archive_view',view),
('passage',dict(id=ident+'-chair-p',version_id=ident+'-v1',exact=exacts[0],prefix=None,suffix=None,article=None,section='İl başkanı seçimi',pdf_page_index=None,printed_page=None)),
('passage',dict(id=ident+'-discipline-p',version_id=ident+'-v1',exact=exacts[1],prefix=None,suffix=None,article=None,section='İl disiplin kurulu',pdf_page_index=None,printed_page=None)),
('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Köroğlu Gazetesi',author=None,social_handle=None,published_at='2020-12-24',date_precision='day',public_url=url,basis='Yerel gazetenin haber sayfasında 24 Aralık 2020 yayın tarihi okunur; kongrenin tam günü açık değil.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/bolu-congress-source-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',entries=[dict(kind=k,values=v) for k,v in rows],note='Bolu il kongresi; Kasım 2020 ulusal 9. kongre ile aynı olay değil.'),ensure_ascii=False,indent=2)+'\n');print(sha,view['view_id'])
