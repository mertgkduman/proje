import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
capture=Path('/tmp/gsd0410-corum-2023.html');raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest()
exacts=['Muharrem Özünel seçildi.','disiplin kurulu &uuml;yeleri ile 8 kişilik genel merkez delegeleri de belirlendi.'];assert all(x in html_source_text(raw) for x in exacts)
origin='https://www.evrensel.net/haber/504486/emep-corum-il-orgutu-kongre-surecini-tamamladi-bu-baski-rejimini-birlikte-puskurtecegiz';url='https://web.archive.org/web/20231127191544id_/'+origin
root=Path('data/practices/sources/emep');obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    p=obj/name
    if p.exists():assert p.read_bytes()==content
    else:p.write_bytes(content)
ident='0410-emep-2023-corum';view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='emep',title='EMEP Çorum il kongresinde seçimler',source_kind='journalism')),
('document_version',dict(id=ident+'-v1',document_id=ident,original_url=origin,final_url=url,document_date='2023-11-27',version_label='27 Kasım 2023 tarihli Evrensel haberi; kongre günü açık değil',accessed_at=access,verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',date_precision='day',date_unknown_reason=None)),('archive_view',view),
('passage',dict(id=ident+'-chair-p',version_id=ident+'-v1',exact=exacts[0],prefix=None,suffix=None,article=None,section='İl başkanı',pdf_page_index=None,printed_page=None)),
('passage',dict(id=ident+'-discipline-p',version_id=ident+'-v1',exact=exacts[1],prefix=None,suffix=None,article=None,section='Kurullar ve genel merkez delegeleri',pdf_page_index=None,printed_page=None)),
('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Evrensel',author='Çorum/Evrensel',social_handle=None,published_at='2023-11-27',date_precision='day',public_url=url,basis='Evrensel tarihsel sayfasında yayın tarihi ve Çorum/Evrensel kaynak bilgisi okunur.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/corum-congress-source-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',entries=[dict(kind=k,values=v) for k,v in rows],note='8 sayısı genel merkez delegelerine aittir; disiplin kurulu kişi sayısı olarak kullanılmaz. İl başkanı seçimi, disiplin kurulu ve delegeler ayrı kayıt noktalarıdır.'),ensure_ascii=False,indent=2)+'\n');print(sha,view['view_id'])
