import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent; page=c/'party-api-pages/page-25.json'; posts={p['id']:p for p in json.loads(page.read_text())}
notes={
3483:'İngilizce EMEP metni İdlib saldırısı sonrasında askerlerin ve tüm yabancı güçlerin Suriye’den çekilmesini ister. Türkçe 3479 ile paraleldir; farklı diller iki bağımsız açıklama sayılmaz. Ölüm sayısı ve sorumluluk yorumları kaynak beyanıdır.',
3479:'Türkçe Genel Merkez metni askerlerin İdlib’den çekilmesi ve Suriye müdahalesinin sonlandırılmasını ister. İngilizce 3483 paralel metindir; 33 ölüm ve diğer olay iddiaları için yetkili kayıt gereklidir.',
3476:'EMEP Genel Merkezi Necmiye Hoca için anma metni yayımlar; ölüm tarihi, yaşı ve siyasal biyografisine ilişkin bilgiler parti beyanıdır. Otobiyografik veya resmî bağımsız kayıtlarla ayrıca incelenmelidir.',
3472:'EMEP Genel Merkezi Gezi yargılamasının düşürülmesini ister, önceki Taksim Dayanışması davasında beraat ve mevcut yargılama hakkında sayısal iddialarda bulunur. Dava kimliği, karar tarihi, kanun yolu ve sonraki kararlar ayrı mahkeme kayıtlarıyla doğrulanmalı.',
3469:'Gürkan İdlib çatışması ve Ukrayna’ya yardım iddiaları bağlamında yabancı güçlerin çekilmesini savunur. Beş ölüm, dokuz yaralı ve 200 milyon TL iddiası ile zamandaşlık yorumu bağımsız kurum kayıtlarıyla doğrulanmamıştır.'}
parts=[]
for pid,note in notes.items():
 p=posts[pid]; body=p['content']['rendered']; digest=hashlib.sha256(body.encode()).hexdigest(); parts.append(dict(post_id=pid,url=p['link'],page=str(page),body_sha256=digest,start_char=0,end_char=len(body),slice_sha256=digest,body_temporal_status='last_modified_at_or_before_cutoff',reading_note=note))
out=dict(tranche_id='0410-emep-api-272',read_at=datetime.now(timezone.utc).isoformat(),method='Özgün Türkçe ve İngilizce API HTML gövdeleri doğrudan okundu; tam gövdeler ve aralıklar UTF-8 SHA-256 ile bağlandı.',limitations=['3483 ve 3479 paralel metinlerdir; bağımsız iki olay değillerdir.','Dava, askerî gelişme ve ölüm sayılarına ilişkin beyanlar bağımsız doğrulanmadı.','Kapsam kapanışı yapılmadı.'],parts=parts,closure_refs=[])
assert sum(p['end_char'] for p in parts)<48000
with (c/'party-api-272-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API272_READING_OK',sum(p['end_char'] for p in parts))
