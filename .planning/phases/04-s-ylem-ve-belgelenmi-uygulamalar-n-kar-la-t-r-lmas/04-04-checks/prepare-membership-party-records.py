import hashlib,json,sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes

root=Path('data/practices/sources/yeni-parti');specs=[('49','9d7316486f89437e1172c1363b400ea13ee9173e49f060f47bf11dcd80780c6a','Üyelik sistemimiz açılmıştır. Herkesi YENİ Parti’ye üye olmaya davet ediyoruz.'),('50','112456905c1482483ad1c2b64b16346d87f6253dc285d6ea942e020326bcc764','YENİ Parti, dijital üyelik kayıt sürecini resmen başlattı.')];entries=[]
for num,digest,exact in specs:
    capture=Path('/tmp/gsd-0404-party'+num+'.json');raw=capture.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
    data=json.loads(raw);assert exact in data['icerik'] and exact.encode() in raw
    stamp=datetime.fromisoformat(data['created_at'].replace('Z','+00:00'));localdate=stamp.astimezone(timezone(timedelta(hours=3))).date().isoformat();access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
    folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
    for name,content in [('original.json',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
        dest=folder/name
        if dest.exists():assert dest.read_bytes()==content
        else:dest.write_bytes(content)
    url='https://api.yeni-parti.org.tr/api/haberler/'+num;ident='0404-yeni-parti-haber-'+num
    rows=[('document',dict(id=ident,party_id='yeni-parti',title=data['baslik'],source_kind='party')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=localdate,version_label='Kamuya açık JSON yayını; created_at '+data['created_at']+' (Türkiye günü '+localdate+').',accessed_at=access,verified_at=checked,mime='application/json',sha256=digest,original_path='objects/'+digest+'/original.json',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),('passage',dict(id=ident+'-uyelik-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Üyelik sistemi duyurusu',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=ident+'-v1',kind='party_publication',publisher='Yeni Parti',author=None,social_handle=None,published_at=localdate,date_precision='day',public_url=url,basis='JSON başlık, yayımlanan içerik ve UTC created_at Türkiye saatine çevrilerek okundu.'))]
    entries += [dict(kind=k,values=v) for k,v in rows];print(num,localdate)
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/membership-party-records-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n')
