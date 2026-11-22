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
aux=read(here/'baglar-cemr-source-records.json')
party=aux['party_id']
package=read(here/'women-workshop-draft.json')
review=read(here/'women-workshop-review-draft.json')
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
            boundary_reason='İlgili politika söylemi ve TBMM işlem zinciri dar kapsamda incelendi.'))
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
        aid=f'cemr-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='İlgili politika söylemi, önerge veya kanun teklifi.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Bağlar Belediye Meclisinin 2015 karar derlemesi.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'dbp'
topic = 'yerel-demokrasi'
stem = '0409-dbp-baglar-2015-cemr'
conference = '0409-cemr-women-'
decision = '0409-cemr-baglar-'
affiliation = '0409-cemr-aa-'
registry = '0409-cemr-tbb-'
statement, target, quote = (stem+suffix for suffix in ('-statement','-target','-quote'))
goal = ('Wan Haber’in aktardığı DBP Yerel Yönetimler Merkezi Kadın Konferansı bildirgesi, '
        'belediyelerin CEMR eşitlik şartını onaylayıp topluca imzalamasını istedi.')
limit = ('2015/48 kararı Bağlar Belediye Meclisine ait. Parti konferansı kararı ile belediye meclisinin ayrı yetkileri var. '
         '2015 oturumunda kişinin oyu, o yıl imzalanan bir belge ve sonraki uygulama açık. '
         'Türkiye Belediyeler Birliği imza tablosu Bağlar için 1 Ekim 2024 tarihini veriyor.')
finding(target,goal,[conference+'conference',conference+'cemr'],
    'Haberin konferans bağlamı ve aktardığı sonuç bildirgesinin CEMR maddesi birlikte okundu.')
finding(quote,passages[conference+'cemr']['exact'],[conference+'cemr'],
    'Wan Haber’de aktarılan kısa bildiri maddesi.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2014-12-22',date_precision='day',
    version_id=passages[conference+'cemr']['version_id'],
    period_basis='Wan Haber bildirgeyi 22 Aralık 2014’te yayımladı. Konferansın imzalı tutanağı açık.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0308-dbp-current-yerel-demokrasi'))
readings(topic,'statement',[conference+'conference',conference+'cemr'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[conference+'cemr']['exact'])):
    task(kind,statement,claim,'Aktarım tarihi biliniyor. Bildirgenin özgün imzalı nüshası ve oy ayrıntıları açık.')

evidence = [
    (decision+'decision-id','action','document','2015/48 eylem kaydında CEMR konusu ve 6 Şubat 2015 tarihi.'),
    (decision+'agenda','action','document','Meclis, Kültür ve Sosyal İşleri Müdürlüğünün 3 Şubat 2015 tarihli yazısını görüştü.'),
    (decision+'chair','action','document','Karar metninde Meclis Başkanı Birsen Kaya Akat ve iki kâtip adı var.'),
    (decision+'approval','result','document','Karar kaydı mevcudun oybirliği ile onayını bildiriyor.'),
]
context = ('Bağlar Belediye Meclisi, 6 Şubat 2015’te 2015/48 sayılı kararla CEMR Kadın-Erkek Eşitliği Şartı’nı '
           'mevcudun oybirliğiyle onayladı. Kararda Meclis Başkanı Birsen Kaya Akat olarak geçiyor.')
eid = event(stem,'2015-02-06','Bağlar Belediye Meclisinin 2015/48 CEMR kararı',context,evidence,limit)
records['practice_event'][-1]['common_event_key'] = 'baglar-belediye-meclisi-2015-48-cemr'
refs = [row[0] for row in evidence]
scope = readings(topic,'event',refs+[affiliation+'election',affiliation+'membership',registry+'signature',registry+'submission'])
rid = stem+'-relation'
result = stem+'-result'
explanation = stem+'-explanation'
result_text = 'Bağlar Belediye Meclisi 6 Şubat 2015’te 2015/48 sayılı kararla CEMR belgesini mevcudun oybirliğiyle onayladı.'
compare = 'DBP konferansının CEMR çağrısı ve Bağlar Belediye Meclisinin 2015/48 kararı aynı eşitlik şartının onaylanmasına ilişkin.'
explanation_text = ('Konferans bildirgesinde CEMR belgesinin belediyelerce onaylanıp imzalanması istendi. '
                    'Bağlar Belediye Meclisi 2015’te belgeyi onayladı. Anadolu Ajansı’nın aktardığı 2014 seçiminde '
                    'Birsen Kaya Akat o zamanki BDP’den seçilmişti. Kararda belediye meclisi başkanı olarak yer aldı. '
                    'Türkiye Belediyeler Birliğinin tablosu Bağlar için 1 Ekim 2024 imzasını gösteriyor. '
                    '2015 kararı ile o döneme ait imza veya uygulama belgesi arasındaki bağ açık.')
finding(result,result_text,[decision+'decision-id',decision+'approval'],
    'Orijinal belediye PDF’si, kaynak sayfa görüntüsü ve metin katmanından onay kararı okundu.')
finding(explanation,explanation_text,[conference+'cemr',decision+'approval',decision+'chair',affiliation+'election',
        affiliation+'membership',registry+'signature'],
    'Konferansın üstlendiği hedef, belediye meclisi onayı, başkanın parti bağı ve TBB imza kaydı ayrı kaynaklardan kontrol edildi.')
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=explanation,temporal_context='22 Aralık 2014 yayımlanan çağrı, 6 Şubat 2015 meclis kararı ve 1 Ekim 2024 TBB imza tarihi.',
    authority_context='DBP konferans bildirgesi ve Bağlar Belediye Meclisi kararı ayrı. Anadolu Ajansı BDP seçimini ve DBP bağını kaydediyor.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',explanation_text),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',result_text),('practice_relation.explanation_finding_id',explanation_text)):
    task(kind,rid,claim,limit)

for entry in entries:
    destination=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in destination:
        destination.append(entry['values'])
for table,rows in records.items():
    destination=snapshot.setdefault(table,[])
    destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,
    [entry['values']['id'] for entry in entries if entry['kind']=='passage'],party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin kaynak, tarih ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('baglar-cemr-draft.json',package),('baglar-cemr-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
