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
aux=read(here/'three-dossiers-source-records.json')
party=aux['party_id']
package=read(here/'siber-7545-draft.json')
review=read(here/'siber-7545-review-draft.json')
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
            boundary_reason='İki kanun teklifi, bir yazılı soru ve ilgili kamu açıklamaları okundu.'))
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
        aid=f'three-dossiers-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Teklif, önerge, TBMM sicili veya önceki açık kamu tutumu.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='TBMM esas kaydı ve imzalı başvuru metni.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='demokrat'
assert sha256((here/'siber-7545-draft.json').read_bytes()).hexdigest()=='b34d00127a035ca541e9d8144ea2f6eeb841ee45c4beab97115b683be4e7dcff'
assert sha256((here/'siber-7545-review-draft.json').read_bytes()).hexdigest()=='029f631fb9347fbe39dbd616f7c9743302c3b5c527fe3882264da6aea05fc9ff'
stem='0412-three-dossiers'
src=stem+'-'

bills=(
 ('city','yerel-demokrasi','2024-11-05','2025-05-22','tbmm-28-3-2-3139',
  '2/3139 Belediye Kanunu değişikliği teklifi',
  'Gültekin Uysal 5 Kasım 2024’te kayyım uygulamasına karşı olduğunu açıkladı.',
  '2/3139 22 Mayıs 2025’te sunuldu. Teklif belediye başkanlığı boşaldığında veya başkan uzaklaştırıldığında belediye meclisi içinden seçim öngörüyor.',
  '23 Mayıs İçişleri Komisyonu sevki sicilde kayıtlı. Erişimde Komisyonda.',
  'TBB ve Demokrat Parti görüşmesi 5 Kasım 2024. Kişisel imzalı teklif 22 Mayıs 2025.',
  'Uysal görüşünü parti genel başkanı olarak açıkladı. 2/3139’un ilk imzacısı Haydar Altıntaş.',
  'Kayyım uygulamasına itiraz ile belediye meclisi içinden seçim öneren yasal girişim aynı yerel temsil alanında.',
  'İmzalı metnin üçüncü ve dördüncü maddelerinde aynı 45. maddeye farklı işlemler var. Şablonun kökeni, komisyon kararı ve uygulama açık.',
  '04-03-v3-0313-demokrat-yerel-demokrasi',
  (
      ('city-register-number','initiative','Esas numarası 2/3139.'),
      ('city-register-filing','action','Başkanlığa geliş 22 Mayıs 2025.'),
      ('city-signed-number','initiative','İmzalı teklif 2/3139 olarak işaretli.'),
      ('city-signed-selection','initiative','İmzalı metin belediye meclisi üyeleri arasından seçim öngörüyor.'),
      ('city-signed-article3','initiative','Teklifin üçüncü maddesi 5393 sayılı Kanunun 45. maddesini değiştiriyor.'),
      ('city-signed-article4','initiative','Teklifin dördüncü maddesi de aynı 45. maddenin kaldırılmasını söylüyor.'),
      ('city-register-committee','action','23 Mayıs İçişleri Komisyonu kaydı.'),
      ('city-register-status','result','Sicil erişimde Komisyonda.'),
  )),
 ('penal','cezaevleri','2024-10-01','2025-05-26','tbmm-28-3-2-3144',
  '2/3144 infaz ve ceza kanunu değişikliği teklifi',
  'Gültekin Uysal, 1 Ekim 2024’te parti sitesinde yayımlanan söyleşisinde yeni ceza kanunu düzenlemesi istedi ve iktidarın af yetkisine karşı çıktı.',
  '2/3144 26 Mayıs 2025’te sunuldu. Koşullu salıverilme genel süresi ve suçta tekerrür için değişiklik önerdi.',
  '28 Mayıs Adalet Komisyonu sevki sicilde kayıtlı. Erişimde Komisyonda.',
  'Söyleşinin parti yayını 1 Ekim 2024. Teklif 26 Mayıs 2025 başvurusu.',
  'Uysal görüşünü parti genel başkanı olarak açıkladı. 2/3144’ün ilk imzacısı Haydar Altıntaş.',
  'Genel ceza reformu çağrısı ile koşullu salıverilme ve tekerrüre ilişkin daha dar yasama girişimi aynı infaz alanında.',
  'Kanunlaşma ve uygulama açık. Uysal’ın af yetkisine ilişkin geniş önerisinin bu dosyada nasıl karşılandığı ayrıca araştırılıyor.',
  '04-03-v3-0313-demokrat-scope-cezaevleri-row',
  (
      ('penal-register-number','initiative','Esas numarası 2/3144.'),
      ('penal-register-filing','action','Başkanlığa geliş 26 Mayıs 2025.'),
      ('penal-signed-number','initiative','İmzalı teklif 2/3144 olarak işaretli.'),
      ('penal-signed-ratio','initiative','Genel gerekçe koşullu salıverilme için dörtte üç oranı öneriyor.'),
      ('penal-signed-recidivism','initiative','Taslak suçta tekerrüre ilişkin değişiklik içeriyor.'),
      ('penal-register-committee','action','28 Mayıs Adalet Komisyonu kaydı.'),
      ('penal-register-status','result','Sicil erişimde Komisyonda.'),
  )),
)
for label,topic,speech_day,day,key,title,goal,context,result,temporal,authority,compare,limit,row,anchors in bills:
    event_stem=f'{stem}-{label}'
    basis='TBMM esas sicili ve imzalı kanun teklifi.'
    quote_pid=src+label+'-statement-quote'
    quote_text=passages[quote_pid]['exact']
    statement_pids=[quote_pid,src+label+'-statement-context']
    statement,target,quote=(event_stem+suffix for suffix in ('-statement','-target','-quote'))
    finding(target,goal,statement_pids,goal)
    finding(quote,quote_text,[quote_pid],'Yayın metnindeki kısa özgün ifade.',pair=target)
    records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
        summary_finding_id=target,quote_finding_id=quote,statement_at=speech_day,date_precision='day',
        version_id=passages[quote_pid]['version_id'],period_basis='Tarihli TBB veya parti yayını.',
        uncertainty_reason=limit,comparison_row_id=row))
    readings(topic,'statement',statement_pids)
    for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
                       ('practice_statement.quote_finding_id',quote_text)):
        task(kind,statement,claim,limit)
    evidence=[(src+pid,stage,'document',claim) for pid,stage,claim in anchors]
    event_id=event(event_stem,day,title,context,evidence,limit)
    records['practice_event'][-1].update(common_event_key=key,occurrence_basis=basis)
    pids=[r[0] for r in evidence]
    scope=readings(topic,'event',pids)
    rid,result_id,explanation=(event_stem+suffix for suffix in ('-relation','-result','-explanation'))
    finding(result_id,result,pids,basis)
    finding(explanation,compare+' '+limit,statement_pids+pids,limit)
    records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=event_id,party_id=party,
        topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,
        result_finding_id=result_id,explanation_finding_id=explanation,temporal_context=temporal,
        authority_context=authority,uncertainty_reason=limit))
    records['practice_candidate'].append(dict(id=event_stem+'-candidate',scope_id=scope,event_id=event_id,
        relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(pids)))
    for kind,claim in (('practice_relation',compare),('practice_relation.target_finding_id',goal),
                        ('practice_relation.result_finding_id',result),('practice_relation.explanation_finding_id',compare)):
        task(kind,rid,claim,limit)

