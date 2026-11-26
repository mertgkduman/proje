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
aux=read(here/'six-leaders-nov-2022-v2-source-records.json')
party=aux['party_id']
package=read(data/'practices/04-saadet.json')
review=read(data/'practices/04-saadet-review.json')
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
            boundary_reason='Altı liderin iki planı ve sonraki etkinlikler incelendi.'))
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
        aid=f'six-leaders-nov-2022-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='Altı liderin ortak planları ve sonraki etkinlikleri.',state='examined',attempt_ids=encoded([aid])))
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
assert party=='saadet'
assert sha256((data/'practices/04-saadet.json').read_bytes()).hexdigest()=='5e2a0d33a3557d4bf07ff4b39fcfbd781f4d19ef3e0e7a4f1bb318506b03f53f'
assert sha256((data/'practices/04-saadet-review.json').read_bytes()).hexdigest()=='8a50931788728638d7cdeec3ec39b87fbeedd291ec359d26aa351bfd3f02fd15'
assert (len(records['practice_event']),len(records['practice_relation']),len(records['practice_closure']))==(38,34,0)
topic='siyasal-ittifaklar';src='0411-six-leaders-nov-2022-'
limit='14 Kasım planları altı genel başkanın ortak açıklamasına aittir. 28 Kasım’da öneri kamuoyuna tanıtıldıktan sonra liderler Demokrat Parti ev sahipliğinde toplandı. Tanıtım, TBMM’ye sunulmuş veya kabul edilmiş bir anayasa değişikliği değildir. DEVA bültenindeki imzalı ortak metin görseli okunmuştur, el yazısı imzalar tek tek kişilere atfedilmemiştir.'
cases=[
 dict(short='presentation',stem='0411-saadet-nov-2022-presentation',sp=[src+'meetingplan-present',src+'meetingplan-role'],quote=src+'meetingplan-present',day='2022-11-14',goal='Saadet Genel Başkanı Karamollaoğlu’nun da katıldığı altı lider, anayasa değişikliği çalışmasını 28 Kasım’da kamuoyuyla paylaşacaklarını açıkladı.',period='14 Kasım altı lider ortak açıklamasının Karar haberindeki aktarımı.',event_title='Altı partinin anayasa değişikliği önerisini kamuoyuna tanıtması',context='Altı siyasi partinin 28 Kasım 2022 tarihinde Ankara Bilkent Otel’de anayasa değişikliği önerisini tanıtması.',key='six-party-2022-11-28-constitutional-proposal-presentation',basis='28 Kasım 2022’de Ankara Bilkent Otel’de altı liderin katıldığı tanıtım toplantısını CHP yayımı ve VOA Türkçe haberi belgeliyor. DEVA Partisinin 28. sayı bültenindeki ortak açıklama, önerinin liderler toplantısından önce tanıtıldığını doğruluyor.',ep=[(src+'voa-location','action','document','VOA Türkçe haberi anayasa önerisi tanıtımının Bilkent Otel’de yapıldığını bildiriyor.'),(src+'voa-speakers','result','document','Habere göre Bülent Kaya öneriyi özetleyen altı parti temsilcisinden biriydi.')],extras=[src+'saadet-present'],observed='Altı parti anayasa değişikliği önerisini 28 Kasım’da Bilkent Otel’de tanıttı. Saadet adına Bülent Kaya sunum yapan temsilciler arasındaydı.',compare='14 Kasım ortak açıklamasındaki 28 Kasım tanıtım planı ile aynı gün Bilkent Otel’de yapılan ortak öneri sunumu karşılaştırılıyor.'),
 dict(short='meeting',stem='0411-saadet-nov-2022-meeting',sp=[src+'meetingplan-next',src+'meetingplan-role'],quote=src+'meetingplan-next',day='2022-11-14',goal='Saadet Genel Başkanı Karamollaoğlu’nun da katıldığı altı lider, sonraki buluşmalarını 28 Kasım’da Demokrat Parti ev sahipliğinde yapacaklarını açıkladı.',period='14 Kasım altı lider ortak açıklamasının Karar haberindeki aktarımı.',event_title='Altı liderin Demokrat Parti ev sahipliğindeki toplantısı',context='Altı siyasi parti liderinin 28 Kasım 2022 tarihinde Demokrat Parti Genel Merkezindeki toplantısı.',key='six-leaders-2022-11-28-dp-meeting',basis='28 Kasım 2022’de Demokrat Parti Genel Merkezinde altı liderin yaptığı toplantıyı DEVA Partisinin 28. sayı bültenindeki ortak açıklama ve İHA haberi belgeliyor.',ep=[(src+'iha-host','action','document','İHA haberi toplantının Demokrat Parti Genel Merkezinde ev sahipliğiyle yapıldığını bildiriyor.'),(src+'iha-joint','result','document','İHA haberine göre toplantıdan sonra altı parti ortak metin yayımladı.')],extras=[src+'saadet-meeting'],observed='Altı lider 28 Kasım’da Demokrat Parti Genel Merkezinde toplandı ve ardından ortak açıklama yayımlandı.',compare='14 Kasım ortak açıklamasında duyurulan Demokrat Parti ev sahipliğindeki 28 Kasım buluşması, aynı gün yapılan liderler toplantısıyla karşılaştırılıyor.')]
