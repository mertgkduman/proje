"""Archive the 2/1019 proposal and 10/4625 preliminary agenda documents."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path,sys.argv[1:])
root = Path('data/practices/sources/iyi')
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
    ('1019.pdf','1019-signed','2/1019 imzalı kanun teklifi','2018-09-17',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y2/T2/WebOnergeMetni/64aeaeb2-4616-4fc7-a9db-e55a2d8e33e9.pdf',
     '4b8b3b052340a6c3237da8ab1df789534b9b58d341054d4e2038f6d3a699cbe3',[
         ('signature','İmzalı teklif yazısının tarihi',0,'Gereğini saygılarımla arz ederim. 17.09.2018'),
         ('stamp','Gelen evrak kaşesinin tarihi',1,'17 Eylül 2018'),
         ('goal','Madde gerekçesinde borçlanma ve sigorta başlangıcı',2,
          'sigortalılık başlangıç tarihinin uzun vadeli sigorta kolları uygulamasında da çırak olarak çalışmaya veya staja başlanılan tarih olarak esas alınması öngörülmektedir.'),
         ('clause','Madde 1, yeni bent ve başlangıç tarihi',4,
          'başlangıç tarihi, stajın veya çıraklığın başladığı tarihtir.'),
     ]),
    ('1019-detail.html','1019-detail','2/1019 TBMM kanun teklifi dosyası',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/KanunTeklifi/f72877c0-b436-037b-e050-007f01005610',
     '75ba8c182be398538b11421c5ce1cdcaa52d0f273b0426113764b27b29b80ddd',[
         ('filed','Başkanlığa geliş 17 Eylül',None,'<td>17/09/2018</td>'),
         ('committee','Komisyon giriş tarihi 15 Ekim',None,'<td>15/10/2018</td>'),
         ('status','TBMM esas kaydında hükümsüzlük',None,'<td>H&#xDC;K&#xDC;MS&#xDC;Z (G)</td>'),
         ('ergun','İlk imza sahibi Metin Ergun ve parti',None,
          'Metin ERGUN\n\n                                            </a>\n                                        </td>\n                                        <td>&#x130;Y&#x130; PART&#x130;</td>'),
         ('turkkan','İlk imza sahibi Lütfü Türkkan ve parti',None,
          'L&#xFC;tf&#xFC; T&#xDC;RKKAN\n\n                                            </a>\n                                        </td>\n                                        <td>&#x130;Y&#x130; PART&#x130;</td>'),
     ]),
    ('1019-oct.pdf','1019-oct','16 Ekim 2018 birleşim tutanağında 2/1019','2018-10-16',None,'TBMM','official',
     'https://www5.tbmm.gov.tr/tutanaklar/TUTANAK/TBMM/d27/c003/tbmm27003007.pdf',
     '516171b6cdf3e1fd6c227537a9a967ecccd891aea03dfaaced51ae74b7b35222',[
         ('conflict','48. sıradaki teklif kaydının farklı geliş tarihi',30,
          'Kanun Teklifi (2/1019) (Milli Eğitim, Kültür, Gençlik ve Spor; Sağlık, Aile, Çalışma ve Sosyal İşler ile\nPlan ve Bütçe Komisyonlarına) (Başkanlığa geliş tarihi: 14.09.2018)'),
     ]),
    ('1019-end.pdf','1019-end','28. dönemin ilk tutanağında hükümsüz teklifler','2023-06-02',None,'TBMM','official',
     'https://www5.tbmm.gov.tr/tutanaklar/TUTANAK/TBMM/d28/c001/tbmm28001001.pdf',
     'ba2883e38fed0a4a930fb66c3d51b7e72248196ebffb8df52e6688fef57a75ed',[
         ('listing','Hükümsüz sayılan teklifler sıra 1013',87,
          '1013 2/1019 Sosyal Sigortalar ve Genel Sağlık Sigortası Kanununda Değişiklik Yapılması Hakkında Kanun\nTeklifi (Muğla Milletvekili Metin Ergun, İYİ Parti Grup Başkanvekili Kocaeli Milletvekili\nLütfü Türkkan)'),
     ]),
    ('inquiry.pdf','inquiry','10/4625 imzalı Meclis araştırması önergesi','2026-10-07',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T10/WebOnergeMetni/a3dbf238-6114-4857-b432-43f0639d7236.pdf',
     '0589a046ca4e2916e39d0a60ad7e0ee32dd3960adc08547a5862446d10a43fb3',[
         ('id','İmzalı kapaktaki esas no',0,'10/4625'),
         ('models','Gerekçede SGK üzerindeki mali etkilerin araştırılması',2,'farklı modellerin Sosyal Güvenlik Kurumu üzerindeki mali etkilerinin'),
     ]),
    ('inquiry.html','inquiry-register','10/4625 TBMM esas dosyası',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/bfbc23a8-bc6c-4c9b-bcb5-01a11b3356f9',
     '4261abc0b3626501ef6d67b754fa290ad97f2093ff13afc4a1fc88f49c66f72a',[
         ('filed','8 Ekim TBMM giriş günü',None,'<td>08/10/2026</td>'),
         ('pending','Esas kaydında gündem durumu',None,'<td>G&#xFC;ndemde</td>'),
     ]),
    ('8-ham.html','floor','20 Ekim TBMM 8. Birleşim tam tutanağı','2026-10-20',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/8/Ham/dcb831f7-1664-48cd-8209-d84d460415f8.html',
     'a1a7038f7af34b3ca15ec0f5603d19b41b7df64468ec04160234c4752377c522',[
         ('call','CHP’nin staj ve çıraklık araştırmasını gündeme alma talebi',None,
          'tüm boyutlarıyla araştırılması amacıyla 7/10/2026 tarihinde Türkiye Büyük Millet Meclisi Başkanlığına verilmiş olan Meclis araştırması önergesinin ön görüşmelerinin, Genel Kurulun 20 Ekim 2026 Salı günkü birleşiminde yapılmasına ilişkin önerisi'),
         ('role','Metin Ergun’un İYİ Parti Grubu sıfatı',None,
          'İYİ PARTİ GRUBU ADINA METİN ERGUN (Muğla)'),
         ('supports','Metin Ergun’un İYİ Parti Grup desteği',None,
          'İYİ PARTİ olarak önergeyi desteklediğimizi ifade ediyor'),
         ('models','Ergun’un sigorta başlangıcı ve borçlanma önerisi',None,
          'staj ve çıraklık başlangıçlarının sigortalılık başlangıcı sayılması, geçmiş dönemler için borçlanma'),
         ('earlier','Ergun’un 2018 teklifine atfı',None,
          'Ben 2018 yılında bir kanun teklifi verdim bu mağduriyetin giderilmesi konusunda.'),
         ('decision','CHP grup önerisinin oylaması ve DEM gündemine geçiş',None,None),
     ]),
    ('8-ozet.html','summary','20 Ekim TBMM 8. Birleşim özeti','2026-10-20',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/8/Ozet/b5c1e670-7316-45f7-ac6a-eae635f303f7.html',
     'f226aa87837ec696421a928c409564229aa31ca81579f45d9eb37e2318564e73',[
         ('call','Özette 7 Ekim tarihli staj araştırması',None,
          'CHP Grubunun, 7/10/2026 tarihinde Ankara Milletvekili Semra Dinçer ve arkadaşları tarafından'),
         ('decision','Özette aynı gün görüşülmesi taleplerinin sonucu',None,
          'Görüşmelerinin Genel Kurulun 20 Ekim 2026 Salı günkü birleşiminde yapılmasına ilişkin önerileri yapılan görüşmelerden sonra kabul edilmedi.'),
     ]),
)
for filename,key,title,date,published,publisher,kind,url,digest,anchors in sources:
    path=stage/filename
    raw=path.read_bytes()
    assert sha256(raw).hexdigest()==digest
    pdf=filename.endswith('.pdf')
    if pdf:
        assert raw.startswith(b'%PDF-')
    doc='0407-ergun-staj-'+key
    vid=doc+'-v1'
    obj=f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable=f'objects/{digest}/readable.html'
    store(obj,raw)
    store(readable,readable_bytes(raw,'pdf' if pdf else 'html',legacy=False))
    add('document',id=doc,party_id='iyi',title=title,source_kind=kind)
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
        if key == 'floor' and suffix == 'role':
            end = text.index(exact)+len(exact)
            start = text.rfind('İYİ Parti Grubu adına Muğla Milletvekili Metin Ergun.',0,end)
            assert 0 <= start < end and end-start < 1500
            exact = text[start:end]
        if exact is None:
            marker = "Halkların Eşitlik ve Demokrasi Partisi Grubu adına İç Tüzük"
            begin = text.rfind("Öneri kabul edilmemiştir.", 0, text.index(marker))
            assert begin >= 0
            exact = text[begin:text.index(marker)+len(marker)]
            assert len(exact) < 900
        manual = pdf and not text.strip()
        assert manual or exact in text, (key, suffix)
        add('passage',id=doc+'-'+suffix,version_id=vid,exact=exact,prefix=None,suffix=None,
            article=None,section=section,pdf_page_index=index,printed_page=None)
        if manual:
            add('manual_passage',passage_id=doc+'-'+suffix,checked_at=now,
                method='Özgün PDF sayfası Poppler görüntüsünden okundu.',
                reason='Metin katmanı bulunmayan özgün sayfada ilgili ifade görsel olarak okundu.')
(checks/'ergun-staj-source-records.json').write_text(json.dumps(dict(party_id='iyi',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'ergun-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
