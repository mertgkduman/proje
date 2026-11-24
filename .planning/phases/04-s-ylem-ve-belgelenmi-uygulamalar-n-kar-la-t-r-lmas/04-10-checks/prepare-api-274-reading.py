import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent; page=c/'party-api-pages/page-25.json'; posts={p['id']:p for p in json.loads(page.read_text())}
notes={
3438:'Gürkan 2019 değerlendirmesinde İZBAN, Tüpraş, TARİŞ, Soma, Birleşik Metal-İş ve Saya işçileriyle kamu emekçilerinin mücadelelerini anar. Her işyeri, toplu sözleşme ve iddia edilen kazanım ayrı kaynaklarla doğrulanmalıdır.',
3433:'EMEP Bölge Örgütü Roboski için sorumluların belirlenmesi ve cezalandırılması çağrısını yineler; AİHM başvurusu ve yargısal sonuçla ilgili açıklama mahkeme kaydıyla sınanmalıdır. Daha önce paketlenmiş Roboski olayıyla birleştirme veya yeni olay sayma yapılmadı.',
3429:'EMEP Bölge Örgütü Üçkiraz kırsalındaki kömür ocağı göçüğünde Hasan İnal’ın öldüğünü aktarır ve işçi güvenliği için ortak mücadele ister. Olay tarihi, maden ruhsatı ve soruşturma sonucu bağımsız kayıtlarda doğrulanmalıdır.',
3424:'EMEP Genel Merkezi Kanal İstanbul ÇED sürecini eleştirerek projeye karşı çıkacağını açıklar. Metin ÇED’in onaylandığını söyler; ilan, nihai ÇED raporu ve kararın hukuki aşamaları yetkili kaynaklarla ayrı tarihlendirilmelidir.',
3421:'Türkçe EMEP açıklaması Libya’ya asker gönderilmesine karşı çıkar ve Doğu Akdeniz’deki tüm güçlerin çekilmesini ister. 273’te okunan İngilizce 3441 aynı açıklamanın paralelidir; bağımsız olay sayılmaz.',
3417:'EMEP Genel Merkezi Şehir Üniversitesi arazisi ve Halkbank tartışması bağlamında kamu arazisi devrini ve kaynak denetimini eleştirir. Danıştay kararı, devir, borç ve sorumluluk iddiaları ayrı belge ve süreçlerle doğrulanmalı.'}
parts=[]
for pid,note in notes.items():
 p=posts[pid]; body=p['content']['rendered']; digest=hashlib.sha256(body.encode()).hexdigest(); parts.append(dict(post_id=pid,url=p['link'],page=str(page),body_sha256=digest,start_char=0,end_char=len(body),slice_sha256=digest,body_temporal_status='last_modified_at_or_before_cutoff',reading_note=note))
out=dict(tranche_id='0410-emep-api-274',read_at=datetime.now(timezone.utc).isoformat(),method='Özgün API HTML gövdeleri doğrudan okundu; tam gövdeler ve aralıklar UTF-8 SHA-256 ile bağlandı.',limitations=['3421 ile 3441 paralel dil metinleridir.','Roboski, maden, ÇED ve dava iddiaları bağımsız yargı ve kurum kanıtlarıyla burada doğrulanmadı.','Kapsam kapanışı yapılmadı.'],parts=parts,closure_refs=[])
assert sum(p['end_char'] for p in parts)<48000
with (c/'party-api-274-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API274_READING_OK',sum(p['end_char'] for p in parts))
