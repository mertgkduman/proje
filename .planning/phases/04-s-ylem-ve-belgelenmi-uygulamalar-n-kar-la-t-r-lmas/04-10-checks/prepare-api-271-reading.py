import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent; page=c/'party-api-pages/page-25.json'; posts={p['id']:p for p in json.loads(page.read_text())}
notes={
3502:'Selma Gürkan Newroz mesajında salgın sırasında ev ve balkonlardan kutlama çağrısı yapar, Kürt sorununun eşit haklar temelinde barışçıl çözümünü savunur; bölgesel savaş ve göç iddiaları atıflıdır.',
3500:'Gürkan 18 Mart açıklamasında ücretli izin, ücretsiz salgın sağlık hizmeti, ücretsiz hijyen araçları, kamu hizmetleri ve cezaevlerine yönelik düzenleme dahil on bir talep sıralar. Başka salgın açıklamalarıyla benzerlik bağımsız süreç sayısı anlamına gelmez.',
3492:'EMEP Genel Merkezi sağlık hizmetine koşulsuz erişim, işyerinde korunma, ücretli izin ve dezenfektana ücretsiz erişim ister. Kaynakta yer alan vaka sayısı, tanı merkezi ve malzeme eksikliği beyanları tarihli sağlık otoritesi kayıtlarıyla ayrıca doğrulanmalıdır.',
3489:'Gürkan 8 Mart mesajında eşitlik, şiddetin önlenmesi, çalışma ve göçmen kadınların koşullarını tartışır. İşsizlik, kayıt dışılık ve sendikalaşma yüzdelerinin dönem, kaynak ve paydaları belirlenmedi.',
3485:'Levent Tüzel İdlib saldırısı ve Meclis kapalı oturumu bağlamında ateşkes, askerin geri çekilmesi ve mülteciler için insani koşullar ister. Ölüm sayısı, oturum ve ateşkes olayları yetkili kaynaklarla ayrı tarihlendirilmeli.'}
parts=[]
for pid,note in notes.items():
 p=posts[pid]; body=p['content']['rendered']; digest=hashlib.sha256(body.encode()).hexdigest(); parts.append(dict(post_id=pid,url=p['link'],page=str(page),body_sha256=digest,start_char=0,end_char=len(body),slice_sha256=digest,body_temporal_status='last_modified_at_or_before_cutoff',reading_note=note))
out=dict(tranche_id='0410-emep-api-271',read_at=datetime.now(timezone.utc).isoformat(),method='Özgün API HTML gövdeleri doğrudan okundu; her tam gövde ve aralığı UTF-8 SHA-256 ile bağlandı.',limitations=['Nedensellik, sayısal ve hukuki iddialar partiye atıflıdır; bağımsız doğrulanmadı.','Bu açıklamalar üzerine uygulama veya kapsam kapanışı ileri sürülmedi.'],parts=parts,closure_refs=[])
assert sum(p['end_char'] for p in parts)<48000
with (c/'party-api-271-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API271_READING_OK',sum(p['end_char'] for p in parts))
