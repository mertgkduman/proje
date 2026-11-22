"""Sevk sonrası iki ayrı açıklama için kaynak baytlarına bağlı taslak pasajlar."""
import json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
root=Path('data/practices/sources/dem'); p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks');caps=json.loads((p/'silopi-reply-captures.json').read_text());entries=[]
def add(k,v):entries.append(dict(kind=k,values=v))
for c in caps:
 raw=(root/c['original_path']).read_bytes();text=html_source_text(raw)
 if c['id']=='3jul': first,last,title='15','48','Ormanlı’nın sevk sonrası açıklaması'
 else:first,last,title='4','25','Silopi Dayanışma İnisiyatifi açıklaması'
 start=text.index('<span data-word-idx="'+first+'" class="tts-word">',90000); end=text.index('</span>',text.index('<span data-word-idx="'+last+'" class="tts-word">',start))+len('</span>');exact=text[start:end]
 assert ('g&ouml;revimin' if c['id']=='3jul' else 'g&ouml;revden') in exact
 ident='0406-silopi-reply-'+c['id'];v=ident+'-v1'
 add('document',dict(id=ident,party_id='dem',title=title,source_kind='journalism'))
 add('document_version',dict(id=v,document_id=ident,original_url=c['original_url'],final_url=c['final_url'],document_date=c['document_date'],version_label='Tarihli haberin özgün HTML baytları',accessed_at=c['accessed_at'],verified_at=c['accessed_at'],mime='text/html',sha256=c['sha256'],original_path=c['original_path'],readable_path=c['readable_path'],date_precision='day',date_unknown_reason=None))
 add('archive_view',c['view'])
 add('passage',dict(id=ident+'-p',version_id=v,exact=exact,prefix=None,suffix=None,article=None,section=title,pdf_page_index=None,printed_page=None))
 add('source_attribution',dict(version_id=v,kind='journalism',publisher='Rûdaw',author=None,social_handle=None,published_at=c['document_date'],date_precision='day',public_url=c['final_url'],basis='Haberin tarihli aktarımı, ilgili kişinin sözü ve süreç evresi birlikte okundu.'))
(p/'silopi-reply-slices-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,limitation='Her iki haber ihraç kararından öncedir; karar sonrası yanıt veya savunma olarak kullanılamaz.'),ensure_ascii=False,indent=2)+'\n');print('SILOPI_REPLY_SLICES_DRAFT',len(entries))
