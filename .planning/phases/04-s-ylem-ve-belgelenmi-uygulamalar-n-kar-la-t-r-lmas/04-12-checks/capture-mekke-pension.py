"""Archive the Saadet pension proposal and the separate adopted law."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path('data/practices/sources/demokrat')
now = datetime.now(timezone.utc).isoformat()
entries = []
paths = set()
sources = [
    ('dp-3489','html','https://tbmm.gov.tr/Yasama/KanunTeklifi/8b53c3ee-85d4-4714-a82a-019be6160a5b',
     '2/3489 emekli ek ödemesi teklifinin TBMM kaydı',None,None,[
        ('id','Kanun teklifinin esas numarası','2 / 3489',None),
        ('submitted','Başkanlığa geliş tarihi','22/01/2026',None),
        ('assigned','Esas ve tali komisyonların giriş tarihi','23/01/2026',None),
        ('status','Erişimde görülen komisyon durumu','Komisyonda',None),
        ('initial','İlk imza sahibi Haydar Altıntaş','Haydar ALTINTA&#x15E;',None),
    ]),
    ('dp-3489','pdf','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/9986fbdb-46e7-4a96-b848-b87fd3401efb.pdf',
     '2/3489 Haydar Altıntaş imzalı teklif ve gerekçe','2026-01-22',None,[
        ('signature','Teklif üst yazısının imzası','Haydar ALTINTAŞ',0),
        ('basis','Gerekçede sayılan ek ödeme alanları','makam, görev veya temsil tazminatından yararlanmayan emekli askerler',2),
        ('proposal','Madde 1’deki hesap önerisi','2345 gösterge rakamının, yürürlükte bulunan memur maaş katsayısı ile',4),
    ]),
    ('dp-retirement-press','html','https://www.dp.org.tr/haber/demokrat-parti-den-emekli-asker-polis-ve-mit-mensuplari-i-cin-ek-odeme-adimi',
     'Demokrat Parti’nin 29 Ocak 2026 ek ödeme açıklaması','2026-01-29','2026-01-29',[
        ('role','Parti yayınının bildirdiği sözcü sıfatı','Demokrat Parti S&ouml;zc&uuml;s&uuml; ve İzmir Milletvekili Haydar Altıntaş',None),
        ('amount','Parti açıklamasının aktardığı gösterge','2345 g&ouml;sterge rakamı',None),
    ]),
    ('altintas-mekke','html','https://tbmm.gov.tr/milletvekili/UyeGenelKurulKonusmalariDetay?eid=149711',
     'Haydar Altıntaş’ın 5 Kasım 2026 Mekke Anlaşması konuşması','2026-11-05',None,[
        ('speaker','Tutanakta konuşmacının kimliği','HAYDAR ALTINTAŞ (İzmir)',None),
        ('quote','Altıntaş’ın Demokrat Parti adına açıkladığı tutum',
         'Bu sebeplerden dolayı biz Demokrat Parti olarak bu anlaşmaya "hayır" oyu vereceğiz.',None),
        ('grounds','Konuşmada bildirilen parlamenter denetim kaygısı',
         'Türkiye Büyük Millet Meclisinin onayından önce kurumsallaşma mekanizmalarının oluşturulması parlamenter denetim açısından soru işaretleri doğurmaktadır.',None),
    ]),
    ('shared-ballot','html','https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/14/AcikOylamaSonuc/cbfb34cb-f290-4c39-a3b3-b902717425ea.html',
     'TBMM 5 Kasım 14. Birleşim 2/3961 açık oy cetveli','2026-11-05',None,[]),
    ('shared-bill','html','https://tbmm.gov.tr/Yasama/KanunTeklifi/76de0ac1-3535-415a-8a7a-01a15e0c9a71',
     'TBMM 2/3961 Mekke Anlaşması onay teklifi kaydı','2026-10-21',None,[
        ('id','2/3961 esas numarası','2 / 3961',None),
    ]),
]
origin=Path('data/practices/sources/saadet')
previous=json.loads(Path('data/practices/04-saadet.json').read_bytes())
versions={e['values']['id']:e['values'] for e in previous['entries'] if e['kind']=='document_version'}
shared={
    'shared-ballot':versions['0411-mekke-ballot-v1'],
    'shared-bill':versions['0411-mekke-bill-v1'],
}

def add(table, **row):
    entries.append({'kind':table, 'values':row})

def put(rel, body):
    path = root/rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes()==body
    else:
        path.write_bytes(body)
    paths.add(path)

for key, ext, url, title, day, published, passages in sources:
    fetched = stage/f'{key}.{ext}'
    prior=shared.get(key)
    raw=(origin/prior['original_path']).read_bytes() if prior else fetched.read_bytes()
    charset='windows-1254' if key=='shared-ballot' else None
    publisher='Demokrat Parti' if key=='dp-retirement-press' else 'TBMM'
    kind='party_publication' if key=='dp-retirement-press' else 'official'
    digest = sha256(raw).hexdigest()
    doc = f'0412-policy-{key}' + ('-signed' if ext=='pdf' else '')
    vid = doc+'-v1'
    original = f'objects/{digest}/original.'+('pdf' if ext=='pdf' else 'html.bin')
    readable = f'objects/{digest}/readable.html'
    put(original, raw)
    put(readable,(origin/readable).read_bytes() if prior else readable_bytes(raw,ext,legacy=False))
    captured=prior['accessed_at'] if prior else datetime.fromtimestamp(fetched.stat().st_mtime,timezone.utc).isoformat()
    add('document',id=doc,party_id='demokrat',title=title,source_kind='party' if kind=='party_publication' else 'official')
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=day,
        date_precision='day' if day else 'unknown',date_unknown_reason=None if day else 'TBMM kayıt sayfasının ilk yayımlandığı gün açık değil. Teklifin geliş, sevk ve kabul tarihleri ayrı görünen pasajlarda.',version_label='Erişilen özgün kaynak kaydı.',
        accessed_at=captured,verified_at=now,mime='text/html' if ext=='html' else 'application/pdf',
        sha256=digest,original_path=original,readable_path=readable)
    add('source_attribution',version_id=vid,publisher=publisher,author=None,kind=kind,
        published_at=published,date_precision='day' if published else 'unknown',social_handle=None,
        public_url=url,basis='Yayıncı ve künye, özgün sayfada görülen bilgiyle kaydedildi.')
    if ext=='html':
        view=build_view(raw,url,root,fetch_assets=False,http_charset=charset)
        view['version_id']=vid
        validate_view(root,view)
        add('archive_view',**view)
        manifest=root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
        body=html_source_text(raw)
        if key=='altintas-mekke':
            first=body.index('HAYDAR ALTINTAŞ (İzmir)')
            ending='Bu sebeplerden dolayı biz Demokrat Parti olarak bu anlaşmaya "hayır" oyu vereceğiz.'
            end=body.index(ending,first)+len(ending)
            passages.append(('authority','Konuşmacı başlığından Demokrat Parti adına beyana kadar tutanak',
                             body[first:end],None))
        if key=='shared-ballot':
            decoded=raw.decode(charset)
            rows=[m.group(1).strip() for m in re.finditer(r'<tr[^>]*>(.*?)</tr>',decoded,re.S|re.I)]
            for suffix,section,markers in (
                ('vote','Haydar Altıntaş’ın Demokrat Parti etiketli ret oyu',('<td>ALTINTA&#x15E;</td>','<td>Haydar</td>','Demokrat Parti','23:49:42')),
                ('yes','Açık cetvel kabul sayısı',('Kabul Edenler','277')),
                ('no','Açık cetvel ret sayısı',('Reddedenler','118')),
                ('duplicates','Açık cetveldeki mükerrer oy sayısı',('kerrer Oylar','3')),
            ):
                matches=[row for row in rows if all(term in row for term in markers)]
                assert len(matches)==1,(suffix,len(matches))
                exact=matches[0]
                if suffix=='duplicates':
                    exact=exact[exact.index('kerrer Oylar'):]
                passages.append((suffix,section,exact,None))
    else:
        assert [pdf_page_text(root/original,n).strip() for n in range(5)]==['']*5
    for suffix, section, exact, page in passages:
        if page is None:
            assert exact in body,(key,suffix,repr(exact))
        pid=doc+'-'+suffix
        add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=section,pdf_page_index=page,printed_page=None)
        if page is not None:
            add('manual_passage',passage_id=pid,checked_at=now,
                method='Özgün PDF Poppler ile sayfa bazında görüntülendi.',
                reason='Beş tarama sayfasının metin katmanı boş. Pasaj ve bağlam gözle okundu.')
out=checks/'mekke-pension-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps({'party_id':'demokrat','entries':entries},ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0412-policy-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(sha256(out.read_bytes()).hexdigest(),len(entries),len(paths))
