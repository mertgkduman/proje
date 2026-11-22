import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root=Path('data/practices/sources/yeni-parti')
specs=[
 ('104641','cbb473b64cb905bcb64df7dc6937a58b448f1fa676d8b202d56ddfaee14a6865','35801ab5-85b1-4318-8a53-01a11b8bb800','Artan okul masraflar&#x131;','10/4641 okul masrafları araştırma önergesi'),
 ('104975','30227263499f5d3d509d11951edd17a059e7ace2d4aaf8e117764f066f4e97b2','1f0d45c3-5602-4965-a724-01a1abe8d35d','MESEM uygulamalar&#x131; ile','10/4975 MESEM ve iş kazaları araştırma önergesi'),
 ('104955','bfd0cc2131df01e7cf4ac6729b50b05459988d159fc9b45d0a342c57476bd9bc','49081965-6eb5-4f30-96bf-01a1a072c472','&#x130;&#x15F; kazalar&#x131; ve meslek','10/4955 iş kazaları araştırma önergesi'),
]
entries=[]
for num,digest,uuid,start,title in specs:
    capture=Path('/tmp/gsd-0404-'+num+'.html');raw=capture.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
    folder=root/'objects'/digest;folder.mkdir(parents=True,exist_ok=True)
    for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
        dest=folder/name
        if dest.exists(): assert dest.read_bytes()==content
        else: dest.write_bytes(content)
    url='https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/'+uuid; ident='0404-tbmm-egitim-is-'+num
    view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=ident+'-v1';validate_view(root,view)
    text=html_source_text(raw);i=text.find(start);j=text.find('</td>',i);assert i>=0 and j>i and '10 / '+num[2:] in text
    access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds');checked=datetime.now(timezone.utc).isoformat(timespec='seconds')
    rows=[('document',dict(id=ident,party_id='yeni-parti',title=title,source_kind='official')),('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url.replace('www.tbmm.gov.tr','tbmm.gov.tr'),document_date=None,version_label='TBMM dinamik kayıt sayfası; yakalanan HTML',accessed_at=access,verified_at=checked,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Dinamik sayfanın yayın tarihi bilinmiyor; önerge tarihi ayrı kaydedilir.')),('archive_view',view),('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=text[i:j],prefix=None,suffix=None,article=None,section=title+' özeti',pdf_page_index=None,printed_page=None)),('source_attribution',dict(version_id=ident+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM kurumsal başlığı ve kayıt künyesi incelendi.'))]
    entries += [dict(kind=k,values=v) for k,v in rows];print(num,view['view_id'])
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks/education-work-records-draft.json');p.write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n')
