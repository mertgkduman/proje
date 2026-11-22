import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds');entries=[]
cases=[('2023','/tmp/gsd0410-aym-2023-archive.html','https://www.anayasa.gov.tr/tr/mahkeme-gundemi/genel-kurul/27-mart-2025-genel-kurul-gundemi-ve-sonuclari/','https://web.archive.org/web/20250407150636id_/https://www.anayasa.gov.tr/tr/mahkeme-gundemi/genel-kurul/27-mart-2025-genel-kurul-gundemi-ve-sonuclari/','E.2024/49 (SPMD)','2025-03-27'),('2024','/tmp/gsd0410-aym-2024-archive.html','https://www.anayasa.gov.tr/tr/mahkeme-gundemi/genel-kurul/26-mart-2026-genel-kurul-gundemi-ve-sonuclari/','https://web.archive.org/web/20260331180550id_/https://www.anayasa.gov.tr/tr/mahkeme-gundemi/genel-kurul/26-mart-2026-genel-kurul-gundemi-ve-sonuclari/','E.2025/78 (SPMD)','2026-03-26')]
def add(k,**v):entries.append(dict(kind=k,values=v))
for year,path,url,archive,case,day in cases:
    raw=Path(path).read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);ident='0410-emep-aym-account-'+year;version=ident+'-v1'
    for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
        target=obj/name
        if target.exists():assert target.read_bytes()==content
        else:target.write_bytes(content)
    add('document',id=ident,party_id='emep',title='AYM Genel Kurul gündeminde EMEP '+year+' kesin hesabı',source_kind='official');add('document_version',id=version,document_id=ident,document_date=None,date_precision='unknown',date_unknown_reason='Gündem toplantı günü vardır; sayfanın kesin yayın zamanı ayrı doğrulanmadı.',version_label=day+' gündemi ve sonraki arşiv görüntüsü',original_url=url,final_url=archive,accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html');view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);add('archive_view',**view);add('source_attribution',version_id=version,publisher='Anayasa Mahkemesi',author=None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=url,basis='AYM Genel Kurul gündemi; toplantı tarihi, yayın ve karar tarihi ile eşitlenmez.')
    s=html_source_text(raw);i=s.find('Emek Partisi '+year+' yılı kesin hesabı');assert i>=0;start=s.rfind('<tr',0,i);end=s.find('</tr>',i)+5;exact=s[start:end];assert case in exact and 'İlk' in exact
    add('passage',id=ident+'-agenda-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='İlk inceleme gündem satırı',pdf_page_index=None,printed_page=None);print(year,sha,view['view_id'])
out=Path(__file__).parent/'account-agendas-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_package_pending',note='AYM gündem satırları yalnız dosya ve planlanan ilk inceleme bilgisidir; incelemenin yapıldığı veya karar verildiği çıkarılmadı.'),f,ensure_ascii=False,indent=2);f.write('\n')
