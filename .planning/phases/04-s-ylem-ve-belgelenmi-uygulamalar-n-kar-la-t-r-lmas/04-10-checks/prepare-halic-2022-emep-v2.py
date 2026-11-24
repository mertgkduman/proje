import json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
c=Path(__file__).resolve().parent;first=json.loads((c/'halic-2022-emep-source-draft.json').read_text());entries=[]
for e in first['entries']:
 v=e['values'];identity=v.get('id') or v.get('version_id') or v.get('document_id') or ''
 if not identity.startswith('0410-halic-2022-hdp'):entries.append(e)
exact='ittifakın yol haritası olarak kabul edilen deklarasyon metni okundu.'
assert exact in html_source_text((c/'halic-2022-emep-sources/meeting.html.bin').read_bytes())
entries.append({'kind':'passage','values':dict(id='0410-halic-2022-meeting-declaration-p',version_id='0410-halic-2022-meeting-v1',exact=exact,prefix=None,suffix=None,article=None,section='EMEP haberinde deklarasyon metninin okunması',pdf_page_index=None,printed_page=None)})
with (c/'halic-2022-emep-v2-source-draft.json').open('x') as f:json.dump({'entries':entries},f,ensure_ascii=False,indent=2);f.write('\n')
text=(c/'prepare-halic-2022-emep.py').read_text()
text=text.replace('halic-2022-emep-source-draft.json','halic-2022-emep-v2-source-draft.json').replace('halic-2022-emep-draft.json','halic-2022-emep-v2-draft.json').replace('halic-2022-emep-review-draft.json','halic-2022-emep-v2-review-draft.json')
text=text.replace(";hdp=pid('hdp-meeting');dec=pid('hdp-declaration')",";dec=pid('meeting-declaration')")
text=text.replace('[news,newsdec,hdp,dec,speech]','[news,newsdec,dec,speech]').replace('[call,plan,six,aug,news,hdp,dec,speech,role,guest,program]','[call,plan,six,aug,news,dec,speech,role,guest,program]').replace('[call,news,hdp,dec,speech]','[call,news,dec,speech]')
text=text.replace(" if hdp in ids:claims.append('HDP yayını Haliç halk buluşmasını bildirir.')\n",'').replace("if dec in ids:claims.append('HDP yayını deklarasyonun okunduğunu bildirir.')","if dec in ids:claims.append('EMEP haberi deklarasyonun okunduğunu bildirir.')")
exec(compile(text,str(c/'prepare-halic-2022-emep.py'),'exec'))
