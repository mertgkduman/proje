from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here=Path(__file__).resolve().parent
root=Path('data/practices/sources/saadet')
entries=[]; paths=set(); now=datetime.now(timezone.utc).isoformat()
def add(table, **row): entries.append({'kind':table,'values':row})
def put(rel,raw):
    target=root/rel; target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists(): assert target.read_bytes()==raw
    else: target.write_bytes(raw)
    paths.add(str(target))
sources=[
 ('statement','party-news-bodies/383.json','https://admin.saadet.org.tr/veriler/api.php?resource=haber_detay&kod=her-seyin-pahali-oldugu-ulkemizde-insan-cani-neden-bu-kadar-ucuz','2023-02-22','Saadet Partisi','party','party_publication','application/json','2026-11-24T20:55:14.641905+00:00','Parti API damgasının Türkiye yerel günü 22 Şubat 2023.', [('call','Karamollaoğlunun yüz yüze eğitim çağrısı','üniversiteler derhal yüz yüze eğitime başlamalıdır',None)]),
 ('yok','education-2023-tbmm-7-193-original.pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y1/T7/WebOnergeMetni/f25afa0d-2c02-42dd-a5ae-f6bf514186ef.pdf','2023-03-31','Yükseköğretim Kurulu','official','official','application/pdf','2026-11-24T20:07:25.624924+00:00','TBMM 7/193 soru cevabı ekindeki 31 Mart tarihli 23957 sayılı YÖK yazısı.', [('decision','30 Mart Genel Kurul değerlendirmesi','30.03.2023 tarihli Yükseköğretim Genel Kurul toplantısında yapılan değerlendirme',6),('effective','3 Nisan başlangıcı','03.04.2023 tarihi itibarıyla',6),('choice','Uzaktan öğretim sürerken yüz yüze seçenek','isteyen öğrencilere devam şartı\naranmaksızın sınıflarda yüz yüze eğitim verilebilmesine,',6),('university','Üniversite kurulları yetkisi','verilebilmesine ilişkin kararları ilgili kurullarında alarak gerekli düzenlemeleri yapmalarına,',6)])]
for key,name,url,day,publisher,kind,attribution,mime,accessed,basis,anchors in sources:
    raw=(here/name).read_bytes(); h=sha256(raw).hexdigest(); doc='0411-education-2023-'+key; vid=doc+'-v1'
    media='pdf' if mime=='application/pdf' else 'html'; original=f'objects/{h}/original.'+('pdf' if media=='pdf' else 'html.bin'); readable=f'objects/{h}/readable.html'
    put(original,raw); put(readable,readable_bytes(raw,media,legacy=False))
    add('document',id=doc,party_id='saadet',title='2023 yükseköğretim '+key,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,date_precision='day',date_unknown_reason=None,version_label=basis,accessed_at=accessed,verified_at=now,mime=mime,sha256=h,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=None,kind=attribution,published_at=day if key=='statement' else None,date_precision='day' if key=='statement' else 'unknown',social_handle=None,public_url=url,basis=basis)
    if media=='html':
        view=build_view(raw,url,root,fetch_assets=False); view['version_id']=vid; validate_view(root,view); add('archive_view',**view)
        manifest=root/view['manifest_path']; paths.add(str(manifest)); paths.update(str(manifest.parent/n) for n in json.loads(manifest.read_bytes())['files'])
    for suffix,section,exact,page in anchors:
        text=pdf_page_text(root/original,page) if page is not None else html_source_text(raw)
        assert exact in text,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)
(here/'education-2023-source-records.json').write_text(json.dumps({'party_id':'saadet','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0411-education-2023-paths').write_text('\n'.join(sorted(paths))+'\n')
print('entries',len(entries),'paths',len(paths))
