"""Bind seven read council decisions to the existing native PDF version."""

import json
from pathlib import Path
import sys

from arsiv import pdf_page_text

here = Path(sys.argv[1])
original = Path('data/practices/sources/dbp/objects/6059362c11b4a6e867ec207394929002475c1b5d0cec6ee142a8eb65e61dccd3/original.pdf')
version = '0409-cemr-baglar-v1'
records = {
    '11': (10, '06/01/2015', '8 geçici işçi için çalışma vizesi', (
        ('positions', 10, 'Geçici işçi vizesi gereği', 'çalıĢtırılabilmesi için geçici iĢ pozisyon vizesi alınması gerekmektedir.'),
        ('table', 11, 'Geçici iş vizesi eki', '96 ADAM/AY'),
        ('approved', 10, 'Vize kararı sonucu', 'kabulüne karar verildi.06/01/2015'),
    )),
    '15': (15, '07/01/2015', 'Aralık nakdi yardım raporunun sunulması', (
        ('people', 15, '2014 nakdi yardım kişi sayısı', 'sosyal güvencesi olmayan, yaĢlı, dul ve herhangi bir geliri olmayan 367 kiĢiye toplam'),
        ('amount', 15, '2014 nakdi yardım bildirilen tutar', '125.050,00 TL. Nakdi yardımın yapıldığı tespit edilmiĢtir.'),
        ('approved', 15, 'Nakdi yardım raporunun sonucu', 'verildi.07/01/2015'),
    )),
    '17': (17, '08/01/2015', 'Kadın Sorunlarını Araştırma Komisyonu raporu', (
        ('review', 17, 'Şeyhşamil muhtar görüşmesi', 'muhtarı ile yapılan görüĢmede mahallelerinde oturan vatandaĢların bir çoğunun, nakdi yardım'),
        ('needs', 17, 'Muhtarlık görüşmesinde yardım talebi', 've havaların soğuk olduğundan dolayı yakacak yardımı talep ettiler. Parklarda uyuĢturucu'),
        ('approved', 17, 'Komisyon raporunun mecliste kabulü', 'verildi.08/01/2015'),
    )),
    '18': (18, '08/01/2015', 'Nevroz Parkı eşitlik raporu', (
        ('review', 18, 'Nevroz Parkı’nın eşitlik yönünden incelenmesi', 'Bağcılar Mahallesinde bulunan Nevroz Parkının cinsiyet eĢitliğine uygun çalıĢmalarının'),
        ('needs', 18, 'Kullanıcıların temizlik ve kullanım talepleri', 'Güvenlikçi sayısının yeterli olmadığını. Emzirme odasının olmadığı.Namaz kılmak'),
        ('channel', 18, 'Park kanalına ilişkin kullanıcı önerileri', 'için mescit talep ettiler. Parkta geçen kanalın üstünün kapatılması veya etrafına korkulukların'),
        ('approved', 18, 'Park raporunun meclisçe kabulü', 'verildi.08/01/2015'),
    )),
    '19': (19, '08/01/2015', 'Eğitim Destek Evi ihtiyaç raporu', (
        ('purpose', 19, 'Yeni dönem için eğitim ihtiyaç tespiti', 'Sosyal ĠĢler Müdürlüğüne bağlı Eğitim Destek Evine yeni dönemle ilgili ihtiyaçların tespit'),
        ('amount', 19, 'Sınav alımı tutarı ve kırtasiye ihtiyacı', 'Test ve Deneme sınavları alımına 11.000 TL ayrıca Kobanili 100\nçocuğa kırtasiye ihtiyacı'),
        ('approved', 19, 'Eğitim Destek Evi raporunun kabulü', 'verildi.08/01/2015'),
    )),
    '21': (21, '08/01/2015', 'Şeyhşamil sokak bakım raporu', (
        ('purpose', 21, 'Mahalle sakinlerinin sorunlarının dinlenmesi', 'ġeyhĢamil Mahallesindeki vatandaĢların sorunlarının dinlenilmesi'),
        ('repairs', 21, 'Şeyhşamil asfalt ve kaldırım onarımı', 'belirlenen sokaklarda asfalt onarımı ve kaldırım\nonarımları yapılacaktır.'),
        ('approved', 21, 'Sokak bakım raporunun kabulü', 'verildi.08/01/2015'),
    )),
    '232': (238, '06/11/2015', 'Kadın basketbol takımı faaliyetleri araştırma kararı', (
        ('subject', 238, 'Belediye takımının araştırılması', 'Kadın Basketbol Takımının çalıĢamlarının araĢtırılıp, incelenmesi'),
        ('committee', 238, 'Gençlik ve Spor Komisyonuna havale', 'söz konusu önergenin Gençlik ve Spor\nKomisyonuna havale edilerek, raporlanması'),
        ('approved', 238, 'Kadın basketbolu hakkındaki sevk oylaması', 'kabulüne karar\nverildi. 06/11/2015'),
    )),
}
pages = {}
rows = []
for number,(index,day,title,anchors) in records.items():
    anchors = (('file',index,title,f'2015/{number}'),('day',index,title+' tarihi',day),*anchors)
    for label,page,section,quote in anchors:
        if page not in pages:
            pages[page] = pdf_page_text(original,page)
        assert quote in pages[page], (number,label,quote)
        row = dict(id=f'0409-baglar-services-{number}-{label}',version_id=version,exact=quote,
                   prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)
        rows.append(dict(kind='passage',values=row))
with (here/'baglar-services-source-records.json').open('x') as out:
    out.write(json.dumps(dict(party_id='dbp',entries=rows),ensure_ascii=False,indent=2)+'\n')
print(len(rows))
