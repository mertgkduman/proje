import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';p=next(x for x in json.loads(page.read_text()) if x['id']==3294);body=p['content']['rendered'];start,end=80000,92000
assert len(body)==115954
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
out={'tranche_id':'0410-emep-api-293','read_at':datetime.now(timezone.utc).isoformat(),'method':'Özgün Türkçe HTML gövdesinin yarı açık [80000,92000) karakter aralığı okundu.','post_id':3294,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':digest(body),'start_char':start,'end_char':end,'total_char':len(body),'slice_sha256':digest(body[start:end]),'reading_note':'Tüzüğün 5–10. maddeleri üyelik koşulları, iki üye tanıklığı, ilçe kabulü, ret itirazı, iki aylık başvuru süresi, aidat olarak metinde 20–1000 TL sınırı, üye hakları ve yazılı istifayı düzenler. 11–21 disiplin sevki, cezalar, savunma ve itirazı; 22–27 mali kaynaklar, birim örgütü ve demokratik merkeziyetçilik dahil örgüt işleyişini anlatır. Aralık parti içi genel tartışma koşullarının içinde kesilir.','limitations':['Bu ulaşılan nüshadaki hükümler ve aidat değerleri, belirli başka tarihlerdeki yürürlük veya güncel ücret olarak varsayılmaz; kabul ve ara değişiklik zamanları ayrı kanıt gerektirir.','92000 sonrası okunmadı; uygulanmış disiplin veya bireysel üyelik sonucu çıkarılmadı.'],'next_unread':{'post_id':3294,'start_char':end,'total_char':len(body)},'closure_refs':[]}
with (c/'party-api-293-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API293_READING_OK',end-start,out['slice_sha256'])
