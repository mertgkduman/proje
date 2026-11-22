import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

root=Path('data/practices/sources/emep')
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks')
specs=[
 ('indy','0410-emep-2020-indy','https://www.indyturk.com/node/275861/haber/emep%E2%80%99-yeni-genel-ba%C5%9Fkan%C4%B1-erc%C3%BCment-akdeniz-oldu','2020-11-22','journalism','Independent Türkçe','Evrensel, Independent Türkçe'),
 ('party','0410-emep-2020-party','https://www.emep.org/partimiz-9-olagan-kongresi-toplandi-isci-sinifi-kazanmanin-yolunu-gosteriyor','2020-11-23','party','Emek Partisi',None),
]
entries=[]
for filename,ident,url,date,kind,publisher,author in specs:
    capture=Path('/tmp/gsd0410-ninth-'+filename+'.html'); raw=capture.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    exact='Ercüment Akdeniz seçildi.'; assert exact in html_source_text(raw)
    obj=root/'objects'/sha; obj.mkdir(parents=True,exist_ok=True)
    for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
        path=obj/name
        if path.exists(): assert path.read_bytes()==content
        else: path.write_bytes(content)
    view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8'); view['version_id']=ident+'-v1';validate_view(root,view)
    access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds')
    rows=[('document',dict(id=ident,party_id='emep',title='EMEP 9. Olağan Kongresi ve genel başkan seçimi',source_kind=kind)),
      ('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=date,version_label=date+' yayın tarihli haber',accessed_at=access,verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',date_precision='day',date_unknown_reason=None)),
      ('archive_view',view),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Genel başkan seçimi',pdf_page_index=None,printed_page=None)),
      ('source_attribution',dict(version_id=ident+'-v1',kind='journalism' if kind=='journalism' else 'party_publication',publisher=publisher,author=author,social_handle=None,published_at=date,date_precision='day',public_url=url,basis=('Independent Türkçe haber künyesi Evrensel ve Independent Türkçe kaynaklarını belirtir.' if kind=='journalism' else 'Partinin kendi kongre haberinin yayıncısı ve 23 Kasım 2020 yayın tarihi özgün HTML içinde okundu.')))]
    entries.extend(dict(kind=k,values=v) for k,v in rows);print(ident,sha,view['view_id'])
(checks/'ninth-congress-source-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,note='22 Kasım 2020 seçimi; Independent Türkçe haberinde Evrensel atfı vardır. Parti yayını ertesi gün tarihlidir.'),ensure_ascii=False,indent=2)+'\n')
