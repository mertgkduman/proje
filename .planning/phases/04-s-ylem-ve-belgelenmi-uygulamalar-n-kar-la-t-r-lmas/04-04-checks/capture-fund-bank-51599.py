"""Archive the original 7/51599 and its pre-cut banking oversight sources."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path,sys.argv[1:])
root = Path('data/practices/sources/yeni-parti')
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
 ('7-51599.pdf','signed','7/51599 imzalı yazılı soru','2026-10-19',None,'TBMM','official',
  'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T7/WebOnergeMetni/ad21f7b9-0a9f-45ac-a8c1-73e7f995146a.pdf',
  'f6a0d23aa8f4f0c90ffc60353adf074cb0d8aa2a45e67714633d38c462bb8b0f',[
    ('group','Grup başlığı ve önerge sayısı',0,'YENİ PARTİ\n515 9 9'),
    ('permit','İkinci paragraf, Şubat faaliyet izni ve Resmî Gazete',0,
      'faaliyet izni verildiği ve bu kararın 4 Mart 2026 tarihli Resmî Gazete'),
    ('risk','Soru 9, fiilen faaliyete geçme ve risk bildirimleri',0,
      'faaliyete başlamasının engellenmesine gerekçe'),
    ('payments','Soru 18, aktarılan, tahsil edilen ve ödenen tutarlar',1,
      'Bu tutarın ne kadarı tahsil edilmiş, ne kadarı yatırımcılara ödenmiştir?'),
    ('public','Soru 19, kamu kaynağıyla finansman',1,
      'diğer kamu kurumlarının kaynaklarından doğrudan ya da dolaylı finansman'),
  ]),
 ('7-51599-detail.html','register','7/51599 TBMM esas kaydı',None,None,'TBMM','official',
  'https://tbmm.gov.tr/Denetim/Yazili-Soru-Onergesi-Detay/6b5fe4e8-2477-49d3-8a53-01a159a95413',
  'a0d36442ac67e9f1744b2a4708851e8444f195b827892f02ec3ed2f1beee474c',[
    ('id','Esas numarası',None,'7 / 51599'),
    ('filed','Başkanlığa geliş 20 Ekim',None,'20.10.2026'),
    ('ministry','Önerge muhatabı',None,'Hazine Ve Maliye Bakan&#x131; Mehmet &#x15E;&#x130;M&#x15E;EK'),
  ]),
 ('fund-gelen-51538-51599.html','gelen','5 Kasım 2026 Gelen Kâğıtlar No. 24','2026-11-05','2026-11-05','TBMM','official',
  'https://tbmm.gov.tr/Gundem/GelenKagitDetay/b51df55a-d2e2-4395-9156-01a1ab76ea13',
  '548e7038e2da0fa2eef8e54c0aaccabc89574873e581c3652551cd6d73e10730',[
    ('date','No. 24, 5 Kasım yayın günü',None,'5.11.2026'),
    ('question','69. sırada 7/51599 yazılı soru kaydı',None,'(7/51599)'),
    ('other','8. sırada ayrı 7/51538 yazılı soru kaydı',None,'(7/51538)'),
  ]),
 ('bddk-4313.pdf','bd-summary','BDDK’nın 14 Ekim komisyon bilgilendirmesine ilişkin açıklaması','2026-10-16',
  '2026-10-16','Bankacılık Düzenleme ve Denetleme Kurumu','official',
  'https://www.bddk.gov.tr/Duyuru/EkGetir/4313?ekId=946',
  '57c3bb8c073b08805edb68ed9eabe06e0019f2937ebee46e33eb3324b6397cc6',[
    ('permit','Fiilî başlangıç onayının kurumca açıklanması',0,
      'sonra fiilen faaliyete geçilebilmesi için Kurumumuzdan ayrıca onay alınması'),
    ('declined','BDDK açıklamasında fiilî faaliyete geçilmesi',0,
      'fiilen faaliyete geçmesi uygun'),
    ('transfer','BDDK açıklamasında devir aşaması',0,'Emlak Katılım Bankası tarafından devralınma aşamasına girdiği'),
  ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0404-bank-51599-'+key
    vid=doc+'-v1'
    obj=f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    store(obj,raw)
    store(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='yeni-parti',title=title,source_kind=kind)
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
(checks/'fund-bank-51599-source-records.json').write_text(json.dumps(dict(party_id='yeni-parti',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'bank-51599-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
