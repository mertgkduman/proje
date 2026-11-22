"""Archive the same public 10/3998 records for İYİ Parti's contribution."""

from hashlib import sha256
import json
from pathlib import Path

from arsiv import html_source_text
from arsiv_gorunum import validate_view

checks = Path(__file__).resolve().parent
origin = checks.parent / '04-08-checks' / 'inquiry-3998-source-records.json'
sources = Path('data/practices/sources')
source_root = sources / 'yeni-yol'
target_root = sources / 'iyi'
old = '0408-stats-yy-3998'
new = '0407-tuik-3998'
selected = ('', '-session', '-summary')
passage_suffixes = ('-id', '-filed', '-status', '-session-motion', '-session-decision',
                    '-session-dalgin-role', '-session-dalgin-call', '-summary-motion', '-summary-result')
titles = {
    '': '10/3998 araştırma önergesinin TBMM dosyası',
    '-session': '8 Nisan 2026 79. Birleşimde İYİ Parti Grubunun TÜİK hakkındaki konuşması',
    '-summary': '79. Birleşim gündem oylamalarının TBMM özeti',
}
paths = set()
entries = []


def copy(relative):
    source = source_root / relative
    target = target_root / relative
    data = source.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes() == data, target
    else:
        target.write_bytes(data)
    paths.add(target)
    return data


for entry in json.loads(origin.read_bytes())['entries']:
    kind = entry['kind']
    row = entry['values'].copy()
    if kind == 'document':
        if row['id'] not in {old + suffix for suffix in selected}:
            continue
        row['title'] = titles[row['id'][len(old):]]
        row['party_id'] = 'iyi'
    elif kind in ('document_version', 'source_attribution', 'archive_view'):
        key = 'id' if kind == 'document_version' else 'version_id'
        if row[key] not in {old + suffix + '-v1' for suffix in selected}:
            continue
        if kind == 'document_version':
            raw = copy(row['original_path'])
            assert sha256(raw).hexdigest() == row['sha256']
            copy(row['readable_path'])
            if row['id'] == old + '-session-v1':
                transcript = html_source_text(raw)
        if kind == 'archive_view':
            manifest = Path(row['manifest_path'])
            for name in json.loads(copy(manifest))['files']:
                copy(manifest.parent / name)
            validate_view(target_root, row)
    elif kind == 'passage':
        if row['id'] not in {old + suffix for suffix in passage_suffixes}:
            continue
    else:
        continue
    for key in ('id', 'version_id', 'document_id'):
        if key in row:
            assert row[key].startswith(old)
            row[key] = new + row[key][len(old):]
    entries.append(dict(kind=kind, values=row))
extra = (
    ('audit', 'Dalgın’ın akademik denetim çağrısı',
     'Bir akademik kurulla şeffaf bir şekilde kendinizi denetlettirin.'),
    ('commission', 'Dalgın’ın TÜİK başkanının komisyonda dinlenmesi çağrısı',
     'TÜİK Başkanını getirin Plan ve Bütçe Komisyonuna Meclisimize hesap versin.'),
)
dalgin_start = transcript.index('Fiyat ve ürün sepetinizi açıklayın')
for suffix, section, exact in extra:
    assert exact in transcript[dalgin_start:dalgin_start + 2500]
    entries.append(dict(kind='passage', values=dict(id=new+'-session-'+suffix,
        version_id=new+'-session-v1', exact=exact, prefix=None, suffix=None,
        article=None, section=section, pdf_page_index=None, printed_page=None)))

output = checks / 'tuik-3998-group-source-records.json'
with output.open('x') as stream:
    stream.write(json.dumps(dict(party_id='iyi', entries=entries), ensure_ascii=False, indent=2)+'\n')
Path('/tmp/gsd0407-tuik-3998-paths').write_text('\n'.join(sorted(map(str, paths)))+'\n')
print(len(entries), len(paths))
