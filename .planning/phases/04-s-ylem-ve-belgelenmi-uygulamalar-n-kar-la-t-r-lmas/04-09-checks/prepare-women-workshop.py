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
aux=read(here/'women-workshop-source-records.json')
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
        aid=f'followup-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='İmzalı teklif veya önerge, TBMM kayıt sayfası ve tutanak.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'dbp'
topic = 'kadin-meclisi'
stem = '0409-dbp-van-women-workshop-2025'
conference='0409-women-dbp-2024-kadin-party-'
series='0409-women-dbp-2025-kadin-party-'
ilke='0409-women-dbp-2025-kadin-ilke-'
politika='0409-women-dbp-2025-kadin-politika-'
charter='0308-dbp-draft-037-passage'
statement,target,quote=stem+'-statement',stem+'-target',stem+'-quote'
goal = 'DBP Kadın Meclisi, Aralık 2024 konferans bildirgesinde eğitimleri bölgesel kadın akademileri yoluyla yaygınlaştırma kararı açıkladı.'
limit = ('İlke TV ve Politika Haber haberleri 13 Ağustos 2025 tarihli. Atölyenin günü ve katılımcı sayısı açık. '
         'Haberler aynı sahayı ve katılımcıları aktarıyor. Politika Haber MA imzalı, iki haberin ayrı gözlem olup olmadığı bilinmiyor.')
finding(target,goal,[conference+'training',conference+'resolution',conference+'occurrence'],
    'Konferans kararının kapsamı ve belge tarihi parti bildirgesinin gövdesinden okundu.')
finding(quote,passages[conference+'training']['exact'],[conference+'training'],
    'Yerel eğitimlerin yaygınlaştırılmasına ilişkin birebir kısa ifade.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2024-12-13',date_precision='day',
    version_id=passages[conference+'training']['version_id'],
    period_basis='Bildirge 13 Aralık imzalı. Parti haber dizini 15 Aralık yayımını gösteriyor.',
    uncertainty_reason=None,comparison_row_id='04-03-v3-0308-dbp-draft-037-row'))
readings(topic,'statement',[conference+'training',conference+'resolution',conference+'occurrence',charter])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',passages[conference+'training']['exact'])):
    task(kind,statement,claim,'Aralık 2024 konferansı bir eğitim yönünü belirliyor. Tekil atölye ve kurum sürekliliği bağı ayrı.')

evidence=[
    (series+'series','initiative','party_announcement','Kadın Meclisi Ağustos bildirgesinde atölye dizisinin Mayıs 2025’te başladığını bildirdi.'),
    (series+'goal','initiative','party_announcement','Meclis, eylül sonuna kadar buluşmaları yaymayı hedeflediğini bildirdi.'),
    (ilke+'venue','action','independent_report','İlke TV, DBP Kadın Meclisi atölyesinin Van Edremit Şehit Fırat Mahallesi’nde düzenlendiğini bildirdi.'),
    (politika+'venue','action','independent_report','Politika Haber’de MA imzalı haber aynı mahalleyi ve atölyeyi bildirdi.'),
    (ilke+'program','result','independent_report','İlke TV, atölyenin soru ve cevap bölümüyle devam ettiğini bildirdi.'),
]
context='İlke TV, DBP Kadın Meclisi’nin Van Edremit’te Kadın Kurtuluş Atölyesi düzenlediğini bildirdi.'
eid=event(stem,None,'DBP Kadın Meclisinin Van Edremit atölyesi',context,evidence,limit)
records['practice_event'][-1].update(occurrence_basis='İlke TV’nin 13 Ağustos 2025 haberinde yer, organizatör ve katılımcılar. MA imzalı eş zamanlı haber aynı mahalleyi bildiriyor.',
    common_event_key='dbp-kadin-meclisi-van-edremit-sehit-firat-atolye-2025',date_precision='unknown',
    date_unknown_reason='Her iki haber 13 Ağustos 2025’te yayımlandı. Atölyenin yapıldığı gün gövdelerinde belirtilmedi.')
refs=[row[0] for row in evidence]
scope=readings(topic,'event',refs+[ilke+'byline',politika+'byline',series+'meeting'])
rid,result,explanation=stem+'-relation',stem+'-result',stem+'-explanation'
compare='2024’teki bölgesel kadın eğitimi hedefi ile aynı Kadın Meclisinin Van’daki atölyesi eğitim faaliyeti düzeyinde karşılaştırılabilir.'
outcome=('13 Ağustos 2025 tarihli İlke TV haberi Van Edremit’teki atölyeyi, Berivan Bahçeci ve diğer katılımcıları ve soru-cevap bölümünü aktarıyor. '
         'Atölye günü ayrıca doğrulanamadı.')
connection=('2024 konferans bildirgesi bölgesel kadın eğitimini yaygınlaştırmayı öngörüyor. 2025 Ağustos bildirgesi bir atölye dizisi açıklıyor. '
            'Van Edremit’teki atölye haberle belgelendi. Akademi statüsü, kalıcı eğitim programı ve ülke geneli sonuçları açık.')
finding(result,outcome,[ilke+'venue',ilke+'program',ilke+'byline',politika+'venue'],
    'İki 13 Ağustos haberinin yeri, somut oturumu ve haber gününü kontrol ettik.')
finding(explanation,connection,[conference+'training',conference+'resolution',series+'series',series+'goal',ilke+'venue'],
    'Bölgesel eğitim hedefi, belirli atölye ve açıklanan yaygınlaştırma hedefi birlikte okundu.')
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,
    comparability_reason=compare,target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,
    temporal_context='Aralık 2024 eğitim kararı. Kaynağın bildirdiği dizi başlangıcı Mayıs 2025. Edremit atölyesinin haberleri 13 Ağustos 2025.',
    authority_context='Karar DBP Kadın Meclisi bildirgesine, yerel atölye ve katılan isimler haber kayıtlarına ait.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',connection),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',outcome),('practice_relation.explanation_finding_id',connection)):
    task(kind,rid,claim,limit)

for entry in entries:
    dest=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in dest: dest.append(entry['values'])
for table,rows in records.items():
    dest=snapshot.setdefault(table,[])
    dest.extend(row for row in rows if row not in dest)
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
        reason=kind+' hedefinin asıl kaynakları, tarihi ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('women-workshop-draft.json',package),('women-workshop-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
