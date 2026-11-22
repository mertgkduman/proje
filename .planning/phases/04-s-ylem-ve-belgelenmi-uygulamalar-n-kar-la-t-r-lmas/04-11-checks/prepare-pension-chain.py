from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from uygulamalar import practice_review_targets, validate_practice_source_review, validate_practices

here=Path(sys.argv[1])
data=Path('data')
def read(path):
    return json.loads(path.read_bytes())
def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
aux=read(here/'pension-source-records.json')
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
assert party == 'saadet'
topic = 'sosyal-guvenlik'
base = '0411-pension-'
proposal = base+'arikan-3456-'
signed = base+'arikan-3456-signed-'
law_history = base+'pension-law-7573-'
law_text = base+'pension-text-7573-'
group = base+'pension-group-'
submitted = [
    (signed+'signature','initiative','document','İmzalı belgede Saadet Genel Başkanı ve Kayseri Milletvekili Mahmut Arıkan yazıyor.'),
    (signed+'article','initiative','document','1. madde 16.881 TL ibaresini asgari ücret ölçütüyle değiştirmeyi öneriyor.'),
    (proposal+'id','initiative','document','TBMM kaydında esas numarası 2/3456.'),
    (proposal+'submitted','initiative','document','Teklifin TBMM Başkanlığına geliş tarihi 5 Ocak 2026.'),
    (proposal+'referred','action','document','6 Ocak 2026’da esas ve tali komisyona sevk kaydı var.'),
]
proposal_limit = ('Erişilen TBMM kaydı Komisyonda gösteriyor. Esas komisyonun kararı ve yasalaşma sonucu açık. '
                  '21 Ocak açıklaması 5 ve 6 Ocak işlemlerinden sonra.')
proposal_stem = '0411-saadet-2026-2-3456'
proposal_context = ('Mahmut Arıkan’ın 2/3456 teklifi, en düşük emekli aylığında 16.881 TL ibaresinin yerine '
                    'asgari ücret ölçütünü önerdi. Teklif 6 Ocak’ta iki komisyona sevk edildi.')
proposal_id = event(proposal_stem,'2026-01-06','2/3456 en düşük emekli aylığı teklifinin komisyona sevki',
    proposal_context,submitted,proposal_limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-2-3456-komisyona-sevk',
    occurrence_basis='TBMM kayıt sayfasındaki geliş ve sevk tarihleri ile imzalı teklif PDF’si.')
proposal_refs = [row[0] for row in submitted]
scope = readings(topic,'event',[*proposal_refs,proposal+'status',proposal+'initial'])
statement_scope = readings(topic,'statement',['0311-saadet-p2-070-sosyal-guvenlik-p',group+'quote',group+'role',group+'graduated',group+'objection'])
unmatched = proposal_stem+'-candidate'
unmatched_reason = ('2019 kapaklı program insana yaraşır gelir ilkesini içeriyor. Asgari ücrete açık bağ kuran '
                    '21 Ocak 2026 açıklaması sevkten sonra yapıldı. Sevkten önceki aynı eşik araştırılıyor.')
records['practice_candidate'].append(dict(id=unmatched,scope_id=scope,event_id=proposal_id,relation_id=None,
    state='unmatched',reason=unmatched_reason,passage_ids=encoded(proposal_refs)))
task('practice_candidate',unmatched,unmatched_reason,proposal_limit)
records['practice_attempt_v2'].append(dict(id=proposal_stem+'-before-statement-search',scope_id=statement_scope,
    attempted_at=when,query='site:saadet.org.tr emekli maaşı asgari ücret Mahmut Arıkan 2024 2025 Saadet en düşük emekli aylığı',
    url=None,result='results',source_version_id=None,
    reason='2019 programı, 2025 bilgi notu, 2026 kampanyası ve 21 Ocak açıklaması görüldü. Teklif öncesi aynı eşik açık.'))
stem = '0411-saadet-2026-7573'
st = stem+'-statement'
target = stem+'-target'
limit = ('7573, 2/3464 numaralı ayrı teklifin yasama sonucu. 2/3456’nın komisyon ve kanun sonucu açık. '
         'Ocak 2026 ödeme dönemi hükümde yazıyor. Fiilî ödeme ve sonucu ek kayıt gerektirir.')
target_text = ('Saadet Partisi Genel Başkanı Mahmut Arıkan, en düşük emekli aylığının en az asgari ücret '
               'seviyesine çıkarılmasını savundu ve 20.000 TL önerisine karşı çıktı.')
finding(target,target_text,[group+'quote',group+'role',group+'objection'],
    '21 Ocak TBMM haberinde sıfat, somut öneri ve ayrı teklif tutumu okundu.')
