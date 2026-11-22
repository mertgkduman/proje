"""Komisyon devam kaynaklarına ait pasif, atıflı pasaj taslağı."""
import json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text,pdf_page_text
root=Path('data/practices/sources/dem');checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
caps=json.loads((checks/'commission-captures.json').read_text());entries=[]
def add(k,v):entries.append(dict(kind=k,values=v))
for c in caps:
 name=c['id']; ident='0406-'+name.replace('_','-');version=ident+'-v1';is_pdf=c['mime']=='application/pdf';is_party=name=='dem_12subat'
 title={'komisyon_12subat':'TBMM kadın şiddeti komisyonu 16. toplantı tutanağı','dem_12subat':'DEM komisyon toplantısından ayrılma açıklaması','aa_komisyon':'Kadına şiddet komisyonu taslak raporu haberi'}[name]
 exact={'komisyon_12subat':'DEM PARTİ milletvekilleri, Zahide Yetiş’in bazı ifadeleri nedeniyle Komisyon toplantı salonunu terk etti.','dem_12subat':'Bu sebeple DEM Partili komisyon üyesi kadınlar olarak bugünkü komisyon toplantısını terk ettik…','aa_komisyon':'113 ek tespit ve öneri sunuldu.'}[name]
 raw=(root/c['original_path']).read_bytes();assert exact in (pdf_page_text((root/c['original_path']).resolve(),1) if is_pdf else html_source_text(raw))
 source='official' if is_pdf else ('party' if is_party else 'journalism')
 add('document',dict(id=ident,party_id='dem',title=title,source_kind=source))
 add('document_version',dict(id=version,document_id=ident,original_url=c['url'],final_url=c['url'],document_date=c['date'],version_label='Özgün tutanak veya yayınlanan HTML',accessed_at=c['accessed_at'],verified_at=c['accessed_at'],mime=c['mime'],sha256=c['sha256'],original_path=c['original_path'],readable_path=c['readable_path'],date_precision='day',date_unknown_reason=None))
 if c['view']:add('archive_view',c['view'])
 add('passage',dict(id=ident+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=title,pdf_page_index=1 if is_pdf else None,printed_page=None))
 add('source_attribution',dict(version_id=version,kind='party_publication' if is_party else source,publisher=c['publisher'],author='İsa Toprak' if name=='aa_komisyon' else None,social_handle=None,published_at=c['date'],date_precision='day',public_url=c['url'],basis='Tarih, yayıncı ve özgün kaynakta ilgili bölüm okundu.'))
(checks/'commission-source-slices-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n')
print('COMMISSION_SOURCE_SLICES_DRAFT',len(entries))
