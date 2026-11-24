from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here=Path(__file__).resolve().parent
root=Path('data/practices/sources/saadet')
now=datetime.now(timezone.utc).isoformat()
entries=[]
paths=set()
def add(table, **row): entries.append({'kind':table,'values':row})
def put(rel, raw):
    path=root/rel
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists(): assert path.read_bytes()==raw
    else: path.write_bytes(raw)
    paths.add(str(path))
sources=[
 ('party','party-news-bodies/443.json','https://admin.saadet.org.tr/veriler/api.php?resource=haber_detay&kod=dostum-trump-demekle-filistine-dusmanim-demek-ayni-mahiyettedir','2024-11-08','Saadet Partisi','application/json','html'),
 ('prior','agriculture-2023-tbmm-original.html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/39/Tam/464b5cb6-aa99-40c5-a6d8-d5906e72304d.html','2023-12-18','TBMM','text/html','html'),
 ('ministry','agriculture-2025-ministry-original.html','https://www.tarimorman.gov.tr/Haber/6721/2025-Genel-Tarim-Sayimi','2025-09-02','Tarım ve Orman Bakanlığı','text/html','html'),
 ('circular3','agriculture-2025-tuik-circular3-original.pdf','https://www.tuik.gov.tr/media/corporatecontent/tuik-uc-nolu-genelge.pdf',None,'TÜİK','application/pdf','pdf')]
for key,name,url,day,publisher,mime,fmt in sources:
    raw=(here/name).read_bytes(); h=sha256(raw).hexdigest(); doc='0411-agriculture-2025-'+key; vid=doc+'-v1'
    original=f'objects/{h}/original.'+('pdf' if fmt=='pdf' else 'html.bin'); readable=f'objects/{h}/readable.html'
    put(original,raw); put(readable,readable_bytes(raw,fmt,legacy=False))
    add('document',id=doc,party_id='saadet',title='2025 Genel Tarım Sayımı: '+key,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'Genelge üzerinde yayım günü belirtilmemiştir.',version_label='Parti API özgün JSON gövdesi.' if key=='party' else 'TÜİK 3 numaralı genelge.' if key=='circular3' else 'Bakanlık özgün duyurusu.',accessed_at=datetime.fromtimestamp((here/name).stat().st_mtime,timezone.utc).isoformat(),verified_at=now,mime=mime,sha256=h,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=None,kind='official',published_at='2024-11-08' if key=='party' else None,date_precision='day' if key=='party' else 'unknown',social_handle=None,public_url=url,basis='Parti API yayım günü ve özgün JSON; kullanıcı sayfası https://saadet.org.tr/dostum-trump-demekle-filistine-dusmanim-demek-ayni-mahiyettedir.' if key=='party' else 'Kurumun özgün belgesi; kaynak yayım saati ayrıca bilinmiyor.')
    if fmt=='html':
        view=build_view(raw,url,root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view)
        m=root/view['manifest_path']; paths.add(str(m)); paths.update(str(m.parent/n) for n in json.loads(m.read_bytes())['files']); body=html_source_text(raw)
    else: body=pdf_page_text(root/original,0)
    anchors={'party':[('identity','Parti kaynağı Kılıcın basın toplantısı sıfatını bildirir','Antalya Milletvekilimiz Şerafettin Kılıç, TBMM’de düzenlediği basın toplantısında gündeme ilişkin değerlendirmelerde bulundu.'),('call','Kılıcın yeni tarım sayımı çağrısı','Yeni bir tarım sayımının ivedilikle yapılması gerekmektedir.')],
      'prior':[('plan','Bakanın 2023 yılı protokol ve sayım planı','TÜİK’le imzaladığımız protokol kapsamında genel tarım sayımı 2026 sonunda tamamlanacaktır.')],
      'ministry':[('start','Bakanlığın sayım başlangıcı','<strong>1 Temmuz 2025</strong> tarihi itibarıyla başlamıştır.')],
      'circular3':[('extension','TÜİK veri derleme süresini uzatıyor','süreci 30.01.2026 tarihine kadar uzatılmıştır.')]}[key]
    for suffix,section,exact in anchors:
        assert exact in body,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=0 if fmt=='pdf' else None,printed_page=None)
(here/'agriculture-2025-source-records.json').write_text(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-agriculture-paths').write_text('\n'.join(sorted(paths))+'\n')
print('source entries',len(entries),'paths',len(paths))
