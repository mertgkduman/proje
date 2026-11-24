import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';posts={p['id']:p for p in json.loads(page.read_text())}
notes={3289:'Genel Başkan Yardımcısı Şükran Doğan 7. Aile Şûrasında Cumhurbaşkanının konuşmasını eleştirir; eşit ücret, kreş ve kadına şiddetin sonlanması taleplerini aktarır. Siyasi nitelemeler, atfedilen sözlerin aslı ve suç iddiaları ayrıca doğrulanmalıdır.',3284:'EMEP Genel Merkezi 1 Mayıs öncesinde kıdem tazminatı, zorunlu BES ve ekonomi reformu hakkında eleştirilerini, çalışma ve özgürlük taleplerini açıklar; ilan edilmiş reformu uygulanmış yasa ve ilerideki gösterileri gerçekleşmiş katılım saymaz.',3281:'EMEP, Selma Gürkanın 27 Şubat 2018 tarihli konuşması nedeniyle 24 Nisan 2019da 10 ay hapis ve para cezasına çevrilme anlatımını aktarır ve istinaf başvurusu yapacağını bildirir. Mahkeme hükmü, hukuki gerekçe, istinafın gerçekleşmesi ve sonucu özgün yargı belgeleriyle ayrıca doğrulanmalıdır.'}
parts=[]
for pid,n in notes.items():
 p=posts[pid];body=p['content']['rendered'];h=hashlib.sha256(body.encode()).hexdigest();parts.append({'post_id':pid,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':h,'start_char':0,'end_char':len(body),'total_char':len(body),'slice_sha256':h,'reading_note':n})
out={'tranche_id':'0410-emep-api-296','read_at':datetime.now(timezone.utc).isoformat(),'method':'API sırasındaki 3289, 3284 ve 3281 özgün HTML gövdeleri tamamen okundu.','parts':parts,'next_unread':{'after_post_id':3281,'page':str(page)},'limitations':['Yargı, ekonomik reform ve siyasi aktörlere atfedilen iddialar parti metnidir; başka kurumlardan ayrı doğrulama gerekir.','Sonraki gövdeler okunmadı, kapsam kapatılmadı.'],'closure_refs':[]}
assert sum(x['end_char'] for x in parts)<48000
with (c/'party-api-296-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API296_READING_OK',sum(x['end_char'] for x in parts))
