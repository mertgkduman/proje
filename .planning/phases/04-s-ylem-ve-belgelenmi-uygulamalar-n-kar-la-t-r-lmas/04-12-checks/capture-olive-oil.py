"""Register the statement and separately dated olive-oil export measures."""

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


raw_sources = {row["name"]: row for row in read("olive-oil-source-reading.json")["sources"]}
source_fields = (('floor',
  'floor.pdf',
  '8 Mayıs 2024 79. Birleşim Altıntaş konuşması',
  '2024-05-08',
  'TBMM',
  (('speaker',
    108,
    '313',
    'Birleşim başkanının şahsı adına söz verdiği kişi',
    'Şahısları adına ikinci söz talebi İzmir Milletvekili Haydar Altıntaş’a aittir.'),
   ('demand',
    108,
    '313',
    'Altıntaş’ın zeytinyağı ihracat kısıtını kaldırma çağrısı',
    'zeytinyağı ihracat yasağı bir an evvel kaldırılıp'))),
 ('quota',
  'quota.pdf',
  '7/12491 cevabında 1 Haziran ihracat kotası',
  '2024-07-03',
  'Tarım ve Orman Bakanlığı',
  (('authority', 0, None, 'TBMM’ye gönderilen 7/12491 cevabının başlığı', 'Soru Önergesi (7/12491)'),
   ('limit',
    1,
    '1',
    'Bakanlığın bildirdiği 50 bin ton kota ve tarihler',
    '1 Haziran 2024 tarihinden itibaren Türk zeytinyağı ihracatçılarına 1 Kasım 2024 tarihine kadar 50 '
    'bin ton kota'))),
 ('removal',
  'removal.pdf',
  '7/23091 cevabında 13 Eylül kısıt kaldırılması',
  '2025-03-20',
  'Tarım ve Orman Bakanlığı',
  (('authority', 0, None, 'TBMM’ye gönderilen 7/23091 cevabının başlığı', 'Soru Önergesi (7/23091)'),
   ('effect',
    2,
    '2',
    'Bakanlığın daha sonraki cevabında kısıtların kaldırıldığı gün',
    '13 Eylül 2024 yılı itibarıyla zeytinyağı ihracatındaki tüm kısıtlar kaldırılmıştır.'))),
 ('gazette',
  'gazette.pdf',
  '14 Eylül Resmî Gazete’de 8957 sayılı karar',
  '2024-09-14',
  'Resmî Gazete',
  (('day', 0, None, '8957 yayım günü ve sayısı', '14 Eylül 2024 CUMARTESİ'),
   ('decision',
    0,
    None,
    '8957 numarası ve aynı sayfanın görüntüsündeki yürürlükten kaldırma hükmü',
    'Karar Sayısı: 8957'))),
 ('old-gazette',
  'gazette-7391-gaib.pdf',
  '19 Temmuz Resmî Gazete’de 7391 sayılı kararın GAİB kopyası',
  '2023-07-19',
  'Resmî Gazete',
  (('decision',
    0,
    None,
    '7391 numarası ve aynı sayfada görüntü olarak yer alan fon kesintisi',
    'Karar Sayısı: 7391'),)),
 ('notice',
  'gaib-notice.html',
  '24 Temmuz 2023 GAİB zeytinyağı kayıt duyurusu',
  '2023-07-24',
  'Güneydoğu Anadolu İhracatçı Birlikleri',
  (('rate',
    None,
    None,
    '7391’e bağlı fon kesintisinin bildirilen kilogram başına tutarı',
    'kg. başına 20 cent kesinti yapılması'),)))
sources = [(label, raw_sources[filename], title, day, publisher, "official", anchors)
           for label, filename, title, day, publisher, anchors in source_fields]

for label, record, title, day, publisher, attribution, anchors in sources:
    path = checks / record['original_path']
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest == record['sha256']
    kind = 'pdf' if path.suffix == '.pdf' else 'html'
    document = f'0412-olive-oil-{label}'
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
        basis='Resmî Gazete sayfasının GAİB kopyası.' if label == 'old-gazette'
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
        optical = label in ('quota', 'removal')
        if optical:
            assert not text.strip()
        else:
            assert exact in text, (label, suffix, exact)
        passage_id = f'{document}-{suffix}'
        add('passage', id=passage_id, version_id=version, exact=exact, prefix=None,
            suffix=None, article=None, section=section, pdf_page_index=index, printed_page=printed)
        if optical:
            add('manual_passage', passage_id=passage_id, checked_at=now,
                method='Özgün tarama PDF sayfası Poppler görüntüsünde okundu.',
                reason='Sayfanın metin katmanı boş. İlgili ibare görüntüden kontrol edildi.')

(checks / 'olive-oil-source-records.json').write_text(
    json.dumps(dict(party_id='demokrat', entries=entries), ensure_ascii=False, indent=2) + '\n')
print('\n'.join(str(p) for p in sorted(paths)))
