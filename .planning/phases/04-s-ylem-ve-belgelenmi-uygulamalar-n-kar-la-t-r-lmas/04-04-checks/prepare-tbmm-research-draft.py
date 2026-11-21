"""Bind captured TBMM records without inventing the HTML publication date."""
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text
from arsiv_gorunum import build_view, validate_view

root=Path('data/practices/sources/yeni-parti')
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
sources=[
 ('0404-tbmm-cemevi','41c44e624cc0150ad807987ef9c51b7a29e0613717cd2f46404cd1d614e6ec25','https://tbmm.gov.tr/Yasama/KanunTeklifi/b9b7a30e-b2b6-4a6f-9fe8-01a0fc6c49d7','2026-11-21T19:21:11.906467+00:00','2/3917 Cemevlerine ibadethane statüsü kanun teklifi','2 / 3917','Esas numarası ve 2 Ekim 2026 geliş tarihi'),
 ('0404-tbmm-siyasi-etik','7ebc13704b17ff99f4559585ce756a17880ee58dd3b8a11e31bcf7b98b272e41','https://tbmm.gov.tr/Yasama/KanunTeklifi/5bb86db7-fd76-4c2e-ad4d-019fcd078d88','2026-11-21T19:25:20.210400+00:00','2/3795 Siyasi Etik Kanunu Teklifi','Siyasi Etik Kanunu Teklifi','Teklif başlığı ve 4 Ağustos 2026 geliş tarihi'),
 ('0404-tbmm-gelen-kagit','49b7ab23335abc63a62806e6ff51e71c58b4248b6bc8a013867dfdaed0288f82','https://tbmm.gov.tr/Gundem/GelenKagitDetay/a23ef9a0-a971-46ea-b750-019fc805f5a7','2026-11-21T19:25:20.993088+00:00','TBMM gelen kâğıtları: 2/3790–2/3792','Yeni Parti Genel Başkanı Manisa Milletvekili &Ouml;zg&uuml;r &Ouml;zel ve Grup Başkanvekilleri Ankara Milletvekili Murat Emir, İstanbul Milletvekili G&ouml;khan G&uuml;naydın ve Mersin Milletvekili Ali Mahir Başarır&#39;ın; Asgari &Uuml;cretin Artırılması','3 Ağustos 2026 asgari ücret teklifi imza sahipleri')
]
sources.append(('0404-tbmm-asgari-ucret','e14f477b9b839b4edc82752ec92d835a04375f21d42776984f2c7495382357b3','https://tbmm.gov.tr/Yasama/KanunTeklifi/99085cfc-46b5-46b8-b34d-019fc7aca761','2026-11-21T19:32:00.679824+00:00','2/3790 Asgari ücretin artırılması kanun teklifi','Teklif ile, asgari &#xFC;cretin ayl&#x131;k net 45.800 T&#xFC;rk liras&#x131; olacak &#x15F;ekilde art&#x131;r&#x131;lmas&#x131; ve sigorta primi i&#x15F;veren pay&#x131;n&#x131;n bir k&#x131;sm&#x131;n&#x131;n Hazinece kar&#x15F;&#x131;lanmas&#x131; ama&#xE7;lanmaktad&#x131;r.','TBMM teklif özeti; güncel sayfanın komisyon kaydı ayrıca görülmeli'))
sources=[('0404-tbmm-yargi-4551', '6f20ae47f079311c791fb3e24f9bde51bc273f81b2194ac6f16f996fcf09cbd0', 'https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/924cbdcb-8da6-4dac-8a8a-01a0f6a0da6d', '2026-11-21T20:12:54.425248+00:00', '10/4551 yargı bağımsızlığı araştırma önergesi', '10 / 4551', '30 Eylül yargı araştırma önergesi esas numarası'), ('0404-tbmm-cocuk-4682', 'e6e1ed43685b649ca1ad503536afbd035b22697000ded4eb67fe3a2b7625d2b4', 'https://www.tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/5faeaf2a-f67f-49e9-b03a-01a143fa54df', '2026-11-21T20:13:24.415448+00:00', '10/4682 çocuk yoksulluğu araştırma önergesi', '10 / 4682', '12 Ekim çocuk yoksulluğu önergesi esas numarası')]
entries=[]
for identity,digest,url,accessed,title,exact,section in sources:
    origin=root/digest; raw=(origin/'original.html.bin').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==digest and exact in html_source_text(raw)
    target=root/'objects'/digest; target.mkdir(parents=True,exist_ok=True)
    for name in ('original.html.bin','readable.html'):
        src,dst=origin/name,target/name
        if dst.exists(): assert dst.read_bytes()==src.read_bytes()
        else: shutil.copyfile(src,dst)
    view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8'); view['version_id']=identity+'-v1'; validate_view(root,view)
    values=[('document',dict(id=identity,party_id='yeni-parti',title=title,source_kind='official')),
      ('document_version',dict(id=identity+'-v1',document_id=identity,original_url=url,final_url=url,document_date=None,version_label='TBMM dinamik kayıt sayfası; yakalanan HTML',accessed_at=accessed,verified_at=accessed,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html',date_precision='unknown',date_unknown_reason='Kayıt sayfasının yayın tarihi belirtilmiyor; teklife ait geliş tarihi sayfada ayrıca yer alıyor.')),
      ('archive_view',view),('passage',dict(id=identity+'-p',version_id=identity+'-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)),
      ('source_attribution',dict(version_id=identity+'-v1',kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM resmî kayıt sayfasının kurumsal başlığı ve teklif künyesi incelendi.'))]
    entries += [dict(kind=kind,values=value) for kind,value in values]
(p/'tbmm-research-records-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n')
print('TBMM_RECORDS_DRAFT',len(entries))
