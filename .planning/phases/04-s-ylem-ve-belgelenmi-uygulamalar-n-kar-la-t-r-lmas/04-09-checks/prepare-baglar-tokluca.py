"""Record four Tokluca municipal decisions with the separate approval question."""

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
aux=read(here/'baglar-tokluca-source-records.json')
party=aux['party_id']
package=read(data/f'practices/04-{party}.json')
review=read(data/f'practices/04-{party}-review.json')
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
def task(kind,identity,body,limitation):
    tasks[(kind,identity)]=(body,limitation)
def scope_for(topic,lane):
    cell=next(row for row in inventory['cells']
              if (row['party_id'],row['topic_id'],row['research_kind'])==(party,topic,lane))
    sid=cell['cell_id']
    if not any(s['id']==sid for s in records['practice_scope_v2']):
        records['practice_scope_v2'].append(dict(id=sid,**{k:cell[k] for k in
            ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
            boundary_reason='Bağlar Belediye Meclisi kararının ilgili bölümü özgün derlemede okundu.'))
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
        aid=f'baglar-tokluca-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Bağlar Belediye Meclisi kararı veya yerel seçim dönem kaydı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Bağlar Belediyesi Meclis karar derlemesindeki tarihli karar.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'dbp'
electoral_context = ['0409-siginak-ysk-district-name','0409-siginak-ysk-district-party']
context_limits = ('YSK kaydı yönetimin 2014 seçim bağlamını veriyor. '
                  'İşlem belediye meclisine ait. Parti adına bağımsız bir karar veya kişisel oy açık.')
common_limitation = (
    '5393 sayılı Kanunda meclis kararı, kaymakam görüşü ve vali onayı ayrı aşamalar. '
    'Bu dosya için vali onayının tarihi, sayısı ile kesinleşme ve yürürlük tarihi doğrulanamadı. '
    '2021 belediye yol çalışmaları raporu Tokluca ve Batıkarakoç’u ayrı satırlarda gösteriyor.'
)
events = (
    ('2015-22', '2015-01-09', 'Tokluca için Avşin adıyla ilk mahalle önerisi',
     'Bağlar Belediye Meclisi, Tokluca Küme Evlerinin Batıkarakoç’tan ayrılarak Avşin adıyla mahalle olması önerisini içeren raporu 9 Ocak’ta kabul etti.',
     'Sakinlerden alınan bilgi 60 hane ve yaklaşık 564 kişiydi. Dayanak nüfus belgesi ile sınır krokisinin özgün eki açık.',
     (('plan','action','Komisyon Tokluca Küme Evlerinin Avşin adıyla mahalle olmasını önerdi.'),
      ('people','action','Komisyon sakinlerden aldığı bilgiyi 60 hane ve yaklaşık 564 kişi olarak kaydetti.'),
      ('vote','result','Belediye meclisi 9 Ocak 2015’te raporu oybirliğiyle kabul etti.'))),
    ('2015-251', '2015-12-11', 'Tokluca ayrılma talebinin yeniden komisyona sevki',
     'Bağlar Belediye Meclisi, Kaymakamlık yazısında aktarılan Tokluca ayrılma talebini 11 Aralık’ta İnceleme ve Araştırma Komisyonuna sevk etti.',
     'Meclis kararı 26 Kasım tarihli 490-E.3299 sayılı kaymakamlık yazısına atıf yapıyor. Yazının kendi metni araştırılıyor.',
     (('letter','action','Meclis kararında 26 Kasım 2015 tarih ve 490-E.3299 sayılı kaymakamlık yazısı anılıyor.'),
      ('referral','action','Meclis öneriyi inceleme, raporlama ve tekrar görüşme için komisyona sevk etti.'),
      ('vote','result','Meclis 11 Aralık 2015’te komisyon sevkini oybirliğiyle kabul etti.'))),
    ('2016-64', '2016-03-11', 'Tokluca için yenilenen Avşin önerisinin kabulü',
     'Bağlar Belediye Meclisi, 7 Aralık 2015 tarihli 583 sayılı yazıya bağlı yeni raporu 11 Mart’ta kabul etti. Önerilen mahalle adı Avşin’di.',
     'Komisyon sakinlerden aldığı bilgiyi 75 hane ve yaklaşık 520 kişi olarak aktardı. 2015 raporundaki tahmin ayrı. Nüfusun resmî teyidi araştırılıyor.',
     (('letter','action','Komisyon 7 Aralık 2015 tarihli 583 sayılı belediye yazısını ele aldı.'),
      ('plan','action','Komisyon ayrılmayı ve yeni yerin Avşin olarak adlandırılmasını önerdi.'),
      ('people','action','Komisyon sakinlerin 75 hane ve yaklaşık 520 kişi bilgisini aktardı.'),
      ('vote','result','Belediye meclisi 11 Mart 2016’da raporu oybirliğiyle kabul etti.'))),
    ('2016-187', '2016-09-08', 'Önerilen mahalle adının Tokluca olarak değiştirilmesi',
     'Bağlar Belediye Meclisi, Mart kararındaki Avşin adını 8 Eylül’de Tokluca olarak değiştirmeyi oybirliğiyle kabul etti.',
     'Meclis kararı 29 Ağustos tarihli dilekçeden ad üzerinde uzlaşmazlık aktarıyor. Dilekçenin kendi metni ve idari sonucu araştırılıyor.',
     (('request','action','Meclis kararı, 29 Ağustos 2016 tarih ve 4774 sayılı dilekçeye atıf yapıyor.'),
      ('name','action','Meclis, Avşin yerine Tokluca adını görüştü.'),
      ('vote','result','Belediye meclisi 8 Eylül 2016’da ad değişikliğini oybirliğiyle kabul etti.'))),
)
topic = 'yerel-demokrasi'
supporting_readings = [
    '0409-tokluca-'+x for x in (
        '2010-227','2011-20','2011-54','2011-183','2021-road','2021-road-later',
        '5393-approval','5393-effect','6360-threshold')
]
for number,day,title,context,detail,anchors in events:
    stem = '0409-tokluca-'+number
    limit = detail+' '+common_limitation+' '+context_limits
    evidence = [(stem+'-file','initiative','document',f'Meclis işlem numarası {number.replace("-", "/")}.')]
    evidence.extend((stem+'-'+suffix,stage,'document',claim) for suffix,stage,claim in anchors)
    eid = event(stem,day,title,context,evidence,limit)
    records['practice_event'][-1]['common_event_key'] = 'baglar-belediye-meclisi-'+number
    pids = [row[0] for row in evidence]
    scope = readings(topic,'event',pids+electoral_context+supporting_readings)
    candidate = stem+'-unmatched'
    reason = ('Yerel karar ve sonraki belediye kullanımı kaynaklandı. '
              'Önceki tarihli parti hedefi ve bu dosyaya ait mülki idare işleminin özgün kaydı araştırılıyor.')
    records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,
        relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(pids)))
    task('practice_candidate',candidate,reason,limit)

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
for name,content in [('baglar-tokluca-draft.json',package),('baglar-tokluca-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
