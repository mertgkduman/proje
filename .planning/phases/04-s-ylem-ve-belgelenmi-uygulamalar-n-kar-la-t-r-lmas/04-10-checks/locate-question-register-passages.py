import json,re,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
rows=[]
for num,day,received in [('4186','11.09.2023','26.10.2023'),('13296','14.06.2024','20.08.2024'),('8988','29.01.2024','07.11.2024')]:
 raw=Path('/tmp/gsd0410-question-'+num+'.html').read_bytes();text=html_source_text(raw);match=re.search(r'Önergenin Özeti</td>\s*<td>(.*?)</td>',text,re.S);assert match,num
 title=match.group(1).strip();owner='Sevda KARACA DEM&#x130;R';ident='0410-emep-question-'+num+'-register'
 for suffix,exact,section in [('subject',title,'Soru özeti'),('date',day,'Başkanlığa geliş tarihi'),('owner',owner,'Soru sahibi'),('answer-received',received,'Bakanlık yanıtının TBMM’ye bildirilişi')]:
  assert exact in text,(num,suffix);rows.append(dict(kind='passage',values=dict(id=ident+'-'+suffix+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)))
out=Path(__file__).parent/'three-questions-register-passages.json';assert not out.exists();out.write_text(json.dumps(dict(status='draft_unvalidated',entries=rows,note='Kayıt ekranı soru sahibi, tarih ve özeti; yanıtın TBMM’ye bildirildiği gün ayrı. Tarama sorular için gerçek metin katmanı yoktur.'),ensure_ascii=False,indent=2)+'\n');print('QUESTION_REGISTER_LOCATORS_OK',len(rows))
