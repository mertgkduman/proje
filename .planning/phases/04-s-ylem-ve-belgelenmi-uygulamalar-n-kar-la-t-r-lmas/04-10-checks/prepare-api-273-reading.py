import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent; page=c/'party-api-pages/page-25.json'; posts={p['id']:p for p in json.loads(page.read_text())}
notes={
3461:'EMEP Genel Merkezi ABD’nin Filistin planını eleştirir; Filistinlilerin kendi devletlerini kurmasını, İsrail’in 1967’de işgal edilen yerlerden çekilmesini ve isteyen mültecilerin dönüşünü savunur. Plana ilişkin toprak ve mali rakamlar özgün planla doğrulanmalı.',
3455:'Gürkan Elazığ merkezli deprem sonrasında hayatını kaybedenlerin yakınlarına başsağlığı diler ve kamu kurumlarının hasar, kayıp ve önlemleri paylaşmasını ister; depremin saati, kayıplar ve hasar ayrıca AFAD kayıtlarıyla doğrulanmalıdır.',
3449:'EMEP Genel Merkezi Cumhurbaşkanının atama töreni konuşmasını, kadına şiddet ve nafaka hakkı politikalarını eleştirir. Konuşmanın tamamı, somut karar ve genelgeler ayrı doğrulanmalıdır; yorumu partiye aittir.',
3443:'EMEP Genel Merkezi Kasım Süleymani’nin Bağdat’ta öldürülmesi üzerine ABD ve diğer askerî güçlerin bölgeden çekilmesini ister. Can kaybı sayısı ve süreçteki nedensellik iddiaları bağımsız kaynaklarla doğrulanmalıdır.',
3441:'İngilizce EMEP metni Doğu Akdeniz anlaşması ve Libya’ya asker gönderilmesi tartışmalarında asker gönderilmesine karşı çıkar; anlaşma, tezkereler ve icra tarihleri birincil belgelerle ayrılmalıdır.'}
parts=[]
for pid,note in notes.items():
 p=posts[pid]; body=p['content']['rendered']; digest=hashlib.sha256(body.encode()).hexdigest(); parts.append(dict(post_id=pid,url=p['link'],page=str(page),body_sha256=digest,start_char=0,end_char=len(body),slice_sha256=digest,body_temporal_status='last_modified_at_or_before_cutoff',reading_note=note))
arabic=posts[3465]; body=arabic['content']['rendered']
gap=dict(post_id=3465,url=arabic['link'],start_char=0,end_char=len(body),body_sha256=hashlib.sha256(body.encode()).hexdigest(),status='unread_language_gap',reason='Arapça gövdenin tamamına güvenilir anlam aktarımı yapılmadı; izleyen Türkçe metinle bağımsız paralellik iddia edilmedi.')
out=dict(tranche_id='0410-emep-api-273',read_at=datetime.now(timezone.utc).isoformat(),method='Arapça gövde dürüstçe açık boşluk bırakılarak sonraki Türkçe ve İngilizce özgün API gövdeleri doğrudan okundu; tam gövde ve aralıklar UTF-8 SHA-256 ile bağlandı.',open_language_gaps=[gap],limitations=['Arapça 3465 okunmuş sayılmadı.','Deprem, savaş, hukuk ve kadınlara yönelik şiddet olguları bağımsız doğrulanmadı.','Kapsam kapanışı yapılmadı.'],parts=parts,closure_refs=[])
assert sum(p['end_char'] for p in parts)<48000
with (c/'party-api-273-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API273_READING_OK',sum(p['end_char'] for p in parts),'ARABIC_GAP',len(body))
