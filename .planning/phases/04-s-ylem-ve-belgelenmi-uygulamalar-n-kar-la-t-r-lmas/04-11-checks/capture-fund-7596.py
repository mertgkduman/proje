"""Archive the dated Saadet statement and reuse official law snapshots byte for byte."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here, stage = map(Path, sys.argv[1:])
source = Path('data/practices/sources/iyi')
target = source.with_name('saadet')
entries, paths = [], set()
now = datetime.now(timezone.utc).isoformat()
prefix = '0411-fund-'
url = 'https://tbmm.gov.tr/Haber/Detay?Id=8b0479b3-8b32-490f-ac26-01a15de8dc42'


def save(relative, raw):
    path = target/relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == raw
    else:
        path.write_bytes(raw)
    paths.add(path)
    return raw


def add(table, **row):
    entries.append(dict(kind=table, values=row))


def passage(version, name, section, exact, body):
    assert exact in body, (name, exact)
    add('passage', id=version.removesuffix('-v1')+'-'+name, version_id=version,
        exact=exact, prefix=None, suffix=None, article=None, section=section,
        pdf_page_index=None, printed_page=None)


selected = {
    'oct22': ('electron', 'accept'), 'oct22-summary': ('accept',),
    'law': ('date', 'pub'), 'law-text': (),
}
old = json.loads((here.parent/'04-07-checks'/'fund-floor-source-records.json').read_bytes())
aliases = {f'0407-fund-{key}{tail}' for key, slices in selected.items()
           for tail in ('', '-v1', *('-'+item for item in slices))}
for entry in old['entries']:
    kind, row = entry['kind'], entry['values'].copy()
    if row.get('id', row.get('version_id')) not in aliases:
        continue
    for key in ('id', 'document_id', 'version_id'):
        if key in row:
            row[key] = row[key].replace('0407-fund-', prefix)
    if kind == 'document':
        row['party_id'] = 'saadet'
    if kind == 'document_version':
        for key in ('original_path', 'readable_path'):
            rel = row[key]
            raw = save(rel, (source/rel).read_bytes())
            if key == 'original_path':
                assert sha256(raw).hexdigest() == row['sha256']
                if row['id'] == prefix+'law-text-v1':
                    law = html_source_text(raw)
    if kind == 'archive_view':
        manifest = Path(row['manifest_path'])
        for name in json.loads(save(manifest, (source/manifest).read_bytes()))['files']:
            rel = manifest.parent/name
            save(rel, (source/rel).read_bytes())
        validate_view(target, row)
    add(kind, **row)
assert sum(entry['kind'] == 'document_version' for entry in entries) == 4

versions = {
    'authority': ('TBMM haber girişinde Arıkan’ın Saadet sıfatı', 'Saadet Partisi Genel Başkanı Mahmut Arıkan,'),
    'date': ('TBMM haber yayım tarihi ve saati', '2026-10-21 - 13:01'),
    'group': ('Toplantının Yeni Yol grubu olduğu haber gövdesinde', "Arıkan, Yeni Yol Partisinin TBMM Grup Toplantısı'nda"),
    'bill': ('Eleştirilen fon teklifinin haber gövdesindeki adı', "Tasfiyesine Karar Verilen Bazı Yatırım Fonları Hakkında Kanun Teklifi'nin görüşmelerine değinen Arıkan"),
    'quote': ('Arıkan’ın doğrudan aktarılmış kısa ifadesi', 'bataklığı kurutmak yerine sivrisinek avlamaya çalışıldığını'),
    'critique': ('TBMM haberinin güvence ve SPK yetkisi aktarımı', "Teklifin, mağdurun parasına güvence vermediğini ifade eden Arıkan, fonların tasfiyesi, değerlemesi, satışı ve yatırımcılara yapılacak ödemeler konusunda SPK'ye geniş yetkiler verilmesini eleştirdi."),
}
file = stage/'arikan.html'
raw = file.read_bytes()
digest = sha256(raw).hexdigest()
assert digest == '5ea1c0b281a8d1c4ef7eb452398650ebaa697157a53a44ea07e44833cea898f7'
original, readable = (f'objects/{digest}/{name}' for name in ('original.html.bin','readable.html'))
save(original, raw)
save(readable, readable_bytes(raw,'html',legacy=False))
doc = prefix+'arikan'
vid = doc+'-v1'
add('document', id=doc, party_id='saadet', title='21 Ekim Yeni Yol grup toplantısında Mahmut Arıkan’ın yatırım fonu teklifi açıklaması', source_kind='official')
add('document_version', id=vid, document_id=doc, original_url=url, final_url=url,
    document_date='2026-10-21', date_precision='day', date_unknown_reason=None,
    version_label='TBMM haberinin erişilen özgün nüshası.',
    accessed_at=datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).isoformat(), verified_at=now,
    mime='text/html', sha256=digest, original_path=original, readable_path=readable)
add('source_attribution', version_id=vid, publisher='TBMM', author=None, kind='official',
    published_at='2026-10-21', date_precision='day', social_handle=None, public_url=url,
    basis='TBMM’nin haber künye tarihi, yayımlanan metin ve konuşmacı sıfatı.')
view = build_view(raw, url, target, fetch_assets=False)
view['version_id'] = vid
validate_view(target, view)
add('archive_view', **view)
manifest = target/view['manifest_path']
paths.add(manifest)
paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
body = html_source_text(raw)
for name, (section, exact) in versions.items():
    passage(vid, name, section, exact, body)

law_version = prefix+'law-text-v1'
for name, section, exact in (
    ('power', 'Madde 3 fıkra 1, SPK’nın belirleme yetkisi',
     'tespitini ve nakde çevrilmesini, değerleme esaslarını, fon pay sahipliğinin\r\nbelirlenme şeklini, ara ve nihai ödemeyi, dağıtım sırasını ve tasfiyeye ilişkin\r\ndiğer usul ve esasları belirlemeye yetkilidir.'),
    ('sale', 'Madde 3 fıkra 2, Borsa dışında satış onayı',
     'talebi üzerine ilgili varlıkların Borsa dışında satışına onay verebilir.'),
    ('interim', 'Madde 4 fıkra 2, 1.000.000 TL ara ödeme üst sınırı',
     '1.000.000 Türk lirası ara ödeme yapılabilir.'),
    ('cash', 'Madde 4 fıkra 3, dağıtılabilir nakdin yetmemesi',
     'hâlinde Kurul; mevcut nakitten mümkün olan en fazla sayıda fon pay sahibinin'),
    ('distribution', 'Madde 6 fıkra 6, geri kazanımın dağıtım oranı',
     'Ödemeler YTM tarafından katılma payı sahipliği oranında yapılır.'),
):
    passage(law_version, name, section, exact, law)
out = here/'fund-7596-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='saadet',entries=entries), ensure_ascii=False, indent=2)+'\n')
Path('/tmp/gsd0411-fund-source-paths').write_text('\n'.join(sorted(map(str, paths)))+'\n')
print(len(entries), len(paths), sha256(out.read_bytes()).hexdigest())
