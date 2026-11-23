from pathlib import Path
from hashlib import sha256
from decimal import Decimal
import json,sys

here=Path(sys.argv[1])
template=(here/'baglar-may-chains-prepare.py').read_text()
head=template[:template.index("assert party=='dbp'")]
head=head.replace("baglar-may-chains-source-records.json","baglar-solin-budget-source-records.json").replace("read(here/'baglar-april-chains-draft.json')","read(data/'practices/04-dbp.json')").replace("read(here/'baglar-april-chains-review-draft.json')","read(data/'practices/04-dbp-review.json')").replace("baglar-may-chains-reading-","baglar-solin-budget-reading-")
exec(head,globals())
assert sha256((data/'practices/04-dbp.json').read_bytes()).hexdigest()=='5d172f30e1a432d55ffb67695863c771c6aac5f64815cc92b05a83027494d507'
assert sha256((data/'practices/04-dbp-review.json').read_bytes()).hexdigest()=='df09db117506d05fbfcfaa1a779e15e1a5071bfa44c1b6dc8bf57e68b44a9c75'
values=list(map(Decimal,'913260.52 1575907.20 85658.43 28029.24 28059.19 27610 217176.61 322.33 133428.70 3386 216 733.50 3156.12 35062.47 1392.40 2700.84'.split()))
assert sum(values)==Decimal('3056099.55')
assert Decimal('5890000')-Decimal('3056099.55')-Decimal('669900.45')==Decimal('2164000')
assert Decimal('395000')==Decimal('166794.22')+Decimal('228205.78')
prefix='0409-baglar-solin-budget-'
electoral=['0409-siginak-ysk-district-name','0409-siginak-ysk-district-party']
base='İşlem belediye meclisine ait; YSK 2014 seçim bağlamını verir. Parti organı kararı, kişisel oylar ve ilk kayıtlar açık.'
cases=[
('139','2015-07-09','kamu-hesap-verebilirlik','Yazı İşleri bütçe kalemleri araştırmasının sevki','Bağlar Belediye Meclisi Yazı İşleri Müdürlüğünün 2014 bütçe kalemlerinin incelenmesini komisyona sevk etti.','Sevk gerçekleşmiş ödeme değildir.', [('file','initiative','2015/139 kararı.'),('topic','action','2014 Yazı İşleri kalemleri araştırması.')]),
('140','2015-07-09','yerel-demokrasi','Solin yaz çalışmaları incelemesinin sevki','Bağlar Belediye Meclisi Solin Çocuk Evindeki yaz çalışmalarının incelenmesini komisyona sevk etti.','Sevk faaliyetlerin tek başına gerçekleşme kanıtı değildir.', [('file','initiative','2015/140 kararı.'),('topic','action','Solin yaz dönemi araştırmasının sevki.')]),
('167','2015-09-08','kamu-hesap-verebilirlik','Yazı İşleri 2014 bütçe raporunun kabulü','Bağlar Belediye Meclisi Yazı İşleri Müdürlüğünün 2014 bütçe harcama kalemleri hakkında komisyon raporunu kabul etti.','Komisyon 395.000 TL bütçe, 166.794,22 TL harcama ve 228.205,78 TL iade bildirdi. Muhasebe fişleri ve ödemeler açık.', [('file','initiative','2015/167 kararı.'),('sum','action','Komisyonun bildirdiği harcama ve iade.'),('approved','result','Rapor mecliste kabul edildi.')]),
('171','2015-09-09','yerel-demokrasi','Solin yaz dönemi komisyon raporunun kabulü','Bağlar Belediye Meclisi Solin Çocuk Evindeki yaz dönemi çalışmalarına ilişkin komisyon raporunu kabul etti.','Komisyon 2015 yazında ay bazında 400 çocuk ve o zamana kadar 45 kadın bildirdi; dönem ve kişi kapsamları farklıdır, toplanamaz. Bireysel katılım kayıtları ve 2015/85 yönetmelik eki açık.', [('file','initiative','2015/171 kararı.'),('children','action','Komisyonun ay bazında çocuk kullanımı beyanı.'),('women','action','Komisyonun şimdiye kadarki kadın kullanımı beyanı.'),('approved','result','Rapor mecliste kabul edildi.')]),
('210','2015-11-03','kamu-hesap-verebilirlik','İnsan Kaynakları 2014 bütçe raporunun kabulü','Bağlar Belediye Meclisi İnsan Kaynakları ve Eğitim Müdürlüğünün 2014 bütçe kalemleri hakkında komisyon raporunu kabul etti.','Komisyon 5.890.000 TL bütçe, 3.056.099,55 TL harcama ve 669.900,45 TL iade bildirdi; aritmetik fark 2.164.000 TL, nedeni ve kapsamı açık. Kalemlerin toplamı bildirilen harcamaya eşit. /256 başka yıla ait sevktir; ödeme ve muhasebe belgeleri açık.', [('file','initiative','2015/210 kararı.'),('budget','action','Komisyonun belirttiği bütçe tutarı.'),('amount','action','Komisyonun harcama ve iade tutarları.'),('approved','result','Rapor mecliste kabul edildi.')]),
('256','2015-12-11','kamu-hesap-verebilirlik','2015 gelir ve gider araştırmasının sevki','Bağlar Belediye Meclisi belediyenin 2015 gelir ve giderlerinin incelenmesini komisyona sevk etti.','Bu sevk /210 içindeki 2014 insan kaynakları farkını açıklamaz; rapor ve kesin hesap açık.', [('file','initiative','2015/256 kararı.'),('topic','action','2015 gelir gider araştırmasının sevki.')])]
for number,day,topic,title,context,detail,anchors in cases:
 stem=prefix+number;limit=detail+' '+base
 ev=[(stem+'-'+label,stage,'document',point) for label,stage,point in anchors]
 prior={'167':'139','171':'140','210':'184'}.get(number)
 if prior:ev.append((prefix+prior+'-file','initiative','document','Önceki 2015/'+prior+' komisyon sevki.'))
 eid=event(stem,day,title,context,ev,limit)
 records['practice_event'][-1]['common_event_key']='baglar-belediye-meclisi-2015-'+number
 pids=[x[0] for x in ev];scope=readings(topic,'event',pids+electoral)
 reason=detail+' Önceleyen aynı kapsamlı tarihli parti hedefi araştırılıyor.'
 cid=stem+'-unmatched'
 records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(pids)))
 task('practice_candidate',cid,reason,limit)
footer=template[template.index('for entry in entries:'):]
footer=footer.replace('baglar-may-chains-draft.json','baglar-solin-budget-draft.json').replace('baglar-may-chains-review-draft.json','baglar-solin-budget-review-draft.json').replace('MAY_CHAINS_SEMANTIC_PASS','SOLIN_BUDGET_SEMANTIC_PASS')
exec(footer,globals())

