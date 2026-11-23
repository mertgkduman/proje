import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,'src')
from arsiv import readable_bytes
from arsiv_gorunum import build_view,validate_view
root=Path('data/practices/sources/tip'); here=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
items=[('ballot','/tmp/gsd-tip-iklim-ballot.html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/104/AcikOylamaSonuc/1abc0fa2-28a9-46b0-b91f-6b6cc340b619.html','f7df0eac646ee87b066a347118dca3c2e74e4e0f08db7084dcb4f95b0256aae4','windows-1254'),('news','/tmp/gsd-tip-iklim-anka.html','https://www.memurlar.net/haber/1132298/iklim-kanunu-teklifi-meclis-te-tepkiyle-karsilandi.html','7ccb883645dd5e576e52c9820f41dd6366001e27545c53fead3675c7539df95c','windows-1254'),('law','/tmp/gsd-tip-iklim-law.html','https://tbmm.gov.tr/Yasama/Kanun/a0d0d465-837b-41f0-bd57-0195237fad31','7cc55ef8965e0cf06950b200fcc50cec931c839981b9beda7e79974538c15b37','utf-8')]
for name,local,url,expected,charset in items:
 raw=Path(local).read_bytes(); h=hashlib.sha256(raw).hexdigest(); assert h==expected
 obj=root/'objects'/h; obj.mkdir(parents=True,exist_ok=True)
 for filename,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=True))]:
  dest=obj/filename
  if dest.exists(): assert dest.read_bytes()==content
  else: dest.write_bytes(content)
 view=build_view(raw,url,root,fetch_assets=False,http_charset=charset); view['version_id']='0405-tip-iklim-2927-'+name+'-v1';validate_view(root,view)
 receipt={'url':url,'sha256':h,'bytes':len(raw),'accessed_at':datetime.fromtimestamp(Path(local).stat().st_mtime,timezone.utc).isoformat(),'encoding':charset,'view':view,'limitations':'Erişim zamanı indirilen dosyanın son yazım zamanı olarak kaydedildi; sayfa henüz tam kaynak incelemesi ve paket kapılarından geçmedi.'}
 (here/('iklim-2927-'+name+'-capture.json')).write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
 print(name,h,view['view_id'])
