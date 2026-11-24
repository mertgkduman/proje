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
aux=read(here/'olive-oil-source-records.json')
party=aux['party_id']
package=read(here/'three-dossiers-draft.json')
review=read(here/'three-dossiers-review-draft.json')
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
            boundary_reason='Zeytinyağı ihracatına ilişkin milletvekili konuşması, bakanlık cevapları ve kararlar okundu.'))
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
        aid=f'olive-oil-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Zeytinyağı ihracat kısıtı, kota veya ayrı fon kesintisi belgesi.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Yetkili kurumun tarih belirten açıklaması veya yayımlanan kararı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='demokrat'
assert sha256((here/'three-dossiers-draft.json').read_bytes()).hexdigest()=='788da75156f75abaed4308410a233206243520239f2a254c78091c06284c9a95'
assert sha256((here/'three-dossiers-review-draft.json').read_bytes()).hexdigest()=='eeab9f54985611823d2a83b40cb8a8897b29fa342128fc2a1d1a4600de6af1dc'
topic='dis-ticaret'
stem='0412-olive-oil'
src=stem+'-'
statement,target,quote=(stem+suffix for suffix in ('-statement','-target','-quote'))
goal='Haydar Altıntaş 8 Mayıs 2024’te Genel Kurulda zeytinyağı ihracat kısıtının kaldırılmasını istedi.'
limit='Konuşma şahsı adına. Stok ve fiyat rakamlarının bağımsız dayanağı ile konuşmanın sonraki kararlara etkisi açık.'
statement_pids=[src+'floor-demand',src+'floor-speaker']
finding(target,goal,statement_pids,'TBMM’nin 8 Mayıs tarihli 79. Birleşim basılı tutanağı.')
finding(quote,passages[src+'floor-demand']['exact'],[src+'floor-demand'],
        'TBMM tutanağındaki kısa özgün ifade.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2024-05-08',date_precision='day',
    version_id=passages[src+'floor-demand']['version_id'],period_basis='79. Birleşim, basılı 313. sayfa.',
    uncertainty_reason=limit,comparison_row_id='04-03-v3-0313-demokrat-dis-ticaret'))
readings(topic,'statement',statement_pids)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[src+'floor-demand']['exact'])):
    task(kind,statement,claim,limit)

