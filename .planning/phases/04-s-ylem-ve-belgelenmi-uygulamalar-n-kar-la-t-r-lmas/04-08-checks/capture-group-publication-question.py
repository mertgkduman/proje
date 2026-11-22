"""Archive the signed question, written answer and official article copies."""

from datetime import datetime, timezone
from hashlib import sha256
import html
import json
from pathlib import Path
import re

from arsiv import html_source_text, pdf_page_exists, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view


checks = Path(__file__).resolve().parent
stage = Path('data/.staging/gsd-0408-yeni-yol-institution')
source = Path('data/practices/sources/yeni-yol')
now = datetime.now(timezone.utc).isoformat()
entries, assets, fetches = [], set(), []
publisher = 'Türkiye Büyük Millet Meclisi'


def record(table, **values):
    entries.append(dict(kind=table, values=values))


def put(relative, payload):
    path = source / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == payload
    else:
        with path.open('xb') as stream:
            stream.write(payload)
    assets.add(str(path))
    return path


def archive(name, slug, title, published, author=None, document_date=None, snippets=()):
    path = stage / name
    meta = json.loads(path.with_suffix(path.suffix + '.json').read_text())
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    assert meta['http_status'] == '200' and digest == meta['sha256'] and len(raw) == meta['byte_count']
    fetches.append(meta)
    kind = path.suffix[1:]
    ident = '0408-question-36200-' + slug
    vid = ident + '-v1'
    ext = 'pdf' if kind == 'pdf' else 'html.bin'
    immutable = f'objects/{digest}/original.{ext}'
    readable = f'objects/{digest}/readable.html'
    original = put(immutable, raw)
    put(readable, readable_bytes(raw, kind, legacy=False))
    record('document', id=ident, party_id='yeni-yol', title=title, source_kind='official')
    document_date = document_date or published
    record('document_version', id=vid, document_id=ident, original_url=meta['original_url'],
           final_url=meta['final_url'], document_date=document_date,
           date_precision='day' if document_date else 'unknown',
           date_unknown_reason=None if document_date else 'TBMM sayfasının ilk yayım günü açık.',
           version_label='TBMM’nin erişilen özgün kaydı.', accessed_at=meta['accessed_at'], verified_at=now,
           mime=meta['mime'].split(';')[0], sha256=digest, original_path=immutable, readable_path=readable)
    record('source_attribution', version_id=vid, publisher=publisher, author=author, kind='official',
           published_at=published, date_precision='day' if published else 'unknown', social_handle=None,
           public_url=meta['final_url'],
           basis='TBMM kaynak adresi, içerik türü, tarih ve ilgili başlık özgün baytlarla denetlendi.')
    if kind == 'html':
        text = html_source_text(raw)
        view = build_view(raw, meta['final_url'], source, fetch_assets=False)
        view['version_id'] = vid
        validate_view(source, view)
        record('archive_view', **view)
        manifest = source / view['manifest_path']
        assets.add(str(manifest))
        assets.update(str(manifest.parent / n) for n in json.loads(manifest.read_text())['files'])
        cells = [m.strip() for m in re.findall(r'>([^<>]+)<', text) if m.strip()]
    for code, section, marker, page in snippets:
        pid = ident+'-'+code
        if page is None:
            exact = next(cell for cell in cells if marker in html.unescape(cell))
        else:
            assert pdf_page_exists(original,page) and not pdf_page_text(original,page).strip()
            exact = marker
        record('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
               section=section,pdf_page_index=page,printed_page='1' if slug=='reply' and page==1 else None)
        if page is not None:
            record('manual_passage',passage_id=pid,checked_at=now,
                   method='İmzalı özgün PDF sayfası Poppler ile görüntülenerek okundu.',
                   reason='Pasaj ilgili soru veya yanıt sayfasındaki metinle karşılaştırıldı.')
    return raw


