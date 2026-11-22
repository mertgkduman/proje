import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
root = Path('data/practices/sources/tip')
entries = []
def add(k, v): entries.append(dict(kind=k, values=v))

info = json.loads((p/'barinma-10mayis-capture.json').read_text())
doc='0405-tip-barinma-10mayis'; vid=doc+'-v1'; sha=info['sha256']; url=info['url']
raw=(root/'objects'/sha/'original.html.bin').read_bytes(); assert hashlib.sha256(raw).hexdigest()==sha
exact="3'ten fazla konutu olanlardan her ev için artan oranda vergi alınarak bir konut destek fonu oluşturulsun."
assert exact in html_source_text(raw)
add('document',dict(id=doc,party_id='tip',title='Erkan Baş: Yaşanan barınma krizi bir siyasal sistem krizidir',source_kind='journalism'))
add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url='https://www.indyturk.com/node/507986/siyaset/erkan-ba%C5%9F-ya%C5%9Fanan-bar%C4%B1nma-krizi-bir-siyasal-sistem-krizidir',document_date='2022-05-10',version_label='Independent Türkçe basın toplantısı haberi',accessed_at=info['accessed_at'],verified_at=info['accessed_at'],mime='text/html',sha256=sha,original_path=f'objects/{sha}/original.html.bin',readable_path=f'objects/{sha}/readable.html',date_precision='day',date_unknown_reason=None))
add('archive_view',info['view'])
add('source_attribution',dict(version_id=vid,kind='journalism',publisher='Independent Türkçe',author=None,social_handle=None,published_at='2022-05-10',date_precision='day',public_url=url,basis='Tarihli haber künye ve tüm gövdesi okundu; toplantı haber aktarımıdır.'))
for name,ex in [('fund',exact),('rental','kira yardımı yapmak')]:
 assert ex in html_source_text(raw)
 add('passage',dict(id=doc+'-'+name+'-p',version_id=vid,exact=ex,prefix=None,suffix=None,article=None,section='Konut ve kira krizi nasıl çözülür?',pdf_page_index=None,printed_page=None))

info=json.loads((p/'barinma-tip-capture.json').read_text()); doc='0405-tip-barinma-duyuru'; vid=doc+'-v1'; sha=info['sha256']; url=info['url']; raw=(root/'objects'/sha/'original.html.bin').read_bytes(); assert hashlib.sha256(raw).hexdigest()==sha
exact='Genel Başkanımız ve Milletvekilimiz Erkan Baş ile Milletvekilleri Sera Kadıgil, Ahmet Şık ve Barış Atay'
assert exact in html_source_text(raw)
add('document',dict(id=doc,party_id='tip',title='Konut Krizine Karşı Kanun Teklifi Sunduk',source_kind='party_publication'))
add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date='2022-05-19',version_label='TİP teklif duyurusu',accessed_at=info['accessed_at'],verified_at=info['accessed_at'],mime='text/html',sha256=sha,original_path=f'objects/{sha}/original.html.bin',readable_path=f'objects/{sha}/readable.html',date_precision='day',date_unknown_reason=None))
view=info['view'].copy(); view['version_id']=vid; add('archive_view',view)
add('source_attribution',dict(version_id=vid,kind='party_publication',publisher='Türkiye İşçi Partisi',author=None,social_handle=None,published_at='2022-05-19',date_precision='day',public_url=url,basis='Tarihli parti duyurusunun tam gövdesi ve yayın künyesi okundu.'))
add('passage',dict(id=doc+'-identity-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section='Teklif duyurusu',pdf_page_index=None,printed_page=None))

info=json.loads((p/'barinma-capture.json').read_text()); doc='0405-tip-barinma-274462-pdf'; vid=doc+'-v1'; sha=info['sha256']; url=info['url']; file=root/'objects'/sha/'original.pdf'; raw=file.read_bytes(); assert hashlib.sha256(raw).hexdigest()==sha
readable=file.parent/'readable.html'; content=readable_bytes(raw,'pdf',legacy=False)
if readable.exists(): assert readable.read_bytes()==content
else: readable.write_bytes(content)
add('document',dict(id=doc,party_id='tip',title='27. dönem 2/4462 barınma kanun teklifi',source_kind='official'))
add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date='2022-05-18',version_label='TBMM özgün teklif metni',accessed_at=info['accessed_at'],verified_at=info['accessed_at'],mime='application/pdf',sha256=sha,original_path=f'objects/{sha}/original.pdf',readable_path=f'objects/{sha}/readable.html',date_precision='day',date_unknown_reason=None))
add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM teklifinin bütün 11 sayfası okundu.'))
for name,page,ex in [('intro',0,'Barınma Sorununu Gidermek Amacıyla Bazı Kanunlarda Değişiklik Yapılması'),('rental',9,"EK MADDE 6- Öğrencilerin yaşadıkları konuma, kiralananın özelliklerine göre\nbelirlenecek kira bedellerinin 3/4'ü kira desteği olarak karşılanır")]:
 assert ex in pdf_page_text(file,page),name
 add('passage',dict(id=doc+'-'+name+'-p',version_id=vid,exact=ex,prefix=None,suffix=None,article=None,section='Teklif kapağı' if page==0 else 'Madde 6',pdf_page_index=page,printed_page=None))

existing='0405-tip-sendika-hukumsuz-v1'; file=root/'objects/ba2883e38fed0a4a930fb66c3d51b7e72248196ebffb8df52e6688fef57a75ed/original.pdf'; t=pdf_page_text(file,235)
for name,ex in [('number','4186 2/4462'),('title','Barınma Sorununu Gidermek Amacıyla Bazı Kanunlarda Değişiklik Yapılması Hakkında\nKanun Teklifi (Türkiye İşçi Partisi Genel Başkanı İstanbul Milletvekili Erkan Baş ve 3\nMilletvekili)')]:
 assert ex in t,name
 add('passage',dict(id='0405-tip-barinma-hukumsuz-'+name+'-p',version_id=existing,exact=ex,prefix=None,suffix=None,article=None,section='Hükümsüz teklifler sıra 4186',pdf_page_index=235,printed_page='202'))
(p/'barinma-sources-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries),ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries))
