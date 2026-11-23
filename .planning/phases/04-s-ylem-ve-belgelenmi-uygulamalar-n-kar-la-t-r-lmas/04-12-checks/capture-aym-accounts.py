"""Archive the 2021/2023 decisions and their separate publication indexes."""

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
    (2021,'rg-pdf.raw','rg-index.raw','2024-12-25','2025-03-14','2025/03/20250314','15','2022/42','2024/116',
     '1d13096b536d818fc328dbf69c413c4088cded2e0befe5854d38c2b4a262eaa3',
     '543ad79c336030286c67a644e58a37933e8fbf04370c129cdb59bc978581ae53',
     'Partiler Kanunu’na uygun olduğuna 25/12/2024 tarihinde OYBİRLİĞİYLE karar verildi.'),
    (2023,'rg2023-q.raw','rg2023-index.html','2025-12-25','2026-04-20','2026/04/20260420','5','2024/69','2025/155',
     '976695db0990f158e9c9b9e745b5d37d220345abb8d45e334ca5b7e921692365',
     '4cdd401bc44187d541d784bb4b8d2d5e66ef153b7eba31b8b4ef096b9f592b28',
     'olduğuna 25/12/2025 tarihinde OYBİRLİĞİYLE karar verildi.'),
)
for year, pdf_file, index_file, decided, published, issue, number, case, decision, pdf_digest, index_digest, final in sources:
    prefix = f'0412-aym-{year}-hesap'
    base = 'https://www.resmigazete.gov.tr/eskiler/'+issue
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
             f'E: {case} (Siyasi Parti Mali Denetimi), K: {decision}'),
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
        final_url = url+'?download=1' if pdf and year==2023 else url
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
out=checks/'aym-accounts-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0412-aym-accounts-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths),sha256(out.read_bytes()).hexdigest())
