"""İki farklı Meclis adayının özgün metne bağlı taslak kanıt zincirleri."""
import hashlib
import json
from pathlib import Path
from arsiv import html_source_text

root = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
sha = 'c3eb7e2855a1d26b1ee984f002583d706b7dcd4adc42bc1feaf8eba2a7ac603f'
raw = Path('data/practices/sources/dem/objects', sha, 'original.html.bin').read_bytes()
assert hashlib.sha256(raw).hexdigest() == sha
body = html_source_text(raw)
extra = {
    '0406-tbmm-2025-24-second-rollcall-p': (
        'Yapılan ikinci yoklamada da toplantı yeter sayısı bulunamadığından, alınan karar gereğince, '
        "kanun teklifleri ile komisyonlardan gelen diğer işleri sırasıyla görüşmek için 4 Aralık 2025 Perşembe günü saat 14.00'te toplanmak üzere birleşimi kapatıyorum."
    ),
    '0406-tbmm-2025-24-media-speech-p': (
        'RTÜK gibi baskıcı kurumların kapatılmasını, Basın İlan Kurumunun tümüyle sivil toplum, '
        "bağımsız sivil toplum örgütlerinin denetimine açılmasını ve Türkiye'deki medya ikliminin tekrar tartışmaya açılmasını öneriyoruz"
    ),
}
draft = json.loads((root / 'tbmm-2025-24-source-slices-draft.json').read_text())
entries = draft['entries']
for ident, exact in extra.items():
    assert body.count(exact) == 1, (ident, body.count(exact))
    entries.append({'kind': 'passage', 'values': {'id': ident, 'version_id': '0406-tbmm-2025-24-v1',
        'exact': exact, 'prefix': None, 'suffix': None, 'article': None,
        'section': 'İkinci yoklama ve kapanış' if 'rollcall' in ident else 'DEM grup konuşmasında medya önerileri',
        'pdf_page_index': None, 'printed_page': None}})
for entry in entries:
    if entry['kind'] == 'passage':
        assert entry['values']['exact'] in body, entry['values']['id']

result = {'durum': 'taslak_kapi_bekliyor', 'ozgun_tutanak_sha256': sha,
 'uyari': 'İki olay ayrı; taslakların varlığı, canlı pakete aktarım veya konu kapsamının kapanışı değildir.',
 'adaylar': [
  {'olay_anahtari':'tbmm-28-4-24-10-3464-gundem','tarih':'2025-12-03','konu':'engellilik',
   'kapsam_id':'practice-ae547a34c2afbfccd7913c6eed51c5a5a6d7f422594965429bb8466e60594705',
   'katki':'Ömer Faruk Gergerlioğlu DEM grubu adına engelli yurttaşların gelirine ilişkin öneriyi açıkladı.',
   'sonuc':'Oylama öncesi iki kez yeter sayı bulunamadı; birleşim kapandı.',
   'pasajlar':['0406-tbmm-2025-24-disability-speaker-p','0406-tbmm-2025-24-disability-income-p','0406-tbmm-2025-24-noquorum-p','0406-tbmm-2025-24-second-rollcall-p'],
   'eslestirme':'Açık: Faz 3 seçili engellilik söylemi parti faaliyetlerinin işaret dili vb. biçimlerde aktarımıdır; bu özel hedefin gerçekleştiği söylenemez.',
   'sinir':'10/3464 araştırma önergesi, ayrı 2/2159 kanun teklifi değildir; teklifin kabulü, reddi veya gelir ödemesi çıkarılamaz.'},
  {'olay_anahtari':'tbmm-28-4-24-10-3465-gundem','tarih':'2025-12-03','konu':'ifade-basin-ozgurlugu',
   'kapsam_id':'practice-33fce432b340885da50a844c295fd2cb8aef5ce118cd8573d928f7e3588cc0de',
   'katki':'Ceylan Akça Cupolo DEM grubu adına Yeni Yol ön görüşme takvimi önerisine evet diyeceklerini söyledi ve medya iklimine ilişkin öneriler sundu.',
   'sonuc':'Başkan ön görüşme takvimi önerisinin kabul edilmediğini duyurdu.',
   'pasajlar':['0406-tbmm-2025-24-speaker-p','0406-tbmm-2025-24-support-p','0406-tbmm-2025-24-media-speech-p','0406-tbmm-2025-24-declined-p'],
   'eslestirme':'Faz 3 0305-dem-program-basin-yerel-summary / quote yerel basını güçlendirme söylemiyle aynı genel alan; sonuç ve kapsamları farklı.',
   'sinir':'Grup adına oy niyeti bireysel oy cetveli değildir; takvim önerisi sonucu alttaki araştırma önergesinin sonucu veya ilan harcaması değildir.'}]}
(root / 'tbmm-2025-24-extended-source-slices-draft.json').write_text(json.dumps(draft, ensure_ascii=False, indent=2)+'\n')
(root / 'tbmm-2025-24-two-candidates-evidence-draft.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print('TWO_CANDIDATES_SOURCE_EXACT_PASS', len([x for x in entries if x['kind']=='passage']))
