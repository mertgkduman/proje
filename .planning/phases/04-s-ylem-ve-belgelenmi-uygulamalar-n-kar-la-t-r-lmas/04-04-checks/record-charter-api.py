import hashlib
import json
from pathlib import Path

raw=Path('/tmp/gsd-0404-party-295.json').read_bytes();digest=hashlib.sha256(raw).hexdigest()
assert digest=='4a1481d97a845c31a4b8c97384ccc94de1dee1014fc8e89ab39337f11e3af6d2'
data=json.loads(raw);assert data['id']==295 and data['created_at']=='2026-11-09T16:08:39.050Z'
assert 'bir sonraki olağan kurultay takvimine kadar geçerli olmak üzere' in data['icerik']
folder=Path('data/practices/sources/yeni-parti/objects')/digest;folder.mkdir(parents=True,exist_ok=True);dest=folder/'original.json'
if dest.exists(): assert dest.read_bytes()==raw
else: dest.write_bytes(raw)
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text());u='https://api.yeni-parti.org.tr/api/haberler/295'
q['initial_readings'].append(dict(read_at='2026-11-21',url=u,section='Yayınlanan JSON icerik: 9 Kasım sözcü açıklaması, parti içi demokrasi ve PM değişikliği',note='Haber sayfasının kendi JavaScripti GET /api/haberler/295 uç noktasını gösterdi; API HTTP 200 özgün JSON gövdesi okundu, created_at ve updated_at 9 Kasım 16:08:39.050Z. Zeynel Emreye atfedilen açıklama bir sonraki olağan kurultay takvimine kadar bir kereye mahsus PMnin 80den 150ye çıkmasını ve 30 yedeği bildiriyor; bu açıklama değişikliğin tam tüzük metni değildir. Aynı açıklama 639.454 üyeye ve yüzde 81 üzeri katılıma atıf yapıyor; önceki 8 Kasım kısmi veriyle kapsam farkı ayrıca araştırılır. Bu domain kullanıcı tarafından seçilen yenipartiyiz.biz ile özdeşlenmedi. JSON ham baytı mevcut HTML/PDF kaynak şemasına dönüştürülmeden araştırma nesnesi olarak saklandı.'))
q['captures'].append(dict(url=u,sha256=digest,accessed_at='2026-11-21T21:34:03+00:00',state='json_raw_unbound'))
q['candidate_leads'].append(dict(url=u,state='read_json_unbound',note='Doğrudan JSON kaynak için desteklenen kaynak sürümü/konumlandırılmış pasaj ve yerel arşiv görünümü yöntemi araştırılacak; yayımlanan haber, tam tüzük değişikliği metniyle eşit değildir.'))
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
