from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from uygulamalar import practice_review_package_targets, validate_practice_source_review, validate_practices

here=Path(sys.argv[1])
data=Path('data')
def read(path):
    return json.loads(path.read_bytes())
def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
aux=read(here/'hububat-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-saadet.json')
review=read(data/'practices/04-saadet-review.json')
snapshot=read(data/'releases'/package['base_release']/'records.json')
inventory=read(data/'practices/04-inventory.json')
entries=package['entries']; entries.extend(aux['entries'])
records=package['practice_records']
when=datetime.now(timezone.utc).isoformat()
passages={r['id']:r for r in snapshot['passage']}
passages.update({e['values']['id']:e['values'] for e in entries if e['kind']=='passage'})
versions={r['id']:r for r in snapshot['document_version']}
versions.update({e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'})
tasks={}
def new(table,**row):
    entries.append(dict(kind=table,values=row))
def finding(id,body,refs,reason,pair=None):
    new('finding',id=id,party_id=party,heading='Belgelenmiş uygulamalar',text=body,pair_id=pair or id,
        provenance='quote' if pair else 'summary',epistemic_type='claim')
    for pid in refs:
        new('finding_evidence',finding_id=id,passage_id=pid,role='support')
        new('verification',finding_id=id,passage_id=pid,checked_at=when,result='confirmed',reason=reason)
    new('review',id='review-'+id,kind='finding',subject_id=id,reviewer_kind='agent',
        reviewed_at=when,result='reviewed',reason=reason)
def task(kind,identity,body,limitation):
    tasks[(kind,identity)]=(body,limitation)
def scope_for(topic,lane):
    cell=next(row for row in inventory['cells']
              if (row['party_id'],row['topic_id'],row['research_kind'])==(party,topic,lane))
    sid=cell['cell_id']
    if not any(s['id']==sid for s in records['practice_scope_v2']):
        records['practice_scope_v2'].append(dict(id=sid,**{k:cell[k] for k in
            ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
            boundary_reason='TMO hububat alım fiyatı, teslim üzerine ödeme talebi, TBMM gündemi ve ödeme açıklamaları okundu.'))
    return sid
def readings(topic,lane,refs):
    sid=scope_for(topic,lane)
    grouped={}
    for pid in refs:
        p=passages[pid]
        grouped.setdefault(p['version_id'],set()).add(p['section'])
    for vid,sections in grouped.items():
        existing=[r for r in records['practice_scope_source'] if (r['scope_id'],r['version_id'])==(sid,vid)]
        if existing and set(json.loads(existing[-1]['inspected_sections']))>=sections:
            continue
        if existing:
            sections.update(json.loads(existing[-1]['inspected_sections']))
            if existing[-1]['inspected_at']==when:
                existing[-1]['inspected_sections']=encoded(sorted(sections))
                continue
        url=versions[vid]['final_url']
        aid=f'hububat-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='2026 hububat alım politikası, Meclis işlemi veya ödeme açıklaması.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Birden fazla yayımlanmış açıklamada toplantı ve tarih doğrulandı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='6c86dc9eaaae1bf80e354cfff7f0785d568daaaf80c4351e47af6d7675c9af4f'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='4065d612309da3353238f300fc3df51ad7410386eac9c5e90d736cd9f9d81864'
topic='tarimsal-fiyatlar'
stem='0411-hububat-2026'
src='0411-hububat-'
statement,target,quote=(stem+label for label in ('-statement','-target','-quote'))
goal='Mahmut Arıkan 10 Haziran’da hububat alım fiyatının ekimden önce açıklanmasını ve üreticilere ürün bedelinin teslimde ödenmesini istedi.'
statement_limit='24 TL/kg konuşmacının destek sonrası maliyet örneği. Metinde toplanan maliyet kalemleri 7.835 TL, verilen toplam 7.830 TL. Fiyat ve maliyet varsayımları ayrı.'
statement_pids=[src+'statement-day',src+'statement-delivery',src+'statement-cost']
finding(target,goal,statement_pids,'10 Haziran grup konuşması, tarih ve kamuya açık hedef okundu.')
finding(quote,passages[src+'statement-quote']['exact'],[src+'statement-quote'],'Açıklamadaki kısa özgün ifade.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-06-10',date_precision='day',
    version_id=passages[src+'statement-delivery']['version_id'],period_basis='10 Haziran 2026 Saadet Genel Başkanı grup toplantısı, TV5 aktarımı.',
    uncertainty_reason=statement_limit,comparison_row_id='04-03-v3-0311-saadet-scope-tarimsal-fiyatlar-row'))
readings(topic,'statement',statement_pids+[src+'statement-quote'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[src+'statement-quote']['exact'])):
    task(kind,statement,claim,statement_limit)

events=(
    ('agenda','tbmm-28-4-100-10-4251-gundem','2026-06-10','10/4251 hububat araştırmasının ön görüşme talebinin reddi',
     'Yeni Yol Grubu, Bülent Kaya ve 19 milletvekilinin hububat fiyatları ve TMO alımlarına ilişkin 10/4251 araştırma önergesinin ön görüşmesinin 10 Haziran 2026 birleşiminde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.',
     'TBMM 28. Dönem 4. Yasama Yılı 100. Birleşim tam tutanağı, imzalı 10/4251 önergesi ve TBMM esas kaydı.',
     'Bakanlığın ilk alım ilanı 2 Haziran. Arıkan’ın grup açıklaması ve TBMM gündem işlemi 10 Haziran.',
     'Saadet Genel Başkanı parti talebini açıkladı. Aynı gün gündem önerisini Yeni Yol Grubu getirdi. Kurul gündem oylamasını TBMM yaptı.',
     'İmzalı araştırma kapsamı fiyat ve üretici gelirini içeriyor. Esas dosya durumu 23 Kasım erişiminde Gündemde. Kişisel oylar ve araştırma sonucu açık.',
     'Yeni Yol’un ön görüşme önerisi reddedildi. İmzalı dosyada üretim maliyeti, TMO alımları, destek ve gelir etkisinin araştırılması istendi.',
     'Saadet’in aynı gün açıkladığı hububat fiyatı ve ödeme koşulu talebi, alım araçlarını incelemeyi isteyen TBMM araştırmasının gündeme alınma işlemiyle karşılaştırıldı.',
     (
         ('register-number','initiative','TBMM esas numarası 10/4251.'),
         ('register-day','initiative','Araştırma önergesi 10 Haziran’da Başkanlığa verildi.'),
         ('signed-number','initiative','İmzalı belge 10/4251 numarasını taşıyor.'),
         ('signed-scope','initiative','Gerekçe üretim maliyeti ve üretici geliri ilişkisini araştırmayı istiyor.'),
         ('floor-agenda','action','Yeni Yol 10 Haziran birleşiminde ön görüşme talep etti.'),
         ('floor-role','action','Şerafettin Kılıç Yeni Yol Grubu adına gerekçeyi açıkladı.'),
         ('floor-vote','result','Başkan ilk gündem talebinin kabul edilmediğini açıkladı.'),
         ('register-pending','result','Esas sicilinin 23 Kasım erişimindeki durumu Gündemde.'),
     )),
    ('payment','tmo-2026-06-25-hububat-ilk-odeme','2026-06-25','TMO’nun ilk hububat ödemeleri açıklaması',
     'Tarım ve Orman Bakanı 25 Haziran 2026’da TMO’nun 3 Haziran’da başlayan hububat alımları için ilk ödemeleri aktarmaya başladığını bildirdi.',
     '2 Haziran ilk alım ilanı, 10 Haziran TBMM açıklaması ve 25 Haziran Bakanlık ödeme duyurusu.',
     '2 Haziran metni teslimden sonra 45 gün içinde ödeme öngördü. 10 Haziran tutanağı 21 gün açıklaması içeriyor. 25 Haziran Bakanlık duyurusu ilk aktarımı ve 21’inci günden itibaren ödeme ifadesini içeriyor.',
     'TMO alım ve ödeme işlemlerini, Tarım ve Orman Bakanlığı kamuya açık duyuruyu yürütüyor.',
     'İkinci grup fiyatlar buğdayda 16.500, arpada 12.750 TL/ton. 3.014 TL/ton destek, Bakanlığın ortalama verim varsayımı. Bireysel banka hareketi ve ödeme günleri açık.',
     'Bakanlık 25 Haziran’da ilk ödemelerin başladığını ve 21’inci günden itibaren sürmesini bildirdi. Arıkan teslimde ödeme istemişti.',
     'Teslimde ödeme hedefi, TMO’nun ilk ödeme açıklamasıyla ve iki ayrı ödeme süresi ifadesiyle karşılaştırıldı.',
     (
         ('price-group','initiative','2 Haziran fiyatları ikinci grup ürünlere ait.'),
         ('price-wheat','initiative','Makarnalık ve ekmeklik buğdayın ikinci grup alım fiyatı 16.500 TL/ton.'),
         ('price-barley','initiative','İkinci grup arpa alım fiyatı 12.750 TL/ton.'),
         ('price-support','initiative','Bakanlık ortalama verimle ton başı 3.014 TL destek eşdeğeri hesapladı.'),
         ('price-window','initiative','İlk duyuru teslimden sonra 45 gün içinde ödeme bildiriyor.'),
         ('floor-days','initiative','Abdullah Doğru 10 Haziran birleşiminde 21 günde ödeme açıklamasını aktardı.'),
         ('pay-day','action','Ödeme başlangıcı açıklaması 25 Haziran tarihli.'),
         ('pay-start','result','Bakan 25 Haziran’da ilk tutarların üretici hesaplarına aktarılmakta olduğunu duyurdu.'),
         ('pay-rule','result','Yeni duyuru 21’inci günden itibaren ödemelerin süreceğini bildiriyor.'),
     )),
    ('july','tmo-2026-07-27-hububat-alim-odeme-bildirim','2026-07-27','TMO’nun 27 Temmuz hububat alım ve ödeme toplamı',
     'Tarım ve Orman Bakanı 27 Temmuz 2026’da 176 bin üreticiden 8,3 milyon ton alım ve 34,3 milyar TL ödeme yapıldığını bildirdi.',
     '27 Temmuz tarihli Bakanlık açıklamasının alım ve ödeme bölümleri.',
     'Toplamlar Bakanlığa göre 21 Mayıs’tan 27 Temmuz’a uzanan süreçteki o güne kadarki durumu gösteriyor.',
     'Alımları TMO yürütüyor. Rakamlar Tarım ve Orman Bakanına ait kurumsal açıklama.',
     'Toplamlar TMO programının ölçeğini gösteriyor. Üretici bazında teslim günü, ödeme günü ve maliyet karşılaştırması açık.',
     'Bakanlık 8,3 milyon ton ve 34,3 milyar TL kümülatif değer açıkladı.',
     'Saadet’in teslimde ödeme talebi, aynı programda açıklanan birikimli ödemeyle karşılaştırıldı. Toplam, teslim anında ödeme oranını göstermiyor.',
     (
         ('july-day','action','Açıklama 27 Temmuz 2026 tarihli.'),
         ('july-amount','result','176 bin üreticiden 8,3 milyon ton hububat alımı bildirildi.'),
         ('july-payment','result','Bakanlık 34,3 milyar TL’nin hesaplara aktarıldığını bildirdi.'),
     )),
    ('august','tmo-2026-08-17-hububat-alim-odeme-bildirim','2026-08-17','TMO’nun 17 Ağustos hububat alım ve ödeme toplamı',
     'Tarım ve Orman Bakanı 17 Ağustos 2026’da 11,5 milyon ton hububat alımı ile yaklaşık 120 milyar TL ödeme bildirdi.',
     '17 Ağustos Bakanlık açıklamasının sezonda gerçekleşen miktar ve ödeme bölümü.',
     '17 Ağustos açıklaması sezon başından o güne kadarki kümülatif işlemleri içeriyor.',
     'Alım ve ödeme TMO’nun işlemi. Açıklamayı Tarım ve Orman Bakanı yaptı.',
     'Bu 17 Ağustos itibarıyla kümülatif değer. Temmuz değeriyle toplanmaz. Üretici bazında fiilî teslim ve ödeme günleri açık.',
     'Bakanlık 11,5 milyon ton alım ve yaklaşık 120 milyar TL ödeme bildirdi.',
     'Saadet’in teslimde ödeme talebi, 17 Ağustos’ta açıklanan birikimli ödeme miktarıyla aynı uygulama alanında takip edildi.',
     (
         ('august-day','action','Açıklama 17 Ağustos 2026 tarihli.'),
         ('august-amount','result','Sezon başından beri 11,5 milyon ton alım bildirildi.'),
         ('august-payment','result','Bakan, yaklaşık 120 milyar TL ödeme yapıldığını bildirdi.'),
     )),
)
for label,key,day,title,context,basis,time,specific_authority,detail,observed,compare,anchors in events:
    event_stem=stem+'-'+label
    limit=detail+' '+statement_limit
    evidence=[(src+pid,stage,'document',claim) for pid,stage,claim in anchors]
    event_id=event(event_stem,day,title,context,evidence,limit)
    records['practice_event'][-1].update(common_event_key=key,occurrence_basis=basis)
    pids=[row[0] for row in evidence]
    scope=readings(topic,'event',pids)
    rid,result,explanation=(event_stem+suffix for suffix in ('-relation','-result','-explanation'))
    finding(result,observed,pids,basis)
    finding(explanation,compare+' '+limit,statement_pids+pids,limit)
    records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=event_id,party_id=party,
        topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,
        result_finding_id=result,explanation_finding_id=explanation,temporal_context=time,
        authority_context=specific_authority,uncertainty_reason=limit))
    candidate=event_stem+'-candidate'
    records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event_id,
        relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(pids)))
    for kind,claim in (
        ('practice_relation',compare),('practice_relation.target_finding_id',goal),
        ('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare),
    ):
        task(kind,rid,claim,limit)

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot, records, [entry['values']['id'] for entry in entries if entry['kind']=='passage'], party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin kaynak metni, tarihi ve iddia sınırları okundu. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('hububat-draft.json',package),('hububat-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
