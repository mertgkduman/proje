"""Archive the separate Kısacık article 5 motion and its context."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path,sys.argv[1:])
root = Path('data/practices/sources/yeni-yol')
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
 ('fund5472.pdf','report','14 Ekim 2026 Plan ve Bütçe Komisyonu tutanağı','2026-10-14',None,'TBMM','official',
  'https://tbmm.gov.tr/Tutanaklar/TutanakGoster/5472',
  'bb6077353f49dbf12c19679e9c883f302ef70165b2010c8bf9390be48e50789b',[
    ('date','Komisyon 2. toplantısı ve 14 Ekim tarihi',0,"2'nci Toplantı\n14 Ekim 2026 Çarşamba"),
    ('text','5. madde 2. fıkraya Kısacık ek önergesinin koşulu',89,
     'uğratılmasına neden olan işlem ve kararlarda doğrudan veya dolaylı olarak sorumluluklarının bulunduğunun tespiti hâlinde, meydana'),
    ('liable','Yazılı ek cümlede müteselsil sorumluluk ifadesi',89,
     'gelen zarar veya kayıptan portföy yönetim şirketiyle birlikte belki müteselsilen sorumludur.'),
    ('signed','İmzalı önerge ve görüşmede Kısacık kimliği',89,
     'Sadullah Kısacık\nAdana\nOTURUM BAŞKANI ORHAN ERDEM - Sayın Kısacık, buyurun.\nSADULLAH KISACIK (Adana)'),
    ('speech','Kısacık’ın ana ve hâkim şirketler için sözlü açıklaması',89,
     'söylediğimiz. Bu anlamda, fonun bağlı olduğu ya da kişilerin bağlı olduğu ana şirketler, hâkim şirketler, holdingler, bunların yönetim'),
    ('reject','Kısacık önergesinin oylama sonucu',89,
     'Önergeyi oylarınızı sunuyorum: Kabul edenler... Etmeyenler.. Önerge kabul edilmemiştir.'),
    ('article','Önergeden sonraki ayrı 5. madde oylaması',89,
     "5'inci maddeyi oylarınıza sunuyorum: Kabul edenler... Etmeyenler... 5'inci madde kabul edilmiştir."),
    ('spk','SPK temsilcisinin taslaktaki tüzel kişi kapsamı açıklaması',85,
     'ettiği tüm gerçek ve tüzel kişiler kapsamdadır.'),
 ]),
 ('committee-membership.html','membership','13 Mart 2025 komisyon üyeliği açıklaması','2025-03-13',None,'TBMM','official',
  'https://www.tbmm.gov.tr/Milletvekili/UyeKomisyonKonusmaTutanakDetay?tutanakId=73618',
  '17ce437fe046bd6ef601f02113f0c948d6b77f5919a973175e46ab37a7f352f5',[
    ('statement','Komisyon Başkanının Yeni Yol üyeliği açıklaması',None,
     'YENİ YOL Partisi Grubundan Komisyon üyeliğine seçilen Adana Milletvekili Sayın Sadullah Kısacık'),
 ]),
 ('7596.html','law','7596 sayılı kanunun TBMM kabul metni','2026-10-22',None,'TBMM','official',
  'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/KanunMetni/e15f4510-0860-4ccb-ab21-5dc05a661ad8.htm',
  '47cd4aab17cfacb1e0f528616d088b634b15e3b4a8ffc37cc5aeda083911123e',[
    ('priority','Kabul edilen 5. maddede takip sırası',None,
     'tutarın portföy yönetim şirketinden tamamen veya kısmen'),
    ('condition','Kabul edilen 5. maddede gerçek ve tüzel kişi sorumluluğu',None,
     'kişiler ile bu kişilerle birlikte hareket ettiği tespit edilenler şahsen'),
 ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0408-fund-kisacik-'+key
    vid=doc+'-v1'
    obj=f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    store(obj,raw)
    store(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='yeni-yol',title=title,source_kind=kind)
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
(checks/'fund-kisacik-source-records.json').write_text(json.dumps(dict(party_id='yeni-yol',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'kisacik-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