for c in cases:
 stem=c['stem'];sp=c['sp'];statement,target,quote=(stem+s for s in ('-statement','-target','-quote'));finding(target,c['goal'],sp,'14 Kasım ortak açıklamasının tarihli Karar aktarımı.');finding(quote,passages[c['quote']]['exact'],[c['quote']],'14 Kasım ortak planın aktarımı.',pair=target)
 records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at=c['day'],date_precision='day',version_id=passages[c['quote']]['version_id'],period_basis=c['period'],uncertainty_reason=limit,comparison_row_id='04-03-v3-0311-saadet-scope-siyasal-ittifaklar-row'));readings(topic,'statement',sp)
 for kind,claim in [('practice_statement',c['goal']),('practice_statement.summary_finding_id',c['goal']),('practice_statement.quote_finding_id',passages[c['quote']]['exact'])]:task(kind,statement,claim,limit)
 eid=event(stem,'2022-11-28',c['event_title'],c['context'],c['ep'],limit);records['practice_event'][-1].update(common_event_key=c['key'],occurrence_basis=c['basis'])
 eids=[r[0] for r in c['ep']]+c['extras'];scope=readings(topic,'event',eids);rid,result,explanation=(stem+s for s in ('-relation','-result','-explanation'))
 finding(result,c['observed'],eids,'Tarihli haberler ve partilerin 28 Kasım yayımları.');finding(explanation,c['compare']+' '+limit,sp+eids,limit)
 records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id=party,topic_id=topic,scope_id=scope,comparability_reason=c['compare'],target_finding_id=target,result_finding_id=result,explanation_finding_id=explanation,temporal_context='14 Kasım 2022 ortak planı ve 28 Kasım 2022 etkinliği.',authority_context='14 Kasım planı Saadet dahil altı genel başkanın ortak açıklamasıdır. Tanıtımda Saadet adına Bülent Kaya konuştu. Demokrat Parti liderler toplantısına ev sahipliği yaptı.',uncertainty_reason=limit))
 records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason=c['compare'],passage_ids=encoded(eids)))
 for kind,claim in [('practice_relation',c['compare']),('practice_relation.target_finding_id',c['goal']),('practice_relation.result_finding_id',c['observed']),('practice_relation.explanation_finding_id',c['compare'])]:task(kind,rid,claim,limit)
for entry in entries:
 destination=snapshot.setdefault(entry['kind'],[])
 if entry['values'] not in destination: destination.append(entry['values'])
for table,rows in records.items():
 destination=snapshot.setdefault(table,[]); destination.extend(row for row in rows if row not in destination)
validate_practices(snapshot)
targets=practice_review_package_targets(snapshot,records,[entry['values']['id'] for entry in entries if entry['kind']=='passage'],party)
reviews=review['practice_source_review']
for (kind,identity),(claim,limitation) in tasks.items():
 pids,owners=targets[(kind,identity)]; assert party in owners
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=when,source_version_ids=encoded(sorted({passages[p]['version_id'] for p in pids})),passage_ids=encoded(sorted(pids)),inspected_sections=encoded(sorted({passages[p]['section'] for p in pids})),supported_claim=claim,limitations=limitation,result='reviewed',reason=kind+' için kaynak ve sınırlar incelendi. '+claim))
validate_practice_source_review(snapshot,reviews,target_keys=targets,party_id=party)
refs=[dict(subject_kind=row['subject_kind'],subject_id=row['subject_id']) for row in reviews]; package['source_review_refs']=review['source_review_refs']=refs
for name,content in [('six-leaders-nov-2022-v2-draft.json',package),('six-leaders-nov-2022-v2-review-draft.json',review)]:
 path=here/name
 with path.open('x') as output: output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
 print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
