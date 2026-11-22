from datetime import datetime,timezone
from hashlib import sha256
import json,sys
import subprocess
from pathlib import Path
import uygulamalar as rules
from arsiv import pdf_page_text

folder=Path(sys.argv[1])
def read(path):
    return json.loads(path.read_text())
package=read(folder/'institution-tracer-v2.json')
previous=json.loads(subprocess.check_output(['git','show','1b0c653:data/practices/04-tip.json']))
base=read(Path('data/releases')/package['base_release']/'records.json')
old_review=read(folder/'institution-review-v2.json')
records=package['practice_records']
package['scope_inventory']=previous['scope_inventory']
records['practice_contract']=base['practice_contract']
assert records['practice_contract'][0]['inventory_digest']==rules._digest(package['scope_inventory'])
for table in ('practice_variant_contract','practice_evidence_contract'):
    records[table]=previous['practice_records'][table]
for table in sorted(set(rules.PRACTICE_VARIANT_TABLES)|set(rules.PRACTICE_EVIDENCE_TABLES)):
    records.setdefault(table,[])
old={(r['event_id'],r['passage_id'],r['stage']) for r in base['practice_event_evidence']}
records['practice_evidence_assessment']=[r for r in previous['practice_records']['practice_evidence_assessment']
    if (r['event_id'],r['passage_id'],r['stage']) in old]+records['practice_evidence_assessment']
assessment=next(r for r in records['practice_evidence_assessment'] if r['event_id']=='0407-2023-kurultay-event')
assessment['basis_kind']='independent_report'
result_evidence=dict(records['practice_event_evidence'][0],stage='result',
    supported_point='Bianet, tek aday Meral Akşener’in 1.127 geçerli oyla yeniden seçildiğini bildirdi.',
    concrete_basis='24 Haziran 2023 tarihli haber genel başkan seçimini ve geçerli oy sayısını birlikte aktarıyor.',
    limitation='Seçim divanı tutanağı ve tüzüğün 2023 ara sürümü ayrıca araştırılıyor.')
records['practice_event_evidence'].append(result_evidence)
records['practice_evidence_assessment'].append(dict(assessment,stage='result'))
now=datetime.now(timezone.utc).isoformat()
entries=package['entries']
for entry in entries:
    if entry['kind']=='finding':
        entry['values']['heading']='Belgelenmiş uygulamalar'
def add(table, **values):
    entries.append(dict(kind=table,values=values))
def finding(identity,passage,text,provenance,pair):
    add('finding',id=identity,party_id='iyi',heading='Belgelenmiş uygulamalar',pair_id=pair,
        text=text,provenance=provenance,epistemic_type='claim')
    add('finding_evidence',finding_id=identity,passage_id=passage,role='support')
    add('verification',finding_id=identity,passage_id=passage,checked_at=now,result='confirmed',
        reason='Metin ve desteklediği sınırlı iddia özgün kaynakla karşılaştırıldı.')
    add('review',id='review-'+identity,kind='finding',subject_id=identity,reviewer_kind='agent',reviewed_at=now,
        result='reviewed',reason='Özgün kaynak, olay tarihi ve yöntem sınırı incelendi.')
statement=records['practice_statement'][0]
charter=next(e['values'] for e in entries if e['kind']=='passage' and e['values']['id']=='0407-2020-charter-kurultay-p')
version=next(v for v in base['document_version'] if v['id']==charter['version_id'])
pdf=Path('data')/version['original_path']
assert sha256(pdf.read_bytes()).hexdigest()==version['sha256']
assert charter['exact'] in pdf_page_text(pdf,charter['pdf_page_index'])
quote='0407-2020-kurultay-statement-quote'
finding(quote,charter['id'],charter['exact'],'quote',statement['summary_finding_id'])
statement['quote_finding_id']=quote
result='0407-2023-kurultay-vote-result'
finding(result,result_evidence['passage_id'],result_evidence['supported_point'],'summary',result)
records['practice_relation'][0]['result_finding_id']=result
for entry in entries:
    target=base.setdefault(entry['kind'],[])
    if entry['values'] not in target:
        target.append(entry['values'])
for table,rows in records.items():
    target=base.setdefault(table,[])
    target.extend(row for row in rows if row not in target)
rules.validate_practices(base)
old_reviews={(r['subject_kind'],r['subject_id']):r for r in old_review['practice_source_review']}
passages={r['id']:r for r in base['passage']}
reviews=[]
for (kind,identity),(pids,parties) in sorted(rules.practice_review_targets(base,records).items()):
    if 'iyi' not in parties:
        continue
    inspected=[passages[p] for p in sorted(pids)]
    prior=old_reviews.get((kind,identity))
    if kind=='practice_statement.quote_finding_id':
        claim='36. maddenin gizli oylama fıkrası PDF metninde bire bir karşılık buluyor.'
        reason='2020 değişiklikli tüzüğün 24. PDF sayfasında alıntının tam noktalaması denetlendi.'
    elif kind=='practice_statement':
        claim='2020 değişiklikli 36. madde, Kurultayın genel başkan ve merkez kurullarını gizli oyla seçmesini düzenliyor.'
        reason='Kurultayın yetkisi 2020 sürümündeki başlık ve fıkra sınırıyla kaydedildi.'
    elif kind=='practice_relation.result_finding_id':
        claim=result_evidence['supported_point']
        reason='Bianet’in tek aday ve geçerli oy sayısı ifadesi seçim sonucu olarak okundu.'
    elif identity.endswith('|result'):
        claim='Bianet haberindeki 1.127 geçerli oy, genel başkan seçiminin bildirilen sonucudur.'
        reason='Yeniden seçilme kaydı ve oy sonucunun başka bir kurul seçimine ait olmadığı kontrol edildi.'
    else:
        assert prior, (kind,identity)
        claim=prior['supported_claim']
        reason=prior['reason']
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,
        source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),
        passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),
        supported_claim=claim,limitations='2023 öncesi ara tüzük sürümü ve divanın seçim tutanağı araştırılıyor.',
        result='reviewed',reason=reason))
rules.validate_practice_source_review(base,reviews,require_coverage=False,party_id='iyi')
references=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
package['source_review_refs']=references
review={'practice_source_review':reviews,'source_review_refs':references}
for name,value in [('institution-tracer-v3.json',package),('institution-review-v3.json',review)]:
    path=folder/name
    with path.open('x') as file:
        file.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(name,sha256(path.read_bytes()).hexdigest())
print('validated',len(reviews))
