"""Register primary printed passages for the motion, official ballot and law record."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, temporary = map(Path, sys.argv[1:])
root = Path('data/practices/sources/demokrat')
checked_at = datetime.now(timezone.utc).isoformat()
entries, saved_paths = [], set()
stem = '0412-siber-7545'
party_accessed_at = '2026-11-24T03:24:02.804369+00:00'


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def save(relative, payload):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == payload
    else:
        path.write_bytes(payload)
    saved_paths.add(path)


sources = (
    ('printed', 'pdf', '65. Birleşim basılı tutanağı ve kesin oy cetveli', '2025-03-12',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/3/65/Basilmis/6285d9cd-b236-4934-9967-b367a97412a3.pdf',
     '805d981e9e8912c58971550e535e9e9f11ad6669a0f754b40b42a7f2b171bee3', (
         ('motion', 112, 'Geçici 1. maddenin çıkarılmasına ilişkin ilk önergenin metni',
          'geçici madde 1’in teklif metninden\nçıkarılmasını arz ve teklif ederiz.'),
         ('signer', 112, 'Önergenin İzmir milletvekili imza hanesi', 'Haydar Altıntaş\nİzmir'),
         ('speech', 112, 'İki önerge üzerine Başkanın ilk söz verdiği konuşmacı',
          'Aynı mahiyetteki önergeler üzerinde ilk konuşmacı İzmir Milletvekili Haydar Altıntaş.'),
         ('motion-vote', 114, 'İki aynı mahiyette önergenin birlikte oylanması',
          'Kabul etmeyenler...\nÖnergeler kabul edilmemiştir.'),
         ('announced', 135, 'Başkanın teklifin tümü üzerindeki ilk sonuç ilanı',
          'Oy sayısı : 348\nKabul : 246\nRet : 102'),
         ('passed', 135, 'Teklifin tümü üzerine oylamanın kabul sonucu',
          'Teklif kabul edilmiş ve kanunlaşmıştır.'),
         ('footnote', 135, 'İlk ilandan kesin cetvele yönlendiren 6. dipnot',
          'Açık oylama kesin sonuçlarını gösteren tablo tutanağa eklidir.'),
         ('final-count', 136, 'Kesin cetvelde kabul ve ret sayısı', ': 245\n: 101'),
         ('duplicate-count', 136, 'Kesin cetvelde iki mükerrer dahil toplam', ':\n2\n: 348'),
         ('named-vote', 144, 'Kesin cetvelde Altıntaş, DP ve Katılmadı hanesi',
          'İzmir Altıntaş Haydar DP Katılmadı'),
     )),
    ('act', 'html', 'TBMM 7545 sayılı Siber Güvenlik Kanunu kaydı', None,
     'https://tbmm.gov.tr/Yasama/Kanun/af1dfbdb-e3e3-4820-a493-0194504c63b4',
     '4f053be022f27bb05cb2a6c2fc5d2462d475cd845dd460779c9c0dadc393b5bd', (
         ('number', None, 'Kanun numarası', '7545'),
         ('acceptance-day', None, 'TBMM kabul tarihi', '<td>12/03/2025</td>'),
         ('gazette-day', None, 'Resmî Gazete yayım tarihi', '<td> 19/03/2025</td>'),
         ('gazette-number', None, 'Resmî Gazete numarası', '<td>32846</td>'),
     )),
    ('party-report',
     'html',
     '19 Mart Demokrat Parti konuşma aktarımı',
     '2025-03-19',
     'https://www.dp.org.tr/haber/demokrat-parti-sozcusu-ve-i-zmir-milletvekili-haydar-altintas-demokrasinin-kesintiye-ugramasinin-bedelini-millet-odedi',
     '87d6a083cc7119748d64d4bc24d933c3566e256e1b6b0673bfe47774dc931247',
     (('membership',
       None,
       'Parti yayınının Altıntaş adı ve görevi geçen başlığı',
       'Demokrat Parti Sözcüsü ve İzmir Milletvekili Haydar Altıntaş'),)),
)
for label, kind, title, day, url, expected, anchors in sources:
    path = temporary / f'{label}.{kind}'
    party_publication = label == 'party-report'
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == expected
    document = f'{stem}-{label}'
    version = document + '-v1'
    original = f'objects/{digest}/' + ('original.pdf' if kind == 'pdf' else 'original.html.bin')
    readable = f'objects/{digest}/readable.html'
    save(original, raw)
    save(readable, readable_bytes(raw, kind, legacy=False))
    add('document', id=document, party_id='demokrat', title=title, source_kind='party' if party_publication else 'official')
    add('document_version', id=version, document_id=document, original_url=url, final_url=url,
        document_date=day, date_precision='day' if day else 'unknown',
        date_unknown_reason=None if day else 'Sicil sayfasının ilk yayın günü bilinmiyor.',
        version_label='Yayıncının özgün nüshası.',
        accessed_at=party_accessed_at if party_publication else
          datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        verified_at=checked_at, mime='application/pdf' if kind == 'pdf' else 'text/html',
        sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=version,
        publisher='Demokrat Parti' if party_publication else 'TBMM', author=None,
        kind='party_publication' if party_publication else 'official',
        published_at=day, date_precision='day' if day else 'unknown', social_handle=None,
        public_url=url, basis='Kaynağın başlığı, yayımlayan kurum ve belirtilen kişi veya yasama işlemi.')
    if kind == 'html':
        view = build_view(raw, url, root, fetch_assets=False)
        view['version_id'] = version
        validate_view(root, view)
        manifest = root / view['manifest_path']
        saved_paths.add(manifest)
        saved_paths.update(manifest.parent / f for f in json.loads(manifest.read_bytes())['files'])
        add('archive_view', **view)
    for suffix, index, section, exact in anchors:
        text = pdf_page_text(root / original, index) if kind == 'pdf' else html_source_text(raw)
        assert exact in text, (label, suffix, exact)
        add('passage', id=f'{document}-{suffix}', version_id=version, exact=exact, prefix=None,
            suffix=None, article=None, section=section, pdf_page_index=index,
            printed_page=str(index + 1) if index is not None else None)
(checks / 'siber-7545-source-records.json').write_text(
    json.dumps(dict(party_id='demokrat', entries=entries), ensure_ascii=False, indent=2) + '\n')
(temporary / 'siber-7545-source-paths').write_text('\n'.join(sorted(map(str, saved_paths))) + '\n')
print(len(entries), len(saved_paths))
