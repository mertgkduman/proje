from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

here=Path(__file__).resolve().parent; root=Path('data/practices/sources/saadet'); now=datetime.now(timezone.utc).isoformat(); entries=[]; paths=set()
def add(table,**values): entries.append(dict(kind=table,values=values))
def put(rel,raw):
 p=root/rel; p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): assert p.read_bytes()==raw
 else: p.write_bytes(raw)
 paths.add(str(p))
sources=[
 ('speech','/tmp/saadet-563-tbmm26.pdf','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/26/Tam/1cf85bb5-760b-40b9-aefb-c83726a61322.pdf','2025-12-08','pdf',[(0,'proposal','1/280 2026 bütçe teklifi','2026 Yılı Merkezi Yönetim Bütçe Kanunu Teklifi (1/280)'),(16,'authority','Yeni Yol grubu süresinin Arıkana devri',"Saadet Partisi Genel Başkanı ve Kayseri\nMilletvekili Mahmut Arıkan'a devredilmiştir."),(18,'stance','Arıkanın bütçenin zihniyetine itirazı','biz sadece rakamları değil bu bütçenin arkasındaki liyakatsiz, güvencesiz ve adaletsiz zihniyeti de reddediyoruz.')]),
 ('vote','/tmp/saadet-budget39.pdf','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/39/Basilmis/b7954d72-112c-4f16-8b75-f67759cc1c77.pdf','2025-12-21','pdf',[(79,'kaya-speech','Bülent Kaya Yeni Yol Grubu ret açıklaması','Biz YENİ YOL Grubu\nolarak bu bütçeye “ret” oyu vereceğiz.'),(165,'kaya-vote','Bülent Kaya kesin oy satırı','İstanbul Kaya Bülent YENİ YOL Ret Ret'),(167,'arikan-vote','Mahmut Arıkan kesin oy satırı','Kayseri Arıkan Mahmut SAADET PARTİSİ Katılmadı Katılmadı'),(158,'totals','226 ve 227 sütunlu kesin sonuç tablosu','Sıra Sayısı : 226 Sıra Sayısı : 227')]),
 ('law','/tmp/saadet-budget-law.html','https://tbmm.gov.tr/Yasama/Kanun/B34C89EB-EC10-4B82-834F-0199F0E94541',None,'html',[(None,'number','7567 sayılı bütçe kanunu sicili','7567'),(None,'adopt','Kanunun kabul tarihi','21/12/2025'),(None,'gazette','Resmî Gazete tarihi ve sayısı','33124 (1. M&#xFC;k)')]),
]
for key,filename,url,day,ext,anchors in sources:
 p=Path(filename); raw=p.read_bytes(); digest=sha256(raw).hexdigest(); doc='0411-budget-1280-'+key; vid=doc+'-v1'; original=f'objects/{digest}/original.'+('pdf' if ext=='pdf' else 'html.bin'); readable=f'objects/{digest}/readable.html'; put(original,raw); put(readable,readable_bytes(raw,ext,legacy=False))
 add('document',id=doc,party_id='saadet',title='1/280 bütçe konuşması ve oylaması: '+key,source_kind='official')
 add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'Sicil sayfasının ilk yayın günü açık.',version_label='TBMM özgün nüshası.',accessed_at=datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,mime='application/pdf' if ext=='pdf' else 'text/html',sha256=digest,original_path=original,readable_path=readable)
 add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',published_at=day,date_precision='day' if day else 'unknown',social_handle=None,public_url=url,basis='Belge, işlem ve erişim tarihleri ayrı kaydedildi.')
 if ext=='html':
  view=build_view(raw,url,root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view); manifest=root/view['manifest_path']; paths.add(str(manifest)); paths.update(str(manifest.parent/name) for name in json.loads(manifest.read_bytes())['files'])
 for page,suffix,section,exact in anchors:
  body=pdf_page_text(root/original,page) if ext=='pdf' else html_source_text(raw)
  if key=="vote" and suffix=="totals": exact=body[body.index("Sıra Sayısı : 226"):body.index("İli Soyadı Adı Parti")].strip()
  assert exact in body,(key,suffix,repr(exact)); add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)
(here/'budget-1280-source-records.json').write_text(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-budget1280-paths').write_text('\n'.join(sorted(paths))+'\n'); print(len(entries),len(paths))
