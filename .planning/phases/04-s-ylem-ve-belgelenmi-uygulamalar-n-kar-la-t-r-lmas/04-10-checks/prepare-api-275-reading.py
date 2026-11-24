import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';posts={p['id']:p for p in json.loads(page.read_text())}
notes={3413:(None,'EMEP Genel Merkezi 25 Kasım’da şiddete, eşitsizliğe ve yoksulluğa karşı kadınları sokaklarda buluşmaya çağırır; İstanbul’da yasaklama iddiasının kapsamı ve karar tarihi yetkili kayıtla doğrulanmalıdır.'),3409:(None,'EMEP Genel Merkezi Bolivya’daki Morales istifasını ve ABD desteği iddiasını darbe olarak niteleyip kınar. ABD rolü, askerî baskı ve sığınma süreci taraf beyanından bağımsız kurum kayıtlarıyla incelenmelidir.'),3406:(None,'EMEP Genel Merkezi MYK üyesi Metin İlgün’ün ölümünü duyurur; 10 Kasım İstanbul töreni ve 11 Kasım Pertek törenini ayrı saatlerle bildirir. Açılıştaki “yarın ... ardından Dersim” ifadesi ile ayrıntılı iki günlük takvim arasındaki ifade farkı, törenlerin fiilen yapıldığını kanıtlamaz.'),3404:(10000,'Suriye politikasını ele alan uzun metnin yalnız ilk 10.000 ham karakteri okundu. 9 Ekim harekâtı, 2011 sonrası aktörler ve PYD/YPG’ye yönelik resmî söylem üzerine EMEP değerlendirmeleri aktarılıyor; askerî ve güvenlik iddiaları parti görüşüdür ve ayrı kaynak gerektirir. 10.000 sonrası okunmadı.')}
parts=[]
for pid,(end,note) in notes.items():
 p=posts[pid];body=p['content']['rendered'];end=len(body) if end is None else end;digest=lambda s:hashlib.sha256(s.encode()).hexdigest();parts.append(dict(post_id=pid,url=p['link'],page=str(page),body_sha256=digest(body),start_char=0,end_char=end,slice_sha256=digest(body[:end]),body_temporal_status='last_modified_at_or_before_cutoff',reading_note=note))
out=dict(tranche_id='0410-emep-api-275',read_at=datetime.now(timezone.utc).isoformat(),method='Özgün Türkçe API HTML gövdeleri doğrudan okundu; tam gövde ve her aralık UTF-8 SHA-256 ile bağlandı.',limitations=['3404 [10000,36234) burada okunmadı ve sonraki dilime bırakıldı.','Siyasi, güvenlik ve yargı olguları bağımsız doğrulanmadı.','Kapsam kapanışı yapılmadı.'],parts=parts,closure_refs=[])
assert sum(p['end_char'] for p in parts)<48000
with (c/'party-api-275-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API275_READING_OK',sum(p['end_char'] for p in parts))
