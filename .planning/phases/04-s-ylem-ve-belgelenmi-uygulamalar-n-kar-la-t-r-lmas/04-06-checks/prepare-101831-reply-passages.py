"""10 Ekim tartışmasındaki somut çağrı ve yanıt için aynı PDF'den ek pasajlar."""
import json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
capture=json.loads((checks/'capture-101831.json').read_text());p=Path(capture['original_path']).resolve();text=pdf_page_text(p,67)
snippets=[('0406-101831-convention-call-p','Koçyiğit İstanbul Sözleşmesi çağrısı','Beklentimiz şudur: Bu Meclis derhâl, hızla İstanbul Sözleşmesi’ne dönülmesi için irade beyanında\nbulunmalıdır'),('0406-101831-government-reply-p','Gül kadına yönelik şiddetle mücadele yanıtı','Bizim bu konuda kadına yönelik şiddetle ilgili mücadelemiz\nçok ciddi bir şekilde, tutarlı ve kararlı bir şekilde devam etmektedir.')]
entries=[]
for ident,section,exact in snippets:
 assert exact in text,ident
 entries.append(dict(kind='passage',values=dict(id=ident,version_id='0406-tbmm-101831-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=67,printed_page=None)))
(checks/'101831-reply-passages-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,limitation='Çağrı ve karşı yanıt birlikte tutulmalı; çağrı Sözleşmeye dönüldüğünü kanıtlamaz.'),ensure_ascii=False,indent=2)+'\n')
print('REPLY_PASSAGE_DRAFT',len(entries))
