import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';p=next(x for x in json.loads(page.read_text()) if x['id']==3294);body=p['content']['rendered'];start,end=32000,44000
assert len(body)==115954
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
out={'tranche_id':'0410-emep-api-289','read_at':datetime.now(timezone.utc).isoformat(),'method':'Özgün Türkçe HTML gövdesinin yarı açık [32000,44000) karakter aralığı okundu.','post_id':3294,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':digest(body),'start_char':start,'end_char':end,'total_char':len(body),'slice_sha256':digest(body[start:end]),'reading_note':'Sosyalist inşa bölümünün sonunda SSCB ve Arnavutluk ile revizyonizm hakkında partinin tarih yorumu sürer. Keskinleşen çelişkiler bölümünde özelleştirme, güvencesiz çalışma, uluslararası kuruluşlar, savaşlar ve doğa tahribatı değerlendirilir. Türkiye devrimi bölümü Türkiye kapitalizminin gelişmesi, Ulusal Kurtuluş Savaşı ve egemen sınıflar üzerine programın görüşleriyle başlar; aralık 2. maddenin içinde kesilir.','limitations':['Partinin tarihsel ve siyasal değerlendirmeleri bağımsız tarihsel veya ekonomik tespit değildir.','44000 sonrası okunmadı; genel çevre görüşü tekil çevre işlemi kanıtı değildir.'],'next_unread':{'post_id':3294,'start_char':end,'total_char':len(body)},'closure_refs':[]}
with (c/'party-api-289-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API289_READING_OK',end-start,out['slice_sha256'])
