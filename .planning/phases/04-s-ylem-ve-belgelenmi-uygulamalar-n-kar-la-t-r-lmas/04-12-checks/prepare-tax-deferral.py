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
aux=read(here/'tax-deferral-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-demokrat.json')
review=read(data/'practices/04-demokrat-review.json')
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
            boundary_reason='Vergi borcunun teciline ilişkin açıklama, kanun ve yürütme işlemi okundu.'))
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
        aid=f'tax-deferral-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='Birden fazla yayımlanmış açıklamada toplantı ve tarih doğrulandı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='demokrat'
assert sha256((data/'practices/04-demokrat.json').read_bytes()).hexdigest()=='465657f17288833b00f17f0bdeb7e569d24b83a35a74fd0f4372718b64550cfd'
assert sha256((data/'practices/04-demokrat-review.json').read_bytes()).hexdigest()=='62d9d411cbb0de6e94de96044eb1e4bb445291e3fe6714fc8c67b20375728aef'
topic='maliye-vergi'
stem='0412-tax-deferral-2026'
src='0412-tax-deferral-'
statement,target,quote=(stem+label for label in ('-statement','-target','-quote'))
goal='Gültekin Uysal 8 Mayıs’ta esnafın vergi borçları için faizin düşürülmesini, kapsamın genişletilmesini ve borcun ödenebilir hâle gelmesini istedi.'
statement_limit='Parti açıklamasındaki yüzde 44’e yakın maliyet için hesaplama yöntemi ve borç profili açıklanmıyor. Düzenleyici faiz oranı adıyla sayısal kıyas yapılmadı.'
statement_pids=[src+'statement-day',src+'statement-speaker',src+'statement-terms',src+'statement-target']
finding(target,goal,statement_pids,'Parti yayınının tarihi, konuşmacısı ve faiz ile kapsam hedefleri okundu.')
finding(quote,passages[src+'statement-quote']['exact'],[src+'statement-quote'],'Açıklamadaki kapsam hedefinin doğrulanabilir kısa aktarımı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-05-08',date_precision='day',
    version_id=passages[src+'statement-target']['version_id'],
    period_basis='8 Mayıs 2026 partinin resmî sayfasındaki tarihli açıklama.',
    uncertainty_reason=statement_limit,comparison_row_id='04-03-v3-0313-demokrat-maliye-vergi'))
readings(topic,'statement',statement_pids+[src+'statement-quote'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[src+'statement-quote']['exact'])):
    task(kind,statement,claim,statement_limit)

events=(
    ('law','tbmm-7582-md1-kabul-2026-05-21','2026-05-21','7582 sayılı Kanunun vergi borcu teciline ilişkin hükmü',
     'TBMM 21 Mayıs 2026’da 7582 sayılı Kanunu kabul etti. 6183 sayılı Kanunun 48. maddesinde tecil süresi tavanı ve teminatsız tecil tutarı değişti.',
     'TBMM 2/3669 teklif kaydı, 7582 sayılı Kanun sicili ve kabul metni.',
     '2/3669 5 Mayıs tarihinde sunuldu. Uysal’ın açıklaması 8 Mayıs. Kanun 21 Mayıs’ta kabul edildi ve 4 Haziran’da yayımlandı.',
     'Kanunun bu maddesi TBMM tarafından kabul edildi. Demokrat Parti’nin açıklaması kendi politika hedefini gösteriyor.',
     'Kanunun 1. maddesi üst vade ve teminat tutarına ilişkin. Başvuru üzerine verilen vadeler, fiilî tahsilat ve esnaf sonuçları açık.',
     'Kanun azami tecil süresini 36 aydan 72 aya, genel teminatsız tutarı 50.000 TL’den 1 milyon TL’ye çıkardı.',
     '8 Mayıs açıklamasındaki vade, maliyet ve kapsam kaygısı aynı 2/3669 teklifinin kabul edilen 1. maddesiyle karşılaştırıldı. Hüküm vade ve teminatsız tutarı değiştiriyor. Faiz oranı ayrı idari belgeyle izleniyor.',
     (
         ('proposal-number','initiative','TBMM 2/3669 esas numarası.'),
         ('proposal-filed','initiative','Teklif TBMM’ye 5 Mayıs’ta sunuldu.'),
         ('register-accept','action','TBMM 7582 sayılı Kanunu 21 Mayıs’ta kabul etti.'),
         ('register-issue','result','Kanun 33270 sayılı Resmî Gazete’de yayımlandı.'),
         ('register-published','result','Resmî Gazete yayım günü 4 Haziran 2026.'),
         ('law-months','result','Kanun 48. maddenin ilk fıkrasındaki 36 ayı 72 ay yaptı.'),
         ('law-guarantee','result','48. maddenin ikinci fıkrasındaki genel teminatsız tutar 1 milyon TL oldu.'),
         ('law-effect','result','7582’nin 1. maddesinin yayım günü yürürlüğü 14. maddenin ç bendine dayanıyor.'),
     )),
    ('teblig','gib-6183-tecil-b20-2026-06-16','2026-06-16','B/20 Tahsilat Genel Tebliğiyle indirimli faizli tecil',
     '16 Haziran 2026 tarihli B/20 Tahsilat Genel Tebliği, 6183 sayılı Kanunun 48. maddesi kapsamında belirli vergi borçlarına indirimli faizle tecil imkânı getirdi.',
     'Gelir İdaresi Başkanlığının 33282 sayılı Resmî Gazete ve B/20 açıklayıcı bilgi notu.',
     '8 Mayıs açıklaması, 4 Haziran kanun yayımı ve 16 Haziran Tebliğ yayımı ayrı. GİB son başvuruyu 31 Ağustos 2026 olarak bildiriyor.',
     'Tebliğ ve vergi dairesi uygulaması Hazine ve Maliye Bakanlığı ile Gelir İdaresine ait. Parti açıklaması bir talepti.',
     'GİB açıklaması 5 Haziran 2026 ve önceki vadeler, kapsam dışı türler ve son başvuru için sınır bildiriyor. Bireysel işlemler ve ödemeler açık.',
     'GİB, uygun borçlarda cari yıllık yüzde 39 yerine yüzde 29 tecil faizi açıkladı. Başvuru 31 Ağustos’a kadar. Özel tüketim vergisi ve geçici vergi kapsam dışında.',
     'Uysal’ın faiz düşürme ve kapsamı genişletme çağrısıyla B/20 usulü aynı tecil alanına ilişkin. İndirimli oran belirli borç ve başvuru koşullarına bağlı.',
     (
         ('gib-day','action','GİB B/20 Tebliğinin 16 Haziran 2026 ve 33282 sayılı Resmî Gazete künyesini veriyor.'),
         ('gib-interest','result','GİB bilgi notunda uygun teciller için yıllık faiz yüzde 39 yerine yüzde 29.'),
         ('gib-date','result','Tebliğ 5 Haziran 2026 ve öncesinde vadesi gelen belirli borçları kapsıyor.'),
         ('gib-exclusions','result','Özel tüketim vergisi ve geçici vergi GİB açıklamasında ayrı istisna.'),
         ('gib-application','result','GİB başvuru için son günü 31 Ağustos 2026 olarak duyurdu.'),
         ('gib-security','result','GİB, bu özel Tebliğ sürecinde 10 milyon TL’yi aşmayan borçlar için teminat aranmayacağını belirtiyor.'),
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
for name,content in [('tax-deferral-draft.json',package),('tax-deferral-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
