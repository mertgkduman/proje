import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';p=next(x for x in json.loads(page.read_text()) if x['id']==3294);body=p['content']['rendered'];start,end=56000,68000
assert len(body)==115954
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
out={'tranche_id':'0410-emep-api-291','read_at':datetime.now(timezone.utc).isoformat(),'method':'Özgün Türkçe HTML gövdesinin yarı açık [56000,68000) karakter aralığı okundu.','post_id':3294,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':digest(body),'start_char':start,'end_char':end,'total_char':len(body),'slice_sha256':digest(body[start:end]),'reading_note':'Demokratik haklar kısmında sendika ve grev, ulusal toplulukların eşitliği ve anadilde kamu hizmetleri, laiklik ve vicdani ret, ücretsiz eğitim ve sağlık talepleri sıralanır. Bağımsız ülke kısmında NATOdan çıkış, yabancı üsler ve Kıbrıstan asker çekilmesi, büyük işletme ve toprakların kamulaştırılması, çiftçi borçları ve üretici örgütleri görüşleri yer alır. Çalışma bölümünde 7 saatlik gün, iş güvenliği ve ücretli ebeveyn izni savunulur; aralık maddenin içinde kesilir.','limitations':['Talepler parti programına aittir; yasa, fiili hizmet veya dış politika işlemi gerçekleşmesi gösterilmez.','68000 sonrası okunmadı.'],'next_unread':{'post_id':3294,'start_char':end,'total_char':len(body)},'closure_refs':[]}
with (c/'party-api-291-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API291_READING_OK',end-start,out['slice_sha256'])
