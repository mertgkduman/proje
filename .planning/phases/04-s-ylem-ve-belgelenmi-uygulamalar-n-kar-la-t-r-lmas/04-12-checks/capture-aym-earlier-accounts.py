"""Archive the 2020/2022 decisions and their separate publication indexes."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/demokrat')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


def add(table, **row):
    entries.append(dict(kind=table,values=row))


def save(relative, raw):
    path = root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==raw
    else:
        path.write_bytes(raw)
    paths.add(path)


sources = (
    (2020,'rg-2020-alt.pdf.part','rg-2020-index.html.part','2024-06-27','2025-01-10','2025/01/20250110','6','2021/57','2024/73',
     'd7cfbb2ee766b61cf16dc65644d792b0690489aeb3458ef06621ec0badc32ad4',
     'cc240d55e52e04ea3c9052ee340e06f65d3b1b5df6e77275aa1f0b242ef59bb1',
     'uygun olduğuna 27/6/2024 tarihinde'),
    (2022,'rg-2022-variant.pdf.part','rg-2022-index-alt.html.part','2025-12-25','2026-04-16','2026/04/20260416','7','2023/39','2025/135',
     '7c9c8a59c1828479d898c4646219ce85a032dbb0c17b55be99ec4c4bce827d9a',
     'a356ee19c6f0b445131eb6b42659ce7d2f9c6fefa11e4b1a9c13489603744737',
     'uygun olduğuna 25/12/2025 tarihinde OYBİRLİĞİYLE'),
)
for year, pdf_file, index_file, decided, published, issue, number, case, decision, pdf_digest, index_digest, final in sources:
    prefix = f'0412-aym-{year}-hesap'
    host = 'resmigazete.gov.tr' if year==2020 else 'www.resmigazete.gov.tr'
    base = f'https://{host}/eskiler/'+issue
    specs = (
        ('',pdf_file,base+'-'+number+'.pdf',pdf_digest,decided,(
            ('year','Üçüncü sayfa, IV. sonuçta incelenen kesin hesap',2,
             f'Demokrat Partinin {year} yılı kesin hesabının incelenmesi sonucunda;'),
            ('review','İkinci sayfa, §7 Genel Merkez kayıt ve gelir incelemesi',1,
             'Parti Genel Merkezinin defter kayıtları ve gelir belgeleri üzerinde yapılan inceleme'),
            ('merit','Üçüncü sayfa, IV. sonuç ve karar tarihi',2,final),
            ('balance','Üçüncü sayfa, IV. sonuçta bilgi ve belge sınırı',2,
             'eldeki bilgi ve belgelere göre doğru, denk'),
        )),
        ('-index',index_file,base+'.htm',index_digest,published,(
            ('identity','Resmî Gazete içindekiler, esas ve karar numarası',None,
             f'E: {case} (Siyasi Parti Mali Denetimi), K: '+('\r\n' if year==2022 else '')+decision),
        )),
    )
    for suffix, name, url, digest, day, slices in specs:
        path = stage/name
        raw = path.read_bytes()
        assert sha256(raw).hexdigest() == digest
        pdf = suffix==''
        doc = prefix+suffix
        vid = doc+'-v1'
        original = f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
        readable = f'objects/{digest}/readable.html'
        save(original,raw)
        save(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
        title = (f'Demokrat Parti {year} kesin hesabı, AYM E.{case} K.{decision}' if pdf else
                 f'{published} Resmî Gazete yayım dizini, AYM K.{decision}')
        final_url = url+'?download=1' if year==2022 else url
        add('document',id=doc,party_id='demokrat',title=title,source_kind='official')
        add('document_version',id=vid,document_id=doc,original_url=url,final_url=final_url,document_date=day,
            date_precision='day',date_unknown_reason=None,version_label='Özgün Resmî Gazete nüshası.',
            mime='application/pdf' if pdf else 'text/html',
            accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
            verified_at=now,sha256=digest,original_path=original,readable_path=readable)
        add('source_attribution',version_id=vid,publisher='Resmî Gazete',author='Anayasa Mahkemesi' if pdf else None,
            kind='official', published_at=published,date_precision='day',social_handle=None,public_url=url,
            basis='Karar tarihi ve yayım günü özgün sayfa ve yayım dizininden ayrı incelendi.')
        if not pdf:
            body = html_source_text(raw)
            view = build_view(raw,url,root,fetch_assets=False,http_charset='windows-1254')
            view['version_id']=vid
            manifest=root/view['manifest_path']
            paths.add(manifest)
            paths.update(manifest.parent/item for item in json.loads(manifest.read_bytes())['files'])
            validate_view(root,view)
            add('archive_view',**view)
        for key,section,page,exact in slices:
            pid=doc+'-'+key
            if pdf:
                assert not pdf_page_text(root/original,page).strip()
            else:
                assert exact in body
            add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
                section=section,pdf_page_index=page,printed_page=None)
            if pdf:
                add('manual_passage',passage_id=pid,checked_at=now,
                    method='Özgün PDF Poppler ile sayfa bazında görüntülendi.',
                    reason='Pasajın bulunduğu sayfada metin katmanı yok. Kararın üç sayfası görsel olarak okundu.')
out=checks/'aym-earlier-accounts-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0412-aym-earlier-accounts-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths),sha256(out.read_bytes()).hexdigest())
