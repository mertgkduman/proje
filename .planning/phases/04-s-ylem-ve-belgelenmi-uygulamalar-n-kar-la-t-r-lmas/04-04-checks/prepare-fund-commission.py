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
aux=read(here/'fund-commission-source-records.json')
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
        aid=f'fund-commission-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='14 Ekim Plan ve Bütçe Komisyonu tam tutanağı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'yeni-parti'
stem = '0404-fon-komisyon-1014'
topic = 'seffaflik-yolsuzluk'
source = '0404-fund-commission-5472-'
prior = '0404-ilk-yayin-takip-fon-23895-'
program = '0303-epm-program-seffaflik-yolsuzluk-p1'
statement = next(row for row in records['practice_statement'] if row['id']=='0404-fon-denetim-program-statement')
target = statement['summary_finding_id']
limit = ('Komisyondaki oy sonuçları önergelere ve 2/3939 teklifine ait. 2/3895 dosyasının sonraki durumu ayrı. '
         'Takasbank ve SPK açıklamaları bildirdikleri işlem ve kurum değerlendirmesini gösteriyor. TLY hakkındaki '
         '20 Ekim tarihli 7/51538 yazılı sorusunun resmî cevabı bu kayıtlarla doğrulanmış değil.')
evidence = [
    (prior+'id','initiative','document','Özlale’nin daha önce sunduğu ayrı fon teklifinin esas numarası 2/3895.'),
    (source+'ari','action','document','Cavit Arı iki fon teklifinin birlikte görüşülmesini istedi.'),
    (source+'merge-motion','action','document','Başkan Yeni Parti birleştirme önergesini tanıttı. Komisyon tutanağında dört imza var.'),
    (source+'karabat','action','document','Özgür Karabat raporlama ve bağımsız denetimi birleştirme gerekçesi olarak açıkladı.'),
    (source+'spk','action','document','SPK İkinci Başkanı Ahmet Aksu açılışın kurul onayı alınmadan yapıldığının tespit edildiğini bildirdi.'),
    (source+'takasbank','action','document','Takasbank Genel Müdürü Yunus Arıncı 7 Temmuz 2025 açılış, 1 Ağustos bildirimiyle alım tarafının durdurulması ve 6 Ağustos yeniden açılışını anlattı.'),
    (source+'takasbank-basis','action','document','Arıncı Takasbank işleminin KAP bildirimine dayandığını söyledi.'),
    (source+'merge-result','result','document','Komisyon 2/3895 ile 2/3939’u birlikte görüşme önergesini kabul etmedi.'),
    (source+'subcommission','result','document','Komisyon 2/3939 için ayrı alt komisyon önergesini kabul etmedi.'),
    (source+'result','result','document','Komisyon 2/3939 teklifinin tümünü kabul etti.'),
]
context = ('Plan ve Bütçe Komisyonu 2/3939 fon tasfiyesi teklifini görüştü. Yeni Parti’nin 2/3895 ile birleştirme '
           'önergesini ve alt komisyon kurulması için verilen ayrı önergeyi kabul etmedi. Komisyon 2/3939’un tümünü kabul etti.')
eid = event(stem,'2026-10-14','2/3939 fon tasfiyesi teklifinin Plan ve Bütçe Komisyonundaki görüşmesi',
            context,evidence,limit)
records['practice_event'][-1]['common_event_key']='tbmm-28-5-plan-butce-2026-10-14-2-3939'
refs=[row[0] for row in evidence]
scope=readings(topic,'event',refs+[source+'cover',source+'usta',prior+'status'])
rid,result,explanation=(stem+tail for tail in ('-relation','-result','-explanation'))
compare = ('Programın Meclis gözetimi ve bağımsız denetim yaklaşımı, 2/3895’in birlikte görüşülmesi isteğini '
           'savunurken dile getirilen raporlama ve denetim gerekçesiyle aynı politika alanında.')
outcome = ('Komisyon 14 Ekim 2026’da birleştirme ve alt komisyon önergelerini reddetti. '
           '2/3939 teklifinin tümünü kabul etti.')
connection = ('Yeni Parti’nin kuruluş programı Meclis gözetimi ve bağımsız denetim öngörüyor. '
              'Komisyondaki birleştirme gerekçesinde Özgür Karabat, raporlama ve bağımsız denetim istedi. '
              '2/3895’in 2/3939 ile birlikte görüşülmesi ve ayrı alt komisyon önergesi reddedildi. '
              '2/3939 komisyonda kabul edildi.')
finding(result,outcome,[source+'merge-motion',source+'merge-result',source+'subcommission',source+'result'],
    'İki ayrı önergenin oylaması ile komisyonun teklifin tümünü kabulü TBMM tutanağında okundu.')
finding(explanation,connection,[program,prior+'id',source+'karabat',source+'merge-result',source+'subcommission',source+'result'],
    'Program hedefi, iki teklifin kimliği, konuşmacının gerekçesi ve komisyon kararları ayrı kaynaklara bağlı.')
records['practice_relation'].append(dict(id=rid,statement_id=statement['id'],event_id=eid,party_id=party,topic_id=topic,
    scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=explanation,
    temporal_context='24 Temmuz programı, 28 Eylül 2/3895 başvurusu, 14 Ekim komisyon ve 22 Ekim Genel Kurul işlemleri ayrı.',
    authority_context='Başkan birleştirme önergesini Yeni Partiye atfediyor. Ayrı dört imzalı alt komisyon önergesi ve komisyon kararları tutanakta.',
    uncertainty_reason=limit))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,
    state='eligible',reason=compare,passage_ids=encoded(refs)))
target_text = next(row['text'] for row in snapshot['finding'] if row['id']==target)
for kind,claim in (('practice_relation',connection),('practice_relation.target_finding_id',target_text),
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
for name,content in [('fund-commission-draft.json',package),('fund-commission-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