dispute=stem+'-city-article-dispute'
dispute_summary=dispute+'-finding'
dispute_text='2/3139’un üçüncü maddesi 5393 sayılı Kanunun 45. maddesini değiştiriyor. Dördüncü madde aynı 45. maddeyi kaldırıyor.'
dispute_limit='İki atıf aynı imzalı nüshada. Düzeltme veya gerekçe açıklaması açık.'
evidence=(
 (src+'city-signed-article3','Üçüncü maddede 45. maddenin değiştirilmesi.','support'),
 (src+'city-signed-article4','Dördüncü maddede aynı 45. maddenin kaldırılması.','conflict'),
)
finding(dispute_summary,dispute_text+' '+dispute_limit,[r[0] for r in evidence],dispute_limit)
records['practice_dispute'].append(dict(id=dispute,event_id=stem+'-city-event',summary_finding_id=dispute_summary,
    supported_points='Her iki hüküm imzalı teklifin ayrı sayfalarında yer alıyor.',
    disputed_points=dispute_text,unresolved_points=dispute_limit))
task('practice_dispute',dispute,dispute_text,dispute_limit)
task('practice_dispute.summary_finding_id',dispute,dispute_text,dispute_limit)
for pid,point,role in evidence:
    section=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,
        source_position=section,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,section)

event_stem=stem+'-drug'
topic='sagliga-erisim'
title='7/20085 ile ilaç teminine ilişkin yazılı soru'
context='Haydar Altıntaş’ın ilaç teminiyle ilgili yazılı sorusu 5 Aralık 2024’te Başkanlığa geldi. 7 Ocak 2025’te süresinde cevaplanmayanlar arasında ilan edildi.'
limit='Gerekçedeki ilaç sayısı TEB’e atfediliyor. Özgün TEB dökümü ve sonraki Bakanlık cevabı açık.'
proof=(
 ('drug-signed-signature-date','initiative','İmzalı soru 4 Aralık 2024 tarihli.'),
 ('drug-signed-questions','initiative','Soru ilaç arzına yönelik tedbir ve teşvikleri kapsıyor.'),
 ('drug-signed-teb-attribution','initiative','Metin 2.500’ü aşan miktarı TEB açıklamasına dayandırıyor.'),
 ('drug-register-number','action','Esas numarası 7/20085.'),
 ('drug-register-filing','action','Başkanlığa geliş 5 Aralık 2024.'),
 ('drug-filed-filing','action','13 Aralık basılı tutanağı geliş tarihini de doğruluyor.'),
 ('drug-notice-heading','result','7 Ocak basılı tutanağı süresinde cevaplanmayanlar başlığını taşıyor.'),
 ('drug-notice-item','result','7/20085 listede 84. sırada.'),
 ('drug-register-status','result','Esas sicili erişimde cevapsızlık ilanı durumunu gösteriyor.'),
)
references=[(src+pid,stage,'document',claim) for pid,stage,claim in proof]
event_id=event(event_stem,'2024-12-05',title,context,references,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-3-7-20085',
    occurrence_basis='İmzalı soru, TBMM sicili ve iki tarihli basılı tutanak eki.')
pids=[r[0] for r in references]
scope=readings(topic,'event',pids)
candidate=event_stem+'-candidate'
reason='Parti programının katkı payı hedefi ilaç tedarikine özel bir önceki söylem dayanağı sağlamıyor. Uygun dönemsel söylem araştırması açık.'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=event_id,
    relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(pids)))
task('practice_candidate',candidate,context,reason+' '+limit)

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
for name,content in [('three-dossiers-draft.json',package),('three-dossiers-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
