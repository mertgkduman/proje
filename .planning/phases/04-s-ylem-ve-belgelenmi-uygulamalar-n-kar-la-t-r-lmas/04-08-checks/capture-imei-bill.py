"""Archive the signed 2/3940 proposal and its distinct TBMM records."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/yeni-yol')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


def add(table, **row):
    entries.append(dict(kind=table, values=row))


def save(relative, content):
    path = root/relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content
    else:
        path.write_bytes(content)
    paths.add(path)


files = [
    ('bill.pdf', 'signed', '2/3940 imzalı kanun teklifi', '2026-10-08',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/WebOnergeMetni/b57b02fd-35c2-418c-bc68-e7c428f059f9.pdf',
     '852de5a6c94e3ee4902c17fc3a9cafe5b9bb63cb6b4edc86f85c14ed9d4a7f81', [
         ('identity', 'İmzalı üst yazıda Selçuk Özdağ’ın adı ve görevi',
          'Doç. Dr. Selçuk Özdağ\nMuğla Milletvekili\nGrup Başkanvekili', 0),
         ('signed-day', 'Üst yazıda imzalı teklif tarihi', '08.10.2026', 0),
         ('stamp', 'TBMM alındı damgası', '08 Ekim 2026', 1),
         ('sent', 'Kapakta komisyona sevk ve esas numarası', 'Tarih: 9-10-2026 Esas No:2/3940', 0),
         ('amount', 'Genel gerekçede 2026 için belirtilen tutar', '54.258 TL', 2),
         ('scope', 'Genel gerekçede harç ile cihaz kaydının ayrılması',
          'harç yükünün kaldırılması amaçlanmaktadır.', 2),
         ('article', 'Madde gerekçesinde kapsam ve kaldırılan harç',
          'elektronik kimlik bilgilerinin kayıt altına alınmasından önce ödenmesi gereken harç kaldırılmaktadır.', 3),
         ('entry', '2. maddede önerilen yürürlük',
          'Bu Kanun yayımı tarihinde yürürlüğe girer.', 4),
     ]),
    ('detail.html', 'detail', 'TBMM 2/3940 işlem dosyası', None,
     'https://tbmm.gov.tr/Yasama/KanunTeklifi/e29eda10-ff2d-445e-badc-01a11bd96a0d',
     '24bca1c5ef0bdd2c22269cc34a5db1fbbfd18ed0e5a1e99685ae98995013822d', [
         ('id', 'Dosyanın esas numarası', '<td>2 / 3940</td>', None),
         ('date', 'Dosyanın Başkanlığa geliş tarihi', '<td>07/10/2026</td>', None),
         ('sent', 'Komisyon tablosunda giriş tarihi', '<td>09/10/2026</td>', None),
         ('status', 'Komisyon tablosunda erişim anındaki durum', '<td>Komisyonda</td>', None),
     ]),
    ('papers.html', 'papers', '9 Ekim 2026 Gelen Kâğıtlar 7, 2/3940', '2026-10-09',
     'https://tbmm.gov.tr/Gundem/GelenKagitDetay/c0b82a6b-5af4-462f-a722-01a11f6539cf',
     'c2ba074d1ffde5e966abbad3c21e614b87b04a9a56dc814df3a06ad893be1464', [
         ('receipt', 'Gelen Kâğıtlarda 2/3940, komisyon ve geliş tarihi',
          'Kanun Teklifi (2/3940) (Plan ve B&uuml;t&ccedil;e Komisyonuna) (Başkanlığa geliş tarihi: 8.10.2026)', None),
     ]),
    ('speech.html', 'speech', '21 Ekim 2026 Selçuk Özdağ Genel Kurul açıklaması', '2026-10-21',
     'https://tbmm.gov.tr/Milletvekili/UyeGenelKurulKonusmalariDetay?eid=149193',
     '0eeb5ccb22fd970c0579bcfd8fc64e67bdc03b8de2aabf90496026a297e06187', [
         ('date', 'Genel Kurul açıklamasının tarihi', '<td width="85%">21.10.2026</td>', None),
         ('claim', 'Açıklamada Özdağ’ın harç tutarına ilişkin ifadesi',
          '55 bin liraya yakın para veriyorduk, onu da 70 bin liraya çıkardınız.', None),
         ('criticism', 'Özdağ’ın harca ilişkin sonuç cümlesi',
          'SELÇUK ÖZDAĞ (Muğla) - O nedenle de IMEI kayıt harcı soygununa da dur demek gerekiyor diyorum.', None),
     ]),
]
for name, key, title, day, url, digest, selected in files:
    source = stage/name
    raw = source.read_bytes()
    assert sha256(raw).hexdigest() == digest
    pdf = name.endswith('.pdf')
    doc = '0408-imei-'+key
    version = doc+'-v1'
    original = f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable = f'objects/{digest}/readable.html'
    save(original, raw)
    save(readable, readable_bytes(raw, 'pdf' if pdf else 'html', legacy=False))
    add('document', id=doc, party_id='yeni-yol', title=title, source_kind='official')
    add('document_version', id=version, document_id=doc, original_url=url, final_url=url,
        document_date=day, date_precision='day' if day else 'unknown',
        date_unknown_reason=None if day else 'İşlem portalının ilk yayın günü açık.',
        version_label='TBMM özgün nüshası.',
        accessed_at=datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now, mime='application/pdf' if pdf else 'text/html',
        sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=version, publisher='TBMM',
        author='Selçuk Özdağ' if key in ('signed','speech') else None,
        kind='official', published_at=day if key=='papers' else None,
        date_precision='day' if key=='papers' else 'unknown', social_handle=None,
        public_url=url, basis='Özgün nüshadaki kurum, belge kimliği ve tarih alanları okundu.')
    if not pdf:
        view = build_view(raw, url, root, fetch_assets=False)
        manifest = root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/f for f in json.loads(manifest.read_bytes())['files'])
        view['version_id'] = version
        validate_view(root,view)
        add('archive_view', **view)
    for suffix, section, exact, page in selected:
        if pdf:
            assert not pdf_page_text(root/original,page).strip()
        else:
            assert exact in html_source_text(raw), (key,suffix)
        pid = doc+'-'+suffix
        add('passage', id=pid, version_id=version, exact=exact, prefix=None, suffix=None,
            article=None, section=section, pdf_page_index=page, printed_page=None)
        if pdf:
            add('manual_passage', passage_id=pid, checked_at=now,
                method='Özgün tarama Poppler ile sayfa sayfa görüntülendi.',
                reason='Metin katmanı boş. Kısa ifade özgün sayfada gözle okundu.')

(checks/'imei-bill-source-records.json').write_text(
    json.dumps(dict(party_id='yeni-yol',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
