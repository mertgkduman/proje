"""Archive the original 2/4007 filing and parliamentary register."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path,sys.argv[1:])
root = Path('data/practices/sources/demokrat')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def store(relative, content):
    path = root/relative
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content
    else:
        path.write_bytes(content)
    paths.add(path)


sources = (
    ('4007.pdf','signed','2/4007 imzalı kanun teklifi','2026-11-02',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/WebOnergeMetni/955ac7ec-c314-474d-bcf9-4b19aed4160d.pdf',
     '2c0bcfc99aa9b7cd6d7fce56637b5f58baa835681281af973f9391b4d3b401de',[
         ('file','Kapak işlem kutusunda 2/4007',0,'4-11-2026 Esas No:2/4007'),
         ('signature','İmzalı kapakta 2 Kasım teklif yazısı',0,'Gereğini arz ederim. 02/11/2026'),
         ('stamp','İkinci sayfada 3 Kasım TBMM evrak kaşesi',1,'3 Kasım 2026'),
         ('thresholds','Madde 1, iki ayrı asgari ücret oranı',4,'bulunan aylık net asgari ücretin yüzde ellisinden; aday çırak ve çıraklara ise yüzde kırkından az'),
         ('start','Madde 1, ilk sigortalılık başlangıcı ve uzun vadeli sigorta',4,'uzun vadeli sigorta kolları için de ilk sigortalılık başlangıç tarihi sayılır.'),
         ('safety','Madde 2, çok tehlikeli iş yasağı ve denetim',4,'Sosyal Güvenlik Bakanlığı iş müfettişlerince yılda en az iki kez resen denetlenir.'),
         ('backdate','Madde 3 sonu, talep edenler için borçlanma',5,'esaslarına göre borçlandırılır ve borçlanılan süreler uzun vadeli sigorta kolları prim ödeme gün'),
     ]),
    ('4007-detail.html','detail','2/4007 TBMM kanun teklifi dosyası',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/KanunTeklifi/18184887-8d78-488e-b2fc-01a1a01b1cbb',
     '71a585cd59ddad90fd2ef98b71ee2a91af94d9d8bf90760911f696a840ca09dc',[
         ('id','Esas numarası',None,'<td>2 / 4007</td>'),
         ('filed','Başkanlığa geliş 3 Kasım',None,'<td>03/11/2026</td>'),
         ('committee','Komisyon giriş tarihi 4 Kasım',None,'<td>04/11/2026</td>'),
         ('pending','Komisyon işlem alanı',None,'<td>Komisyonda</td>'),
         ('membership','İmza tablosunda Altıntaş, Demokrat Parti ve İzmir',None,
          'Haydar ALTINTA&#x15E;\n\n                                            </a>\n                                        </td>\n                                        <td>DEMOKRAT PART&#x130;</td>'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0412-staj-4007-'+key
    vid=doc+'-v1'
    obj=f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    store(obj,raw)
    store(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='demokrat',title=title,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=date,
        date_precision='day' if date else 'unknown',date_unknown_reason=None if date else 'Dinamik kayıt ilk yayın gününü belirtmiyor.',
        version_label='Özgün kurum veya parti nüshası.',accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),
        verified_at=now,mime='application/pdf' if pdf else 'text/html',sha256=digest,original_path=obj,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=None,kind='official' if kind=='official' else 'party_publication',
        published_at=published,date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
        basis='Özgün üst başlık ve varsa gün, parti, ilk imza ve kurum bağlamı birlikte okundu.')
    if not pdf:
        view=build_view(raw,url,root,fetch_assets=False)
        view['version_id']=vid
        validate_view(root,view)
        manifest=root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
        add('archive_view',**view)
    for suffix,section,index,exact in anchors:
        text=pdf_page_text(root/obj,index) if pdf else html_source_text(raw)
        assert exact in text,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=index,printed_page=None)
(checks/'staj-4007-source-records.json').write_text(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'4007-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
