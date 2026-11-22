"""5344'te 15 Ocak 2026 doğrudan katkı için partiye özgü kaynak kayıtları."""
import hashlib, json
from pathlib import Path
from arsiv import pdf_page_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
original=json.loads(Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-07-checks/pension-floor-final-source-records.json').read_text())['entries']
old='0407-floor-iyi-7573-commission'; new='0406-7573-commission'; result=[]
for e in original:
 k=e['kind'];v=e['values']; ident=v.get('id',''); version=v.get('version_id','')
 if k=='document' and ident!=old: continue
 if k=='document_version' and v['document_id']!=old: continue
 if k=='source_attribution' and version!=old+'-v1': continue
 if k not in ('document','document_version','source_attribution'): continue
 v=json.loads(json.dumps(v,ensure_ascii=False).replace(old,new))
 if k=='document':v['party_id']='dem'
 result.append(dict(kind=k,values=v))
version=next(e['values'] for e in result if e['kind']=='document_version');path=Path('data/practices/sources/dem')/version['original_path']
assert hashlib.sha256(path.read_bytes()).hexdigest()==version['sha256']
for idx,start,end,section in [(8,'HAKKI SARUHAN OLUÇ (Antalya) - Teşekkür ederim Sayın Başkan.','16 milyon emekli için yaşam son derece zor', 'Emeklilik ve 20 bin lira önerisine eleştiri'),(9,'O nedenle, lafı çok uzatmadan bir kez daha söyleyeyim:', 'Teşekkür ediyorum.', 'Kamusal sosyal güvenlik ve yapısal reform talebi'),(58,'HAKKI SARUHAN OLUÇ (Antalya) - Teşekkür ederim Sayın Başkan.', 'Teşekkür ediyorum.', 'Altıncı maddede işsizlik fonu eleştirisi')]:
 text=pdf_page_text(path,idx); a=text.index(start);b=text.index(end,a)+len(end);exact=text[a:b]
 result.append(dict(kind='passage',values=dict(id=f'{new}-p{idx}',version_id=new+'-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=idx,printed_page=str(idx+1))))
out=p/'2026-5344-direct-source-records.json';out.write_text(json.dumps(dict(party_id='dem',entries=result),ensure_ascii=False,indent=2)+'\n');print(hashlib.sha256(out.read_bytes()).hexdigest())
