from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text,pdf_page_exists,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view
here=Path(__file__).resolve().parent; root=Path('data/practices/sources/saadet'); entries=[]; paths=set(); now=datetime.now(timezone.utc).isoformat()
def add(table,**row): entries.append({'kind':table,'values':row})
def put(rel,raw):
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists(): assert p.read_bytes()==raw
    else: p.write_bytes(raw)
    paths.add(str(p))
sources=[
 ('statement','party-news-bodies/380.json','https://admin.saadet.org.tr/veriler/api.php?resource=haber_detay&kod=sozde-yerli-ve-milliler','2023-01-18','Saadet Partisi','party','party_publication','application/json','2026-11-24T21:51:25.714316+00:00','Parti API damgasının Türkiye yerel günü 18 Ocak 2023.', [('call','Seçim kararı ve iki ay çağrısı','Bugün seçim kararı alınsın, en geç 2 ay içerisinde de seçime gidelim.',None)]),
 ('ysk','election-2023-ysk-90-original.pdf','https://www.resmigazete.gov.tr/eskiler/2023/03/20230310M2-1.pdf?download=1','2023-03-10','Yüksek Seçim Kurulu','official','official','application/pdf','2026-11-24T22:22:50.608144+00:00','10 Mart 2023 ve 2023/90 sayılı YSK kararı.', [('renew','Cumhurbaşkanı yenileme kararı','Cumhurbaşkanının 10.03.2023 tarihli ve 2023/121 sayılı kararı ile',1),('day','YSK oy verme günü kararı','14 Mayıs 2023 Pazar günü',2)]),
 ('floor','election-2023-tbmm-first-original.html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak20230120/28/1/1/Tam/3fa77d2f-e0ad-452d-81a1-83949e1c8487.html','2023-06-02','TBMM','official','official','text/html','2026-11-24T23:12:03.720841+00:00','28. Dönem 1. Birleşim tam tutanağı.', [('parliament','14 Mayıs milletvekili seçiminin yapılması','14 Mayıs 2023 tarihinde yapılan milletvekili genel seçimiyle',None),('president','Cumhurbaşkanı seçimi ilk ve ikinci turu','ilk turu 14 Mayıs 2023, ikinci turu da 28 Mayıs 2023 tarihinde yapılan Cumhurbaşkanı seçiminde',None)])]
for key,name,url,day,publisher,kind,attr,mime,accessed,basis,anchors in sources:
    raw=(here/name).read_bytes(); h=sha256(raw).hexdigest(); doc='0411-election-2023-'+key; vid=doc+'-v1'; media='pdf' if mime=='application/pdf' else 'html'; original=f'objects/{h}/original.'+('pdf' if media=='pdf' else 'html.bin'); readable=f'objects/{h}/readable.html'
    put(original,raw);put(readable,readable_bytes(raw,media,legacy=False)); add('document',id=doc,party_id='saadet',title='2023 seçim yenileme '+key,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day',date_unknown_reason=None,version_label=basis,accessed_at=accessed,verified_at=now,mime=mime,sha256=h,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=None,kind=attr,published_at=day if key=='statement' else None,date_precision='day' if key=='statement' else 'unknown',social_handle=None,public_url=url,basis=basis)
    if media=='html':
        view=build_view(raw,url,root,fetch_assets=False);view['version_id']=vid;validate_view(root,view);add('archive_view',**view);m=root/view['manifest_path'];paths.add(str(m));paths.update(str(m.parent/n) for n in json.loads(m.read_bytes())['files'])
    for suffix,section,exact,page in anchors:
        pid=doc+'-'+suffix
        if page is not None: assert pdf_page_exists(root/original,page) and not pdf_page_text(root/original,page).strip()
        else: assert exact in html_source_text(raw),(key,suffix)
        add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)
        if page is not None: add('manual_passage',passage_id=pid,checked_at=now,method='Özgün YSK karar sayfası Poppler görüntüsünde okundu.',reason='Bu sayfanın metin katmanı boş.')
(here/'election-2023-source-records.json').write_text(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n');Path('/tmp/gsd0411-election-2023-paths').write_text('\n'.join(sorted(paths))+'\n');print('entries',len(entries),'paths',len(paths))
