"""Archive the framework law, party statement and two vote records."""

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
    ('dp-aug07.html','statement','Demokrat Parti’nin 7 Ağustos çerçeve kanun açıklaması','2026-08-07','2026-08-07','Demokrat Parti','party',
     'https://www.dp.org.tr/haber/teror-orgutu-pkk-yi-kurt-kokenli-vatandaslarimizin-hamisi-vasisi-yapacak-her-tesebbusun-karsisindayiz',
     '08ea1aeefb613ffcaf70881adba7e10177927eaa3164bda4aa707a3a4cfce0de',[
         ('day','Parti duyurusunda gösterilen gün',None,'07/08/2026'),
         ('target','Parti açıklamasının itirazını özetleyen başlık',None,
          'Terör örgütü PKK’yı Kürt kökenli vatandaşlarımızın hamisi vasisi yapacak her teşebbüsün karşısındayız.'),
         ('quote','Parti açıklamasındaki itirazın doğrudan aktarımı',None,'her teşebbüsün karşısındayız.'),
     ]),
    ('proposal.html','proposal','2/3793 sayılı kanun teklifi ve komisyon sicili',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/KanunTeklifi/3270cca3-ed00-434b-aa64-019fd1c2dd00',
     'c19f453968fc82a8407e542d7abefc8539c8b7fb6bae021f557a9373150c151f',[
         ('number','Kanun teklifinin esas numarası',None,'2 / 3793'),
         ('filed','Teklifin TBMM Başkanlığına geliş günü',None,'05/08/2026'),
         ('report','Adalet Komisyonunun rapor kararı günü',None,'08/08/2026'),
     ]),
    ('7595-signed.pdf','signed','2/3793 imzalı kanun teklifinin üst yazısı','2026-08-05',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/7a2bdba9-f0eb-4de1-86a2-01dd10713cc4.pdf',
     '928d478d246f21c3d5eb05c5b261a439907110c0297272baabac4160e6c464bd',[
         ('date','İmzalı dosyanın evrak kapağındaki geliş ve esas numarası',1,'Tarih: 5-8-2026 Esas No:2/3793'),
     ]),
    ('register.html','register','7595 sayılı kanunun kabul ve yayım sicili',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/Kanun/3270cca3-ed00-434b-aa64-019fd1c2dd00',
     'fb2f4fd4ed9bbf614c24a705fceb235af5f0b9d493ad22b13b5232f7898d2919',[
         ('accepted','TBMM sicilinde Kanunun kabul günü',None,'10/08/2026'),
         ('published','Resmî Gazete’de belirtilen yayım günü',None,'18/08/2026'),
         ('issue','Resmî Gazete yayımlanan sayı',None,'33344'),
     ]),
    ('law.html','law','7595 sayılı kanunun kabul edilen metni','2026-08-10','2026-08-18','TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/KanunMetni/08e9230f-a758-4a9e-a2ec-42d8937100c8.htm',
     '983c2f1117829d2a65b1edf1a9de226430fbb71cd459ff37a6dcd4fbc5d0bf44',[
         ('condition','7595 m.1. MGK teyidinin Resmî Gazete’de yayımı şartı',None,
          'teyidine dair Milli Güvenlik Kurulu Kararının Resmî Gazete’de yayımlanmasını'),
         ('exceptions','7595 m.3. Erteleme kapsamındaki yasal istisnalar',None,
          'yayımlanmış olması koşuluyla, örgüt faaliyeti çerçevesinde işlenen kasten\r\nöldürme suçu'),
         ('effect','7595 m.11. Yayım tarihinde yürürlük',None,'Bu Kanun yayımı tarihinde yürürlüğe girer.'),
     ]),
    ('altintas-commission-2025.html','identity','TBMM 27 Ağustos 2025 Altıntaş basın açıklaması','2025-08-27','2025-08-27','TBMM','official',
     'https://tbmm.gov.tr/Haber/Detay?Id=74062136-1cc1-4c6d-bd57-0198eb658a0f',
     'd3c4863020912b2018b7fb50172133faf34d5351e5b28708ce07f9a109341c02',[
         ('speaker','Önceki TBMM kaydında milletvekilinin adı ve seçim çevresi',None,
          'İzmir Milletvekili Haydar Altıntaş, üniter devletin vazgeçilmez olduğunu belirterek'),
     ]),
    ('altintas-aug11.html','membership','TBMM 11 Ağustos 2026 Altıntaş basın toplantısı','2026-08-11','2026-08-11','TBMM','official',
     'https://www.tbmm.gov.tr/Haber/Detay?Id=bad5ec75-efe5-4fd1-9d38-019ff2da5d50',
     '4c45fc158d7a55505e112322616d1ac32dcbbc151eaabb6f8044539eaed8924b',[
         ('party','TBMM basın toplantısı haberinde Altıntaş’ın parti hanesi',None,
          'Demokrat Parti (DP) İzmir Milletvekili Haydar Altıntaş'),
         ('tally','Basın toplantısında atıf yapılan kesin oy sayıları',None,
          '467 kabul, 87 ret, 7 çekimser oyla kabul edildiğini belirtti.'),
     ]),
    ('125-printed.pdf','minutes','10 Ağustos 2026 125. Birleşim basılı tutanağı ve kesin oy cetvelleri','2026-08-10',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/4/125/Basilmis/0a8ddea1-3d61-4bbb-887a-46331a5e4624.pdf',
     '2cef11386de77e51f0a4534a44271797a82b736a6256258883dfa36457da0c31',[
         ('announced','Basılı 318. sayfada birleşimde okutulan açık oylama sonucu',163,
          'Kullanılan oy sayısı : 562\nKabul : 468\nRet :\nÇekimser :\n88\n6'),
         ('conclusion','Basılı 318. sayfada başkanın kabul açıklaması',163,
          'Teklif kabul edilmiş ve kanunlaşmıştır'),
         ('two-columns','Basılı 319. sayfada iki ayrı oylama',164,
          'Teklifi’nin maddelerine geçilmesine dair verilen oyların sonucu'),
         ('official-count','Basılı 319. sayfada tüm teklif oylamasının kesin kabul, ret ve çekimser sayıları',164,
          ': 467\n:\n87\n:\n7'),
         ('duplicates','Basılı 319. sayfada iki mükerrer satır ve 563 kayıt',164,
          ': 467\n:\n87\n:\n7\n:\n0\n:\n0\n:\n2\n: 563'),
         ('nominal','Basılı 327. sayfada Haydar Altıntaş’ın iki kişisel oyu ve parti hanesi',172,
          'İzmir Altıntaş Haydar DP Katılmadı Ret'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0412-framework-7595-'+key
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
            article=None,section=section,pdf_page_index=index,printed_page=str(index+155) if key=="minutes" else None)
(checks/'framework-7595-source-records.json').write_text(json.dumps(dict(party_id='demokrat',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'framework-7595-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
