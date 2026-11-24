import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';p=next(x for x in json.loads(page.read_text()) if x['id']==3294);body=p['content']['rendered'];start,end=44000,56000
assert len(body)==115954
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
out={'tranche_id':'0410-emep-api-290','read_at':datetime.now(timezone.utc).isoformat(),'method':'Özgün Türkçe HTML gövdesinin yarı açık [44000,56000) karakter aralığı okundu.','post_id':3294,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':digest(body),'start_char':start,'end_char':end,'total_char':len(body),'slice_sha256':digest(body[start:end]),'reading_note':'Türkiye devrimi bölümünde Kürt ulusal hakları, bölgeler arası gelişme, köylerin zorla boşaltılması ve kırdan göçe ilişkin değerlendirmeler bulunur. Devamında halk iktidarı anlayışı, seçilmiş kurucu meclis ve yerel meclisler, seçilmişlerin ücretleri, oy ve seçilme hakkı, halkın yargıç seçimi, kadın erkek eşitliği ve kamu verilerine ücretsiz erişim önerilir; aralık dolaylı vergiler maddesinde kesilir.','limitations':['İddialar ve öneriler program metnine atfedilir; gerçekleşmiş mevzuat ve uygulama olarak sunulmaz.','56000 sonrası okunmadı.'],'next_unread':{'post_id':3294,'start_char':end,'total_char':len(body)},'closure_refs':[]}
with (c/'party-api-290-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API290_READING_OK',end-start,out['slice_sha256'])
