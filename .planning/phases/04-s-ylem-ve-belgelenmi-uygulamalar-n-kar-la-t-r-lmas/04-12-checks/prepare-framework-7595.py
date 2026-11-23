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
aux=read(here/'framework-7595-source-records.json')
party=aux['party_id']
package=read(here/'tax-deferral-draft.json')
review=read(here/'tax-deferral-review-draft.json')
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
            boundary_reason='Çerçeve kanun görüşü, işleme alınması ve oylama kayıtları okundu.'))
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
        aid=f'framework-7595-reading-{lane}-{topic}-{vid}'
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
        occurrence_basis='Birden fazla yayımlanmış açıklamada toplantı ve tarih doğrulandı.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='demokrat'
topic='kurt-sorunu'
stem='0412-framework-7595'
src=stem+'-'
context='TBMM, 2/3793 esas ve 290 sıra sayılı teklifi 10 Ağustos 2026 tarihli 125. Birleşimde kabul etti. 7595 sayılı Kanun 18 Ağustos’ta yayımlandı.'
limit=('Kesin cetvel ve birleşim sırasında okutulan sayılar farklı. TBMM her iki kayıtta kabulü gösteriyor. '
       'MGK teyidinin Resmî Gazete yayımı ve kişiye özgü erteleme kararları araştırmaya açık.')
evidence=[
    (src+'proposal-number','initiative','document','Teklif 2/3793 esas numarasıyla kaydedildi.'),
    (src+'proposal-filed','initiative','document','Teklifin Başkanlığa geliş günü 5 Ağustos 2026.'),
    (src+'proposal-report','action','document','Adalet Komisyonu 8 Ağustos tarihli raporu verdi.'),
    (src+'signed-date','initiative','document','İmzalı dosya üstünde 5 Ağustos ve 2/3793 evrak kaydı var.'),
    (src+'minutes-two-columns','action','document','Basılı kesin cetvelde maddelere geçme ve teklifin tümü için iki ayrı sütun var.'),
    (src+'minutes-nominal','action','document','İzmir milletvekili Haydar Altıntaş DP hanesinde. İlk oylamada katılmamış, teklifin tümüne ret yazıyor.'),
    (src+'minutes-conclusion','result','document','Birleşim başkanı teklifin kabul edildiğini açıkladı.'),
    (src+'minutes-official-count','result','document','Kesin cetvel teklifin tümünde 467 kabul, 87 ret ve 7 çekimser oy gösteriyor.'),
    (src+'minutes-duplicates','result','document','Kesin cetvelde iki mükerrer oy dahil 563 kayıt var.'),
    (src+'register-accepted','result','document','TBMM sicilinde Kanunun kabul tarihi 10 Ağustos.'),
    (src+'register-published','result','document','Kanunun Resmî Gazete yayım günü 18 Ağustos.'),
    (src+'register-issue','result','document','Yayım 33344 sayılı Resmî Gazete’de yapıldı.'),
    (src+'law-condition','result','document','1. madde ilgili MGK teyidinin Resmî Gazete’de yayımlanmasını şart koşuyor.'),
    (src+'law-exceptions','result','document','3. maddede örgüt faaliyeti kapsamında kasten öldürme suçu istisnalar arasında.'),
    (src+'law-effect','result','document','11. madde Kanunun yayım günü yürürlüğe gireceğini belirtiyor.'),
]
eid=event(stem,'2026-08-10','2/3793 teklifinin tümünün açık oylamada kabulü',context,evidence,limit)
records['practice_event'][-1].update(common_event_key='tbmm-28-4-125-2-3793-7595-kabul',
    occurrence_basis='TBMM 28. Dönem 4. Yasama Yılı 125. Birleşim basılı tutanağı ve kesin oy cetveli, 2/3793 teklif kaydı ve 7595 sayılı Kanun sicili.')
pids=[row[0] for row in evidence]
announced=src+'minutes-announced'
scope=readings(topic,'event',pids+[announced,src+'identity-speaker',src+'membership-party',src+'membership-tally'])

statement,target,quote=(stem+suffix for suffix in ('-statement','-target','-quote'))
goal='Demokrat Parti 7 Ağustos’ta çerçeve kanun sürecine itiraz etti ve PKK’nın Kürt kökenli vatandaşların temsilcisi ya da vasisi olarak konumlandırılmasına karşı olduğunu açıkladı.'
statement_pids=[src+'statement-day',src+'statement-target']
finding(target,goal,statement_pids,'7 Ağustos parti açıklamasının dar tutumu ve yayın günü ayrı okundu.')
finding(quote,passages[src+'statement-quote']['exact'],[src+'statement-quote'],'Parti açıklamasındaki yayımlanmış itiraz.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at='2026-08-07',date_precision='day',
    version_id=passages[src+'statement-target']['version_id'],period_basis='Partinin 7 Ağustos 2026 tarihli resmî açıklaması.',
    uncertainty_reason='Açıklama partinin tutumu ve önceden taslak dolaşımı iddiasını içeriyor. 5 Ağustos TBMM geliş kaydı ve sonraki aşamalar TBMM kaynaklarında.',
    comparison_row_id='04-03-v3-0313-demokrat-kurt-sorunu'))
readings(topic,'statement',statement_pids+[src+'statement-quote'])
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[src+'statement-quote']['exact'])):
    task(kind,statement,claim,'Parti tutumu kaynaklandı. Önceki taslak dolaşımı iddiası ayrıca araştırılıyor.')

