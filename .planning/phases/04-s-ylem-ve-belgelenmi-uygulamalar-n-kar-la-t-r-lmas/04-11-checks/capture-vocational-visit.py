"""Archive the original published accounts and the prior parliamentary speech."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/saadet')
now = datetime.now(timezone.utc).isoformat()
sources = (
    ('visit-anka','habererk','Arıkan ve federasyon görüşmesi, ANKA haberi','Habererk','ANKA','news','2026-10-04',
     'https://www.habererk.com/haber/arikan-staj-ve-ciraklik-sigortasi-magdurlarina-destek-sozu-verdi_354144/',
     '2f24a7248ac3010826a862a644ea75b5c31f93062a176bd0257350729ba14969',(
        ('visit','Ankara’da görüşme, heyet ve görev',"Federasyonu Başkanı Murat Aydın ve beraberindeki heyet ile Ankara'da bir araya geldi."),
        ('topic','Görüşme gündemi, emeklilikte staj ve çıraklık süreleri','staj ve çıraklık dönemlerindeki çalışma sürelerinin emeklilik hesaplamalarında dikkate alınmamasının yarattığı mağduriyet ele alındı.'),
        ('statement','Haberde Arıkan’ın açıklamasının kaynağı','Mahmut Arıkan, sosyal medya hesabından yaptığı açıklamada'),
    )),
    ('visit-egundem','egundem','4 Ekim görüşmesi ve dayanak açıklaması','E-Gündem',None,'news','2026-10-05',
     'https://www.e-gundem.net/arikan-staj-sigortasi-talebini-tbmmde-gundemde-tutacak',
     'e32bf2fffeaff96386b1408f573048125d0caa64f80169e0e0075817d2c431e9',(
        ('date','Haber metninde 4 Ekim olay tarihi ve duyuru kaynağı',
         'Mahmut Arıkan, 4 Ekim Pazar günü Ankara’da Stajyer ve Çıraklık Sigortası Mağdurları Federasyonu Başkanı Murat Aydın ve heyetiyle bir araya geldi. Görüşme, partinin resmi hesabından duyuruldu.'),
    )),
    ('visit-karaman','karaman','26 Şubat Mehmet Karaman staj ve çıraklık açıklaması','TBMM','Mehmet Karaman','official',None,
     'https://www.tbmm.gov.tr/milletvekili/UyeGenelKurulKonusmalariDetay?eid=142663',
     '08e1b50de6467e2e1c4284ca1f902f031a17d9530bacbab725f8d09effa04da2',(
        ('date','65. Birleşim görüşme tarihi','26.02.2026</td>'),
        ('proposal','Karaman’ın borçlanma şartlı sigorta başlangıcı önerisi',
         'borçlanma şartıyla staj ve çıraklık süreleri sigorta başlangıcı kabul edilmeli'),
    )),
)
entries, paths = [], set()


def add(table, **values):
    entries.append(dict(kind=table,values=values))


def save(path, content):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        assert path.read_bytes()==content
    else:
        path.write_bytes(content)
    paths.add(path)


for filename,key,title,publisher,author,kind,published,url,digest,anchors in sources:
    raw_file=stage/f'{filename}.raw'; raw=raw_file.read_bytes()
    assert sha256(raw).hexdigest()==digest
    doc=f'0411-vocational-visit-{key}';version=doc+'-v1'
    original=f'objects/{digest}/original.html.bin';readable=f'objects/{digest}/readable.html'
    save(root/original,raw);save(root/readable,readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='saadet',title=title,source_kind=kind)
    add('document_version',id=version,document_id=doc,original_url=url,final_url=url,document_date=published or '2026-02-26',
        date_precision='day',date_unknown_reason=None,version_label='Özgün yayımlanan web nüshası.',mime='text/html',
        accessed_at=datetime.fromtimestamp(raw_file.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,
        sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=version,publisher=publisher,author=author,
        kind='journalism' if kind=='news' else 'official',published_at=published,
        date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
        basis='Yayıncı, görüşme ve açıklama atıfları özgün gövdede okundu.')
    view=build_view(raw,url,root,fetch_assets=False);view['version_id']=version;validate_view(root,view)
    manifest=root/view['manifest_path'];paths.add(manifest)
    paths.update(manifest.parent/n for n in json.loads(manifest.read_bytes())['files'])
    add('archive_view',**view)
    body=html_source_text(raw)
    for suffix,section,exact in anchors:
        assert exact in body,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=version,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=None,printed_page=None)
out=checks/'vocational-visit-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'visit-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths),sha256(out.read_bytes()).hexdigest())
