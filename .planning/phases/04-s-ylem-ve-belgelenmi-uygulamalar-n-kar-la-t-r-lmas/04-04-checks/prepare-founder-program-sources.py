import hashlib,json,sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text,readable_bytes

root=Path('data/practices/sources/yeni-parti');entries=[]
for num,digest in [('287','243cb46d1ab7ae32710d7be7a33d48240a010fbf99891b49201286603441a415'),('290','6973786efe8630e7d3b8af0e7f9f6799b10f6f93365595d19410136363871162')]:
    capture=Path('/tmp/gsd-0404-party'+num+'.json');raw=capture.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest;data=json.loads(raw);exact='Özgür Özel’in Kuruluş Kurultayı Genel Başkanlık Çalışma Programı kitapçığına buradan ulaşabilirsiniz.';assert exact in data['icerik'] and exact.encode() in raw
    folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
    for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
        dest=folder/name
        if dest.exists():assert dest.read_bytes()==content
        else:dest.write_bytes(content)
    url='https://api.yeni-parti.org.tr/api/haberler/'+num;ident='0404-yeni-parti-haber-'+num;stamp=datetime.fromisoformat(data['created_at'].replace('Z','+00:00'));day=stamp.astimezone(timezone(timedelta(hours=3))).date().isoformat();access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
    rows=[('document',dict(id=ident,party_id='yeni-parti',title=data['baslik'],source_kind='party')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=day,version_label='Parti JSON duyurusu; created_at '+data['created_at'],accessed_at=access,verified_at=checked,mime='application/json',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Çalışma programı kitapçığı duyurusu',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=ident+'-v1',kind='party_publication',publisher='Yeni Parti',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='JSON içeriği ve UTC oluşturma zamanı Türkiye gününe çevrilerek okundu; ayrı yayın tarihi belirlenmedi.'))]
    entries += [dict(kind=k,values=v) for k,v in rows]
capture=Path('/tmp/gsd-0404-kurultay-program.pdf');raw=capture.read_bytes();digest=hashlib.sha256(raw).hexdigest();assert digest=='a78eb2daf884f0ac432eb7fd4cc2f12d3e08957294c8243ac666fdf7fcf65180';folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
for name,content in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
    dest=folder/name
    if dest.exists():assert dest.read_bytes()==content
    else:dest.write_bytes(content)
page=pdf_page_text(capture,10);exact='1. Üyelik başvurusu, değerlendirme, bildirim ve itiraz süreçlerini açık kurallarla yürüteceğiz.';assert exact in page
url='https://cdn.yeni-parti.org.tr/site/calisma_programi.pdf';ident='0404-ozel-kurultay-calisma-programi';access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='yeni-parti',title='Özgür Özel kuruluş kurultayı çalışma programı',source_kind='party')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date='2026-11-05',version_label='Kapak 5 Kasım 2026; 7 ve 8 Kasım duyuruları aynı adrese bağlanır; yakalanan baytların o günkü sürümle özdeşliği ayrıca belirlenmedi.',accessed_at=access,verified_at=checked,mime='application/pdf',sha256=digest,original_path='objects/'+digest+'/original.pdf',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),('passage',dict(id=ident+'-uyelik-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Üyelik hakları ve dijital katılım',pdf_page_index=10,printed_page='7')),('source_attribution',dict(version_id=ident+'-v1',kind='party_publication',publisher='Yeni Parti',author='Özgür Özel',social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Kapak, 5 Kasım belge tarihi ve yazar kimliği; 7–8 Kasım duyurularında URL bağı okundu. PDF XMP üretimi yayın tarihi sayılmaz.'))]
entries += [dict(kind=k,values=v) for k,v in rows];p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/founder-program-sources-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n');print('records',len(entries))
