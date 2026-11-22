"""Preserve the DBP decisions and reporting on the Edremit workshop."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/dbp')
now = datetime.now(timezone.utc).isoformat()
paths, entries = set(), []


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def save(relative, body):
    path = root/relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert body == path.read_bytes()
    else:
        path.write_bytes(body)
    paths.add(path)


sources = (
    ('dbp-2024-kadin-party',
     'https://dbp.org.tr/kadin/haberler/kadin/haberler/3-kadin-konferansi-sonuc-bildirgemizi-yayinladik',
     'DBP 3. Kadın Konferansı bildirgesi', '2024-12-13', '2024-12-15', 'Demokratik Bölgeler Partisi',
     'DBP Kadın Meclisi','party',[
        ('occurrence','Konferans tarihi ve yeri','13 Aralık 2024’te Amed’de gerçekleştirdik.'),
        ('training','Yerel kadın akademisi eğitimleri','bölge odaklı kadın akademileri şeklinde yaygınlaştırılarak'),
        ('resolution','Konferansın eğitim yönündeki kararı','kadın akademileri ile büyütmeyi karar altına almıştır.'),
    ]),
    ('dbp-2025-kadin-party',
     'https://dbp.org.tr/kadin/haberler/kadin/haberler/demokratik-toplum-kadinlarin-esit-ve-ozgur-geleceginin-teminatidir',
     'DBP Kadın Meclisi 2 Ağustos toplantısı bildirgesi', '2025-08-02', '2025-08-05', 'Demokratik Bölgeler Partisi',
     'DBP Kadın Meclisi','party',[
        ('meeting','Kadın Meclisi toplantı günü','2 Ağustos 2025 tarihinde toplanan meclisimiz'),
        ('series','Parti kaynağında atölye dizisinin başlangıcı','Mayıs 2025’te Colemêrg’den başlattığımız kadın kurtuluş ideolojisi atölyeleri'),
        ('goal','Atölye dizisinin devamına yönelik hedef','Eylül ayının sonuna kadar bu buluşmaların daha da yaygınlaştırılması hedeflenmiştir.'),
    ]),
    ('dbp-2025-kadin-ilke','https://ilketv.com.tr/vanda-kadin-atolyesi-duzenledi/',
     'İlke TV, Edremit kadın atölyesi', '2025-08-13', '2025-08-13','İlke TV','Haber Merkezi','news',[
        ('byline','Haberin yayın zamanı','13 Ağustos 2025 19:17'),
        ('venue','Atölyenin yeri ve katılımcıları','Edremit ilçesine bağlı Şehit Fırat Mahallesi’nde gerçekleştirilen atölyeye DBP Van İl Eşbaşkanı Gönül Uzunay, DBP Kadın Meclisi Sözcüsü Berivan Bahçeci, DBP Parti Meclisi üyesi Hebun Aslan'),
        ('program','Atölyedeki soru ve cevap bölümü','Soru-cevap bölümüyle devam eden atölye'),
    ]),
    ('dbp-2025-kadin-politika','https://politikahaber.com/wanda-kadin-atolyesi/',
     'Politika Haber’de MA imzalı Edremit kadın atölyesi', '2025-08-13', '2025-08-13','Politika Haber','MA','news',[
        ('venue','MA haberinde mahalle ve atölye','Şehit Fırat Mahallesi’nde yapılan atölyeye'),
        ('byline','Haberin MA imzası','<p><strong>MA</strong></p>'),
    ]),
)
for name,url,title,date,published,publisher,author,kind,passages in sources:
    local=stage/(name+'.html')
    raw=local.read_bytes()
    doc=f'0409-women-{name}'
    vid=doc+'-v1'
    digest=sha256(raw).hexdigest()
    original=f'objects/{digest}/original.html.bin'
    readable=f'objects/{digest}/readable.html'
    save(original,raw)
    save(readable,readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='dbp',title=title,source_kind=kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,
        document_date=date,date_precision='day',date_unknown_reason=None,version_label='Erişilen özgün yayın.',
        accessed_at=datetime.fromtimestamp(local.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,
        mime='text/html',sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=author,
        kind='party_publication' if kind=='party' else 'journalism',published_at=published,
        date_precision='day',social_handle=None,public_url=url,basis='Gövde tarihi, sayfanın yayın tarihi ve kaynak imzası ayrı kontrol edildi.')
    view=build_view(raw,url,root,fetch_assets=False)
    view['version_id']=vid
    validate_view(root,view)
    add('archive_view',**view)
    manifest=root/view['manifest_path']
    paths.add(manifest)
    paths.update(manifest.parent/n for n in json.loads(manifest.read_bytes())['files'])
    body=html_source_text(raw)
    for key,section,exact in passages:
        assert exact in body,(name,key,exact)
        add('passage',id=doc+'-'+key,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=None,printed_page=None)
out=checks/'women-workshop-source-records.json'
with out.open('x') as f:
    f.write(json.dumps(dict(party_id='dbp',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0409-women-workshop-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