measures=(
    ('quota','ticaret-bakanligi-zeytinyagi-kota-2024-06-01','2024-06-01',
     'Dökme ve varilli zeytinyağına 50 bin ton ihracat kotası',
     'Tarım ve Orman Bakanlığı 7/12491 cevabında, Ticaret Bakanlığının 1 Haziran 2024’ten itibaren dökme ve varilli zeytinyağı ihracatına 50 bin ton kota ile izin verdiğini bildirdi.',
     '7/12491 cevabının ilgili eki. TBMM alım damgası 3 Temmuz 2024.',
     'Başlangıç 1 Haziran. Cevap başlangıçta 1 Kasım’a kadar süre öngörüldüğünü bildiriyor.',
     'İzin Ticaret Bakanlığına atfediliyor. Cevabı Tarım ve Orman Bakanlığı başka bir milletvekilinin sorusu üzerine verdi.',
     'Başlangıç süresi ve kota Bakanlığın cevabına dayanıyor. Kota kullanım miktarı ve doğrudan izin yazısı açık.',
     '1 Haziran başlangıcında 50 bin ton kota izni bildirildi.',
     'Tam kaldırma talebi, aynı dönemde dökme ve varilli zeytinyağında kota ile getirilen izinle karşılaştırıldı.',
     (
         ('quota-authority','action','TBMM’ye iletilen cevap 7/12491 dosyasına ait.'),
         ('quota-limit','result','Cevap 1 Haziran başlangıcı, 50 bin ton kota ve başlangıçta 1 Kasım sınırı bildiriyor.'),
     )),
    ('removal','ticaret-bakanligi-zeytinyagi-kisit-kaldirma-2024-09-13','2024-09-13',
     '13 Eylül zeytinyağı ihracat kısıtlarının kaldırılması',
     'Tarım ve Orman Bakanlığı, 7/23091 cevabında zeytinyağı ihracatındaki kısıtların 13 Eylül 2024 itibarıyla kaldırıldığını bildirdi.',
     '7/23091 cevabının ihracat bölümü. TBMM alım damgası 20 Mart 2025.',
     '8 Mayıs söylemi, 1 Haziran kota izni ve 13 Eylül kaldırma işlemi tarih sırasıyla izleniyor.',
     'Cevap kurumsal Tarım ve Orman Bakanlığı kaydı. Altıntaş’ın yetkisi Genel Kurulda kişisel söylem.',
     'Cevap geriye dönük. İlk kaldırma yazısı ve bireysel ihracat işlemleri açık. Fon kesintisinin kaldırılması 14 Eylül tarihli ayrı karar.',
     'Bakanlık, kısıtların 13 Eylül 2024 itibarıyla kaldırıldığını bildirdi.',
     '8 Mayıs kaldırma talebi, aynı ürün grubuna ilişkin daha sonraki kısıt kaldırma bildirimiyle karşılaştırıldı.',
     (
         ('removal-authority','action','TBMM’ye iletilen cevap 7/23091 dosyasına ait.'),
         ('removal-effect','result','Cevap kaldırma gününü 13 Eylül 2024 olarak bildiriyor.'),
     )),
)
for label,key,day,title,context,basis,temporal,authority,detail,result,compare,anchors in measures:
    stage_limit=detail+' '+limit
    event_stem=f'{stem}-{label}'
    evidence=[(src+pid,stage,'document',claim) for pid,stage,claim in anchors]
    event_id=event(event_stem,day,title,context,evidence,stage_limit)
    records['practice_event'][-1].update(common_event_key=key,occurrence_basis=basis)
    pids=[ref[0] for ref in evidence]
    scope=readings(topic,'event',pids)
    rid,result_id,explanation=(event_stem+suffix for suffix in ('-relation','-result','-explanation'))
    finding(result_id,result,pids,basis)
    finding(explanation,compare+' '+stage_limit,statement_pids+pids,stage_limit)
    records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=event_id,party_id=party,
        topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,
        result_finding_id=result_id,explanation_finding_id=explanation,temporal_context=temporal,
        authority_context=authority,uncertainty_reason=stage_limit))
    records['practice_candidate'].append(dict(id=event_stem+'-candidate',scope_id=scope,event_id=event_id,
        relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(pids)))
    for kind,claim in (('practice_relation',compare),('practice_relation.target_finding_id',goal),
                        ('practice_relation.result_finding_id',result),('practice_relation.explanation_finding_id',compare)):
        task(kind,rid,claim,stage_limit)

fund_stem=stem+'-fund'
fund_title='8957 ile dökme ve varilli zeytinyağında fon kesintisini kaldırma kararı'
fund_context='8957 sayılı Cumhurbaşkanı Kararı, 7391 ile belirlenen kilogram başına 20 sent karşılığı TL fon kesintisinin yer aldığı bendi kaldırdı. Yürürlük günü 14 Eylül 2024.'
fund_limit='8957 ve 7391 sayfalarının karar maddeleri görüntüde okundu. Kayıtlar fon kesintisini belgeliyor. Kısıt kaldırma bildiriminden ayrı bir düzenleme.'
fund_reason='8 Mayıs konuşması ihracat kısıtına ilişkin. Fon kesintisinin kaldırılmasına yönelik önceki özgül söylem araştırması açık.'
proof=(
    (src+'old-gazette-decision','initiative','7391 kararı ve aynı sayfadaki fon kesintisi hükmü.'),
    (src+'notice-rate','initiative','GAİB, 7391’e göre kilogram başına 20 sent kesinti bildiriyor.'),
    (src+'gazette-decision','result','8957, aynı bent için yürürlükten kaldırma hükmü taşıyor.'),
    (src+'gazette-day','result','Kararın yayım ve yürürlük günü 14 Eylül 2024.'),
)
fund_id=event(fund_stem,'2024-09-14',fund_title,fund_context,
    [(pid,stage,'document',claim) for pid,stage,claim in proof],fund_limit)
records['practice_event'][-1].update(common_event_key='rg-2024-09-14-8957-zeytinyagi-dfif',
    occurrence_basis='14 Eylül Resmî Gazete nüshası, 7391 sayılı önceki kararın GAİB kopyası ve tarihli GAİB duyurusu.')
pids=[row[0] for row in proof]
scope=readings(topic,'event',pids)
candidate=fund_stem+'-candidate'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=fund_id,relation_id=None,
    state='unmatched',reason=fund_reason,passage_ids=encoded(pids)))
task('practice_candidate',candidate,fund_context,fund_reason+' '+fund_limit)

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
for name,content in [('olive-oil-draft.json',package),('olive-oil-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
