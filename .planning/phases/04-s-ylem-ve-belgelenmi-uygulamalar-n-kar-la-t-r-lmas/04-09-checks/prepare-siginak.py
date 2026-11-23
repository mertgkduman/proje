"""Record the dated independent shelter report and election context."""

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
aux=read(here/'siginak-source-records.json')
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
            boundary_reason='Belediye hizmeti, İHD raporu ve yerel seçim belgeleri dar kapsamda incelendi.'))
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
        aid=f'siginak-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Konuya ilişkin bağımsız saha raporu, yerel seçim veya parti derlemesi.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='İHD Diyarbakır Şubesi raporu ve yayımlayanın tarihli dizin kaydı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'dbp'
topic = 'yerel-demokrasi'
stem = '0409-diyarbakir-2016-siginak'
src = '0409-siginak-'
day = '2016-03-10'
limit = ('10 Mart raporun yayın tarihi. Görüşme günleri ve belediye bazında dağılım açık. '
         'Görüşme grubu belediyelerin toplam hizmet kullanıcısını veya hizmet etkisini göstermiyor. '
         'Seçim sonuçları 2014 dönem bağlamını gösteriyor. Belediyelerin sığınak açma kararları, '
         'harcamaları ve DBP’nin bu hizmetteki yetkili katkısı araştırmaya açık.')
context = ('İHD Diyarbakır Şubesi Kadın Komisyonu, Diyarbakır Büyükşehir Belediyesi ve Bağlar Belediyesi '
           'birimlerine başvuruların karşılanması sonrasında 17 kadınla yaptığı görüşmeleri yayımladı.')
evidence = [
    (src+'index-date','action','document','İHD yayın dizini raporu 10 Mart 2016 tarihine yerleştiriyor.'),
    (src+'index-link','action','document','Yayın dizini aynı beş sayfalı özgün rapora bağlanıyor.'),
    (src+'ihd-decision','initiative','independent_report','İHD kendi araştırma kararının 12 Ocak 2015 tarihinde alındığını bildiriyor.'),
    (src+'ihd-institutions','result','independent_report','Rapor Diyarbakır Büyükşehir ve Bağlar’daki iki belediye birimini ayrı tanımlıyor.'),
    (src+'ihd-sample','result','independent_report','Rapor 17 kadınla onama dayalı görüşme yapıldığını kaydediyor.'),
    (src+'ihd-support','result','independent_report','Rapor görüşmelerde barınma ve temel ihtiyaç desteğine ilişkin olumlu yanıtlar aktarıyor.'),
    (src+'ihd-gap','result','independent_report','Rapor kalış süresiyle ilgili yeterli bilgilendirme yapılmadığını kaydediyor.'),
]
eid = event(stem,day,'İHD’nin Diyarbakır’da sığınma evi görüşmelerini yayımlaması',context,evidence,limit)
refs = [row[0] for row in evidence]
scope = readings(topic,'event',refs+[src+key for key in (
    'ihd-credit','ihd-recommendations','ihd-followup','ysk-big-name','ysk-big-party',
    'ysk-district-name','ysk-district-party','dbp-report-shelters',
)])
reason = ('YSK iki belediyenin 2014 seçim bağlamını gösteriyor. İHD raporu hizmetlerin tanıklığa dayalı bir kesitini sunuyor. '
          'Sığınma evi hizmetinden önceki tarihli, aynı kapsamda bir parti taahhüdü araştırmaya açık.')
records['practice_candidate'].append(dict(id=stem+'-unmatched',scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(refs)))
task('practice_candidate',stem+'-unmatched',reason,limit)

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
for name,content in [('siginak-draft.json',package),('siginak-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
