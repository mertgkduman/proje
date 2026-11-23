"""Bind seven February Bağlar decisions to the published council pages."""

import json
from pathlib import Path
import sys

from arsiv import pdf_page_text

here=Path(sys.argv[1])
original=Path('data/practices/sources/dbp/objects/6059362c11b4a6e867ec207394929002475c1b5d0cec6ee142a8eb65e61dccd3/original.pdf')
version='0409-cemr-baglar-v1'
cases={
    '32': (34,'03/02/2015',(
        ('action','Glutensiz gıda desteği kişi sayısı ve süresi','40 kiĢiye toplam 6 aylık glutensiz gıda'),
        ('approved','Gıda desteği oylaması','birliği ile kabulüne karar verildi.03/02/2015'),
    )),
    '35': (39,'04/02/2015',(
        ('action','5 Nisan Mahallesi sakini talepleri','Mahalle sakinlerinin acil olarak çöp konteyneri'),
        ('approved','Mahalle sorunları raporunun kabulü','verildi.04/02/2015'),
    )),
    '36': (40,'04/02/2015',(
        ('action','Kursların protokol kapsamında düzenlenmesi','Yapılan Protokol gereği Eğitim Destek Evi, Kardelen Kadın Evi'),
        ('centers','Kursların bildirilen Eğitim Destek Evi katılımcıları','Bilgisayar 16 kiĢi, Halk oyunları 16 kiĢi ve Resim Kursunda 15 kiĢi'),
        ('approved','Ortak kurs raporunun kabulü','verildi.04/02/2015'),
    )),
    '37': (41,'04/02/2015',(
        ('action','Pazar raporunda mahalle sakinlerinin görüşü','kesinlikle Cuma pazarının kaldırılmasını istemiyor.'),
        ('hygiene','Pazar gıda hijyeni hakkında bildirilen kaygı','sakatat ürünlerinin hijyenik olmadığı ve halkın sağlığını tehdit ettiği.'),
        ('approved','Çevre ve Sağlık Komisyonu raporunun kabulü','verildi.04/02/2015'),
    )),
    '39': (43,'05/02/2015',(
        ('action','Semt pazarlarına küçük kamyonet önerisi','küçük kamyonetlerin gelmesinin daha uygun olacağını'),
        ('towing','Pazarda araç çekicisi istemi','araba\nçekicisi istenmiĢtir.'),
        ('approved','İnceleme ve Araştırma Komisyonu raporunun kabulü','verildi.05/02/2015'),
    )),
    '40': (44,'05/02/2015',(
        ('action','Suruç Belediyesine çöp aracının hibe önerisi','hacimli çöp sıkıĢtırma aracının Suruç Belediyesine hibe edilmesi'),
        ('approved','Hibe kararının kabulü','kabulüne karar verildi.05/02/2015'),
    )),
    '41': (45,'05/02/2015',(
        ('action','Yenişehir çadır alanına ilişkin elektrik gideri','Elektrik abonelerinin aylık giderlerinin'),
        ('authority','Bağlar belediye başkanına ödeme ve yardım yetkisi','Belediye BaĢkanımız Birsen KAYA AKAT‟ a Yetki Verilmesine'),
        ('approved','Yetki kararının kabulü','kabulüne karar\nverildi. 05/02/2015'),
    )),
}
rows=[]
for number,(index,day,anchors) in cases.items():
    text=pdf_page_text(original,index)
    refs=(('file','Belediye meclisi karar numarası',f'2015/{number}'),('date','Belediye meclisi karar tarihi',day),*anchors)
    for label,heading,exact in refs:
        assert exact in text,(number,label,exact)
        rows.append(dict(kind='passage',values=dict(id=f'0409-baglar-february-{number}-{label}',
            version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=heading,
            pdf_page_index=index,printed_page=None)))
out=here/'baglar-february-source-records.json'
with out.open('x') as stream:
    stream.write(json.dumps(dict(party_id='dbp',entries=rows),ensure_ascii=False,indent=2)+'\n')
print(len(rows),'passages')
