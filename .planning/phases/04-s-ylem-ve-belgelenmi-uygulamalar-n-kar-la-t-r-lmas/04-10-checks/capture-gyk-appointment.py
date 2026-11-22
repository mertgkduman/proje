import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
capture=Path('/tmp/gsd0410-gyk-20230517.html');raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest()
exact='17 Mayıs tarihinde toplanan Genel Yönetim Kurulu’muz (GYK) Genel Başkanlık görevine, Genel Başkan Yardımcımız Selma Gürkan’ı getirmiştir.';assert exact in html_source_text(raw)
origin='https://www.gercekgundem.com/secim/emepin-yeni-genel-baskani-ercument-akdenizin-istifasinin-ardindan-selma-gurkan-oldu-423214'
url='https://web.archive.org/web/20230518102050id_/https://www.gercekgundem.com/secim/emepin-yeni-genel-baskani-ercument-akdenizin-istifasinin-ardindan-selma-gurkan-oldu-423214'
root=Path('data/practices/sources/emep');obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    p=obj/name
    if p.exists(): assert p.read_bytes()==content
    else:p.write_bytes(content)
ident='0410-emep-2023-gyk-anka';view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='emep',title='EMEP GYK 17 Mayıs 2023 genel başkan görevlendirmesi',source_kind='journalism')),
('document_version',dict(id=ident+'-v1',document_id=ident,original_url=origin,final_url=url,document_date='2023-05-18',version_label='18 Mayıs 2023 tarihli ANKA haber aktarımı; aynı gün arşiv yakalaması',accessed_at=access,verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',date_precision='day',date_unknown_reason=None)),
('archive_view',view),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='GYK görevlendirmesine ilişkin parti açıklaması',pdf_page_index=None,printed_page=None)),
('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Gerçek Gündem',author='ANKA',social_handle=None,published_at='2023-05-18',date_precision='day',public_url=url,basis='Arşiv HTML haberde ANKA kaynak atfı ve 18 Mayıs yayın günü; parti açıklamasının içinde 17 Mayıs GYK toplantısı görülür.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/gyk-appointment-source-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',entries=[dict(kind=k,values=v) for k,v in rows],note='17 Mayıs GYK görevlendirmesi ve Haziran olağanüstü kongre seçimi ayrı işlem.'),ensure_ascii=False,indent=2)+'\n');print(sha,view['view_id'])
