import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';p=next(x for x in json.loads(page.read_text()) if x['id']==3294);body=p['content']['rendered'];start,end=20000,32000
assert len(body)==115954
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
out={'tranche_id':'0410-emep-api-288','read_at':datetime.now(timezone.utc).isoformat(),'method':'Özgün Türkçe HTML gövdesinin yarı açık [20000,32000) karakter aralığı okundu.','post_id':3294,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':digest(body),'start_char':start,'end_char':end,'total_char':len(body),'slice_sha256':digest(body[start:end]),'reading_note':'Emperyalizm ve ulusal hareketler bölümü işçi hareketinin uluslararasılaşması, ezilen halk mücadeleleri, üretim araçlarının ortak mülkiyeti ve sosyalist geçişe ilişkin program görüşlerini sürdürür. Ekim Devrimi ve sosyalist inşa bölümünün başlangıcı 1917, iki dünya savaşı, SSCB ve sömürgecilik karşıtı mücadeleler hakkında partinin tarih yorumunu verir; 20. Kongre sonrası gelişmeler tartışması içinde aralık kesilir.','limitations':['Tarihsel ve kuramsal görüşler partiye atfedilir, bağımsız tarih doğrulaması olarak sunulmaz.','32000 sonrası okunmadı; İngilizce ve Türkçe metinlerin tümü aynı sürüm kabul edilmedi.'],'next_unread':{'post_id':3294,'start_char':end,'total_char':len(body)},'closure_refs':[]}
with (c/'party-api-288-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API288_READING_OK',end-start,out['slice_sha256'])
