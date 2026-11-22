"""TBMM 224 sayılı rapor için kesintisiz sayfa sırası ve kısmi okuma kaydı."""
import datetime
import hashlib
import json
from pathlib import Path
from arsiv import pdf_page_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
capture=json.loads((p/'2025-224-report-capture.json').read_text())
raw=Path('data/practices/sources/dem')/capture['original_path']
assert hashlib.sha256(raw.read_bytes()).hexdigest()=='ed1e950a9d23850333dd94cd3fbae9acf4747da5861019c1b14b0ea5ed891bb0'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
pages=[]
for i in range(986,1002):
 text=pdf_page_text(raw,i)
 assert text.strip()
 pages.append(dict(pdf_page_index=i,printed_page=i-21,text_sha256=hashlib.sha256(text.encode()).hexdigest(),characters=len(text)))
assert 'DEM PARTİ MUHALEFET ŞERHİ' in pdf_page_text(raw,986)
assert 'Adalet KAYA' in pdf_page_text(raw,1001) and 'Özgül SAKİ' in pdf_page_text(raw,1001)
queue=[]
for start in range(0,986,20):queue.append(dict(first=start,last=min(start+19,985),state='pending'))
queue.append(dict(first=986,last=1001,state='examined',review_file='2025-224-dem-serhi-reading.md',reviewed_at=now,pages=pages))
for start in range(1002,1054,20):queue.append(dict(first=start,last=min(start+19,1053),state='pending'))
assert [x for r in queue for x in range(r['first'],r['last']+1)]==list(range(1054))
result=dict(version=1,source_sha256=capture['sha256'],total_pages=1054,examined_pages=16,pending_pages=1038,queue=queue,limitations='Yalnız DEM şerhi ve içindeki bağımsız örgüt görüşleri incelendi; raporun diğer bölümleri okunmadı, sonuçların uygulanması ve hukuki etki doğrulanmadı.')
(p/'2025-224-report-reading-queue.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('224_REPORT_QUEUE_EXACT',len(queue),'examined',16,'pending',1038)
