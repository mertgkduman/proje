"""Her iki TBMM esas numarası için özgün ayrıntı sayfası taslak pasajları."""
import json
from pathlib import Path
from arsiv import html_source_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
source=Path('data/practices/sources/dem')
out=[]
for number in ('103464','103465'):
    x=json.loads((p/(number+'-capture.json')).read_text())[0]
    text=html_source_text((source/x['original_path']).read_bytes())
    document='0406-tbmm-'+number+'-detail'; version=document+'-v1'
    out.append({'kind':'document','values':dict(id=document,party_id='dem',title='TBMM '+number[:2]+'/'+number[2:]+' araştırma önergesi ayrıntıları',source_kind='official')})
    out.append({'kind':'document_version','values':dict(id=version,document_id=document,original_url=x['original_url'],final_url=x['final_url'],document_date=None,version_label='TBMM araştırma önergesi ayrıntısı; erişim sırasındaki görünüm',accessed_at=x['accessed_at'],verified_at=x['accessed_at'],mime='text/html',sha256=x['sha256'],original_path=x['original_path'],readable_path=x['readable_path'],date_precision='unknown',date_unknown_reason='Ayrıntı sayfasının yayım ve güncelleme tarihi belirlenmedi.')})
    view=dict(x['view']);view['version_id']=version
    out.append({'kind':'archive_view','values':view})
    out.append({'kind':'source_attribution','values':dict(version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=x['original_url'],basis='TBMM resmî detay sayfasının esas numarası ve başkanlığa geliş tarihi okundu; güncel durum kesim tarihi için varsayılmadı.')})
    for suffix,exact,section in [('number','10 / '+number[2:],'Esas numarası'),('received','03/12/2025','Başkanlığa geliş tarihi')]:
        assert text.count(exact)>=1,(number,suffix)
        out.append({'kind':'passage','values':dict(id='0406-tbmm-'+number+'-detail-'+suffix+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)})
(p/'2025-detail-source-slices-draft.json').write_text(json.dumps({'status':'draft_unvalidated','entries':out},ensure_ascii=False,indent=2)+'\n')
print('TWO_DETAIL_PAGES_SOURCE_EXACT_PASS',len(out))
