"""Archive two separate Democrat Party bills and the independent 7573 ballot."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
sources = Path('data/practices/sources')
root = sources/'demokrat'
origin_root = sources/'iyi'
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def save(relative, raw):
    path = root/relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes()==raw
    else:
        path.write_bytes(raw)
    paths.add(path)
    return raw


def passage(doc, key, section, exact, page=None, manual=False):
    pid = doc+'-'+key
    add('passage',id=pid,version_id=doc+'-v1',exact=exact,prefix=None,suffix=None,
        article=None,section=section,pdf_page_index=page,printed_page=None)
    if manual:
        add('manual_passage',passage_id=pid,checked_at=now,method='Özgün PDF sayfası Poppler ile görüntülendi.',
            reason='Metin katmanı boş. Sayfadaki kısa ifade gözle doğrulandı.')


def archive_view(view, version, read_path):
    view['version_id'] = version
    manifest = Path(view['manifest_path'])
    for name in json.loads(save(manifest,read_path(manifest)))['files']:
        save(manifest.parent/name,read_path(manifest.parent/name))
    validate_view(root,view)
    add('archive_view',**view)


common = {
    'iyi-7573-50': ('tally','accept'),
    'iyi-7573-ballot': ('tally','duplicates'),
    'pension-text-7573': ('floor','effect'),
    'pension-law-7573': ('day','session'),
}
docs = {'0407-floor-'+key for key in common}
versions = {f'{key}-v1' for key in docs}
passage_ids = {'0407-floor-'+key+'-'+suffix for key,items in common.items() for suffix in items}
iyichecks = checks.parent/'04-07-checks'
ballot_body = None
for asset in ('pension-floor-source-records.json','pension-floor-final-source-records.json'):
    for entry in json.loads((iyichecks/asset).read_bytes())['entries']:
        kind = entry['kind']
        row = entry['values'].copy()
        if kind == 'document':
            if row['id'] not in docs:
                continue
            row['party_id'] = 'demokrat'
        elif kind in ('document_version','source_attribution','archive_view'):
            key = 'id' if kind == 'document_version' else 'version_id'
            if row[key] not in versions:
                continue
            if kind == 'document_version':
                raw = save(row['original_path'],(origin_root/row['original_path']).read_bytes())
                assert sha256(raw).hexdigest()==row['sha256']
                save(row['readable_path'],(origin_root/row['readable_path']).read_bytes())
                if row['id']=='0407-floor-iyi-7573-ballot-v1':
                    ballot_body = html_source_text(raw)
            if kind == 'archive_view':
                archive_view(row,'0412-floor-'+row[key].removeprefix('0407-floor-'),
                    lambda name: (origin_root/name).read_bytes())
                continue
        elif kind == 'passage':
            if row['id'] not in passage_ids:
                continue
        else:
            continue
        for key in ('id','version_id','document_id'):
            if key in row:
                row[key] = '0412-floor-'+row[key].removeprefix('0407-floor-')
        add(kind,**row)
rows = [row.strip() for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',ballot_body,re.S|re.I)
        if '>Demokrat Parti<' in row]
assert len(rows)==1 and 'ALTINTA&#x15E;' in rows[0] and 'Haydar' in rows[0] and 'KATILMADI' in rows[0]
passage('0412-floor-iyi-7573-ballot','altintas','Demokrat Parti etiketli Haydar Altıntaş kesin cetvel satırı',rows[0])

assets = (
    ('file1597','html','2/1597 TBMM dosyası',None,None,'TBMM','official',
     '151387a2239bb292fba0b5cdbc0c447e110edc6bc66c1c756e02a82005a24ce5',[
         ('id','Esas numarası','<td>2 / 1597</td>',None),
         ('filed','Başkanlığa geliş','<td>28/09/2023</td>',None),
         ('sent','Komisyon girişi','<td>03/10/2023</td>',None),
         ('status','Erişilen dosya durumu','<td>KOM&#x130;SYONDA</td>',None),
     ]),
    ('signed1597','pdf','2/1597 imzalı kanun teklifi','2023-09-28',None,'TBMM','official',
     'b4a1a7a884ed771e5634d855c6f52a5d62ab7f81fbd8479fbc7a42e0e06aa72f',[
         ('signature','Kapakta üç Demokrat Parti milletvekilinin adı','Cemal ENGINYURT Haydar ALTINTAŞ M. Salih UZUN\nDemokrat Parti Demokrat Parti Demokrat Parti',0),
         ('proposal-id','Kapağın komisyon tarihi ve esas numarası','Tarih; 3-10-2023 Esas No:2/1597',0),
         ('goal','3. maddede 5510 Ek 19 için önerilen taban','net asgari ücretten az olamaz',4),
         ('index','1. maddede ayrı ek ödeme aracı','(15.965) gösterge rakamının memur aylık katsayısı ile çarpımı',4),
     ]),
    ('file3489','html','2/3489 TBMM dosyası',None,None,'TBMM','official',
     'aad8ac801fe7ea6aa86120a43d7c052d568336396469fec9c03cb9886a516535',[
         ('id','Esas numarası','<td>2 / 3489</td>',None),
         ('filed','Başkanlığa geliş','<td>22/01/2026</td>',None),
         ('sent','Komisyon girişi','<td>23/01/2026</td>',None),
         ('status','Erişilen dosya durumu','<td>KOM&#x130;SYONDA</td>',None),
     ]),
    ('signed3489','pdf','2/3489 imzalı kanun teklifi','2026-01-22',None,'TBMM','official',
     'dc72038b2bd5ff21a824955d3bfccc3518606da7c9ff3d2658ca41633453caca',[
         ('id','Kapakta esas numarası','2/3489',0),
         ('signature','Kapakta Haydar Altıntaş ve imzası','Haydar ALTINTAŞ',0),
         ('group','Genel gerekçede kapsanan emekliler','emekli emniyet mensupları ve MİT emeklilerine',2),
         ('index','1. maddede önerilen gösterge','2345 gösterge rakamının',4),
     ]),
    ('agenda3489','html','23 Ocak 2026 TBMM Gelen Kâğıtlar, 2/3489','2026-01-23','2026-01-23','TBMM','official',
     '1664a24279317c0a626e005d0da1bd803e08c5c75af4d25e80dc334f599ea9e9',[
         ('id','Gelen Kâğıtlar 78’de teklif esas numarası','Kanun Teklifi (2/3489)',None),
     ]),
    ('party3489','html','Demokrat Parti, 29 Ocak 2026 ek ödeme açıklaması','2026-01-29','2026-01-29','Demokrat Parti','party',
     'c83e41d4c2db1ec78f43dfc009f94fdd47f9bf781c3d502f7f80c80e4b977409',[
         ('published','Parti açıklamasının görünür yayın tarihi','29/01/2026',None),
         ('index','Parti açıklamasındaki 2.345 gösterge','2345 g&ouml;sterge rakamı esas alınarak',None),
     ]),
)
for name,ext,title,day,published,publisher,kind,digest,anchors in assets:
    local=stage/(name+'.body')
    raw=local.read_bytes()
    url=(stage/(name+'.meta')).read_text().split()[-1]
    assert sha256(raw).hexdigest()==digest
    doc='0412-retire-'+name
    vid=doc+'-v1'
    original=f'objects/{digest}/'+('original.pdf' if ext=='pdf' else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    save(original,raw)
    save(readable,readable_bytes(raw,ext,legacy=False))
    add('document',id=doc,party_id='demokrat',title=title,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,
        date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'Erişilen dosyanın ilk yayın günü açık. Yasama işlem tarihleri ayrı.',
        version_label='Erişilen özgün belge.',accessed_at=datetime.fromtimestamp(local.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if ext=='pdf' else 'text/html',sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=None,
        kind='party_publication' if kind=='party' else 'official',published_at=published,
        date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
        basis='Belge ve parti açıklamasındaki yayıncı, tarih ve içerik bağlamı kontrol edildi.')
    if ext=='html':
        view=build_view(raw,url,root,fetch_assets=False)
        archive_view(view,vid,lambda name: (root/name).read_bytes())
    for key,section,exact,page in anchors:
        body = html_source_text(raw) if page is None else pdf_page_text(root/original,page)
        manual = name == 'signed3489'
        if manual:
            assert not body.strip()
        else:
            assert exact in body,(name,key,repr(exact))
        passage(doc,key,section,exact,page,manual)

output=checks/'pension-separate-source-records.json'
with output.open('x') as stream:
    stream.write(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0412-pension-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
