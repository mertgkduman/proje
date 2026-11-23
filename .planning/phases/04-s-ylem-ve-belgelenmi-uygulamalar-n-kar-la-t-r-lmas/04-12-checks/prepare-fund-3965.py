"""Compare the 2/3965 proposal with the earlier archived policy."""

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
aux=read(here/'fund-3965-source-records.json')
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
        aid=f'fund-3965-reading-{lane}-{topic}-{vid}'
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
topic = 'makroekonomik-politika'
stem = '0412-demokrat-2026-2-3965'
anchor = '0412-fund-3965-'
program = '0412-fund-3965-program'
program_version = '0210-demokrat-program-archive-v1'
program_context = program+'-context'
program_exact = 'vatandaşın gönül\nrahatlığıyla ve güvenle birikimlerini yatırabileceği bir sermaye\npiyasası kurumuna dönüştüreceğiz.'
new('passage',id=program,version_id=program_version,exact=program_exact,prefix=None,suffix=None,
    article=None,section='Finansal Hizmetler ve Borsalar',pdf_page_index=46,printed_page='53')
passages[program] = entries[-1]['values']
new('passage',id=program_context,version_id=program_version,exact='Borsayı manipülasyonlar ve\nspekülatif hareketlerin egemen olduğu',prefix=None,suffix=None,
    article=None,section='Finansal Hizmetler ve Borsalar',pdf_page_index=46,printed_page='53')
passages[program_context]=entries[-1]['values']
statement,target,quote = (stem+tail for tail in ('-statement','-target','-quote'))
goal = ('Demokrat Parti’nin 2021’de arşivlenmiş programı, yatırımcıların birikimlerini güvenle '
        'değerlendirebildiği ve manipülasyona karşı korunan bir sermaye piyasası hedefliyor.')
statement_limit = ('29 Aralık 2021 arşiv yakalaması nüshanın o tarihteki varlığını gösteriyor. '
                   'Kabul günü ve Ekim 2026’daki yürürlüğü açık.')
finding(target,goal,[program,program_context],statement_limit)
finding(quote,program_exact,[program],statement_limit,pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at=None,date_precision='unknown',
    version_id=program_version,period_basis='Program nüshası 29 Aralık 2021’de arşivlendi.',
    uncertainty_reason=statement_limit,comparison_row_id='04-03-v3-0313-demokrat-makroekonomik-politika'))
readings(topic,'statement',[program,program_context])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                   ('practice_statement.quote_finding_id',program_exact)):
    task(kind,statement,claim,statement_limit)

context = ('Demokrat Parti İzmir Milletvekili Haydar Altıntaş, 20 Ekim 2026’da 2/3965 sayılı yatırım fonu '
           'teklifini sundu. Teklif 21 Ekim’de ilgili komisyonlara girdi.')
limit = ('2/3965 dosyasında komisyon girişi 21 Ekim ve erişilen işlem alanı Komisyonda. '
         'Yasalaşma, tazminat ve düzenlemenin etkisi açık.')
evidence = [
    (anchor+'detail-id','initiative','document','Teklif esas numarası 2/3965.'),
    (anchor+'detail-filed','initiative','document','Başkanlığa geliş 20 Ekim 2026 olarak kaydedildi.'),
    (anchor+'detail-membership','initiative','document','İmza tablosunda Demokrat Parti İzmir milletvekili Haydar Altıntaş var.'),
    (anchor+'signed-stamp','initiative','document','İkinci sayfada TBMM’nin 20 Ekim 2026 evrak kaşesi var.'),
    (anchor+'signed-risk-limit','initiative','document','Madde 1 risk için yüzde on sınır ve üç aylık bağımsız denetim öneriyor.'),
    (anchor+'signed-liability','initiative','document','Madde 1 şahsi ve müteselsil sorumluluk öneriyor.'),
    (anchor+'signed-payment','initiative','document','Madde 2 belirli durumlarda YTM üzerinden otuz günde ödeme öneriyor.'),
    (anchor+'signed-index','initiative','document','Madde 2 reel değer kaybı telafisini de öngörüyor.'),
    (anchor+'agenda-id','action','document','21 Ekim listesi esas ve tali komisyona gönderimi kaydediyor.'),
    (anchor+'detail-committee','action','document','Komisyon giriş alanı 21 Ekim 2026.'),
    (anchor+'detail-pending','action','document','Erişilen TBMM dosyasında işlem Komisyonda.'),
]
eid = event(stem,'2026-10-20','Altıntaş’ın 2/3965 yatırım fonu teklifi',context,evidence,limit)
records['practice_event'][-1]['common_event_key']='tbmm-28-5-2-3965-basvuru'
refs=[row[0] for row in evidence]
scope=readings(topic,'event',refs+[anchor+key for key in ('signed-file','signed-investor','signed-committee-report',
    'party-title','party-day','party-audit','party-payment')])
rid=stem+'-relation'
explanation=stem+'-explanation'
compare = ('Arşiv programı yatırımcı güvenliği hedefi verir. 2/3965, fon denetimi ve belirli yatırımcıların '
           'tazmini için somut yasama araçları önerir.')
explanation_text = ('2/3965 yüzde on risk sınırı, üç ayda bir denetim, yönetici sorumluluğu ve bazı fonlarda otuz '
                    'günde YTM ödemesi öngörüyor. 21 Ekim’de komisyon girişleri kayda geçti. '
                    'Arşiv programının kabul günü ve dönemdeki yürürlüğü açık.')
finding(explanation,explanation_text,[program,program_context,*refs],limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=None,
    explanation_finding_id=explanation,temporal_context='2021 arşiv nüshası, 20 Ekim 2026 başvuru, 21 Ekim 2026 komisyon girişi.',
    authority_context='TBMM imza tablosunda Altıntaş ilk imza sahibi. Komisyon sevki TBMM işlem kaydı.',uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
for kind,claim in (('practice_relation',explanation_text),('practice_relation.target_finding_id',goal),
                   ('practice_relation.explanation_finding_id',explanation_text)):
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
for name,content in [('fund-3965-draft.json',package),('fund-3965-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
