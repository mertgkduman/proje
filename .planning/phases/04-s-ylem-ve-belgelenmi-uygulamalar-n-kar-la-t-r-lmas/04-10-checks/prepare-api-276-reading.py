import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';p=next(x for x in json.loads(page.read_text()) if x['id']==3404);body=p['content']['rendered'];digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
notes=[
 (10000,20000,'Parti metni Kürt sorunu, sınır ötesi ulusal güvenlik ve “milli politika” söylemine ilişkin yorumlarını sürdürüyor. Suriye/Irak asker gönderme tezkerelerinin her yıl çıkarıldığı ve HDP dışındaki partilerin desteklediği iddiası için her yetki, tarih ve oy ayrı TBMM kaydıyla doğrulanmalı; belirli 2019 tezkere kimliği bu pasajda açıkça verilmez.'),
 (20000,30000,'Metin yabancı askerî güçlerin Suriye’den çekilmesini, Suriyeli göçmenlerin iş, eğitim, sağlık ve güvenli geleceğe erişimini ve yerli-göçmen işçiler için aynı çalışma koşullarını savunuyor. Güvenli bölge ve 2 milyon kişinin yerleştirilmesiyle ilgili anlatı parti iddiasıdır; resmî öneri, karar ve fiilî yerleşim ayrı incelenmelidir.'),
 (30000,len(body),'Son bölüm savaş giderleri ve ekonomik yük üzerine parti değerlendirmesi yapar; ABD ve Rusya ile mutabakatlardan söz edip Suriye’de yabancı askerî üs ve birliklerin çekilmesini, Türkiye’de İncirlik dahil yabancı üslerin kapatılmasını ister. Mutabakatların tam tarih ve metni ile açıklama sonrasındaki uygulama burada kanıtlanmaz.')]
parts=[dict(post_id=3404,url=p['link'],page=str(page),body_sha256=digest(body),start_char=a,end_char=b,slice_sha256=digest(body[a:b]),body_temporal_status='last_modified_at_or_before_cutoff',reading_note=note) for a,b,note in notes]
out=dict(tranche_id='0410-emep-api-276',read_at=datetime.now(timezone.utc).isoformat(),method='275te 10.000 karakterde bırakılan özgün Türkçe HTML gövdesi [10000,20000), [20000,30000), [30000,36234) aralıklarında doğrudan okundu; gövde ve her aralık UTF-8 SHA-256 ile bağlandı.',limitations=['Barış Pınarı tezkere kimliği, tarihli oylama ve ABD/Rusya mutabakatları birincil belgelerle ayrıca doğrulanmadı; sonraki 2021 3/1704 ile eşlenmedi.','Sınır saldırısı, savaşın maliyeti ve göçmen tercihlerine dair genellemeler partiye atıflıdır.','Belirli 3404 gövdesinin okunması tüm corpus kapsamını kapatmaz.'],parts=parts,closure_refs=[])
assert notes[0][0]==10000 and notes[-1][1]==36234 and sum(b-a for a,b,_ in notes)<48000
with (c/'party-api-276-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API276_READING_OK',sum(b-a for a,b,_ in notes),digest(body))
