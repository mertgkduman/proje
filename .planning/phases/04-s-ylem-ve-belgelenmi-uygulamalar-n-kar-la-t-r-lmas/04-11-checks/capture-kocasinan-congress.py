"""Archive the original published accounts of the Kocasinan district congress."""

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
 ('kocasinan-plan','plan','Kocasinan 8. Olağan İlçe Kongresi ön duyurusu','Kayseri Haber','Döndü Nur Demir','news','2026-08-27',
  'https://www.kayserihaber.com/mahmut-arikan-kayseriye-geliyor-tarih-yer-belli',
  '465ce34a00ccb6f5c451bf0aed7a341dc0ee7830ebe58053c5e8b0f3a82cfdcf',(
    ('day','28 Ağustos planlanan gün ve yer',
     '28 Ağustos 2026 Cuma günü saat 19.30’da İl Kültür Müdürlüğü Konferans Salonu’nda yapılacak.'),
  )),
 ('kocasinan-day','day','28 Ağustos Kayseri programında Kocasinan kongresi','Kayseri Haber','Döndü Nur Demir','news','2026-08-28',
  'https://www.kayserihaber.com/mahmut-arikan-bugun-kayseride-iste-programi',
  '3edff54cd3f3b9a380810b2c860ec4d5f23095ee911f175337f810ccecafb033',(
    ('published','28 Ağustos gün içi program yayımı','datePublished" content="2026-08-28T10:55:00+03:00'),
    ('planned','Kongrenin gün içi programda planlı yeri',
     'Kocasinan İlçe Kongresi saat 19.30’da İl Kültür Müdürlüğü Konferans Salonu’nda gerçekleştirilecek.'),
  )),
 ('kocasinan-kayseri','kayseri','Kayseri Haber Kocasinan seçim sonucu','Kayseri Haber','Eray Sena Kösedağ','news','2026-08-29',
  'https://kayserihaber.com.tr/mahmut-arikanin-katildigi-kongrede-surpriz-yok-baskan-yeniden-secildi',
  'b686f839866f34fa31f886eae8f3dc3fbfb2ffc8e6b743852fca9a33e44686a7',(
    ('published','29 Ağustos seçim haberi yayımı','datePublished" content="2026-08-29T15:51:02+03:00'),
    ('election','Selçuk Onat’ın yeniden seçildiği haber özeti',
     'Selçuk Onat, delegelerin oy birliğiyle yeniden göreve seçildi.'),
  )),
 ('kocasinan-talas','talas','Talas Express Kocasinan kongresi ve seçim sonucu','Talas Express Haber','Ferhat','news','2026-08-29',
  'https://talasexpresshaber.com/haber/saadet-partisi-kocasinan-da-yeni-donem-icin-guclu-mesaj-hak-gelecek-adalet-gelecek-saadet-gelecek',
  '124f743044a0ca2a29ec4d8fd24691239a93ed05914c552836d0ad63f063034c',(
    ('published','29 Ağustos haber yayımı','datePublished" content="2026-08-29T10:50:00+00:00'),
    ('updated','Arşivlenen nüshanın 9 Ekim güncellemesi','dateModified" content="2026-10-09T11:55:21+00:00'),
    ('occurred','Mahmut Arıkan ve Erdal Altun’un katılımıyla gerçekleşme',
     'Kongresi, Genel Başkan Mahmut Arıkan’ın teşrifleri, İl Başkanı Erdal Altun,\nteşkilat mensupları, delegeler ve vatandaşların yoğun katılımıyla\ngerçekleştirildi.'),
    ('election','Haber gövdesinde Selçuk Onat’ın yeniden seçilmesi',
     'mevcut İlçe Başkanı Selçuk Onat, delegelerin oy\nbirliğiyle yeniden Kocasinan İlçe Başkanı seçilerek güven tazeledi.'),
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
    raw_file=stage/f'{filename}.html'; raw=raw_file.read_bytes()
    assert sha256(raw).hexdigest()==digest
    doc=f'0411-kocasinan-congress-{key}';version=doc+'-v1'
    original=f'objects/{digest}/original.html.bin';readable=f'objects/{digest}/readable.html'
    save(root/original,raw);save(root/readable,readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='saadet',title=title,source_kind=kind)
    add('document_version',id=version,document_id=doc,original_url=url,final_url=url,document_date=published,
        date_precision='day',date_unknown_reason=None,version_label='Özgün yayımlanan web nüshası.',mime='text/html',
        accessed_at=datetime.fromtimestamp(raw_file.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,
        sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=version,publisher=publisher,author=author,
        kind='journalism',published_at=published,
        date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
        basis='Yayıncı, kongre ve sonuç atıfları özgün gövdede okundu.')
    view=build_view(raw,url,root,fetch_assets=False);view['version_id']=version;validate_view(root,view)
    manifest=root/view['manifest_path'];paths.add(manifest)
    paths.update(manifest.parent/n for n in json.loads(manifest.read_bytes())['files'])
    add('archive_view',**view)
    body=html_source_text(raw)
    for suffix,section,exact in anchors:
        assert exact in body,(key,suffix)
        add('passage',id=doc+'-'+suffix,version_id=version,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=None,printed_page=None)
out=checks/'kocasinan-congress-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'kocasinan-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths),sha256(out.read_bytes()).hexdigest())
