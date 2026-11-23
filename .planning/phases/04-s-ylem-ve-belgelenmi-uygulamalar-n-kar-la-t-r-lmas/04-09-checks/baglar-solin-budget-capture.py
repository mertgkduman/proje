from pathlib import Path
import json,sys
sys.path.insert(0,'src')
from arsiv import pdf_page_text
here=Path(__file__).parent
pdf=Path('data/practices/sources/dbp/objects/6059362c11b4a6e867ec207394929002475c1b5d0cec6ee142a8eb65e61dccd3/original.pdf')
anchors={
 '139':[(144,'file','2015/139','Yazı İşleri 2014 hesabı sevk kararı'),(144,'topic','Müdürlüğüne 2014 yılında ayrılan Bütçe','Yazı İşleri bütçe kalemleri incelemesi')],
 '140':[(145,'file','2015/140','Solin yaz çalışmalarının sevk kararı'),(145,'topic','Çocuk Evinde yaz döneminde yapılan çalıĢmaların','Solin yaz dönemi araştırması')],
 '167':[(172,'file','2015/167','Yazı İşleri komisyon raporu'),(172,'sum','166.794,22 TL harcanmıĢ olup, 228.205,78 TL','Yazı İşleri raporunda harcama ve iade'),(172,'approved','verildi.08/09/2015','Yazı İşleri raporunun kabulü')],
 '171':[(176,'file','2015/171','Solin komisyon raporu'),(176,'children','2015 yazında ay bazında 400 çocuğun yüzme havuzundan','Komisyonun aylık çocuk sayısı beyanı'),(176,'women','kadın da yüzme havuzundan faydalanmıĢtır.','Komisyonun o zamana kadarki kadın sayısı beyanı'),(177,'approved','verildi.09/09/2015','Solin raporunun kabulü')],
 '184':[(189,'file','2015/184','İnsan Kaynakları hesabının sevki')],
 '210':[(215,'file','2015/210','İnsan Kaynakları raporu'),(215,'budget','5.890.000.00 TL','Komisyonun belirttiği 2014 bütçe'),(216,'amount','3.056.099,55 TL harcanmıĢ olup, 669.900,45 TL','Komisyonun harcama ve iade tutarı'),(216,'approved','verildi.03/11/2015','İnsan Kaynakları raporunun kabulü')],
 '256':[(262,'file','2015/256','2015 gelir gider araştırması sevki'),(262,'topic','2015 yılına ait Gelir ve','2015 yılı gelir ve gider araştırması')]
}
rows=[]
for number,parts in anchors.items():
 for index,label,exact,section in parts:
  assert exact in pdf_page_text(pdf,index),(number,index,exact)
  rows.append(dict(kind='passage',values=dict(id='0409-baglar-solin-budget-'+number+'-'+label,version_id='0409-cemr-baglar-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=index,printed_page=None)))
(here/'baglar-solin-budget-source-records.json').write_text(json.dumps(dict(party_id='dbp',entries=rows),ensure_ascii=False,indent=2)+'\n')
print('CAPTURE',len(rows))

