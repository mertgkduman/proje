"""Kaya'nın 2/3464 hakkındaki grup açıklamasını özgün sayfadan ayıkla."""
import hashlib,json
from pathlib import Path
from arsiv import pdf_page_text
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
rows=json.loads((p/'2026-5344-direct-source-records.json').read_text())['entries'];entries=[e for e in rows if e['kind'] in ('document','document_version','source_attribution')]
v=next(e['values'] for e in entries if e['kind']=='document_version');f=Path('data/practices/sources/dem')/v['original_path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==v['sha256']
parts=[(20,'ADALET KAYA (Diyarbakır) - Sayın Başkan, teşekkürler.','TÜRK-İŞ verilerine göre', 'Komisyonda teklifin ve 20 bin liralık alt aylığın eleştirisi'),(21,'Şimdi, biz DEM PARTİ olarak ne diyoruz?', 'Emeklilik, bir yurttaşlık hakkıdır.', 'DEM adına emekli aylığı ve yaşlı kadın geliri talepleri')]
for idx,start,end,section in parts:
 text=pdf_page_text(f,idx);a=text.index(start);b=text.lower().index(end.lower(),a)+len(end);exact=text[a:b]
 entries.append(dict(kind='passage',values=dict(id=f'0406-7573-commission-kaya-p{idx}',version_id=v['id'],exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=idx,printed_page=str(idx+1))))
out=p/'2026-5344-kaya-source-records.json';out.write_text(json.dumps(dict(party_id='dem',entries=entries),ensure_ascii=False,indent=2)+'\n');print(hashlib.sha256(out.read_bytes()).hexdigest())
