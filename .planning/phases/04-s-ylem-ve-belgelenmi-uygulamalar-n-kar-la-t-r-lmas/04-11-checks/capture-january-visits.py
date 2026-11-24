"""Preserve the January announcement and both parties' public meeting accounts."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/saadet')
when = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


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


sources = (
    ('dha-28', '28 Ocak Arıkan’ın partiler arası görüşme açıklaması', '2026-01-28',
     'Demirören Haber Ajansı', 'Aliekber Mete ve Emirhan Yüzügüldü', 'journalism',
     'https://www.dha.com.tr/yerel-haberler/ankara/arikan-yeni-yol-grubuna-ozellikle-ak-partili-2807314',
     'b1fc59b45addd42133d5399c8ed6f3d62066af03fbf7fc6e35fe67a875ffb22d',
     (
         ('dem', '28 Ocak basın buluşmasında ertesi gün için duyurulan DEM Parti ziyareti',
          'yarın DEM Parti heyeti partimize ziyarette bulunacak'),
         ('iyi', '28 Ocak basın buluşmasında duyurulan İYİ Parti görüşmesi',
          'Anahtar Parti ve İYİ Parti ile görüşmelerimiz olacak'),
         ('quote', 'Arıkan’ın genel temas hedefi', 'bütün partilerle görüşeceğiz'),
     )),
    ('independent-29', '29 Ocak Saadet ve DEM Parti basın açıklaması', '2026-01-29',
     'Independent Türkçe', None, 'journalism',
     'https://www.indyturk.com/node/772046/siyaset/dem-partiden-saadet-partisine-ziyaret-saadet-partisinin-mecliste-suriyeyle',
     '928a1998e5667d8eab049850da762d8abe1d9640c7bf9c8fe419e9b3f8863e84',
     (
         ('place', 'Saadet Partisi Genel Merkezindeki ziyaret', 'Saadet Partisi Genel Merkezi’nde gerçekleşen görüşmede'),
         ('press', 'Görüşme sonrasındaki basın açıklaması', 'taraflar basın mensuplarına açıklamalarda bulundu'),
         ('support', 'Bakırhan’ın Meclis heyeti önerisine desteği', 'buna katılıyoruz, destekliyoruz.'),
     )),
    ('nefes-30', '30 Ocak Saadet ve İYİ Parti görüşmesinin ANKA aktarımı', '2026-01-30',
     'Nefes', 'ANKA Haber Ajansı', 'journalism',
     'https://www.nefes.com.tr/dervisoglu-turkiyenin-bir-guvenlik-koridoru-olusturmasi-gerekiyor-100415',
     '33fee13346a73903897ee07fb9bd7586c1ce1c9cd823b7aafa3068b66c890c9e',
     (
         ('visit', 'Arıkan’ın İYİ Parti kurultayı sonrasındaki ziyaret açıklaması',
          'İYİ Parti’nin 4. Olağan Kurultayı sonrasında bir hayırlı olsun ziyareti gerçekleştirdik'),
         ('contact', 'Arıkan’ın partiler arası görüşmelerin sürmesine yönelik açıklaması',
          'iki parti arasındaki müzakerelerin devam etmesi'),
     )),
)

for label, title, day, publisher, author, kind, url, digest, anchors in sources:
    path = stage / (label + '.html')
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == digest
    document = '0411-jan-visits-' + label
    version = document + '-v1'
    original = f'objects/{digest}/original.html.bin'
    readable = f'objects/{digest}/readable.html'
    store(original, raw)
    store(readable, readable_bytes(raw, 'html', legacy=False))
    add('document', id=document, party_id='saadet', title=title,
        source_kind='party' if kind == 'party_publication' else 'journalism')
    add('document_version', id=version, document_id=document, original_url=url, final_url=url,
        document_date=day, date_precision='day', date_unknown_reason=None,
        version_label='Yayıncının özgün HTML nüshası.',
        accessed_at=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        verified_at=when, mime='text/html', sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=version, publisher=publisher, author=author, kind=kind,
        published_at=day, date_precision='day', social_handle=None, public_url=url,
        basis='Yayıncı, haber künyesi ve tarihli kamuya açık toplantı aktarımı.')
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

(checks / 'january-visits-source-records.json').write_text(
    json.dumps(dict(party_id='saadet', entries=entries), ensure_ascii=False, indent=2) + '\n')
(stage / 'january-visits-source-paths').write_text('\n'.join(sorted(map(str, paths))) + '\n')
print(len(entries), len(paths))