finding(stem+'-quote',passages[group+'quote']['exact'],[group+'quote'],
    '21 Ocak TBMM haberinin birebir cümlesi.',pair=target)
records['practice_statement'].append(dict(id=st,party_id=party,topic_id=topic,taxonomy_version=4,
   summary_finding_id=target,quote_finding_id=stem+'-quote',statement_at='2026-01-21',date_precision='day',
   version_id=passages[group+'quote']['version_id'],
   period_basis='21 Ocak 2026 Yeni Yol grup toplantısında Saadet Partisi Genel Başkanı sıfatıyla konuştu.',
   uncertainty_reason=None,comparison_row_id='04-03-v3-0311-saadet-sosyal-guvenlik'))
for kind,claim in (('practice_statement',target_text),('practice_statement.summary_finding_id',target_text),
                   ('practice_statement.quote_finding_id',passages[group+'quote']['exact'])):
    task(kind,st,claim,'Konuşmacının 21 Ocak tutumu. 5 Ocak’ta verilen teklifin hükmü ayrıca kaynaklı.')
accepted = [
    (base+'pension-bill-23464-id','initiative','document','2/3464 esas numarası ayrı teklifin TBMM kaydında.'),
    (law_history+'accept','action','document','TBMM 23 Ocak’ta 7573 sayılı kanunu kabul etti.'),
    (base+'pension-bill-23464-law','result','document','TBMM 2/3464’ü 7573 sayılı kanuna bağladı.'),
    (law_text+'article','result','document','7573 sayılı kanunun 7. maddesi 16.881 TL yerine 20.000 TL getirdi.'),
    (law_text+'effect','result','document','7. madde için Ocak 2026 ödeme döneminden itibaren uygulama öngörüldü.'),
    (law_history+'gazette','result','document','TBMM kanun kaydı 33152 sayılı Resmî Gazete yayımını gösteriyor.'),
]
eid = event(stem,'2026-01-23','2/3464’ten çıkan 7573 sayılı kanunda en düşük emekli aylığı',
    '7573 sayılı kanunun 7. maddesi, en düşük aylıkta 16.881 TL ibaresini 20.000 TL olarak değiştirdi.',accepted,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-050-2-3464-7573',
    occurrence_basis='TBMM yasama kaydı, 23 Ocak kabul kaydı ve 7573 sayılı kanunun tam metni.')
event_refs = [row[0] for row in accepted]
readings(topic,'event',event_refs)
rid = stem+'-relation'
result_id = stem+'-result'
expl = stem+'-explanation'
compare = '21 Ocak açıklaması ve 7573 sayılı kanunun 7. maddesi aynı asgari aylık ödemesinin alt sınırına değiniyor.'
result = ('TBMM 23 Ocak 2026’da 7573 sayılı kanunu kabul etti. 7. madde 20.000 TL belirledi. '
          'Kanun, bu tutarın Ocak 2026 ödeme döneminden itibaren uygulanmasını öngörüyor.')
connection = ('Arıkan en az asgari ücret düzeyini savundu. TBMM ayrı 2/3464 ile sabit 20.000 TL tutarını kabul etti. '
              'Arıkan’ın 2/3456 teklifinin yasama sonucu açık.')
finding(result_id,result,[law_history+'accept',law_text+'article',law_text+'effect'],
    'TBMM kabul kaydı, kanun değişikliği ve yürürlük metni ayrı tek tek okundu.')
finding(expl,connection,[group+'quote',group+'objection',law_history+'accept',law_text+'article',proposal+'status'],
    'İki teklif numarası ve iki farklı eşik özgün TBMM belgelerinden ayrıldı.')
records['practice_relation'].append(dict(id=rid,statement_id=st,event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result_id,
    explanation_finding_id=expl,temporal_context='21 Ocak açıklaması, 23 Ocak kabulü ve 29 Ocak yayımı ayrı günler.',
    authority_context='Arıkan Saadet Genel Başkanı sıfatıyla açıklama yaptı. 7573 TBMM Genel Kurulunun kabul ettiği kanun.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(event_refs)))
for kind,claim in (('practice_relation',connection),('practice_relation.target_finding_id',target_text),
                   ('practice_relation.result_finding_id',result),('practice_relation.explanation_finding_id',connection)):
    task(kind,rid,claim,limit)
for entry in entries:
    dest=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in dest: dest.append(entry['values'])
for table,rows in records.items():
    dest=snapshot.setdefault(table,[])
    dest.extend(row for row in rows if row not in dest)
validate_practices(snapshot)
targets=practice_review_targets(snapshot,records)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limitation,result='reviewed',
        reason=kind+' hedefinin asıl kaynakları, tarihi ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,selection=records,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('pension-draft.json',package),('pension-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
