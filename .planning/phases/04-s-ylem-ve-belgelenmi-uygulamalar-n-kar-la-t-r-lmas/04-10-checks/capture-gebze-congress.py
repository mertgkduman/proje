import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/emep');now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds');rows=[]
sources=[('party','/tmp/gsd0410-gebze-party.html','https://www.emep.org/aslan-bu-duzen-curudu-degistirmek-icin-birlesmeliyiz','2026-10-12','party','Emek Partisi','EMEP Gebze 11. Olağan Kongresi parti haberi'),('plan','/tmp/gsd0410-gebze-plan.html','https://www.gebzeemek.com/haber/siyaset/emep-gebzede-11nci-kongre-ekimin-11inde/4765.html','2026-10-06','journalism','Gebze Emek','EMEP Gebze kongresi ön duyurusu')]
def add(k,**v):rows.append(dict(kind=k,values=v))
for role,path,url,date,kind,publisher,title in sources:
    raw=Path(path).read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True);ident='0410-emep-gebze-2026-'+role;version=ident+'-v1'
    for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
        dest=obj/name
        if dest.exists():assert dest.read_bytes()==content
        else:dest.write_bytes(content)
    add('document',id=ident,party_id='emep',title=title,source_kind=kind);add('document_version',id=version,document_id=ident,original_url=url,final_url=url,document_date=date,date_precision='day',date_unknown_reason=None,version_label='Kongre haberi' if role=='party' else 'Kongre öncesi bağımsız duyuru',accessed_at=now,verified_at=now,mime='text/html',sha256=sha,original_path='objects/'+sha+'/original.html.bin',readable_path='objects/'+sha+'/readable.html');view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);add('archive_view',**view);add('source_attribution',version_id=version,kind=kind,publisher=publisher,author=None,social_handle=None,published_at=date,date_precision='day',public_url=url,basis='Parti kongre haberi' if role=='party' else 'Yerel haberin kongre öncesi tarihli duyurusu; seçim tahmini sonuç değildir.')
    text=html_source_text(raw)
    if role=='party':
        start=text.find('Emek Partisi (EMEP) Gebze İlçe Örgütünün 11. Olağan Kongresi');assert start>=0;end=text.find('</p>',start);exact=text[start:end];section='Partinin kongrenin gerçekleştiğine ilişkin haberi'
    else:
        exact='11 Ekim Pazar</strong> günü saat <strong>13.00</strong>';assert exact in text;section='Kongre öncesi duyurulan tarih'
    add('passage',id=ident+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)
    print(role,sha,view['view_id'])
out=Path(__file__).parent/'gebze-congress-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=rows,status='source_read_package_pending',note='6 Ekim haberi 11 Ekim için plan/tahmin; 12 Ekim parti haberi gerçekleşen kongreyi bildirir. Yönetim seçimi sonucu veya kesin olay günü iki metinden çıkarılmaz.'),f,ensure_ascii=False,indent=2);f.write('\n')
