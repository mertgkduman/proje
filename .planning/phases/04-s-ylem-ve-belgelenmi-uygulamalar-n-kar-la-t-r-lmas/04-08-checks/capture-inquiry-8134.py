"""Archive the signed motion and the official filing and appendix records."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_exists, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/yeni-yol')
stem = '0408-inquiry-8134'
now = datetime.now(timezone.utc).isoformat()
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
    ('register.html', 'register', '8/134 genel görüşme önergesi TBMM esas kaydı', None,
     'https://tbmm.gov.tr/Denetim/Genel-Gorusme-Onergesi-Detay/70ad73c1-989d-4ea3-bbcd-019edee4a171',
     '7d06afa4774d8c2eb7eb30277085353099844687a364094fed563e30fc789b9e', (
         ('number', 'TBMM 8/134 esas numarası', None, '8 / 134'),
         ('day', 'TBMM Başkanlığına geliş tarihi', None, '17/06/2026'),
         ('party', 'İlk imza sahibinin parti ve seçim çevresi', None, ' B&#xFC;lent KAYA</a></td>\n                                        <td>Yeni Yol Partisi</td>'),
         ('pending', 'TBMM esas kaydında erişimde gösterilen durum', None, 'G&#xFC;ndemde'),
     )),
    ('signed.pdf', 'signed', '8/134 imzalı genel görüşme önergesi', '2026-06-17',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T8/WebOnergeMetni/9516925c-a2a9-4363-9814-289108a37f4d.pdf',
     '72a0dde5187f0557c862474aca020a72b5f51a595e561473802a09c4262806be', (
         ('number', 'İmzalı önergenin numara katmanı', 0, '8/134'),
         ('request', 'İmzalı dosyanın gerekçesinde genel görüşme istemi', 2,
          'bir Genel Görüşme açılması zaruri ve ertelenemez bir görevdir.'),
         ('lower-bound', 'Gerekçe son paragrafında alt sınır ve tedbir', 2,
          'en düşük emekli aylığının hiçbir koşulda asgari ücretin altına düşmeyecek şekilde yasal güvenceye kavuşturulması'),
         ('adjustment', 'Gerekçe son paragrafında intibak talebi', 2, 'adil bir intibak yasasının çıkarılması'),
         ('signatories', 'İmzalar sayfası Bülent Kaya satırı', 3, 'BÜLENT KAYA    İSTANBUL'),
     )),
    ('incoming.html', 'incoming', '108. Birleşim gelen kâğıtlar listesi', '2026-07-01',
     'https://tbmm.gov.tr/Gundem/GelenKagitDetay/32b91820-51d0-430b-a400-019f1c67bf61',
     '49c63a51a20ec32a663f997a7ada93184708231ba0dad492ebbe9daf8375e728', (
         ('listed', 'Gelen kâğıtlar listesinde 8/134 ve 17 Haziran kaydı', None,
          '(8/134) (Başkanlığa geliş tarihi:17.06.2026)'),
     )),
    ('108.pdf', 'appendix', '1 Temmuz 2026 TBMM 108. Birleşim basılı tutanağı', '2026-07-01',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/108/Basilmis/8c78bb73-5fa2-43ca-965a-aa0deaac261e.pdf',
     '64997aaa954056faaeea620b8d5519d03f44b5269922388a8c9340560369fa79', (
         ('listed', 'Basılı sayfa 931 genel görüşme önergeleri eki', 32,
          'açılmasına ilişkin önergesi (8/134) (Başkanlığa geliş tarihi:17.06.2026)'),
     )),
)
for filename, label, title, day, url, digest, anchors in sources:
    path = stage / filename
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == digest
    fmt = 'pdf' if filename.endswith('.pdf') else 'html'
    doc = f'{stem}-{label}'
    version = f'{doc}-v1'
    obj = f'objects/{digest}/' + ('original.pdf' if fmt == 'pdf' else 'original.html.bin')
    readable = f'objects/{digest}/readable.html'
    store(obj, raw)
    store(readable, readable_bytes(raw, fmt, legacy=False))
    add('document', id=doc, party_id='yeni-yol', title=title, source_kind='official')
    add('document_version', id=version, document_id=doc, original_url=url, final_url=url, document_date=day,
        date_precision='day' if day else 'unknown', date_unknown_reason=None if day else 'Dinamik TBMM esas kaydının ilk yayın günü bilinmiyor.',
        version_label='TBMM özgün kaynak nüshası.', accessed_at=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        verified_at=now, mime='application/pdf' if fmt == 'pdf' else 'text/html', sha256=digest,
        original_path=obj, readable_path=readable)
    add('source_attribution', version_id=version, publisher='TBMM', author='Bülent Kaya ve 19 milletvekili' if label=='signed' else None,
        kind='official', published_at=None, date_precision='unknown', social_handle=None, public_url=url,
        basis='TBMM esas kaydı, imzalı önerge veya gelen kâğıtların tutanak eki.')
    if fmt == 'html':
        view = build_view(raw, url, root, fetch_assets=False)
        view['version_id'] = version
        validate_view(root, view)
        manifest = root / view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent / name for name in json.loads(manifest.read_bytes())['files'])
        add('archive_view', **view)
    for suffix, section, index, exact in anchors:
        passage = f'{doc}-{suffix}'
        manual = label == 'signed' and suffix != 'number'
        if manual:
            assert pdf_page_exists(root / obj, index) and not pdf_page_text(root / obj, index).strip()
        else:
            text = pdf_page_text(root / obj, index) if fmt == 'pdf' else html_source_text(raw)
            assert exact in text, (label, suffix)
        add('passage', id=passage, version_id=version, exact=exact, prefix=None, suffix=None, article=None,
            section=section, pdf_page_index=index, printed_page='931' if label == 'appendix' else None)
        if manual:
            add('manual_passage', passage_id=passage, checked_at=now,
                method='Özgün dört imzalı PDF sayfası Poppler görüntüsünde okundu.',
                reason='İmza veya gerekçe pasajı taranmış görselden kontrol edildi.')
(checks / 'inquiry-8134-v2-source-records.json').write_text(json.dumps(dict(party_id='yeni-yol', entries=entries), ensure_ascii=False, indent=2) + '\n')
(stage / 'inquiry-8134-source-paths').write_text('\n'.join(sorted(map(str, paths))) + '\n')
print(len(entries), len(paths))
