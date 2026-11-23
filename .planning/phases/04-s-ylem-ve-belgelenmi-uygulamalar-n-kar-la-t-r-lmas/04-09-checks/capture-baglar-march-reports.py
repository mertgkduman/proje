"""Bind Bağlar referral and report decisions to their exact council pages."""

import json
from pathlib import Path
import sys

from arsiv import pdf_page_text

here=Path(sys.argv[1])
original=Path('data/practices/sources/dbp/objects/6059362c11b4a6e867ec207394929002475c1b5d0cec6ee142a8eb65e61dccd3/original.pdf')
version='0409-cemr-baglar-v1'
cases={
    '42': (46,'05/02/2015',(
        ('step','Fatih Mahallesi önergesinin komisyona sevki','Halkla ĠliĢkiler Komisyonuna havale'),
    )),
    '43': (47,'06/02/2015',(
        ('step','Kaynartepe fırınlarının incelenmesi önerisi','bulunan Kaynartepe Mahallesindeki Fırınların\nDenetlenmesine'),
    )),
    '51': (55,'04/03/2015',(
        ('budget','Fen İşleri 2014 ödeneği ve dönemi','bütçenin 18.420.000.00 TL olduğu'),
        ('spending','Harcama ve iade toplamı',
         'Toplam 2014 yılı içerisinde 14.060.244,50 TL harcanmıĢ olup, 4.359.755,50 TL\'si ise iade'),
        ('approved','Fen İşleri raporunun mecliste kabulü','verildi.04/03/2015'),
    )),
    '52': (56,'04/03/2015',(
        ('proposal','Komisyon raporuna geçen kız öğrenci eğitimi önerisi',
         'eğitimciler öğrenci kız çocuklarına sağlık ve psikolojik eğitiminin verilmesinin çok yararlı'),
        ('approved','Kadın Sorunlarını Araştırma Komisyonu raporunun kabulü','verildi.04/03/2015'),
    )),
    '54': (58,'04/03/2015',(
        ('reported','Görüşülen çalışanların ev ve çocuk bakımı anlatımı',
         'gidip ev iĢleriyle çocuklarla uğraĢtıkları için erkekler gibi sosyal bir faaliyetlerinin olmadığını'),
        ('proposal','Çalışanların kurum içi sosyal etkinlik önerisi',
         'Kurum içinde bazen sosyal etkinlik yapılması için öneride bulundular.'),
        ('approved','Kadın-Erkek Eşitlik Komisyonu raporunun kabulü','verildi.04/03/2015'),
    )),
    '56': (60,'05/03/2015',(
        ('service','Fatih Mahallesi konteyner ve kaldırım talepleri',
         'Mahalle sakinlerinin acil olarak çöp konteyneri, ihtiyaçlarının\nolduklarını, kaldırımların düzenli bir Ģekilde esnaf iĢgalinden temizlenmesi.'),
        ('approved','Fatih Mahallesi raporunun mecliste kabulü','verildi.05/03/2015'),
    )),
    '57': (61,'05/03/2015',(
        ('inspection','Kaynartepe fırınlarına yönelik inceleme başlığı',
         'Kaynartepe Mahallesindeki fırınların denetlenmesi'),
        ('fine','Eksik gramaja ilişkin bildirilen işlem',
         'ekmekler eksik gramajdan dolayı cezai iĢlem\nuygulandı.'),
        ('warning','Komisyon raporunda yer alan uyarı örneği',
         'temizliğin yetersiz olduğu tarafımızdan tespit edilerek uyarı yapılmıĢtır.'),
        ('administrative','Komisyon raporunda yer alan idari yaptırım tutanağı',
         'idari yaptırım\ntutanağı düzenlendi.'),
        ('approved','Denetim raporunun mecliste kabulü','verildi.05/03/2015'),
    )),
    '58': (62,'05/03/2015',(
        ('transit','Esnafın caddenin trafiğe kapalı kalması talebi',
         'Sakarya caddesi trafiğe kapalı olmasını araç giriĢ çıkıĢlarının olmamasını'),
        ('light','Esnafın aydınlatma talebi',
         'Sokağın saat 17:00 dan sonra karanlık olduğunu ıĢıklandırılmasını istiyorlar.'),
        ('approved','İnceleme ve Araştırma Komisyonu raporunun kabulü','verildi.05/03/2015'),
    )),
}
rows=[]
for number,(index,day,anchors) in cases.items():
    text=pdf_page_text(original,index)
    refs=(('file','Belediye meclisi karar numarası',f'2015/{number}'),('date','Belediye meclisi karar tarihi',day),*anchors)
    for label,heading,exact in refs:
        assert exact in text,(number,label,exact)
        rows.append(dict(kind='passage',values=dict(id=f'0409-baglar-march-reports-{number}-{label}',
            version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=heading,
            pdf_page_index=index,printed_page=None)))
for number,index,section,exact in (
    ('26',28,'2015/26 Fen İşleri harcama incelemesinin komisyona sevki','2015/26'),
    ('29',31,'2015/29 kadın çalışanların sorunlarına ilişkin komisyon sevki','2015/29'),
    ('31',33,'2015/31 ana hizmet binasında cinsiyet eşitliği komisyon sevki','2015/31'),
    ('47',51,'2015/47 Sakarya Caddesi için iki komisyona sevk','2015/47'),
):
    assert exact in pdf_page_text(original,index),(number,index)
    rows.append(dict(kind='passage',values=dict(id=f'0409-baglar-march-reports-{number}-referral',
        version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,
        pdf_page_index=index,printed_page=None)))
out=here/'baglar-march-reports-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps(dict(party_id='dbp',entries=rows),ensure_ascii=False,indent=2)+'\n')
print(len(rows),'passages')
