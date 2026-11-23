"""Archive the original 2/3965 filing, parliamentary listing, and party account."""

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
    ('signed.pdf','signed','2/3965 imzalı kanun teklifi','2026-10-20',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/WebOnergeMetni/79046dd7-01d4-4b9d-9eb9-cb3503333166.pdf',
     'a9765f0c0ca8b9c6933ff8c0072e74a215aad4105c584f58d87e03b26f14a163',[
         ('file','Kapak işlem kutusunda 2/3965',0,'Esas No:2/3965'),
         ('stamp','İkinci tarama sayfasında TBMM evrak kaşesi',1,'2 O Ekim 2026'),
         ('investor','Genel gerekçe, yatırımcı koruma mekanizması',2,'Kamuyu Aydınlatma Platformu (KAP) üzerinden üçer aylık şeffaf raporlama'),
         ('committee-report','Madde gerekçesi, denetim raporu',3,'Kurulunca TBMM Plan ve Bütçe Komisyonuna sunulması'),
         ('risk-limit','Madde 1, yüzde on risk ve üç aylık bağımsız denetim',4,'büyüklüğü fon toplam değerinin yüzde onunu aşamaz ve bu işlemler her üç ayda bir bağımsız'),
         ('liability','Madde 1, yöneticilerin şahsi ve müteselsil sorumluluğu',4,'müteselsilen sorumludur.'),
         ('payment','Madde 2, otuz gün ve YTM',4,'geç otuz gün içinde YTM tarafından nakden ve defaten ödenir.'),
         ('index','Madde 2, enflasyona göre telafi',4,'üzere hesaplanacak reel değer kaybı telafisiyle birlikte'),
     ]),
    ('detail.body','detail','2/3965 TBMM kanun teklifi dosyası',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/KanunTeklifi/6228fb3f-0641-4eb0-875a-01a1591878b8',
     'e27751a1ea745646a8aa569b8ec646e6afeca33abd6e31a9a86cb54d5ee4c9e5',[
         ('id','Esas numarası',None,'<td>2 / 3965</td>'),
         ('filed','Başkanlığa geliş tarihi',None,'<td>20/10/2026</td>'),
         ('committee','Komisyon giriş tarihi',None,'<td>21/10/2026</td>'),
         ('pending','Komisyon işlem alanı',None,'<td>Komisyonda</td>'),
         ('membership','İmza tablosunda Altıntaş, Demokrat Parti ve İzmir',None,
          'Haydar ALTINTA&#x15E;\n\n                                            </a>\n                                        </td>\n                                        <td>DEMOKRAT PART&#x130;</td>'),
     ]),
    ('agenda.body','agenda','TBMM Gelen Kâğıtlar 15, 21 Ekim 2026','2026-10-21','2026-10-21','TBMM','official',
     'https://www.tbmm.gov.tr/Gundem/GelenKagitDetay/cfa20ad1-6674-4173-bef3-01a15e29ddef',
     '6bcabebc8a39717ec5fa58e773c977f65404baa0db2863157087def66deb18f1',[
         ('id','Milletvekili teklifleri 5. sıra',None,'Teklifi (2/3965) (Sanayi, Ticaret, Enerji, Tabii Kaynaklar, Bilgi ve Teknoloji ile Plan ve B&uuml;t&ccedil;e Komisyonlarına)'),
     ]),
    ('party.body','party','Demokrat Parti’nin 2/3965 açıklaması','2026-10-20','2026-10-20','Demokrat Parti','party',
     'https://www.dp.org.tr/haber/dp-parti-sozcusu-ve-i-zmir-milletvekili-haydar-altintas-tan-fon-krizi-i-cin-kanun-teklifi-yatirimcinin-birikimi-korunmali-sorumlular-hesap-vermeli',
     '884f3d5f884652d7f5a4c55115d16af4dcbbdc29d95f2438dcbe87fa493c93ea',[
         ('day','Parti açıklamasının günü',None,'20/10/2026</div>'),
         ('title','Parti sitesinde sözcü ve milletvekili sıfatı',None,'DP Parti Sözcüsü ve İzmir Milletvekili Haydar Altıntaş’tan Fon Krizi İçin Kanun Teklifi'),
         ('audit','Üç aylık bağımsız denetim ve KAP',None,'&uuml;&ccedil;er aylık d&ouml;nemlerle bağımsız denetime'),
         ('payment','Parti metninde 30 günlük tazmin önerisi',None,'en ge&ccedil; 30 g&uuml;n i&ccedil;inde yapılması hedefleniyor.'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0412-fund-3965-'+key
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
(checks/'fund-3965-source-records.json').write_text(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'package-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
