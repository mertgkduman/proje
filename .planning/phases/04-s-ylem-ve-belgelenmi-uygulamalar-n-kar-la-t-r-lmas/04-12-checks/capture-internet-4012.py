"""Archive the original 2/4012 filing and its legislative context."""

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
    ('4012.pdf','signed','2/4012 imzalı kanun teklifi','2026-11-02',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T2/WebOnergeMetni/7085211b-0aa3-4b61-a79e-3af2917b6a32.pdf',
     '97ae7b68849e28c6a3ec47c0c2565c4e174566217161e38c6fc29b0821dd9bed',[
         ('signature','İmzalı yazının 2 Kasım tarihi',0,'Gereğini arz ederim. 02/11/2026'),
         ('routing','Kapakta komisyon ve esas numarası',0,'Tarih: 5-11-2026 Esas No:2/4012'),
         ('age','Madde 1, kimlik bilgisi içermeyen belirteç',4,'karşılamadığını gösteren ve kimlik bilgisi içermeyen tek kullanımlık kriptografık doğrulama'),
         ('privacy','Madde 1, biyometrik ve kimlik verisi sınırı',4,'Türkiye Cumhuriyeti kimlik numarası, resmi kimlik belgesi görüntüsü, banka veya kredi kartı'),
         ('blind','Madde 1, çift yönlü körleştirme ve kayıt kısıtı',4,'üretilmesi sırasında çift yönlü körleştirme tekniği uygulanması zorunlu olup, hiçbir kamu kurum'),
         ('limit','Madde 2, bant genişliği yaptırımı',4,'genişliğinin yüzde elli ve yüzde doksan oranına kadar daraltılmasına ilişkin hükümler madde'),
         ('court','Madde 2, yerleşim yeri sulh hukuk hâkimliği ve süre',4,
          'yanı sıra yerleşim yeri sulh hukuk hâkimliğine başvurarak hesabın yeniden açılmasını talep\nedebilir. Bu başvurular her türlü resim ve harçtan muaftır ve hâkimlikçe en geç beş iş günü'),
     ]),
    ('4012-detail.html','detail','2/4012 TBMM kanun teklifi dosyası',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/KanunTeklifi/95459352-1089-4c61-9a45-01a1a01ad6af',
     '5967a598fb344d8ce76c27a57494e479e86aa2f97ce481fbddd8ebeb64cbefcb',[
         ('id','Teklif esas numarası',None,'<td>2 / 4012</td>'),
         ('filed','Başkanlığa geliş 3 Kasım',None,'<td>03/11/2026</td>'),
         ('committee','Komisyon giriş tarihi 5 Kasım',None,'<td>05/11/2026</td>'),
         ('pending','Erişilen komisyon işlem alanı',None,'<td>Komisyonda</td>'),
         ('membership','İlk imza sahibi, parti ve seçim çevresi',None,
          'Haydar ALTINTA&#x15E;\n\n                                            </a>\n                                        </td>\n                                        <td>DEMOKRAT PART&#x130;</td>'),
     ]),
    ('4012-gelen.html','gelen','5 Kasım 2026 Gelen Kâğıtlar No. 24','2026-11-05','2026-11-05','TBMM','official',
     'https://tbmm.gov.tr/Gundem/GelenKagitDetay/b51df55a-d2e2-4395-9156-01a1ab76ea13',
     '548e7038e2da0fa2eef8e54c0aaccabc89574873e581c3652551cd6d73e10730',[
         ('listed','2/4012 ve iki komisyonun 5 Kasım bültenindeki kaydı',None,
          '(2/4012) (Dijital Mecralar ile Adalet Komisyonlarına)'),
     ]),
    ('7578-register.html','lawregister','7578 sayılı kanunun TBMM kabul ve yayım kaydı',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/Kanun/5F9CED52-3776-46E4-BE23-019CB8DA2666',
     'c4803e7cf3b96a55d3088cfc25df253c3da7bd342b357a25dd67187cdbc65f86',[
         ('approval','7578 sayılı kanun kabul tarihi',None,'<td>22/04/2026</td>'),
         ('publication','7578 sayılı kanun Resmî Gazete tarihi',None,'<td> 01/05/2026</td>'),
     ]),
    ('7578-tbmm.html','law','7578 sayılı kanunun TBMM’de kabul edilen metni','2026-04-22',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/KanunMetni/9bf93173-7648-4771-ab36-0e45666c423d.htm',
     'aabf5dc4bf56d57f906446f9529d6b7898388617ffec3cd95fb9beb74ea4e7d4',[
         ('age','Madde 22, 15 yaş sınırı ve yaş doğrulama',None,
          'onbeş yaşını doldurmamış çocuklara hizmet sunamaz ve bu'),
         ('term','Madde 27, 22 ve 23. maddelerin altı aylık yürürlük süresi',None,
          '23 üncü maddeleri yayımı tarihinden itibaren 6 ay sonra,'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0412-internet-4012-'+key
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
(checks/'internet-4012-source-records.json').write_text(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'4012-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
