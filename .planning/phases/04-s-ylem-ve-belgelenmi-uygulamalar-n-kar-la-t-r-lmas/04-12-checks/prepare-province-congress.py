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
aux=read(here/'province-congress-source-records.json')
party=aux['party_id']
package=read(here/'kucukbas-v2-draft.json')
review=read(here/'kucukbas-v2-review-draft.json')
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
            boundary_reason='İl kongresinin tarihsel tüzük maddesi ve uygulama haberleri okundu.'))
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
        aid=f'province-congress-reading-{lane}-{topic}-{vid}'
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=sid,attempted_at=when,query=url,url=url,
            result='examined',reason='Belgenin belirtilen bölümü ve aktör bağlamı özgün nüshada okundu.',source_version_id=vid))
        records['practice_scope_source'].append(dict(scope_id=sid,version_id=vid,inspected_at=when,
            inspected_sections=encoded(sorted(sections))))
        if not any(l['scope_id']==sid and l['url']==url for l in records['practice_lead']):
            records['practice_lead'].append(dict(id='lead-'+aid,scope_id=sid,url=url,
                relevance_reason='İl kongresi, seçim veya organ listesi hakkında kaynak.',state='examined',attempt_ids=encoded([aid])))
    return sid
def event(stem,day,title,context,refs,limit):
    eid=stem+'-event'
    records['practice_event'].append(dict(id=eid,common_event_key=stem,event_at=day,date_precision='day',
        date_unknown_reason=None,title=title,scope_context=context,
        occurrence_basis='Kongreye ilişkin tarihli yerel haber.'))
    for pid,stage,basis,point in refs:
        records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,stage=stage,
            supported_point=point,concrete_basis=passages[pid]['section'],limitation=limit,epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage=stage,basis_kind=basis))
        task('practice_event_evidence','|'.join((eid,pid,stage)),point,limit)
    task('practice_event',eid,context,limit)
    return eid
assert party=='demokrat'
assert sha256((here/'kucukbas-v2-draft.json').read_bytes()).hexdigest()=='36f61414fb9f6eff55fa2850ace673eb22b71e23a5467b09c725d458ee06b735'
assert sha256((here/'kucukbas-v2-review-draft.json').read_bytes()).hexdigest()=='708c183f18ee2cb4aa26e15cbc16b479c1ce6d316b498cbdf934947afe1cf52a'
topic='orgut-il-kongre'
stem='0412-province-congress'
src=stem+'-'
statement,target,quote=(stem+label for label in ('-statement','-target','-quote'))
charter='0312-demokrat-1-026-orgut-il-kongre-p'
charter_context='0312-demokrat-1-026-orgut-il-kongre-context'
goal=('Haziran 2022’de arşivlenen Demokrat Parti tüzük nüshasının 27. maddesi il kongresine, il başkanı, '
      'il yönetim ve disiplin kurulları ile büyük kongre delegelerini seçme görevini veriyor.')
statement_limit='Nüshanın kabul ve yürürlük tarihi ile her kongrede hangi sürümün uygulandığı açık.'
statement_pids=[charter,charter_context]
finding(target,goal,statement_pids,'Arşivlenen 27. madde ve kongre görevleri okundu.')
finding(quote,passages[charter]['exact'],[charter],'Arşivdeki 27. madde pasajı.',pair=target)
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=target,quote_finding_id=quote,statement_at=None,date_precision='unknown',
    version_id=passages[charter]['version_id'],period_basis='18 Haziran 2022 arşiv yakalaması nüsha için tarihsel gözlem.',
    uncertainty_reason=statement_limit,comparison_row_id='04-03-v3-0312-demokrat-1-026-orgut-il-kongre-row'))
readings(topic,'statement',statement_pids)
for kind,claim in (('practice_statement',goal),('practice_statement.summary_finding_id',goal),
    ('practice_statement.quote_finding_id',passages[charter]['exact'])):
    task(kind,statement,claim,statement_limit)

