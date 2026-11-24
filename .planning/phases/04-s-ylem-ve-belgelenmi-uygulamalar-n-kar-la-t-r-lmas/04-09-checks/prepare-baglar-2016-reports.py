from pathlib import Path
from hashlib import sha256
import json,sys
here=Path(sys.argv[1]); template=(here/'baglar-may-chains-prepare.py').read_text()
head=template[:template.index("assert party=='dbp'")]
head=head.replace('baglar-may-chains-source-records.json','baglar-2016-reports-source-records.json').replace("read(here/'baglar-april-chains-draft.json')","read(data/'practices/04-dbp.json')").replace("read(here/'baglar-april-chains-review-draft.json')","read(data/'practices/04-dbp-review.json')").replace('baglar-may-chains-reading-','baglar-2016-reports-reading-').replace('Bağlar Belediyesi 2015 Meclis karar derlemesindeki tarihli karar.','Bağlar Belediyesi 2016 Meclis karar derlemesindeki tarihli karar.')
exec(head,globals())
assert party=='dbp'
assert sha256((data/'practices/04-dbp.json').read_bytes()).hexdigest()=='c261a747122fd39d50250c84c2ae6aed9884515ba5a8506610a9ff55f06b2957'
assert sha256((data/'practices/04-dbp-review.json').read_bytes()).hexdigest()=='56f9115e9e4006f24900431a9ac442a0b7d56590ec6dcbcdbaefc816d48c3cae'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(64,7,0)
prefix='0409-baglar-2016-reports-';electoral=['0409-siginak-ysk-district-name','0409-siginak-ysk-district-party']
cases=[
 ('18','2016-01-06','tuketici-haklari','Bağlar’da gıda denetimi raporunun kabulü','Bağlar Belediye Meclisi Çevre ve Sağlık Komisyonunun gıda tüketim noktaları hakkındaki raporunu kabul etti.','Komisyon 447 noktanın denetlendiğini ve uygunsuz ürünlerin imha edildiğini bildirdi. Tekil denetim tutanakları, tarih aralığı, sonuçların dağılımı ve önerilen eğitimin uygulanması açık.', [('file','initiative','2016/18 meclis kararı.'),('count','action','Komisyonun 447 nokta beyanı.'),('report','action','Komisyonun ürün imhası beyanı.'),('approval','result','Rapor mecliste kabul edildi.')]),
 ('20','2016-01-07','sosyal-hizmet','Bağlar Kardelen Kadın Evi danışmanlık raporunun kabulü','Bağlar Belediye Meclisi Kardelen Kadın Evi-1 hizmetlerine ilişkin Halkla İlişkiler Komisyonu raporunu kabul etti.','Komisyon danışmanlık ve eğitim hizmetlerini bildirdi. Bireysel yararlanma kayıtları, hizmetin başlangıcı ve sonraki sürekliliği açık; 2015/214 kurs raporu ile ayrı tarihli karardır.', [('file','initiative','2016/20 meclis kararı.'),('services','action','Komisyonun danışmanlık anlatımı.'),('seminars','action','Komisyonun seminer ve eğitim anlatımı.'),('approval','result','Rapor mecliste kabul edildi.')])]
for number,day,topic,title,context,detail,anchors in cases:
 stem=prefix+number; limit=detail+' İşlem belediye meclisine aittir; 2014 seçim kaydı dönem bağlamı verir. Parti organı kararı, bireysel oy ve parti talimatı çıkarılmaz.'
 ev=[(stem+'-'+label,stage,'document',point) for label,stage,point in anchors]
 eid=event(stem,day,title,context,ev,limit);records['practice_event'][-1]['common_event_key']='baglar-belediye-meclisi-2016-'+number
 pids=[v[0] for v in ev];scope=readings(topic,'event',pids+electoral);reason=detail+' Önceleyen aynı kapsamlı tarihli parti hedefi araştırılıyor.';cid=stem+'-unmatched'
 records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(pids)));task('practice_candidate',cid,reason,limit)
footer=template[template.index('for entry in entries:'):]
footer=footer.replace('baglar-may-chains-draft.json','baglar-2016-reports-draft.json').replace('baglar-may-chains-review-draft.json','baglar-2016-reports-review-draft.json').replace('MAY_CHAINS_SEMANTIC_PASS','DBP2016_REPORTS_SEMANTIC_PASS').replace('tutar farkı, ödeme','denetim ve hizmetin sınırları, ödeme')
exec(footer,globals())
