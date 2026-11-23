"""Archive the tax deferral statement, statute and administrative notice."""

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
    ('uysal-019.html','statement','8 Mayıs Demokrat Parti Genel Başkanı açıklaması','2026-05-08','2026-05-08','Demokrat Parti','party',
     'https://www.dp.org.tr/haber/demokrat-parti-genel-baskani-gultekin-uysal-esnaf-ayakta-kalamazsa-devlet-de-tahsil-edemez',
     'ba57a14003c42b106e3ca8875b0b2ffa3728c03708e4d0e274a12c39609984de',[
         ('day','Parti yayınının gösterdiği tarih',None,'08/05/2026'),
         ('speaker','Parti yayınının açıklamayı atfettiği genel başkan',None,'Demokrat Parti Genel Başkanı Gültekin Uysal: Esnaf'),
         ('terms','Açıklamada geçen maliyet ve taksit süresi',None,'%44&rsquo;e yaklaşan maliyetle 72 ay taksit'),
         ('target','Faiz ve kapsam hakkındaki parti yaklaşımı',None,
          'Faizi d&uuml;ş&uuml;rmek, kapsamı genişletmek, borcu &ouml;denebilir hale getirmektir.'),
         ('quote','Parti açıklamasında kapsam hedefi',None,'kapsamı genişletmek'),
     ]),
    ('7582-proposal.html','proposal','2/3669 tecil süresi değişikliği teklif kaydı',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/KanunTeklifi/40d8244e-d703-48e3-a36b-019df6df408b',
     '904d440891e6f00528cc629c9922c6b8dce390fcc7de4f136e1299b6d3a29620',[
         ('number','2/3669 esas numarası',None,'2 / 3669'),
         ('filed','Teklifin TBMM’ye geliş tarihi',None,'05/05/2026'),
     ]),
    ('7582-register.html','register','7582 sayılı kanunun kabul ve yayım kaydı',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/Kanun/40d8244e-d703-48e3-a36b-019df6df408b',
     '451db71068549086132e7ece602480e4f7390db2e7f1354f4c3fbe6fe0201dfa',[
         ('accept','TBMM’nin kaydettiği kabul tarihi',None,'21/05/2026'),
         ('issue','Resmî Gazete 33270 sayılı yayım kaydı',None,'33270'),
         ('published','Kanunun Resmî Gazete yayım tarihi',None,'04/06/2026'),
     ]),
    ('7582-law.html','law','7582 sayılı Kanunun kabul edilen metni','2026-05-21','2026-06-04','TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/KanunMetni/4b916eb3-fb9a-4f40-aea8-3c044342be21.htm',
     '622af3262b0d2696d93328f0d49f2f201f2e8d7d25d8ca7e5fd8c08ee2484962',[
         ('months','7582 m.1. Tecil süresi tavanı değişikliği',None,'yer alan “36” ibaresi “72”'),
         ('guarantee','7582 m.1. Teminatsız tutar değişikliği',None,'“ellibin Yeni Türk Lirasını” ibareleri\r\n“bir milyon Türk lirasını” şeklinde değiştirilmiştir.'),
         ('effect','7582 m.14/ç. Diğer maddelerin yayım günü yürürlüğü',None,'ç) Diğer\r\nmaddeleri yayımı tarihinde,'),
     ]),
    ('tecil-gib.pdf','gib','GİB’in Seri B Sıra No 20 Tahsilat Genel Tebliği açıklaması','2026-06-16',None,'Gelir İdaresi Başkanlığı','official',
     'https://cdn.gib.gov.tr/api/gibportal-file/file/getFile?objectKey=DUYURU%2FUNIVERSAL%2F2026%2F6183_Teblig_B_20_abn.pdf',
     'c864044c8e99fb3fad0c7c5b4a3eac1e49d4226e870214d005b53a71d3a3fad9',[
         ('day','GİB açıklamasında Tebliğ tarihi ve Resmî Gazete sayısı',0,'16/6/2026\n33282'),
         ('interest','Uygun başvurularda yıllık tecil faizi',0,'Cari faiz oranı olan yıllık %39 yerine %29 tecil faizi uygulanması,'),
         ('date','Vergi dairesince takip edilen borçlar için vade kapsamı',0,'vadesi 5/6/2026 tarihi ve öncesi olan tüm amme'),
         ('exclusions','Özel tüketim vergisi ve geçici vergi istisnaları',0,
          'alacaklarının (özel tüketim vergisi ve geçici vergi hariç) taksitlendirilebilmesi,'),
         ('application','31 Ağustos son başvuru tarihi',0,'31/8/2026 tarihine kadar (bu tarih dahil)'),
         ('security','GİB’in özel rejimdeki teminat açıklaması',0,'Tebliğde 10 milyon TL’yi aşmayan borçlar için teminat alınmayacağı,'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0412-tax-deferral-'+key
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
(checks/'tax-deferral-source-records.json').write_text(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'tax-deferral-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
