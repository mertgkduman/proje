from datetime import datetime,timezone
from hashlib import sha256
import json,subprocess,sys
from pathlib import Path
from arsiv import html_source_text
from uygulamalar import validate_practices,practice_review_targets,validate_practice_source_review

here=Path(sys.argv[1])
def read(path):
    return json.loads(path.read_text())
def encode(data):
    return json.dumps(data,ensure_ascii=False,sort_keys=True)
inventory=read(Path('data/practices/04-inventory.json'))
release=inventory['base_release']
base=read(Path('data/releases')/release/'records.json')
template=json.loads(subprocess.check_output(['git','show','1b0c653:data/practices/04-tip.json']))
records={name:[] for name in template['practice_records']}
for t in ('practice_coverage_contract','practice_variant_contract','practice_evidence_contract'):
    records[t]=template['practice_records'][t]
records['practice_contract']=base['practice_contract']
existing={e['id'] for e in base['practice_event']}
records['practice_evidence_assessment']=[row for row in template['practice_records']['practice_evidence_assessment'] if row['event_id'] in existing]
entries=read(here/'myk-source-records.json')['entries']
now=datetime.now(timezone.utc).isoformat()
party='dbp'
topic='merkez-kurul-olusumu'
stem='0409-dbp-myk-2025'
event=stem+'-event'
relation=stem+'-relation'
statement=stem+'-statement'
charter_version='0207-dbp-charter-v1'
charter=next(v for v in base['document_version'] if v['id']==charter_version)
raw=(Path('data')/charter['original_path']).read_bytes()
assert sha256(raw).hexdigest()==charter['sha256'] and charter['document_date']=='2025-01-12'
clause='Merkez Yürütme Kurulu, Parti Meclisi Üyeleri arasından gizli oyla seçilen 9 üye ve Eş Genel Başkanlardan oluşur.'
assert clause in html_source_text(raw)
charter_p=stem+'-article61'
party_p='0409-myk-party-summary-meeting'
action_p='0409-myk-reported-result-meeting'
result_p='0409-myk-reported-result-roles'
def add(table,**row):
    entries.append(dict(kind=table,values=row))
add('passage',id=charter_p,version_id=charter_version,exact=clause,prefix=None,suffix=None,article='Madde 61',
    section='Merkez Yürütme Kurulunun oluşumu',pdf_page_index=None,printed_page=None)
summary=stem+'-statement-summary'
quote=stem+'-statement-quote'
explanation=stem+'-explanation'
result=stem+'-result'
facts={
    summary:('12 Ocak 2025 değişikliklerini içeren tüzüğün 61. maddesi MYK’nın Parti Meclisinden gizli oyla seçilen dokuz üye ve eş genel başkanlardan oluşmasını düzenliyor.',[charter_p]),
    quote:(clause,[charter_p]),
    explanation:('DBP, kongreden sonraki ilk Parti Meclisi toplantısının 19 Ocakta yapıldığını bildirdi. Artı Gerçek, toplantı sonrasında MYK’nın belirlendiğini ve görev dağılımını aktardı. İki kaynak, tüzükteki merkez kurulu oluşturma mekanizmasıyla ilgili.',[charter_p,party_p,action_p,result_p]),
    result:('23 Ocak tarihli haber yeni MYK ve görev dağılımını bildirdi. Örgütleme ve eğitim eşsözcülükleri için isimler verildi. Gizli oy veya sandık tutanağının sonucu açık.',[action_p,result_p]),
}
for fid,(text,pids) in facts.items():
    add('finding',id=fid,party_id=party,heading='Belgelenmiş uygulamalar',pair_id=summary if fid==quote else fid,
        text=text,provenance='quote' if fid==quote else 'summary',epistemic_type='claim')
    for pid in pids:
        add('finding_evidence',finding_id=fid,passage_id=pid,role='support')
        add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',
            reason='Bağlı özgün pasaj, olay tarihi ve kaynak yetki sınırı okundu.')
    add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,
        result='reviewed',reason='12 Ocak tüzük hükmü ile 19 Ocak toplantısı ve 23 Ocak haberinin atıfları ayrı kontrol edildi.')
passages={r['values']['id']:r['values'] for r in entries if r['kind']=='passage'}
versions={r['values']['id']:r['values'] for r in entries if r['kind']=='document_version'}
versions[charter_version]=charter
limits='Parti Meclisi toplantısının günü parti bildirgesinde. MYK belirleme günü, oylama usulünün uygulanması ve resmî seçim tutanağı açık.'
for lane,groups in [('statement',[[charter_p]]),('event',[[party_p],[action_p,result_p]])]:
    cell=next(c for c in inventory['cells'] if (c['party_id'],c['topic_id'],c['research_kind'])==(party,topic,lane))
    scope=cell['cell_id']
    if lane=='event': event_scope=scope
    records['practice_scope_v2'].append(dict(id=scope,**{k:cell[k] for k in
        ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')},
        boundary_reason='7. Olağan Kongre sonrası MYK ve tüzük dayanağının ilk dar incelemesi.'))
    for group in groups:
        v=versions[passages[group[0]]['version_id']]
        aid=stem+'-reading-'+v['id']; url=v['final_url']
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',
            reason='Arşivli '+v['id']+' kaydının tarih, kurum ve ilgili bölümünün okuması.',source_version_id=v['id']))
        records['practice_scope_source'].append(dict(scope_id=scope,version_id=v['id'],inspected_at=now,
            inspected_sections=encode([passages[p]['section'] for p in group])))
        records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason='Merkez kurulu ve Parti Meclisi yetkisi.',
            state='examined',attempt_ids=encode([aid])))
