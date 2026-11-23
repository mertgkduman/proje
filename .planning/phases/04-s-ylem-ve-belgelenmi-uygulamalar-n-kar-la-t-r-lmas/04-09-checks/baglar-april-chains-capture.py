from pathlib import Path
import json,sys
sys.path.insert(0,'src')
from arsiv import pdf_page_text
here=Path(__file__).parent;pdf=Path('data/practices/sources/dbp/objects/6059362c11b4a6e867ec207394929002475c1b5d0cec6ee142a8eb65e61dccd3/original.pdf');version='0409-cemr-baglar-v1';prefix='0409-baglar-april-chains-';rows=[]
anchors={
 '46':[(50,'file','2015/46','2015/46 sevk kararı'),(50,'topic','Yapı Kontrol','Yapı kontrol çalışmalarının incelenmesi')],
 '61':[(65,'file','2015/61','2015/61 sevk kararı'),(65,'topic','Sakarya Caddesindeki Kadın','Sakarya Caddesinde kadınların sorunları')],
 '66':[(70,'file','2015/66','2015/66 sevk kararı'),(70,'date-head','06/03/2015','Üstte yazılı karar tarihi'),(70,'date-end','06/03/2014','Karar sonunda yazılı farklı tarih'),(70,'parcel','4209 ada,4 nolu','4209 ada 4 parsel incelemesi')],
 '82':[(86,'file','2015/82','2015/82 imar raporu'),(86,'request','4209 ada 4 nolu','Aynı taşınmaz hakkında komisyon raporu'),(86,'plan','plan notlarına','İki imar planı notu talebi'),(87,'approved','verildi.08/04/2015','Raporun mecliste kabulü')],
 '83':[(87,'file','2015/83','2015/83 yapı kontrol raporu'),(87,'period','30.03.2014 ile 31.12.2014','Rapor edilen inceleme dönemi'),(87,'demolition','2 inĢaat yıkımı gerçekleĢtirilmiĢtir.','Komisyonun iki yıkım bildirimi'),(87,'fine','1.353.551,71 TL. para cezası kesilmiĢtir.','Komisyonun kesilen ceza bildirimi'),(88,'approved','verildi.09/04/2015','Yapı kontrol raporunun mecliste kabulü')],
 '84':[(88,'file','2015/84','2015/84 kadın görüşmeleri raporu'),(88,'request','tam teĢeküllü hijyenik tuvalet','Görüşülen kadınların tuvalet talebi'),(88,'approved','verildi.09/04/2015','Kadın sorunları raporunun mecliste kabulü')],
 '81':[(85,'file','2015/81','2015/81 yardım kararı'),(85,'amount','10.000,00 TL.Para yardımı','Halfeti için para yardımı kararı'),(85,'conflict','reddine karĢılık mevcudun oy birliği ile kabulüne karar verildi.','Aynı cümlede ret ve oybirliği ifadeleri'),(85,'reject','reddine karĢılık','Ret beyanı'),(85,'unanimous','mevcudun oy birliği ile kabulüne','Oybirliği ifadesi')]
}
for number,parts in anchors.items():
 for index,label,exact,section in parts:
  assert exact in pdf_page_text(pdf,index),(number,label,exact)
  rows.append(dict(kind='passage',values=dict(id=prefix+number+'-'+label,version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=index,printed_page=None)))
(here/'baglar-april-chains-source-records.json').write_text(json.dumps(dict(party_id='dbp',entries=rows),ensure_ascii=False,indent=2)+'\n');print('APRIL_CHAINS_CAPTURE',len(rows))
