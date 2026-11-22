import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text,readable_bytes

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); root=Path('data/practices/sources/tip')
a=json.loads((p/'kadin-4653-capture.json').read_text()); b=json.loads((p/'kadin-1566-capture.json').read_text()); entries=[]
def add(k,v):entries.append(dict(kind=k,values=v))
for doc,cap,date,label in [('0405-tip-kadin-274653',a,'2022-10-11','27. dönem 2/4653 kadın danışma merkezi teklifi'),('0405-tip-kadin-281566',b[1],'2023-09-07','28. dönem 2/1566 kadın danışma merkezi teklifi')]:
 sha=cap['sha256']; f=root/'objects'/sha/'original.pdf'; raw=f.read_bytes(); assert hashlib.sha256(raw).hexdigest()==sha; readable=f.parent/'readable.html'; rb=readable_bytes(raw,'pdf',legacy=False)
 if readable.exists(): assert readable.read_bytes()==rb
 else: readable.write_bytes(rb)
 vid=doc+'-v1';url=cap['url'];add('document',dict(id=doc,party_id='tip',title=label,source_kind='official'))
 add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,version_label='TBMM özgün teklif metni',accessed_at=cap['accessed_at'],verified_at=cap['accessed_at'],mime='application/pdf',sha256=sha,original_path=f'objects/{sha}/original.pdf',readable_path=f'objects/{sha}/readable.html',date_precision='day',date_unknown_reason=None))
 add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Teklif aslı ve gerekçesinin beş sayfası okundu.'))
 text=pdf_page_text(f,4); exact='tüm belediyeler kadın damşma merkezi açmak zorundadır.' if 'tüm belediyeler kadın damşma merkezi açmak zorundadır.' in text else 'tüm belediyeler kadın danışma merkezi açmak zorundadır.'
 assert exact in text
 add('passage',dict(id=doc+'-duty-p',version_id=vid,exact=exact,prefix=None,suffix=None,article='MADDE 1',section='Belediye danışma merkezi yükümlülüğü',pdf_page_index=4,printed_page=None))

result=root/'objects/ba2883e38fed0a4a930fb66c3d51b7e72248196ebffb8df52e6688fef57a75ed/original.pdf';text=pdf_page_text(result,243)
for suffix,exact in [('number','4366 2/4653'),('title','Belediye Kanununda Değişiklik Yapılmasına Dair Kanun Teklifi (İstanbul Milletvekili Saliha\nSera Kadıgil Sütlü)')]:
 assert exact in text
 add('passage',dict(id='0405-tip-kadin-hukumsuz-'+suffix+'-p',version_id='0405-tip-sendika-hukumsuz-v1',exact=exact,prefix=None,suffix=None,article=None,section='Hükümsüz teklifler sıra 4366',pdf_page_index=243,printed_page='210'))
(p/'kadin-sources-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries),ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries))
