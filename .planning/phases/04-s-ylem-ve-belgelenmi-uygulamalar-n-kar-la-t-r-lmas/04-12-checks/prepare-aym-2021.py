"""Compare the archived charter with the documented 2021 accounts decision."""

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
aux=read(here/'aym-2021-source-records.json')
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
        aid=f'aym-2021-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='TBMM’nin teklif dosyası, imzalı teklif ve Gelen Kâğıtlar listesi.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'demokrat'
topic = 'mali-kesin-hesap'
stem = '0412-demokrat-aym-2021-hesap'
prefix = '0412-aym-2021-hesap-'
version = '0210-demokrat-charter-archive-v1'
charter = stem+'-charter'
exact = 'haziran ayı sonuna\nkadar Anayasa Mahkemesine ve bilgi için Cumhuriyet Başsavcılığına verir.'
new('passage', id=charter, version_id=version, exact=exact, prefix=None, suffix=None,
    article='74', section='Tüzük madde 74, kesin hesabın ilgili mercilere gönderilmesi',pdf_page_index=41, printed_page='41')
passages[charter] = entries[-1]['values']
statement, target, quote = (stem+tail for tail in ('-statement','-target','-quote'))
goal = ('Demokrat Parti’nin arşivlenmiş tüzüğünün 74. maddesi, birleştirilmiş kesin hesap ve onaylı '
        'teşkilat hesaplarının haziran sonuna kadar AYM’ye ve bilgi için Cumhuriyet Başsavcılığına verilmesini öngörüyor.')
period_limit = ('Tüzük nüshası 18 Haziran 2022’de arşivlendi. Kabul günü ve 2021 hesaplarının sunulduğu '
                'tarihteki yürürlük durumu ayrıca araştırılıyor.')
finding(target,goal,[charter],period_limit)
finding(quote,exact,[charter],'74. maddenin gönderim mercii ve süre cümlesi.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at=None,date_precision='unknown',
    version_id=version,period_basis='Tüzük nüshasının 18 Haziran 2022 arşiv yakalaması.',
    uncertainty_reason=period_limit,comparison_row_id='04-03-v3-0312-demokrat-2-034-mali-kesin-hesap-row'))
readings(topic,'statement',[charter])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',exact)):
    task(kind,statement,claim,period_limit)

context = ('Anayasa Mahkemesi, Demokrat Parti’nin 2021 kesin hesabının eldeki bilgi ve belgelere göre doğru, '
           'denk ve 2820 sayılı Kanun’a uygun olduğuna 25 Aralık 2024’te oybirliğiyle karar verdi.')
limit = ('Karar 14 Mart 2025 Resmî Gazete’de yayımlandı. Partinin ilk gönderim günü, Başsavcılığa bilgi '
         'gönderme tarihi ve ilgili nüshanın o tarihteki yürürlük durumu araştırılıyor.')
evidence = [
    (prefix+'identity','action','document','Karar künyesi K.2024/116.'),
    (prefix+'year','action','document','Dosya Demokrat Parti’nin 2021 kesin hesabı hakkında.'),
    (prefix+'submission','action','document','Mahkeme, partinin sunduğu kesin hesap çizelgelerini kayda aldı.'),
    (prefix+'review','action','document','Sayıştay inceleme raporu Heyete sunuldu.'),
    (prefix+'merit','result','document','Mahkeme 25 Aralık 2024 tarihli sonucunu oybirliğiyle verdi.'),
    (prefix+'balance','result','document','Sonuç, eldeki bilgi ve belgelerin kapsamı ile sınırlı.'),
]
eid = event(stem,'2024-12-25','Demokrat Parti 2021 kesin hesabına ilişkin AYM kararı',context,evidence,limit)
records['practice_event'][-1].update(common_event_key='aym-spmd-2022-42-2024-116-demokrat-2021',
    occurrence_basis='Anayasa Mahkemesinin Resmî Gazete’de yayımlanan mali denetim kararı.')
refs=[item[0] for item in evidence]
scope=readings(topic,'event',refs)
rid,result,explanation=(stem+tail for tail in ('-relation','-result','-explanation'))
comparison = ('Tüzüğün 74. maddesi kesin hesabın AYM’ye sunulmasını öngörüyor. AYM kararı 2021 hesabına ait '
              'çizelgelerin Mahkemeye sunulduğunu ve bunların incelendiğini belgeliyor.')
detail = comparison+' '+context+' '+limit
finding(result,context,refs,'Karar konusu ile hüküm aynı özgün nüshada okundu.')
finding(explanation,detail,[charter,*refs],limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=comparison,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=explanation,temporal_context='2021 hesap yılı, 2022 tüzük yakalaması, 2024 karar ve 2025 yayım.',
    authority_context='Kesin hesap çizelgeleri Demokrat Parti tarafından sunuldu. Sonuç Anayasa Mahkemesinin.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=comparison,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',detail),('practice_relation.target_finding_id',goal),
                   ('practice_relation.result_finding_id',context),('practice_relation.explanation_finding_id',detail)):
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
for name,content in [('aym-2021-draft.json',package),('aym-2021-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
