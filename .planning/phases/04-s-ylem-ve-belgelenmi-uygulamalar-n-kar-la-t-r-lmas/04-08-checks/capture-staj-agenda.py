"""Archive the original 2/3778 and 10/4625 parliamentary records."""

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
    ('offer.pdf','bill','2/3778 imzalı kanun teklifi','2026-07-21',None,'TBMM','official',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/8b1600fe-37df-480e-a2e0-37b9093887dd.pdf',
     '2eabfcb1f840e9ae60bc09377f7ce56821d0df3e149a068b925756a3798ad3ba',[
         ('identity','İmzalı kapakta Selçuk Özdağ ve grup görevi',0,'Doç. Dr. Selçuk Özdağ\nMuğla Milletvekili\nGrup Başkanvekili'),
         ('stamp','İmzalı kapakta esas no ve komisyon işlem kutusu',0,'Tarih: 22-7-2026 Esas No:2/3778'),
         ('bill-date','İkinci sayfadaki TBMM evrak kaşesi',1,'21 Temmuz 2026'),
         ('target','Teklif gerekçesinde uzun vadeli sigorta ve geçmiş süreler',2,'geçmişte geçen çıraklık, staj ve eğitim sürelerinin sigorta başlangıcında değerlendirilmesine imkân verilmektedir.'),
         ('options','Madde gerekçeleri, başvuru ile sigorta ve borçlanma',3,'çıraklık, staj ve eğitim sürelerinin borçlanılabilecek süreler arasına eklenmesi'),
         ('window','Madde 4, istem ve geriye dönük borçlanma',4,'3 ay içinde talepte bulunmaları ve geriye doğru borçlanmaları hâlinde, sigorta başlangıç tarihinin hesaplanmasında dikkate alınır.'),
     ]),
    ('offer.html','bill-register','2/3778 TBMM esas dosyası',None,None,'TBMM','official',
     'https://tbmm.gov.tr/Yasama/KanunTeklifi/feedea6f-fa38-47cf-a2b9-019f85314930',
     '6822ef88f53262d12176ada6085e6f341efd94eb8df21dbed31746ba425dab31',[
         ('id','Esas no',None,'<td>2 / 3778</td>'),
         ('filed','21 Temmuz başvuru',None,'<td>21/07/2026</td>'),
         ('commission','22 Temmuz komisyon girişi',None,'<td>22/07/2026</td>'),
         ('pending','Komisyon işlem durumu',None,'<td>Komisyonda</td>'),
         ('owner','Özdağ’ın ilk imza ve Yeni Yol aidiyeti',None,
          'Sel&#xE7;uk &#xD6;ZDA&#x11E;\n\n                                            </a>\n                                        </td>\n                                        <td>YEN&#x130; YOL PART&#x130;S&#x130;</td>'),
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
         ('role','Elif Esen’in birleşimdeki Yeni Yol Grup sıfatı',None,
          None),
         ('supports','Elif Esen’in Yeni Yol Grubu adına gündem önerisine açık desteği',None,
          'emeklilik mağduriyetinin araştırılmasına ilişkin vermiş olduğu öneriyi YENİ YOL Grubu olarak elbette destekliyoruz.'),
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
    doc='0408-staj-agenda-'+key
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
        if key == 'floor' and suffix == 'role':
            role = 'YENİ YOL GRUBU ADINA ELİF ESEN (İstanbul)'
            end = text.index(role)+len(role)
            begin = text.rfind('Elif Esen.',0,end)
            assert begin >= 0
            exact = text[begin:end]
            assert len(exact) < 1500
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
(checks/'staj-agenda-source-records.json').write_text(json.dumps(dict(party_id='yeni-yol',entries=entries),ensure_ascii=False,indent=2)+'\n')
(stage/'agenda-source-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries),len(paths))
