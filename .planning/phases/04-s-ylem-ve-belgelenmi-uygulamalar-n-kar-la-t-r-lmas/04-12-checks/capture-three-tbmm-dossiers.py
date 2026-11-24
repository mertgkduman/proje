"""Register TBMM filings, dates and public antecedents for three researched cases."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(sys.argv[1])
root = Path('data/practices/sources/demokrat')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def save(relative, payload):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == payload
    else:
        path.write_bytes(payload)
    paths.add(path)


def read(filename):
    return json.loads((checks / filename).read_bytes())


may = {r['name']: r for r in read('may-2025-bills-source-reading.json')['sources']}
drug = {r['name']: r for r in read('drug-20085-source-reading.json')['sources']}
interview = next(row for row in read('party-news-007-reading.json')['examined'] if row['position'] == 74)
sources = (
    ('city-statement', may['tbb-visit.html'], '5 Kasım 2024 TBB ve Demokrat Parti görüşmesi', '2024-11-05',
     'Türkiye Belediyeler Birliği', 'official', (
         ('quote', None, None, 'Uysal’ın kayyım uygulaması üzerine açıklaması',
          'Bu uygulamaları hiçbir şekilde kabul etmiyoruz.'),
         ('context', None, None, 'TBB’nin görüşme konusu',
          'belediyelere kayyım atamaları gündemini değerlendirmek üzere'),
     )),
    ('city-register', may['register-3139.html'], '2/3139 TBMM esas sicili', None, 'TBMM', 'official', (
         ('number', None, None, 'Esas numarası', '2 / 3139'),
         ('filing', None, None, 'Başkanlığa geliş günü', '22/05/2025'),
         ('committee', None, None, 'Komisyona sevk günü', '23/05/2025'),
         ('status', None, None, 'Erişim sırasındaki durum', 'KOM&#x130;SYONDA'),
     )),
    ('city-signed', may['signed-3139.pdf'], '2/3139 imzalı teklif', '2025-05-22', 'TBMM', 'official', (
         ('number', 0, None, 'Esas numarası ve İçişleri Komisyonu kaydı', 'Esas No:2/3139'),
         ('article3', 4, None, 'Üçüncü maddenin 5393 sayılı Kanunun 45. maddesine değişiklik teklifi',
          'Kanunun 45. maddesi şu şekilde değiştirilmiştir'),
         ('selection', 5, None, 'Belediye meclisi üyeleri arasından gizli oyla seçim',
          'Belediye başkanı veya başkan vekili belediye meclis üyeleri arasından ve gizli oyla seçilir.'),
         ('article4', 5, None, 'Dördüncü maddede 5393 sayılı Kanunun 45. maddesinin kaldırılması',
          'Kanunun 45. Maddesi yürürlükten'),
     )),
    ('penal-statement', interview, '1 Ekim 2024 Uysal’ın söyleşisinin Demokrat Parti aktarımı', '2024-10-01',
     'Demokrat Parti', 'party_publication', (
         ('quote', None, None, 'Ceza kanunu düzenlemesi çağrısı', 'yeni ceza kanunu yapmalıyız.'),
         ('context', None, None, 'Uysal’ın af yetkisi üzerine ayrı cümlesi',
          'Hi&ccedil;bir iktidarın da af &ccedil;ıkarma yetkisi olmamalı.'),
     )),
    ('penal-register', may['register.html'], '2/3144 TBMM esas sicili', None, 'TBMM', 'official', (
         ('number', None, None, 'Esas numarası', '2 / 3144'),
         ('filing', None, None, 'Başkanlığa geliş günü', '26/05/2025'),
         ('committee', None, None, 'Komisyona sevk günü', '28/05/2025'),
         ('status', None, None, 'Erişim sırasındaki durum', 'KOM&#x130;SYONDA'),
     )),
    ('penal-signed', may['signed.pdf'], '2/3144 imzalı teklif', '2025-05-26', 'TBMM', 'official', (
         ('number', 0, None, 'Esas numarası ve Adalet Komisyonu kaydı', 'Esas No:2/3144'),
         ('ratio', 3, None, 'Genel gerekçede koşullu salıverilme süresinin artırılması',
          'genel sürenin yarıdan dörtte üçe çıkarılması'),
         ('recidivism', 8, None, 'Türk Ceza Kanununun 58. maddesi için tekerrür değişikliği', 'Suçta tekerrür'),
     )),
    ('drug-signed', drug['question.pdf'], '7/20085 imzalı yazılı soru', '2024-12-04', 'TBMM', 'official', (
         ('signature-date', 0, None, 'İmzalı yazılı soru metnindeki tarih', '04.12.2024'),
         ('questions', 0, None, 'İlaç arzı, üretim ve teşvikleri hakkında yazılı soru',
          'ne tür teşvikler'),
         ('teb-attribution', 0, None, 'Soru gerekçesinde TEB’e atfedilen miktar', '2.500’ü aştığı'),
     )),
    ('drug-register', drug['register.html'], '7/20085 TBMM esas sicili', None, 'TBMM', 'official', (
         ('number', None, None, 'Esas numarası', '7 / 20085'),
         ('filing', None, None, 'Başkanlığa geliş günü', '05.12.2024'),
         ('status', None, None, 'Erişim sırasındaki durum',
          'Cevaplanmad&#x131;&#x11F;&#x131; Gelen Ka&#x11F;&#x131;tlarda &#x130;lan Edildi'),
     )),
    ('drug-filed', drug['printed-33.pdf'], '13 Aralık 2024 basılı birleşim listesi', '2024-12-13', 'TBMM', 'official', (
         ('filing', 16, '721', 'İlk listede geliş tarihi ve esas numarası',
          '(7/20085) (Başkanlığa geliş tarihi: 05.12.2024)'),
     )),
    ('drug-notice', drug['printed-44.pdf'], '7 Ocak 2025 basılı birleşim ve süresinde cevaplanmayan sorular',
     '2025-01-07', 'TBMM', 'official', (
         ('heading', 17, '702', 'Süresinde cevaplanmayan sorular dizininin başlığı',
          'Süresi İçinde Cevaplandırılmayan Yazılı Soru Önergeleri'),
         ('item', 21, '706', 'Sağlık Bakanlığı başlığında 84. sıradaki kayıt', 'önergesi (7/20085)'),
     )),
)

for label, record, title, day, publisher, attribution, anchors in sources:
    path = checks / record['original_path']
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == record['sha256']
    kind = 'pdf' if path.suffix == '.pdf' else 'html'
    document = f'0412-three-dossiers-{label}'
    version = document + '-v1'
    original = f'objects/{digest}/' + ('original.pdf' if kind == 'pdf' else 'original.html.bin')
    readable = f'objects/{digest}/readable.html'
    save(original, raw)
    save(readable, readable_bytes(raw, kind, legacy=False))
    add('document', id=document, party_id='demokrat', title=title,
        source_kind='party' if attribution == 'party_publication' else 'official')
    add('document_version', id=version, document_id=document, original_url=record['url'], final_url=record['url'],
        document_date=day, date_precision='day' if day else 'unknown',
        date_unknown_reason=None if day else 'Dinamik sicil sayfasının ilk yayın günü bilinmiyor.',
        version_label='Yayıncının özgün nüshası.', accessed_at=record['accessed_at'], verified_at=now,
        mime='application/pdf' if kind == 'pdf' else 'text/html',
        sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=version, publisher=publisher, author=None,
        kind=attribution, published_at=day, date_precision='day' if day else 'unknown', social_handle=None,
        public_url=record['url'],
        basis='Parti sayfası söyleşiyi Sözcü’ye atfediyor.' if label == 'penal-statement'
        else 'Yayımlayan kurum, belge kimliği ve belge içi kayıt.')
    if kind == 'html':
        view = build_view(raw, record['url'], root, fetch_assets=False)
        view['version_id'] = version
        validate_view(root, view)
        manifest = root / view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent / f for f in json.loads(manifest.read_bytes())['files'])
        add('archive_view', **view)
    for suffix, index, printed, section, exact in anchors:
        text = pdf_page_text(root / original, index) if kind == 'pdf' else html_source_text(raw)
        assert exact in text, (label, suffix, exact)
        add('passage', id=f'{document}-{suffix}', version_id=version, exact=exact, prefix=None,
            suffix=None, article=None, section=section, pdf_page_index=index, printed_page=printed)

(checks / 'three-dossiers-source-records.json').write_text(
    json.dumps(dict(party_id='demokrat', entries=entries), ensure_ascii=False, indent=2) + '\n')
print('\n'.join(str(p) for p in sorted(paths)))