rid,result,explanation=(stem+suffix for suffix in ('-relation','-result','-explanation'))
observed=('Teklifin tümü 10 Ağustos’ta kabul edildi. Kesin cetvelde DP milletvekili Haydar Altıntaş’ın ret oyu var. '
          'Kanun 18 Ağustos’ta yayımlandı. İlgili erteleme hükümlerinin uygulanması MGK teyidinin yayımlanması koşuluna bağlı.')
compare=('7 Ağustos Demokrat Parti açıklaması ve 10 Ağustos Altıntaş’ın ret oyu aynı çerçeve kanun sürecine ilişkin. '
         'Partinin itirazı ve milletvekilinin kişisel oyu ayrı kaynaklandı. Kanun TBMM’de kabul edildi.')
finding(result,observed,pids,'TBMM kabul tarihi, oylama cetveli ve yayımlanmış m.1 ile m.11 birlikte okundu.')
finding(explanation,compare+' '+limit,statement_pids+pids,limit)
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,
    topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,result_finding_id=result,
    explanation_finding_id=explanation,temporal_context='5 Ağustos başvuru, 7 Ağustos parti tutumu, 10 Ağustos oylama ve 18 Ağustos yayım.',
    authority_context='Demokrat Parti kendi tutumunu açıkladı. Altıntaş kendi oyunu kullandı. Kabul TBMM’ye, sonraki özel işlemler yetkili kurumlara ait.',
    uncertainty_reason=limit))
candidate=stem+'-candidate'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,
    relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(pids)))
for kind,claim in (
    ('practice_relation',compare),('practice_relation.target_finding_id',goal),
    ('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare),
):
    task(kind,rid,claim,limit)

person,actor,contribution,contribution_finding=(stem+suffix for suffix in (
    '-person','-actor','-contribution','-contribution-finding'))
nominal=src+'minutes-nominal'
new('person',id=person,name='Haydar Altıntaş')
new('actor',id=actor,kind='individual_mp',party_id=party,person_id=person,authorization_passage_id=None)
role=('Kesin oy cetvelindeki DP milletvekili Haydar Altıntaş maddelere geçilmesi oylamasına katılmadı. '
      'Teklifin tümüne ret oyu verdi.')
finding(contribution_finding,role,[src+'minutes-two-columns',nominal,src+'identity-speaker',src+'membership-party'],
    'Basılı 319 ve 327. sayfalarda başlık, iki oy sütunu ve DP parti hanesi ayrı kontrol edildi.')
records['practice_contribution'].append(dict(id=contribution,event_id=eid,party_id=party,actor_id=actor,
    contribution_kind='objection',finding_id=contribution_finding,authority_passage_id=None,
    membership_passage_id=src+'membership-party',responsibility_limit='Cetvel kişisel oyu, DP hanesini ve 10 Ağustos oturumunu gösteriyor.'))
records['practice_actor_period'].append(dict(contribution_id=contribution,valid_from='2026-08-10',
    valid_to='2026-08-10',identity_passage_id=src+'identity-speaker'))
task('practice_contribution',contribution,role,'İki oy sütunu ve kişisel oy ayrı okundu.')
task('practice_contribution.finding_id',contribution,role,'İlk sütun maddelere geçiş, ikinci sütun teklifin tümü.')

dispute=stem+'-vote-dispute'
dispute_summary=dispute+'-finding'
dispute_text=('Birleşimde okutulan sonuç 562 oy, 468 kabul, 88 ret ve 6 çekimser. '
              'Kesin cetvel 467 kabul, 87 ret, 7 çekimser ve 2 mükerrer dahil 563 kayıt gösteriyor. '
              'İki kaynak da teklifin kabul edildiğini gösteriyor.')
dispute_pids=[announced,src+'minutes-official-count',src+'minutes-duplicates']
finding(dispute_summary,dispute_text,dispute_pids,'Basılı 318. sayfadaki ilk ilan ve 319. sayfadaki kesin cetvel ayrı okundu.')
records['practice_dispute'].append(dict(id=dispute,event_id=eid,summary_finding_id=dispute_summary,
    supported_points='Birleşim ilanı ve kesin cetvel teklifin kabul edildiği konusunda uyuşuyor.',
    disputed_points='Birleşim sırasında 468 kabul, 88 ret ve 6 çekimser açıklandı. Kesin cetvel 467 kabul, 87 ret, 7 çekimser ve 2 mükerrer gösteriyor.',
    unresolved_points='İlk ilanın kesin cetvele nasıl dönüştüğüne ilişkin ayrı düzeltme işlemi araştırılıyor.'))
task('practice_dispute',dispute,dispute_text,'İlk ilan ve kesin cetvel ayrı. İki mükerrer kesin cetvelde.')
task('practice_dispute.summary_finding_id',dispute,dispute_text,'Kabul sonucu ortak. Sayılar kendi kayıtlarına atfedildi.')
for pid,point,role in (
    (announced,'Birleşimde 562 toplam, 468 kabul, 88 ret ve 6 çekimser açıklandı.','conflict'),
    (src+'minutes-official-count','Kesin cetvelde 467 kabul, 87 ret ve 7 çekimser var.','support'),
    (src+'minutes-duplicates','Kesin cetvelde toplam 563 kayıt ve iki mükerrer oy var.','support'),
):
    position=passages[pid]['section']
    records['practice_dispute_evidence'].append(dict(dispute_id=dispute,passage_id=pid,point=point,
        source_position=position,role=role))
    task('practice_dispute_evidence','|'.join((dispute,pid,point,role)),point,position)

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
for name,content in [('framework-7595-draft.json',package),('framework-7595-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
