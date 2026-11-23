"""Record the 2/4012 proposal and its source boundaries."""

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
aux=read(here/'internet-4012-source-records.json')
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
            boundary_reason='Teklif, işleme giriş ve yürürlük bağlamı özgün TBMM kaynaklarında okundu.'))
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
        aid=f'internet-4012-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='İnternet teklifine ve kanuni yaş doğrulama çerçevesine ilişkin TBMM kaydı.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='TBMM’nin teklif sicili, ilk imzalı nüsha ve Gelen Kâğıtlar bülteni.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party == 'demokrat'
topic = 'ifade-basin-ozgurlugu'
source = '0412-internet-4012-'
stem = '0412-demokrat-2026-2-4012'
context = ('Demokrat Parti İzmir Milletvekili Haydar Altıntaş’ın 2/4012 teklifi 3 Kasım 2026’da TBMM Başkanlığına ulaştı. '
           'Teklif sosyal ağlarda yaş doğrulamasında kimlik verilerini sınırlamayı, bant daraltma hükümlerini kaldırmayı '
           've haksız hesap kısıtına karşı harçsız mahkeme başvurusu getirmeyi öngörüyor.')
limit = ('İmzalı teklif 2 Kasım, TBMM’ye geliş 3 Kasım, Adalet ve Dijital Mecralar komisyonlarına giriş 5 Kasım. '
         'Erişilen TBMM dosyasında iki komisyon için durum Komisyonda. Kabul, yürürlük ve fiilî sonuç açık.')
reason = ('Arşivde aynı yaş doğrulama, bant daraltma ve başvuru araçları için önceden açıklanmış '
          'tarihli ve doğrudan karşılaştırılabilir Demokrat Parti hedefi araştırılıyor.')
evidence = (
    ('detail-id','initiative','TBMM belge esas numarası 2/4012.'),
    ('detail-membership','initiative','İlk imza Demokrat Parti İzmir Milletvekili Haydar Altıntaş’a ait.'),
    ('signed-signature','initiative','İmzalı teklif yazısı 2 Kasım 2026 tarihli.'),
    ('detail-filed','initiative','Başkanlığa geliş tarihi 3 Kasım 2026.'),
    ('signed-age','initiative','Madde 1 kimlik bilgisi içermeyen tek kullanımlık yaş doğrulama belirteci öngörüyor.'),
    ('signed-privacy','initiative','Madde 1 kimlik ve banka veya kredi kartı bilgisi ile biyometrik verinin talep edilmesine, işlenmesine ve saklanmasına yasak öneriyor.'),
    ('signed-blind','initiative','Madde 1 doğrulama belirtecinde çift yönlü körleştirme ve kamunun eşleştirme kaydı tutmasına yasak öneriyor.'),
    ('signed-limit','initiative','Madde 2 yüzde 50 ve yüzde 90’a kadar bant daraltma hükümlerini kaldırmayı öneriyor.'),
    ('signed-court','initiative','Madde 2 haksız hesap kısıtında yerleşim yeri sulh hukuk hâkimliğine harçsız başvuru ve en geç beş iş günü içinde karar öneriyor.'),
    ('detail-committee','action','Sicil iki komisyon için 5 Kasım 2026 girişini gösteriyor.'),
    ('gelen-listed','action','5 Kasım bülteni Dijital Mecralar ve Adalet komisyonlarını 2/4012 ile birlikte listeliyor.'),
    ('detail-pending','action','Erişilen sicilde iki komisyonun durumu Komisyonda.'),
)
refs = [(source+pid,stage,'document',claim) for pid,stage,claim in evidence]
eid = event(stem,'2026-11-03','Altıntaş’ın 2/4012 internet düzenlemesi teklifi',context,refs,limit)
records['practice_event'][-1]['common_event_key'] = 'tbmm-28-5-2-4012-basvuru'
evidence_ids = [row[0] for row in refs]
legal_context = [source+suffix for suffix in ('lawregister-approval','lawregister-publication','law-age','law-term')]
scope = readings(topic,'event',evidence_ids+legal_context+[source+'signed-routing'])
candidate = stem+'-unmatched'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,relation_id=None,
    state='unmatched',reason=reason,passage_ids=encoded(evidence_ids)))
task('practice_candidate',candidate,reason,limit)

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
for name,content in [('internet-4012-draft.json',package),('internet-4012-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
