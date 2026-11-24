import datetime,hashlib,json
from pathlib import Path
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
c=Path(__file__).resolve().parent;root=Path('data/practices/sources/dem')
items=[('party',Path('/tmp/gsd-dem-tasimali-2024.html'),'https://www.demparti.org.tr/tr/tasimali-egitimde-yasanan-sorunlar/20353/','2024-09-19','text/html'),('register',Path('/tmp/gsd-dem-101783-register.html'),'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/f858f8ee-5bc8-4ce8-98b8-01921ddb8b07',None,'text/html'),('signed',Path('/tmp/gsd-dem-101783-signed.pdf'),'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y2/T10/WebOnergeMetni/54f6f3be-a5b0-49de-b69b-35644b47af60.pdf','2024-09-19','application/pdf')]
out={}
for key,path,url,date,mime in items:
 raw=path.read_bytes();h=hashlib.sha256(raw).hexdigest();folder=root/'objects'/h;folder.mkdir(parents=True,exist_ok=True);kind='pdf' if mime=='application/pdf' else 'html';original='original.pdf' if kind=='pdf' else 'original.html.bin'
 for name,data in [(original,raw),('readable.html',readable_bytes(raw,kind,legacy=False))]:
  dest=folder/name
  if dest.exists():assert dest.read_bytes()==data
  else:dest.write_bytes(data)
 item=dict(url=url,date=date,mime=mime,accessed_at=datetime.datetime.fromtimestamp(path.stat().st_mtime,datetime.timezone.utc).isoformat(),sha256=h,original_path=f'objects/{h}/{original}',readable_path=f'objects/{h}/readable.html')
 if kind=='html':
  v=build_view(raw,url,root,fetch_assets=False);v['version_id']='0406-101783-'+key+'-v1';validate_view(root,v);item['view']=v
 out[key]=item
party=html_source_text(items[0][1].read_bytes());reg=html_source_text(items[1][1].read_bytes());assert '19 Eylül 2024' in party and 'Köy okullarının kapanmasının' in party
assert '20/09/2024' in reg and '10 / 1783' in reg and 'G&#xFC;ndemde' in reg
assert pdf_page_text(items[2][1],0)=='10/1783'
(c/'tasimali-101783-capture.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False,indent=2))