events=(
    ('afyon','demokrat-afyon-16-il-kongresi-2025-12-14','2025-12-14','Afyonkarahisar 16. İl Kongresi ve il başkanı seçimi',
     '14 Aralık 2025’te Demokrat Parti Afyonkarahisar 16. Olağan İl Kongresi yapıldı. Yerel yayınlar Hikmet Bülbül’ün il başkanlığına yeniden seçildiğini bildiriyor.',
     '14 Aralık Afyon Haber ve Afyon Şehir haberleri ile Odak Gazetesinin 15 Aralık basılı kongre haberi.',
     '14 Aralık kongre günü. Odak 15 Aralık sayısında önceki günün toplantısını aktarıyor.',
     'Seçime kongre delegeleri katıldı. Yerel yayınlar sonucu ve listeyi aktarıyor.',
     'Haberler tek liste ve başkan sonucunu veriyor. Sayım, resmî imzalı seçim tutanağı ve nüshanın kongrede yürürlüğü açık.',
     'Hikmet Bülbül tek listeli seçimde yeniden il başkanı seçildi. Afyon Haber yönetim ve disiplin listesini, Odak Adnan Demirel’in üst kurul delegeliğini bildiriyor.',
     'Yerel haberlerdeki başkan, yönetim, disiplin ve delege sonuçları arşivli 27. maddenin saydığı organlarla karşılaştırıldı.',
     (
         ('afyon-day','initiative','Afyon Haber kongre gününde haberi yayımladı.'),
         ('afyon-congress','action','Afyon Haber 16. Olağan Kongrenin yapıldığını bildiriyor.'),
         ('odak-site','action','Odak önceki günün kongresini Uydukent Derya Düğün Salonu’nda izlediğini bildiriyor.'),
         ('afyon-result','result','Afyon Haber tek listeyle Bülbül’ün yeniden seçildiğini bildiriyor.'),
         ('afyonsehir-result','result','Afyon Şehir Bülbül’ün yeniden seçildiğini bildiriyor.'),
         ('odak-result','result','Odak Bülbül’ün delegelerce yeniden seçilmesini aktarıyor.'),
         ('afyon-boards','result','Afyon Haber yönetim ve disiplin kurulu listelerini yayımladı.'),
         ('afyon-delegates','result','Afyon Haber üst kurul delegeleri arasında bazı isimleri anıyor.'),
         ('odak-delegate','result','Odak, Adnan Demirel’in üst kurul delegesi seçildiğini bildiriyor.'),
     )),
    ('konya','demokrat-konya-il-kongresi-2026-03-29','2026-03-29','Konya Olağan İl Kongresi ve il organları seçimi',
     '29 Mart 2026’da Demokrat Parti Konya Olağan İl Kongresi yapıldı. Anadolu’da Bugün güncellenen haberinde Mehmet Ali Yavuz’un il başkanı seçildiğini bildiriyor.',
     'Evren Atcı’nın Anadolu’da Bugün’de 29 Mart 15.16’da yayımlanan ve 15.50’de güncellenen kongre haberi.',
     '29 Mart güncellemesi il başkanlığı sonucu ve kurul listelerini içeriyor.',
     'Haber, kongrenin seçim sonucunu ve listeleri yayımlıyor. Oy dökümü ve kurul tescili ilgili seçim evrakından doğrulanabilir.',
     'Haber önceki başkan Muhsin Ekmekçi’yi katılımcı ve yeni yönetim üyesi olarak ayrı tanımlıyor. Resmî tutanak, oylama sayısı ve tarihsel tüzük yürürlüğü açık.',
     'Güncellenen haberde Mehmet Ali Yavuz il başkanı. 20 asıl yönetim üyesi, disiplin kurulu ve büyük kongre delegelerinin listeleri yayımlandı.',
     'Haberin ayrı başkan, yönetim, disiplin ve delege başlıkları arşivli 27. maddedeki kongre görevleriyle karşılaştırıldı.',
     (
         ('konya-day','initiative','Haberin güncellendiği gün 29 Mart 2026.'),
         ('konya-session','action','Evren Atcı Konya Olağan İl Kongresinin yapıldığını bildiriyor.'),
         ('konya-result','result','Haber Mehmet Ali Yavuz’un il başkanı seçildiğini bildiriyor.'),
         ('konya-board','result','Haber asıl ve yedek yönetim kurulu listelerini veriyor.'),
         ('konya-discipline','result','Haber asıl ve yedek disiplin kurulu listelerini veriyor.'),
         ('konya-delegates','result','Haber büyük kongre delegeleri listesini veriyor.'),
     )),
)
for label,key,day,title,context,basis,time,authority,detail,observed,compare,anchors in events:
    event_stem=stem+'-'+label
    limit=detail+' '+statement_limit
    evidence=[(src+pid,stage,'independent_report',claim) for pid,stage,claim in anchors]
    event_id=event(event_stem,day,title,context,evidence,limit)
    records['practice_event'][-1].update(common_event_key=key,occurrence_basis=basis)
    pids=[row[0] for row in evidence]
    scope=readings(topic,'event',pids)
    rid,result,explanation=(event_stem+suffix for suffix in ('-relation','-result','-explanation'))
    finding(result,observed,pids,basis)
    finding(explanation,compare+' '+limit,statement_pids+pids,limit)
    records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=event_id,party_id=party,
        topic_id=topic,scope_id=scope,comparability_reason=compare,target_finding_id=target,
        result_finding_id=result,explanation_finding_id=explanation,temporal_context=time,
        authority_context=authority,uncertainty_reason=limit))
    records['practice_candidate'].append(dict(id=event_stem+'-candidate',scope_id=scope,event_id=event_id,
        relation_id=rid,state='eligible',reason=compare,passage_ids=encoded(pids)))
    for kind,claim in (
        ('practice_relation',compare),('practice_relation.target_finding_id',goal),
        ('practice_relation.result_finding_id',observed),('practice_relation.explanation_finding_id',compare),
    ):
        task(kind,rid,claim,limit)

