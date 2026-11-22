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
examined=set(range(36,40)) | set(range(54,57)) | set(range(986,1002))
for i in sorted(examined):
 text=pdf_page_text(raw,i)
 assert text.strip()
 pages.append(dict(pdf_page_index=i,printed_page=i-21,text_sha256=hashlib.sha256(text.encode()).hexdigest(),characters=len(text)))
assert 'DEM PARTİ MUHALEFET ŞERHİ' in pdf_page_text(raw,986)
assert 'Adalet KAYA' in pdf_page_text(raw,1001) and 'Özgül SAKİ' in pdf_page_text(raw,1001)
queue=[]
i=0
while i<1054:
 state='examined' if i in examined else 'pending'; end=i
 while end+1<1054 and (end+1 in examined)==(state=='examined') and end-i<19:end+=1
 row=dict(first=i,last=end,state=state)
 if state=='examined':row.update(review_file='2025-224-dem-serhi-reading.md',reviewed_at=now,pages=[x for x in pages if i<=x['pdf_page_index']<=end])
 queue.append(row);i=end+1
assert [x for r in queue for x in range(r['first'],r['last']+1)]==list(range(1054))
result=dict(version=1,source_sha256=capture['sha256'],total_pages=1054,examined_pages=23,pending_pages=1031,queue=queue,limitations='Yalnız DEM şerhi, içindeki bağımsız örgüt görüşleri, önerge ve takdim/kuruluş sayfaları incelendi; diğer bölümler okunmadı, sonuçların uygulanması ve hukuki etki doğrulanmadı.')
(p/'2025-224-report-reading-queue.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('224_REPORT_QUEUE_EXACT',len(queue),'examined',23,'pending',1031)
