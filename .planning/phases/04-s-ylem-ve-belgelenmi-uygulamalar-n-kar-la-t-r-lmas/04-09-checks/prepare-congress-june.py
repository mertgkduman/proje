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
def hashlib_sha(path):
    return sha256(path.read_bytes()).hexdigest()
def encoded(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True)
aux=read(here/'congress-june-source-records.json')
party=aux['party_id']
parent_package=here/'research-1056-draft.json'
parent_review=here/'research-1056-review-draft.json'
assert hashlib_sha(parent_package)=='8b1f94c034f0eca3ceefbe35a8872ef676134b80a28be637024caef373e1b05d'
assert hashlib_sha(parent_review)=='94a2c6242b80f6e30f4efc33e1948d95e4de6727f70292819bc7bb983abaab9f'
package=read(parent_package)
review=read(parent_review)
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
topic = 'genel-baskan-secimi'
stem = '0409-dbp-2023-5-olaganustu'
jinha = '0409-policy-dbp-congress-june-jinha-'
ercis = '0409-policy-dbp-congress-june-2023-'
context = ('25 Haziran tarihli JINHAGENCY ve 26 Haziran tarihli Haber Erciş, Ankara’daki DBP 5. Olağanüstü '
           'Kongresinde Saliha Aydeniz ile Keskin Bayındır’ın yeniden eş genel başkan seçildiğini bildirdi.')
limit = ('Yayın tarihleri ayrı ve olay Haziran 2023 olarak kaydedildi. Haber Erciş aday önergesinin oy birliğiyle '
         'kabul edildiğini bildirdi. Seçim tutanağı, kesin oy dökümü, yöntem ve geçerli tüzük nüshası açık.')
refs = [
    (jinha+'venue', 'action', 'independent_report', 'JINHAGENCY Ankara Dünya Ticaret Merkezi’nde 5. Olağanüstü Kongreyi haberleştirdi.'),
    (ercis+'venue', 'action', 'independent_report', 'Haber Erciş aynı sıra ve yerdeki kongreyi 26 Haziran tarihli haberde aktardı.'),
    (jinha+'result', 'result', 'independent_report', 'JINHAGENCY iki ismin yeniden seçildiğini bildirdi.'),
    (ercis+'vote', 'result', 'independent_report', 'Haber Erciş aday önergesinin oy birliğiyle kabulünü ve iki ismin yeniden seçilmesini bildirdi.'),
]
eid = event(stem, None, 'DBP 5. Olağanüstü Kongresinde eş genel başkan seçimi', context, refs, limit)
records['practice_event'][-1].update(date_precision='unknown',
    date_unknown_reason='Haberler 25 ve 26 Haziran 2023’te yayımlandı. Ayrı tarihli bir kongre tutanağı yok.',
    occurrence_basis='Kongrenin yeri ve seçimi 25 ve 26 Haziran tarihli iki haberle belgeleniyor.')
scope = readings(topic, 'event', [jinha+'date', *[x[0] for x in refs]])
reason = ('Bu kongredeki eş genel başkan seçimi tarihli haberlerle belgeleniyor. Olay dönemine ait seçim '
          'maddesi ve uygulanmış oy verme usulü için araştırma sürüyor.')
cid = stem+'-candidate'
records['practice_candidate'].append(dict(id=cid, scope_id=scope, event_id=eid, relation_id=None,
    state='unmatched', reason=reason, passage_ids=encoded([x[0] for x in refs])))
task('practice_candidate', cid, reason, limit)
statement = scope_for(topic, 'statement')
records['practice_attempt_v2'].append(dict(id=stem+'-rules-search', scope_id=statement, attempted_at=when,
    query='DBP 5 olağanüstü kongre 25 Haziran 2023 Dünya Ticaret Merkezi Saliha Aydeniz Keskin Bayındır',
    url=None, result='results', source_version_id=None,
    reason='Haberlerde sıra, yer ve aday önergesi bulundu. Dönemin tam tüzük metni veya oy verme yöntemi gösterilmedi.'))
for entry in entries:
    dest=snapshot.setdefault(entry['kind'],[])
    if entry['values'] not in dest: dest.append(entry['values'])
for table,rows in records.items():
    dest=snapshot.setdefault(table,[])
    dest.extend(row for row in rows if row not in dest)
validate_practices(snapshot)
targets=practice_review_targets(snapshot,records)
reviews=review['practice_source_review']
for (kind,identity),(claim,limit) in tasks.items():
    pids,owners=targets[(kind,identity)]
    assert party in owners
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,
        source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),
        passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),
        supported_claim=claim,limitations=limit,result='reviewed',
        reason=kind+' hedefinin asıl kaynakları, tarihi ve iddia sınırları kontrol edildi. '+claim))
validate_practice_source_review(snapshot,reviews,selection=records,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]
package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('congress-june-draft.json',package),('congress-june-review-draft.json',review)]:
    path=here/name
    with path.open('x') as f:f.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(party,name,sha256(path.read_bytes()).hexdigest())
print(party,len(tasks),'new review targets')
