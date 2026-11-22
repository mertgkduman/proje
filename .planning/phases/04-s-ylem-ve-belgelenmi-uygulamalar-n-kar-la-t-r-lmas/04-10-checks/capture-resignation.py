import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
capture=Path('/tmp/gsd0410-resignation-20230516.html');raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest();text=html_source_text(raw)
exacts=['parti üyeliğinden istifa ettiğini duyurdu.','istifanın bi&ccedil;iminin parti t&uuml;z&uuml;ğ&uuml;m&uuml;z ve işleyişi a&ccedil;ısından izahı m&uuml;mk&uuml;n değildir.']
assert all(x in text for x in exacts)
origin='https://www.evrensel.net/haber/490142/emepten-istifa-aciklamasi';url='https://web.archive.org/web/20230516162242id_/https://www.evrensel.net/haber/490142/emepten-istifa-aciklamasi'
root=Path('data/practices/sources/emep');obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
    p=obj/name
    if p.exists():assert p.read_bytes()==content
    else:p.write_bytes(content)
ident='0410-emep-2023-resignation';view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='emep',title='Akdeniz’in istifa açıklaması ve EMEP MYK yanıtı',source_kind='journalism')),
('document_version',dict(id=ident+'-v1',document_id=ident,original_url=origin,final_url=url,document_date='2023-05-16',version_label='16 Mayıs 2023 Evrensel haberi; aynı gün arşiv yakalaması',accessed_at=access,verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html',date_precision='day',date_unknown_reason=None)),('archive_view',view),
('passage',dict(id=ident+'-resignation-p',version_id=ident+'-v1',exact=exacts[0],prefix=None,suffix=None,article=None,section='İstifa bildirimi',pdf_page_index=None,printed_page=None)),
('passage',dict(id=ident+'-response-p',version_id=ident+'-v1',exact=exacts[1],prefix=None,suffix=None,article=None,section='MYK açıklaması',pdf_page_index=None,printed_page=None)),
('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Evrensel',author='Haber Merkezi',social_handle=None,published_at='2023-05-16',date_precision='day',public_url=url,basis='Evrensel arşiv HTML içinde 16 Mayıs 2023 tarih ve Haber Merkezi künyesi okunur.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/resignation-source-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',entries=[dict(kind=k,values=v) for k,v in rows],note='Akdeniz istifa gerekçesi olarak parti içi demokrasiye müdahale iddiası ileri sürer; MYK açıklaması istifa biçimini eleştirir, iddiaya doğrudan yanıt sayılmaz. İstifa ihraç değildir.'),ensure_ascii=False,indent=2)+'\n');print(sha,view['view_id'])
