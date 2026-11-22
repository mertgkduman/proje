"""Preserve Yeni Yol's retirement debate and the common decision sources."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
source = Path('data/practices/sources/iyi')
root = source.parent / 'yeni-yol'
entries = json.loads((checks/'pension-floor-final-source-records.json').read_bytes())['entries']
paths = set()
now = datetime.now(timezone.utc).isoformat()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def save(relative, content):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content, path
    else:
        path.write_bytes(content)
    paths.add(path)
    return content


prefix = '0407-floor-'
keep = {
    'iyi-7573-50': ('accept','tally'),
    'pension-bill-23464': ('id','law'),
    'pension-law-7573': ('day','session'),
    'pension-text-7573': ('floor','effect'),
}
origin = checks.parent/'04-07-checks'/'pension-floor-source-records.json'
docs = {prefix+suffix for suffix in keep}
versions = {key+'-v1' for key in docs}
passages = {prefix+key+'-'+suffix for key,segments in keep.items() for suffix in segments}
for entry in json.loads(origin.read_bytes())['entries']:
    kind = entry['kind']
    row = entry['values'].copy()
    if kind == 'document':
        if row['id'] not in docs:
            continue
        row['party_id'] = 'yeni-yol'
    elif kind in ('document_version','source_attribution','archive_view'):
        ref = row['id'] if kind == 'document_version' else row['version_id']
        if ref not in versions:
            continue
        if kind == 'document_version':
            assert sha256(save(row['original_path'], (source/row['original_path']).read_bytes())).hexdigest()==row['sha256']
            save(row['readable_path'], (source/row['readable_path']).read_bytes())
        if kind == 'archive_view':
            manifest = Path(row['manifest_path'])
            for name in json.loads(save(manifest,(source/manifest).read_bytes()))['files']:
                save(manifest.parent/name,(source/manifest.parent/name).read_bytes())
            validate_view(root,row)
    elif kind == 'passage':
        if row['id'] not in passages:
            continue
    else:
        continue
    for key in ('id','version_id','document_id'):
        if key in row:
            row[key] = '0408-floor-'+row[key][len(prefix):]
    add(kind,**row)

own = (
    ('yy-2026-46','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/46/Ham/4f4628c2-d296-456e-8ea9-73afc1a5334a.html',
     '13 Ocak 2026, 46. Birleşim ham tutanağı, Yeni Yol emekli aylığı çağrısı','2026-01-13',
     'b068c7c25bc91aa7928c4e14585ab4c04a695e58c35662d32760348a6229a02e',[
        ('role','Özdağ’ın Yeni Yol Grubu adına söz aldığı başlık','YENİ YOL GRUBU ADINA SELÇUK ÖZDAĞ (Muğla)'),
        ('goal','Özdağ’ın asgari ücret düzeyi önerisi',
         'Biz, en düşük emekli maaşını asgari ücret noktasında değerlendirmek istiyoruz.'),
        ('agenda','13 Ocak genel görüşme önergesinin ön görüşmesi',
         '13/1/2026 tarihinde Türkiye Büyük Millet Meclisi Başkanlığına verilmiş olan genel görüşme önergemizin'),
     ]),
    ('yy-2026-48','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/48/Tam/6213e938-f6dc-41b3-bb98-e507a85bc65f.html',
     '20 Ocak 2026, 48. Birleşimde Kısacık’ın Yeni Yol Grubu adına konuşması','2026-01-20',
     '8da4d1ef445ddc42d38dd9cd5c15461c7b0be5b834b8ecb128633fcb38f94898',[
        ('role','Kısacık’ın Yeni Yol Grubu adına söz aldığı başlık','YENİ YOL GRUBU ADINA SADULLAH KISACIK (Adana)'),
        ('objection','Teklifin tümü görüşmesinde 20.000 TL eleştirisi',
         '20 bin TL bir maaşla bugün hiç kimsenin geçinemeyeceğini hepimiz biliyoruz değil mi?'),
     ]),
)
for key,url,title,day,digest,anchors in own:
    local = stage/(key+'.html')
    raw = local.read_bytes()
    assert sha256(raw).hexdigest()==digest
    doc = '0408-floor-'+key
    vid = doc+'-v1'
    original = f'objects/{digest}/original.html.bin'
    readable = f'objects/{digest}/readable.html'
    save(original,raw)
    save(readable,readable_bytes(raw,'html',legacy=True))
    add('document',id=doc,party_id='yeni-yol',title=title,source_kind='official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,
        date_precision='day',date_unknown_reason=None,
        version_label='TBMM ham tutanağı.' if key.endswith('46') else 'TBMM tam tutanağı.',
        accessed_at=datetime.fromtimestamp(local.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='text/html',sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher='TBMM',author=None,kind='official',
        published_at=None,date_precision='unknown',social_handle=None,public_url=url,
        basis='Birleşim tarihi, konuşmacı başlığı ve özgün tutanak türü kontrol edildi.')
    view = build_view(raw,url,root,fetch_assets=False,http_charset='windows-1254')
    view['version_id'] = vid
    validate_view(root,view)
    add('archive_view',**view)
    manifest = root/view['manifest_path']
    paths.add(manifest)
    paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
    body = html_source_text(raw)
    for suffix,section,exact in anchors:
        assert exact in body,(key,suffix,exact)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=None,printed_page=None)

output = checks/'pension-floor-yeni-yol-source-records.json'
with output.open('x') as stream:
    stream.write(json.dumps(dict(party_id='yeni-yol',entries=entries),ensure_ascii=False,indent=2)+'\n')
paths.update(Path(line) for line in Path('/tmp/gsd-0408-pension-floor-final-paths').read_text().splitlines())
Path('/tmp/gsd0408-floor-yeni-yol-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
