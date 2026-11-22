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
aux=read(here/'statistics-source-records.json')
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
        aid=f'statistics-reading-{lane}-{topic}-{vid}'
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
assert party == 'demokrat'
stem = '0412-demokrat-2026-2-4030'
topic = 'makroekonomik-politika'
registry = '0412-stat-dp-4030-'
signed = '0412-stat-dp-4030-signed-'
summary = ('Demokrat Parti İzmir Milletvekili Haydar Altıntaş, TÜFE ve Yİ-ÜFE sepetlerini, '
           'ağırlıkları ve aylık birim fiyatları açıklamayı, bağımsız bir doğrulama kurulu kurmayı önerdi.')
limit = ('İmzalı teklif ve TBMM kaydı 6 Kasım 2026 gelişini gösteriyor. Sicildeki 10 Kasım komisyon '
         'giriş saati açık. Kanunlaşma, verilerin yayımlanması ve kurulun kurulmasına ilişkin sonuç açık.')
evidence = [
    (registry+'id','initiative','document','Esas numarası 2/4030.'),
    (registry+'filed','initiative','document','TBMM teklifin 6 Kasım 2026 gelişini kaydediyor.'),
    (signed+'signature','initiative','document','İmzalı belgede İzmir Milletvekili Haydar Altıntaş adı var.'),
    (signed+'date-stamp','initiative','document','Tarama görüntüsündeki kaşe 6 Kasım 2026 gelişini gösteriyor.'),
    (signed+'transparency','initiative','document','1. madde sepeti, ağırlıkları, veri derleme yöntemlerini ve aylık fiyatları kapsıyor.'),
    (signed+'publication','initiative','document','Verinin işlenebilir elektronik biçimde kamuya açılması öneriliyor.'),
    (signed+'review','initiative','document','Bağımsız Fiyat ve Veri Doğrulama Kurulu öngörülüyor.'),
    (signed+'reports','initiative','document','Kurulun her ay rapor yayımlaması ve TBMM komisyonuna sunması öneriliyor.'),
]
eid = event(stem,'2026-11-06','2/4030 ile TÜİK fiyat verilerinin açıklanması önerisi',summary,evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-5-2-4030-basvuru',
    occurrence_basis='TBMM yasama kaydı ve 6 Kasım tarihli imzalı teklif.')
refs = [r[0] for r in evidence]
scope = readings(topic,'event',refs+[signed+'date',registry+'commission',registry+'status'])
reason = ('Altıntaş imzalı 2/4030 teklifinin geliş tarihi, önerdiği veri alanları ve kurul belgelendi. '
          'Aynı veri yayımı ve bağımsız kurul araçlarını önceleyen Demokrat Parti açıklaması araştırılıyor.')
cid = stem+'-candidate'
records['practice_candidate'].append(dict(id=cid,scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(refs)))
task('practice_candidate',cid,reason,limit)
statement_scope = scope_for(topic,'statement')
records['practice_attempt_v2'].append(dict(id=stem+'-statement-search',scope_id=statement_scope,
    attempted_at=when,query='Haydar Altıntaş TÜİK sepeti veri açıklama bağımsız kurul 6 Kasım 2026 öncesi site:tbmm.gov.tr OR site:dp.org.tr',
    url=None,result='results',source_version_id=None,
    reason='Nisan 2026 TÜİK tartışmasında benzer denetim çağrısı İYİ Parti Grubu adına Burak Dalgın’a ait. Demokrat Parti’nin 2/4030 araçlarını önceleyen tarihli kayıt açık.'))
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
for name,content in [('statistics-draft.json',package),('statistics-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
