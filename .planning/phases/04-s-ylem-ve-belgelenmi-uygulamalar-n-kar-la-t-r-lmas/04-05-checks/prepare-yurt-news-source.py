import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks'); root=Path('data/practices/sources/tip')
r=json.loads((p/'yurt-gercek-capture.json').read_text()); doc='0405-tip-yurt-gercek'; vid=doc+'-v1'; sha=r['sha256']; url=r['url']; raw=(root/'objects'/sha/'original.html.bin').read_bytes(); assert hashlib.sha256(raw).hexdigest()==sha
text=html_source_text(raw); entries=[]
def add(k,v): entries.append(dict(kind=k,values=v))
add('document',dict(id=doc,party_id='tip',title='Yurt krizi TBMM’ye taşındı: TİP’li 4 vekilden kanun teklifi',source_kind='journalism'))
add('document_version',dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date='2021-09-23',version_label='Gerçek Haberci haber yakalaması',accessed_at=r['accessed_at'],verified_at=r['accessed_at'],mime='text/html',sha256=sha,original_path=f'objects/{sha}/original.html.bin',readable_path=f'objects/{sha}/readable.html',date_precision='day',date_unknown_reason=None))
add('archive_view',r['view'])
add('source_attribution',dict(version_id=vid,kind='journalism',publisher='Gerçek Haberci',author=None,social_handle=None,published_at='2021-09-23',date_precision='day',public_url=url,basis='Yayın tarihi, editör Adem Nakçı künyesi ve haberin tüm gövdesi okundu; önceki gece ifadesi haber aktarımıdır.'))
for name,exact in [('intent','TİP olarak TBMM’ye kanun teklifi vereceklerini söyledi.'),('free','KYK yurtlarının ücretsiz hale getirilmesi')]:
 assert exact in text,name
 add('passage',dict(id=doc+'-'+name+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section='Öğrenci nöbeti ve teklif haberi',pdf_page_index=None,printed_page=None))
(p/'yurt-news-source-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries),ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries))
