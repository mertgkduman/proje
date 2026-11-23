"""Archive published evidence for two private-school teacher meetings."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage, paths_output = map(Path,sys.argv[1:])
root=Path('data/practices/sources/saadet')
now=datetime.now(timezone.utc).isoformat()
sources=(
    ('talk-june','TV5','Hümeyra Kaya','2026-06-24','journalism','journalism',
     'Arıkan’ın özel sektör öğretmenlerine ilişkin 24 Haziran konuşması',
     'https://www.tv5.com.tr/mahmut-arikan-turkiyede-aklanmanin-yeri-ak-parti-binalari-degil-mahkemelerdir',
     '6cebee384a6c1d1fe2976fa70909b0c57d359d0bfb188f2d8b351ef18ec22c9e',
     (('call','24 Haziran grup toplantısında sözü verilen görüşmeye çağrı',
       'Bakanlığın, devletin garantör olduğu, söz verilen toplantının gerçekleşmesi…'),)),
    ('talk-july','TV5','Hümeyra Kaya','2026-07-29','journalism','journalism',
     'Arıkan’ın 29 Temmuz’da özel sektör öğretmenleri toplantısına ilişkin açıklaması',
     'https://www.tv5.com.tr/mahmut-arikan-iktidarin-elinde-beklettigi-kac-dosya-var',
     'b648b0c915f53ab9dcaac08ce1f35595e78f153fd26316f75929c60b6e90830c',
     (('schedule','Arıkan’ın toplantı tarihine ilişkin beyanı',
       'Söz konusu toplantının yarın, yani 30 Temmuz 2026 Perşembe günü gerçekleştirileceği resmen bildirildi.'),
      ('target','Arıkan’ın öğretmenlerin özlük haklarına ilişkin talebi',
       'özel sektör öğretmenlerimizin hayrına, somut ve kalıcı kararlar çıkmalıdır!'))),
    ('tes','Türk Eğitim-Sen','Basın Bürosu','2026-07-30','independent_report','other',
     'Türk Eğitim-Sen’in 30 Temmuz özel okul öğretmenleri çalıştayı açıklaması',
     'https://www.turkegitimsen.org.tr/haberler/genel-baskan-yardimcimiz-irfan-kilincer-ozel-okul-ogretmenlerinin-haklari-guvence-altina-alinmalidir',
     'b625daecdf1b304a2a63be5047d35b98c208355339b2fcaaa71726ba109ccd81',
     (('day','Çalıştayın tarihi ve bakanlığın ev sahipliği',
       'Çalışma ve Sosyal Güvenlik Bakanlığı’nın ev sahipliğinde, 30 Temmuz 2026 tarihinde'),
      ('attend','Türk Eğitim-Sen’in toplantıdaki temsilcisi',
       'Çalıştaya sendikamızı temsilen Genel Başkan Yardımcımız İrfan Kılınçer katıldı.'),
      ('contract','Türk Eğitim-Sen’in sözleşme önerisi',
       'Öğretmen sözleşmeleri en az 4 yıllık yapılmalıdır.'))),
    ('sendika','Sendika Bülteni',None,'2026-07-30','journalism','journalism',
     'ANKA aktarımıyla Hüseyin Aksoy’un 30 Temmuz toplantısı açıklaması',
     'https://sendikabulteni.com/haber/ogretmenlerden-bakanlik-toplantisi-sonrasi-aciklama-talepler-icin-teknik-ekipler-kurulacak-118717',
     '17ccf027654bc0ccf1c02045f1362b771334e072065ce5b48070b25432f07104',
     (('technical','Özel Sektör Öğretmenleri Sendikası’nın çalışma grubu beyanı',
       'Talepler &uuml;zerinde konuşulması amacıyla ekipler kurulacak'),
      ('duration','Özel Sektör Öğretmenleri Sendikası’nın sözleşme talebi',
       'belirsiz s&uuml;reli s&ouml;zleşme olanaklarının konuşulmasıydı.'))),
    ('anka-aug','GazeteKalem','Batuhan Dükel','2026-08-12','journalism','journalism',
     'GazeteKalem’de ANKA kaynaklı ikinci toplantı haberi',
     'https://gazetekalem.com.tr/ozel-sektor-ogretmenlerinin-calisma-bakanligindaki-ikinci-toplantisi-tamamlandi-bakanlik-sorunun-cozulmesini-istiyor/',
     '774b681128c04ce4866126d54796aac330276d8e27848e2e6b9baf38af93ffe1',
     (('day','Haberin ilk yayın zamanı','2026-08-12T15:20:09+03:00'),
      ('result','Edebali’nin taban ücret sonucu açıklaması',
       'Şu an taban ücretin gelmediği koşullarda somut bir kazanım yok.'),
      ('next','Edebali’nin üçüncü görüşme planı açıklaması',
       'Bir sonraki toplantı iki hafta sonra planlandı.'))),
    ('patika-aug','Gazete Patika',None,'2026-08-12','journalism','journalism',
     'Gazete Patika’da Sendika.Org kaynaklı ikinci toplantı ve ücret seçenekleri',
     'https://gazetepatika.org/ozel-sektor-ogretmenleri-sendikasindan-bakanlik-gorusmesi-sonrasi-aciklama-181653',
     '2f886c2a6501927f70b475e31764390ae3b3750d34ac715e73cde445bd5b9126',
     (('roles','İkinci toplantıda bildirilen katılımcılar',
       'Toplantıya Özel Sektör Öğretmenleri Sendikası, işveren dernekleri, TOBB Eğitim Meclisi ve ilgili bakanlıkların temsilcilikleri katıldı.'),
      ('agenda','Sendika.Org kaynaklı gündem atfı',
       'toplantının ana gündemi taban ücret ve çözüm formülleri oldu.'))),
)
entries=[]
written=set()

def add(table,**values):
    entries.append(dict(kind=table,values=values))

def archive(path,body):
    dest=root/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.is_file():
        assert dest.read_bytes()==body
    else:
        dest.write_bytes(body)
    written.add(str(dest))

for key,publisher,author,published,source_kind,attribution_kind,title,url,digest,passages in sources:
    path=stage/f'teacher-{key}.html'
    raw=path.read_bytes()
    body=html_source_text(raw)
    assert sha256(raw).hexdigest()==digest
    doc=f'0411-teacher-{key}'
    vid=doc+'-v1'
    original=Path('objects')/digest/'original.html.bin'
    readable=original.parent/'readable.html'
    archive(original,raw)
    archive(readable,readable_bytes(raw,'html',legacy=False))
    add('document',id=doc,party_id='saadet',title=title,source_kind=source_kind)
    add('document_version',id=vid,document_id=doc,original_url=url,final_url=url,document_date=published[:10],
        date_precision='day',date_unknown_reason=None,version_label='Yayının erişilen özgün HTML sürümü.',
        accessed_at=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,
        mime='text/html',sha256=digest,original_path=str(original),readable_path=str(readable))
    add('source_attribution',version_id=vid,publisher=publisher,author=author,kind=attribution_kind,
        published_at=published[:10],date_precision='day',social_handle=None,public_url=url,
        basis='Yayın adı ve zaman bilgisi özgün sayfada. Yazar adı mevcutsa yayındaki atıf kullanıldı.')
    view=build_view(raw,url,root,fetch_assets=False)
    view['version_id']=vid
    validate_view(root,view)
    add('archive_view',**view)
    manifest=root/view['manifest_path']
    written.add(str(manifest))
    written.update(str(manifest.parent/key) for key in json.loads(manifest.read_bytes())['files'])
    for name,heading,exact in passages:
        assert exact in body,(key,name,exact)
        add('passage',id=doc+'-'+name,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,
            section=heading,pdf_page_index=None,printed_page=None)
with (checks/'private-teacher-meetings-source-records.json').open('x') as stream:
    stream.write(json.dumps(dict(party_id='saadet',entries=entries),ensure_ascii=False,indent=2)+'\n')
paths_output.write_text('\n'.join(sorted(written))+'\n')
print(len(entries),len(written))
