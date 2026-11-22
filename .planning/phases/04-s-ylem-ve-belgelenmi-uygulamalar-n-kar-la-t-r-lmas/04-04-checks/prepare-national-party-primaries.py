import hashlib,json,sys
from datetime import datetime,timezone,timedelta
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import readable_bytes

root=Path('data/practices/sources/yeni-parti');specs=[('289','cf8452a40626b75945985145ec73102287324840cf6c3700bd9987ff31c6e403','YENİ Parti Genel Başkanı Özgür Özel, partisinin Ankara İl Başkanlığında Genel Başkanlık Ön Seçimine katıldı.'),('291','5e1b0e0bdf4797c14b6c3d981c3439fca60f59572f339089517908bbb57c2d73','Ülke genelinde %81,3 katılım oranıyla sandığa giderek partisine ve geleceğine sahip çıkan, bizleri Genel Başkanlığa layık gören tüm üyelerimize yürekten teşekkür ediyorum.')];entries=[]
for num,digest,exact in specs:
    capture=Path('/tmp/gsd-0404-party'+num+'.json');raw=capture.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest;data=json.loads(raw);assert exact in data['icerik'] and exact.encode() in raw
    folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
    for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
        dest=folder/name
        if dest.exists():assert dest.read_bytes()==content
        else:dest.write_bytes(content)
    url='https://api.yeni-parti.org.tr/api/haberler/'+num;ident='0404-yeni-parti-haber-'+num;stamp=datetime.fromisoformat(data['created_at'].replace('Z','+00:00'));day=stamp.astimezone(timezone(timedelta(hours=3))).date().isoformat();access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
    rows=[('document',dict(id=ident,party_id='yeni-parti',title=data['baslik'],source_kind='party')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=day,version_label='Parti JSON yayını; created_at '+data['created_at']+' (Türkiye günü '+day+').',accessed_at=access,verified_at=checked,mime='application/json',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='day',date_unknown_reason=None)),('passage',dict(id=ident+'-onsecim-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Genel başkanlık ön seçimi parti açıklaması',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=ident+'-v1',kind='party_publication',publisher='Yeni Parti',author=None,social_handle=None,published_at=day,date_precision='day',public_url=url,basis='Parti JSON başlığı, içeriği ve UTC oluşturma zamanı Türkiye gününe çevrilerek okundu.'))]
    entries += [dict(kind=k,values=v) for k,v in rows];print(num,day)
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/national-party-primaries-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n')