archive('question-36200-register.html','register','7/36200 TBMM kayıt ve cevap bilgileri',None,snippets=[
    ('number','Yasama dönemi içindeki esas numarası','7 / 36200',None),
    ('filer','Soru sahibi','Ankara Milletvekili İdris ŞAHİN',None),
    ('file-date','TBMM Başkanlığına geliş günü','07.11.2025',None),
    ('reply-date','TBMM cevabın geldiği gün','26.11.2025',None),
])
archive('official-signed.pdf','filing','Meclis Haber grup toplantıları yazılı sorusu',None,'İdris Şahin',
        document_date='2025-11-06',snippets=[
    ('letterhead','İmzalayan ve Yeni Yol Grup Başkanlığı evrak başlığı','T.B.M.M. - YENİ YOL',0),
    ('count','Soru sahibinin aynı gün iki haber için bildirdiği ilk sayı','tarihindeki grup toplantısı haber metni yalnızca 252 kelimeden oluşmaktadır.',0),
    ('criteria','Meclis Haber kapsam ve ölçüt sorusu','hangi ölçütler esas alınmaktadır?',0),
])
archive('question-36200-signed-reply.pdf','reply','TBMM Başkanvekilinin 7/36200 yazılı cevabı',
        '2025-11-26','Bekir Bozdağ',snippets=[
    ('date','Yanıt üst yazısı ve soru kimliği','07.11.2025 tarihli ve 7/36200 esas numaralı yazılı soru önergeniz.',0),
    ('television','Cevapta atıf yapılan 8 Mart 2007 toplantısının bildirilen kararı','Milletvekilleri dışında herhangi bir kimseye grup toplantılarında konuşma imkânı tanınmayacağı',1),
    ('rule','Meclis Haber için cevapta açıklanan uygulama','milletvekili olan genel başkan, genel başkanvekili veya grup başkanlarının konuşmalarına Meclis Haber Sitesinde yer verilmektedir.',1),
    ('other','İki bileşen başkanının konuşmasının yayımlanmamasına verilen gerekçe','milletvekili olmamaları nedeniyle haber yapılamamaktadır.',1),
])

reports = [
    ('group-05','2025-11-05','Yeni Yol grubunda 5 Kasım Meclis Haber kaydı',
     'Yurt dışındaki vatandaşların TBMM’de atılacak adımları beklediğini',252,32),
    ('group-12','2025-11-12','Yeni Yol grubunda 12 Kasım Meclis Haber kaydı',
     'Toplantıda Saadet Partisi Genel Başkanı Mahmut Arıkan ve Gelecek Partisi Genel Başkanı Ahmet Davutoğlu',437,13),
    ('ak-group-05','2025-11-05','AK Parti grubunda 5 Kasım Meclis Haber karşılaştırma kaydı',
     'AK Parti TBMM Grup Toplantısı',3162,27),
]
counts = []
for slug,day,title,marker,expected_body,expected_summary in reports:
    raw = archive(f'question-36200-{slug}.html',slug,title,day,snippets=[
        ('published','Haber sayfasının yayın günü',day,None),
        ('group','Haber gövdesinde toplantı ve konuşmacı',marker.replace('’', "'"),None),
    ])
    text = html_source_text(raw)
    parts = {}
    for selector in ('haber-detay-ozet','haber-detay-aciklama'):
        contents = text.split(f'id="{selector}"',1)[1].split('</div>',1)[0].split('>',1)[1]
        parts[selector] = html.unescape(re.sub(r'<[^>]+>',' ',contents))
    article, summary = (parts[selector] for selector in ('haber-detay-aciklama','haber-detay-ozet'))
    assert (len(article.split()),len(summary.split())) == (expected_body,expected_summary)
    counts.append(dict(version_id=f'0408-question-36200-{slug}-v1',body_words=expected_body,summary_words=expected_summary,
                       article_body_mentions={name:article.count(name) for name in ('Arıkan','Babacan','Davutoğlu')}))

out = checks / 'group-publication-question-sources.json'
with out.open('x') as stream:
    stream.write(json.dumps(dict(party_id='yeni-yol',fetches=fetches,entries=entries,word_counts=counts,
        word_count_method='Arşivli HTML içinde haber-detay-aciklama gövdesinde etiket çıkarımı ve boşluk sınırlı sözcük sayımı. Özet ayrı sayıldı.'),
        ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0408-group-publication-source-paths').write_text('\n'.join(sorted(assets))+'\n')
print(len(fetches),len(entries),len(assets),sha256(out.read_bytes()).hexdigest())
