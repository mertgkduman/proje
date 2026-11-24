"""Preserve the public bargaining statement and municipal signature reports."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/demokrat')
when = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()
party_accessed_at = '2026-11-24T03:24:01.630431+00:00'


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def store(relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content
    else:
        path.write_bytes(content)
    paths.add(path)


sources = (('party-statement',
  '3 Haziran Altıntaş’ın İzmir grevi açıklaması',
  '2025-06-03',
  'Demokrat Parti',
  'Haydar Altıntaş',
  'party_publication',
  'https://www.dp.org.tr/haber/parti-sozcusu-ve-i-zmir-milletvekili-haydar-altintas-i-zmir-buyuksehir-belediyesi-nde-yasanan-grev-sadece-bir-toplu-is-sozlesmesi-krizinden-ibaret-degildir',
  '83b1dbb33fd55623f95417e7e69b6826508a9598cc97c9367ba28e56e1dc13bf',
  (('target',
    'Altıntaş’ın görüşmeleri yeniden başlatma talebi',
    'Toplu s&ouml;zleşme g&ouml;r&uuml;şmeleri derhal sosyal diyalog ilkesi &ccedil;er&ccedil;evesinde '
    'yeniden başlatılmalıdır.'),
   ('quote', 'Altıntaş’ın görüşmeler için kullandığı kısa ifade', 'yeniden başlatılmalıdır.'))),
 ('municipal-izelman',
  '4 Haziran İZELMAN toplu iş sözleşmesi imza duyurusu',
  '2025-06-04',
  'İzmir Büyükşehir Belediyesi',
  None,
  'official',
  'https://www.izmir.bel.tr/tr/Haberler/izmir-buyuksehir-belediyesi-ile-izelman-arasinda-suren-tiste-imzalar-atildi/56342/156',
  '2fffecf1cf22e8bec3f6521079be56928ce1d6fa54f76cd8045e793e41674e29',
  (('union', 'İZELMAN imza duyurusunda iki sendika şubesi', "İzmir 1 ve 3 No'lu Şubeler"),
   ('signature', 'İZELMAN imza duyurusunda imzaya katılan kişiler', "3 No'lu Şube Başkanı Serap Yılmaz"),
   ('izenerji', 'Aynı yayında İZENERJİ görüşmelerinin o andaki durumu', 'sona gelindiğini aktardı.'))),
 ('municipal-later',
  '19 Haziran belediye duyurusunda önceki sözleşme imzalarına atıf',
  '2025-06-19',
  'İzmir Büyükşehir Belediyesi',
  None,
  'official',
  'https://www.izmir.bel.tr/tr/Haberler/izdeniz-de-imzalar-atildi/56419/156',
  'c465c1a0e838cebdf627096e1e30f353f68a3f4e42e1c587aef254521408e689',
  (('date',
    'İZELMAN ve İZENERJİ sözleşmelerinin imza gününe yapılan atıf',
    'İzelman AŞ ve İzenerji AŞ ile DİSK Genel İş arasında 4 Haziran’da imzalanan sözleşmede'),
   ('rate',
    'Belediye başkanının önceki ücret artışına ilişkin aktarımı',
    'yüzde 30 zam oranının kabul edildiğini'))))

for label, title, day, publisher, author, kind, url, digest, anchors in sources:
    path = stage / (label + '.html')
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == digest
    document = '0412-izmir-tis-' + label
    version = document + '-v1'
    original = f'objects/{digest}/original.html.bin'
    readable = f'objects/{digest}/readable.html'
    store(original, raw)
    store(readable, readable_bytes(raw, 'html', legacy=False))
    add('document', id=document, party_id='demokrat', title=title,
        source_kind='party' if kind == 'party_publication' else 'official')
    add('document_version', id=version, document_id=document, original_url=url, final_url=url,
        document_date=day, date_precision='day', date_unknown_reason=None,
        version_label='Yayıncının özgün HTML nüshası.',
        accessed_at=party_accessed_at if label == 'party-statement' else
                    datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        verified_at=when, mime='text/html', sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=version, publisher=publisher, author=author, kind=kind,
        published_at=day, date_precision='day', social_handle=None, public_url=url,
        basis='Parti açıklaması veya belediyenin günlü toplu iş sözleşmesi duyurusu.')
    view = build_view(raw, url, root, fetch_assets=False)
    view['version_id'] = version
    validate_view(root, view)
    manifest = root / view['manifest_path']
    paths.add(manifest)
    paths.update(manifest.parent / name for name in json.loads(manifest.read_bytes())['files'])
    add('archive_view', **view)
    text = html_source_text(raw)
    for suffix, section, exact in anchors:
        assert exact in text, (label, suffix, exact)
        add('passage', id=document + '-' + suffix, version_id=version, exact=exact,
            prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)

(checks / 'izmir-tis-source-records.json').write_text(
    json.dumps(dict(party_id='demokrat', entries=entries), ensure_ascii=False, indent=2) + '\n')
(stage / 'izmir-tis-source-paths').write_text('\n'.join(sorted(map(str, paths))) + '\n')
print(len(entries), len(paths))
