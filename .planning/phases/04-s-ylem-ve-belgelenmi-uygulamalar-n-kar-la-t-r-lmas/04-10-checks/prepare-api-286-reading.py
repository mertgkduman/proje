import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
c = Path(__file__).resolve().parent
page = c / 'party-api-pages/page-25.json'
posts = {p['id']: p for p in json.loads(page.read_text())}
notes = {
    3301: 'Genel Başkan Yardımcısı Levent Tüzel, Soma faciasının beşinci yılında 301 madencinin ölümü üzerinden iş güvenliği ve yargılama sürecini eleştirir; örgütlü mücadele çağrısı yapar. Yargılama ve kişisel sorumluluk hakkındaki yorumlar parti temsilcisine aittir.',
    3298: 'EMEP Genel Merkezi İstanbul büyükşehir seçiminin iptal kararını ve karar sürecini eleştirir, 23 Haziran için yenileme tarihini anar. Karar gerekçesi ve sonraki seçim sonucu bu siyasi beyanın ayrıca kurum kayıtlarıyla doğrulanmasını gerektirir.',
    3294: 'Türkçe program ve tüzüğün yalnız ilk 0–8000 özgün HTML karakteri okundu. Giriş parti hedeflerini işçi sınıfı ve uluslararası dayanışma çerçevesinde tanımlar; A bölümünün ilk maddeleri kapitalist üretim, sermaye yoğunlaşması, kadın emeği ve işsizliğe ilişkin kuramsal görüşleri işler. Bu gövdenin kalan 8000 sonrası okunmadı.'
}
parts=[]
for pid, note in notes.items():
    p=posts[pid]; body=p['content']['rendered']; end=8000 if pid==3294 else len(body)
    digest=lambda s: hashlib.sha256(s.encode('utf-8')).hexdigest()
    parts.append({'post_id':pid,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':digest(body),'start_char':0,'end_char':end,'total_char':len(body),'slice_sha256':digest(body[:end]),'reading_note':note})
assert sum(p['end_char'] for p in parts)<=48000
out={'tranche_id':'0410-emep-api-286','read_at':datetime.now(timezone.utc).isoformat(),'method':'API sırasıyla iki kısa gövdenin tamamı ve sonraki program-tüzük gövdesinin 0–8000 özgün HTML karakteri okundu.','parts':parts,'next_unread':{'post_id':3294,'start_char':8000,'total_char':len(posts[3294]['content']['rendered'])},'limitations':['İddialar ve tarihsel değerlendirmeler kaynak sahiplerine atfedilir; bu makbuz somut mahkeme veya seçim sonucu değildir.','Türkçe ve İngilizce program sürümleri karşılaştırılmadan eş tutulmadı; sonraki bölümler açıktır.'],'closure_refs':[]}
with (c/'party-api-286-source-reading.json').open('x') as f: json.dump(out,f,ensure_ascii=False,indent=2); f.write('\n')
print('API286_READING_OK',sum(p['end_char'] for p in parts))
