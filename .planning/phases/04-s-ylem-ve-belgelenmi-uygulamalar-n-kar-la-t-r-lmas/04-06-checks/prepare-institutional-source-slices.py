"""Owner-scoped kaynak pasaj taslakları; kullanım öncesi paket ve source gate gerektirir."""
import json
import sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text, pdf_page_text

root=Path('data/practices/sources/dem')
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
caps={x['id']:x for x in json.loads((checks/'institutional-captures.json').read_text())}
snippets={
 'calli':('gazete','Şükrü Çallı ön seçim ve itiraz','itirazda bulundum. İtirazım seçim kanunu ve seçim işlerine ilişkin içtihatlara aykırı bir şekilde reddedildi.','Tahir Dayan'),
 'calli_reply':('gazete','DEM Hakkâri örgütünün ön seçim itirazına cevabı','Yapılan incelemeler sonucunda yaptığı itirazın hiçbir maddi dayanağı olmadığı kararına varılmış ve bu karar kendisine tebliğ edilmiştir.','Tahir Dayan'),
 'silopi':('party','DEM Silopi disiplin açıklaması','Disiplin Kurulu, yürüttüğü sürecin ardından 6 Ağustos 2025 tarihinde Jiyan Ormanlı’nın partimizden ihraç edilmesine karar vermiştir.',None),
 'silopi_dha':('gazete','DHA Silopi sevk ve ihraç haberi','2 Temmuz’da kesin ihraç istemiyle Merkez Disiplin Kurulu’na sevk edilen', 'Sekvan Küden ve Mehmet Selim Yalçın'),
 'ipek':('party','DEM Kızıltepe disipline sevk açıklaması','Devamında ise “kesin ihraç” istemiyle DEM Parti Merkez Disiplin Kuruluna sevk edilmiştir.',None),
 'women_report':('official','TBMM taslak rapora basın toplantısı','dinlemek istedikleri bazı sivil toplum örgütlerinin komisyon toplantılarına davet edilmemesini eleştirdi.',None),
}
entries=[]
def add(kind, values): entries.append(dict(kind=kind,values=values))
for name,(typ,title,exact,author) in snippets.items():
 c=caps[name]; ident='0406-'+name.replace('_','-'); v=ident+'-v1'; raw=(root/c['original_path']).read_bytes(); assert exact in html_source_text(raw),(name,exact)
 sk={'gazete':'journalism','party':'party','official':'official'}[typ]
 add('document',dict(id=ident,party_id='dem',title=title,source_kind=sk))
 add('document_version',dict(id=v,document_id=ident,original_url=c['url'],final_url=c['url'],document_date=c['document_date'],version_label='Yayınlanan HTML; özgün baytlar',accessed_at=c['accessed_at'],verified_at=c['accessed_at'],mime='text/html',sha256=c['sha256'],original_path=c['original_path'],readable_path=c['readable_path'],date_precision='day',date_unknown_reason=None))
 add('archive_view',c['view'])
 add('passage',dict(id=ident+'-p',version_id=v,exact=exact,prefix=None,suffix=None,article=None,section=title,pdf_page_index=None,printed_page=None))
 add('source_attribution',dict(version_id=v,kind='party_publication' if typ=='party' else sk,publisher='DEM Parti' if typ=='party' else c['publisher'],author=author,social_handle=None,published_at=c['document_date'],date_precision='day',public_url=c['url'],basis=('Parti açıklaması Demokratik Yerel Yönetimler Kuruluna atfedilir.' if typ=='party' else 'Yayıncı, yayın tarihi ve ilgili kaynak bağlamı incelendi.')))
c=json.loads((checks/'capture-101831.json').read_text()); ident='0406-tbmm-101831';v=ident+'-v1';path=Path(c['original_path']);url=c['original_url']
add('document',dict(id=ident,party_id='dem',title='10 Ekim 2024 TBMM 6. Birleşim tutanağı ve 10/1831',source_kind='official'))
add('document_version',dict(id=v,document_id=ident,original_url=url,final_url=url,document_date='2024-10-10',version_label='28. dönem 3. yasama yılı 6. birleşim basılı tutanak',accessed_at=c['accessed_at'],verified_at=c['verified_at'],mime='application/pdf',sha256=c['sha256'],original_path='objects/'+c['sha256']+'/original.pdf',readable_path='objects/'+c['sha256']+'/readable.html',date_precision='day',date_unknown_reason=None))
parts=[('submission',16,'1.- DEM PARTİ Grubu adına Grup Başkanvekili Kars Milletvekili Gülüstan Kılıç Koçyiğit’in,\nkadın cinayetleri başta olmak üzere kadına yönelik her türlü şiddetin önlenmesi ve toplumsal cinsiyet\neşitliği politikalarının uygulanabilmesi amacıyla bir Meclis araştırması açılmasına ilişkin önergesi\n(10/1831) (Başkanlığa geliş tarihi: 10.10.2024)'),('result',69,'Şimdi, Meclis araştırması açılıp açılmaması hususunu oylarınıza sunuyorum: Meclis araştırması\naçılmasını kabul edenler... Kabul etmeyenler... Kabul edilmiştir.\nMeclis araştırmasını yapacak komisyonun 22 üyeden kurulmasını oylarınıza sunuyorum: Kabul\nedenler... Kabul etmeyenler... Kabul edilmiştir.')]
for name,page,exact in parts:
 assert exact in pdf_page_text(path.resolve(),page),name
 add('passage',dict(id=ident+'-'+name+'-p',version_id=v,exact=exact,prefix=None,suffix=None,article=None,section='Önerge sunuşu' if name=='submission' else 'Birleştirilmiş görüşme ve komisyon kararı',pdf_page_index=page,printed_page=None))
add('source_attribution',dict(version_id=v,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at='2024-10-10',date_precision='day',public_url=url,basis='Resmî basılı Genel Kurul tutanağı, önerge ve karar sayfaları okundu.'))
(checks/'institutional-source-slices-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries,exclusions=['2023 sonrası yeni Yeşil Sol Parti kaynağı kimlik ayrımı için kullanıldı, DEM parti kaynağı olarak eklenmedi.']),ensure_ascii=False,indent=2)+'\n')
print('SOURCE_SLICES_DRAFT',len(entries))
