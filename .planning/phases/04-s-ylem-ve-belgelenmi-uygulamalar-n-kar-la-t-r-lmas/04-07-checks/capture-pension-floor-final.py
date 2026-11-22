"""Archive the 2/3464 committee transcript and certified open ballot."""

from datetime import datetime, timezone
from hashlib import sha256
import html
import json
from pathlib import Path
import re
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:3])
party, plan = sys.argv[3:]
root = Path('data/practices/sources')/party
now = datetime.now(timezone.utc).isoformat()
entries = []
paths = set()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def save(relative, content):
    path = root/relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content, path
    else:
        path.write_bytes(content)
    paths.add(path)


def cells(row):
    return [html.unescape(re.sub(r'<[^>]+>', '', cell)).strip()
            for cell in re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.S | re.I)]


def personal_row(source, surname, given, label, result):
    rows = [row for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', source, re.S | re.I)
            if len(cells(row)) == 9 and cells(row)[1:4] == [surname, given, label]]
    assert len(rows) == 1 and cells(rows[0])[6] == result, (surname, rows)
    exact = rows[0].strip()
    assert '\ufffd' not in exact
    return exact


def deposit(key, extension, url, title, date, passages):
    local = stage/f'{key}.{extension}'
    raw = local.read_bytes()
    digest = sha256(raw).hexdigest()
    doc_id = f'{plan}-floor-{key}'
    vid = doc_id+'-v1'
    mime = 'application/pdf' if extension == 'pdf' else 'text/html'
    original = f'objects/{digest}/original.'+('pdf' if extension == 'pdf' else 'html.bin')
    readable = f'objects/{digest}/readable.html'
    save(original, raw)
    save(readable, readable_bytes(raw, extension, legacy=extension == 'html'))
    accessed = datetime.fromtimestamp(local.stat().st_mtime, timezone.utc).isoformat()
    add('document', id=doc_id, party_id=party, title=title, source_kind='official')
    add('document_version', id=vid, document_id=doc_id, original_url=url, final_url=url,
        document_date=date, date_precision='day', date_unknown_reason=None,
        version_label='TBMM’nin erişime açtığı özgün kayıt.', accessed_at=accessed, verified_at=now,
        mime=mime, sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=vid, publisher='TBMM', author=None, kind='official',
        published_at=None, date_precision='unknown', social_handle=None, public_url=url,
        basis='Kurumun resmî yayını. Toplantı ve oylama tarihleri belgenin bağlamında kaydedildi.')
    if extension == 'html':
        view = build_view(raw, url, root, fetch_assets=False, http_charset='windows-1254')
        view['version_id'] = vid
        validate_view(root, view)
        add('archive_view', **view)
        manifest = root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
    for suffix, section, exact, page in passages:
        body = html_source_text(raw) if page is None else pdf_page_text(root/original, page)
        assert exact in body, (key, section, exact)
        add('passage', id=doc_id+'-'+suffix, version_id=vid, exact=exact,
            prefix=None, suffix=None, article=None, section=section,
            pdf_page_index=page, printed_page=str(page+1) if page is not None else None)


raw = (stage/'iyi-7573-ballot.html').read_bytes()
assert sha256(raw).hexdigest() == '40054311417ad26e380935c60142c0a172e5adfc897e72111a9ff9c7ce4ea833'
source = html_source_text(raw)
rows = [cells(row) for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', raw.decode('cp1254'), re.S | re.I)]
assert [row[1].strip() for row in rows if len(row) == 2 and row[0] in
        ('Kabul Edenler','Reddedenler','Mükerrer Oylar','Toplam')] == [':\xa0245',':\xa0179',':\xa02',':\xa0426']
ballot = []
for key, start, end, section in (
    ('tally', 'Kabul Edenler </td>', ':&nbsp;179</td>', 'Kesin kabul ve ret toplamı'),
    ('duplicates', 'kerrer Oylar </td>', ':&nbsp;426</td>', 'İki mükerrer oy ve 426 toplam'),
):
    left = source.index(start)
    right = source.index(end, left)+len(end)
    assert '\ufffd' not in source[left:right]
    ballot.append((key, section, source[left:right], None))

named = {
    'iyi': [('usta','USTA','Erhan','İYİ Parti','KATILMADI'),
            ('turkes','TÜRKEŞ TAŞ','Ayyüce','İYİ Parti','RET'),
            ('fakibaba','FAKIBABA','Ahmet Eşref','İYİ Parti','RET')],
    'saadet': [('arikan','ARIKAN','Mahmut','Saadet Partisi','KATILMADI')],
    'yeni-yol': [('kisacik','KISACIK','Sadullah','Yeni Yol Partisi','RET'),
                ('bulent','KAYA','Bülent','Yeni Yol Partisi','RET')],
}
for key, surname, given, label, result in named[party]:
    ballot.append((key, f'{given} {surname} adına kesin cetvel satırı',
                   personal_row(source, surname, given, label, result), None))

deposit('iyi-7573-ballot', 'html',
        'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/50/AcikOylamaSonuc/7254d212-c78d-48e4-b30e-aa59e82803d0.html',
        '248 sıra sayılı teklif için 50. Birleşim kesin açık oylama cetveli', '2026-01-23', ballot)

if party in ('iyi','yeni-yol'):
    day = (stage/'iyi-7573-commission.pdf').read_bytes()
    assert sha256(day).hexdigest() == 'f50b2fc6c56ac1ce14a9159aa43ee5e22845d21b723701a0f18f7fed6fa59d1d'
    text = pdf_page_text(stage/'iyi-7573-commission.pdf', 57)
    start = text.index("Teklifi'nin 5'inci maddesinde yer alan")
    end = text.index('Müteakip önergeye okutuyorum:', start)
    target = text[start:end].strip()
    assert all(needle in target for needle in ('"25.000"', 'Erhan Usta', 'Ayyüce Türkeş Taş', 'Kabul edilmemiştir.'))
    separate = text[text.index('birinci fıkrasında yer alan "16.881 Türk Lirasından"'):
                    text.index("Şimdi, 5'inci maddeyi oylarınıza sunuyorum:")].strip()
    assert 'Sadullah Kısacık' in separate and 'asgari ücretten' in separate and 'Önerge kabul edilmemiştir.' in separate
    deposit('iyi-7573-commission', 'pdf', 'https://www.tbmm.gov.tr/Tutanaklar/TutanakGoster/5344',
            '15 Ocak 2026 Plan ve Bütçe Komisyonu 26. toplantı tutanağı', '2026-01-15', [
                ('cover','Toplantı tarihi, sırası ve gündemi','15 Ocak 2026 Perşembe',0),
                ('amendment','5. madde için Usta ve Türkeş Taş’ın 25.000 TL önergesi ve ret kararı',target,57),
                ('kisacik','Kısacık’ın asgari ücrete ilişkin ayrı önergesi ve ret kararı',separate,57),
            ])

out = checks/'pension-floor-final-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps(dict(party_id=party, entries=entries), ensure_ascii=False, indent=2)+'\n')
Path(f'/tmp/gsd-{plan}-pension-floor-final-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(out.read_bytes()).hexdigest(),len(entries),len(paths))