tokat_limit='7 Mart haberinde oy verme başlamış. 23 Mayıs haberi Yüksekkaya’yı il başkanı diye anıyor. 7 Mart seçim sayımı, resmî sonuç ve organ listesi açık.'
tokat_refs=[
    (src+'tokat-day','initiative','independent_report','Tokat Haber 7 Mart’ta yayımlandı.'),
    (src+'tokat-session','action','independent_report','Kongrenin parti binasında yapıldığı bildirildi.'),
    (src+'tokat-list','action','independent_report','Seyfettin Yüksekkaya’nın seçime tek listeyle katıldığı bildirildi.'),
    (src+'tokat-opening','action','independent_report','Haberde delege oylamasının başladığı belirtiliyor.'),
]
tokat=event(stem+'-tokat','2026-03-07','Tokat İl Kongresi ve oy verme işleminin başlaması',
    'Tokat Haber 7 Mart 2026’da il kongresinin yapıldığını ve delege oylarının başladığını bildirdi.',tokat_refs,tokat_limit)
records['practice_event'][-1].update(common_event_key='demokrat-tokat-il-kongresi-2026-03-07',
    occurrence_basis='Burhan Arar’ın 7 Mart tarihli Tokat Haber kongre haberi.')
tokat_pids=[row[0] for row in tokat_refs]
scope=readings('organ-secim-yontemi','event',tokat_pids+[src+'tokat-may-position'])
reason='7 Mart’ta kongre ve oylamanın başladığı bildirildi. Seyfettin Yüksekkaya tek listeyle girdi. Sayım, resmî sonuç ve organ listesi araştırılıyor.'
records['practice_candidate'].append(dict(id=stem+'-tokat-candidate',scope_id=scope,event_id=tokat,
    relation_id=None,state='unmatched',reason=reason,passage_ids=encoded(tokat_pids)))
task('practice_candidate',stem+'-tokat-candidate',reason,tokat_limit)

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
for name,content in [('province-congress-draft.json',package),('province-congress-review-draft.json',review)]:
    path=here/name
    with path.open('x') as output:
        output.write(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print(len(tasks),'new targets')