records['practice_statement'].append(dict(id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=summary,quote_finding_id=quote,statement_at='2025-01-12',date_precision='day',
    version_id=charter_version,period_basis='Özgün HTML başlığında 12 Ocak 2025 tarihli 7. Olağan Kongre değişiklikleri belirtiliyor.',
    uncertainty_reason='Belgenin ilk yayın günü ve 61. maddenin daha eski sürümü ayrıca araştırılıyor.',
    comparison_row_id='04-03-v3-0308-dbp-alternative-01-html-row'))
records['practice_event'].append(dict(id=event,common_event_key='dbp-2025-01-19-pm-sonrasi-myk',
    event_at='2025-01-19',date_precision='day',date_unknown_reason=None,title='DBP Parti Meclisi ve bildirilen MYK görev dağılımı',
    scope_context='DBP’nin ilk Parti Meclisi toplantısı. Sonraki haberde MYK ve görevleri açıklandı.',
    occurrence_basis='Parti toplantı gününü bildirdi. Sonraki haber toplantının yapılmasını ve görevlendirmeleri aktardı.'))
for pid,stage,basis,point in [
    (party_p,'initiative','party_announcement','DBP’nin bildirgesi ilk Parti Meclisi toplantısı için 19 Ocak günü verdi.'),
    (action_p,'action','independent_report','Artı Gerçek, 12 Ocak kongresi ardından Parti Meclisi toplantısı yapıldığını bildirdi.'),
    (result_p,'result','independent_report','Artı Gerçek, MYK görev dağılımında eğitim eşsözcülerini adlandırdı.')]:
    records['practice_event_evidence'].append(dict(event_id=event,passage_id=pid,stage=stage,supported_point=point,
        concrete_basis=passages[pid]['section'],limitation=limits,epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=event,passage_id=pid,stage=stage,basis_kind=basis))
records['practice_relation'].append(dict(id=relation,statement_id=statement,event_id=event,party_id=party,topic_id=topic,
    scope_id=event_scope,comparability_reason='Tüzük ile bildirilen görev dağılımı aynı parti merkez yürütme kuruluna ilişkin.',
    target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,
    temporal_context='12 Ocak değişiklikli metin, 19 Ocak toplantısı ve 23 Ocak haber ayrı günler.',
    authority_context='Tüzükte MYK oluşumu Parti Meclisine bağlı. Parti ve haber ayrı kaynaklardan konuya ilişkin kayıt veriyor.',
    uncertainty_reason=limits))
records['practice_candidate'].append(dict(id=stem+'-candidate',scope_id=event_scope,event_id=event,
    relation_id=relation,state='eligible',reason='Aynı merkez kurulunun bileşimi ve bildirilen görev dağılımı.',
    passage_ids=encode([action_p,result_p])))
for e in entries: base.setdefault(e['kind'],[]).append(e['values'])
for table,rows in records.items():
    dest=base.setdefault(table,[])
    dest.extend(r for r in rows if r not in dest)
validate_practices(base)
targets=practice_review_targets(base,records)
reviews=[]
for (kind,ident),(pids,parties) in sorted(targets.items()):
    if party not in parties: continue
    if kind=='practice_event_evidence':
        claim=next(e['supported_point'] for e in records[kind] if
            '|'.join((e['event_id'],e['passage_id'],e['stage']))==ident)
    else:
        field={'practice_statement':summary,'practice_statement.quote_finding_id':quote,
               'practice_statement.summary_finding_id':summary,'practice_relation.target_finding_id':summary,
               'practice_relation.result_finding_id':result,'practice_event':explanation,
               'practice_relation':explanation,'practice_relation.explanation_finding_id':explanation}[kind]
        claim=facts[field][0]
    reviews.append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,
        source_version_ids=encode(sorted({passages[p]['version_id'] for p in pids})),passage_ids=encode(sorted(pids)),
        inspected_sections=encode(sorted({passages[p]['section'] for p in pids})),supported_claim=claim,
        limitations=limits,result='reviewed',reason=f'{kind} hedefinin özgün metin, tarih ve yetki sınırı incelendi. {claim}'))
validate_practice_source_review(base,reviews,party_id=party,require_coverage=False)
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
package=dict(contract_version=1,base_release=release,party_id=party,taxonomy_version=4,stage='tracer',
             entries=entries,practice_records=records,scope_inventory=template['scope_inventory'],tranches=[],source_review_refs=refs)
for filename,value in [('myk-institution-draft.json',package),('myk-institution-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    p=here/filename
    with p.open('x') as out:out.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(filename,sha256(p.read_bytes()).hexdigest())
print(len(reviews),'review targets')
