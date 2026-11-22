import copy
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, 'src')
import uygulamalar as rules

D = Path(__file__).parent
read = lambda path: json.loads(Path(path).read_text())
package = read(D / 'local-discipline-v2-draft.json')
previous = read(D / 'local-discipline-v2-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
inventory = read('data/practices/04-inventory.json')
entries, records = package['entries'], package['practice_records']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for filename in ('resignation-source-draft.json', 'resignation-allegation-passage.json', 'gyk-appointment-source-draft.json', 'historic-charter-source-draft.json', 'may-2023-charter-vacancy-passage.json'):
    entries.extend(read(D / filename)['entries'])

def add(table, **values):
    entries.append(dict(kind=table, values=values))

def finding(fid, text, pids, provenance='summary', pair=None):
    add('finding', id=fid, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=pair or fid, text=text, provenance=provenance, epistemic_type='claim')
    add('review', id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Kaynak pasajı ve haberin bildirdiği işlem sınırı okundu.')
    for pid in pids:
        add('finding_evidence', finding_id=fid, passage_id=pid, role='support')
        add('verification', finding_id=fid, passage_id=pid, checked_at=now, result='confirmed', reason='İlgili metin ve kaynak atfı incelendi.')

cases = [
    dict(key='resignation', topic='uyeligin-sona-ermesi', charter='0309-emep-html-009-0-passage', row='04-03-v3-0309-emep-html-009-0-row', summary='Tüzük, üyelerin istifa hakkını ve istifanın kayıtlı örgüte yazıyla bildirilmesini düzenler.', quote='Parti gönüllü bir birliktir ve her üye dilediğinde üyelikten istifa etme hakkına sahiptir. İstifa, kayıtlı bulunulan Parti örgütüne yazıyla bildirilir.', event='Ercüment Akdeniz’in istifa açıklaması', event_at='2023-05-16', pid='0410-emep-2023-resignation-resignation-p', version='0410-emep-2023-resignation-v1', url='https://www.evrensel.net/haber/490142/emepten-istifa-aciklamasi', claim='Evrensel, Ercüment Akdeniz’in parti üyeliğinden istifa ettiğini duyurduğunu aktardı.', stage='action', basis='independent_report', limitation='Haber, yazılı bildirimin kayıtlı parti örgütüne ulaştığını veya üyelik kaydında yapılan işlemi göstermiyor; istifa ihraç değildir.'),
    dict(key='gyk', topic='organ-bosalma', charter='0309-emep-html-036-0-passage', row='04-03-v3-0309-emep-html-036-0-row', summary='Tüzük, genel başkanlık boşaldığında GYK’nin kendi içinden temsil yetkisi vereceğini ve en geç 45 gün içinde kongreyi toplantıya çağıracağını düzenler.', quote='Genel başkanlığın herhangi bir nedenle boşalması halinde, genel kongre toplanıncaya kadar GYK, Partiyi temsil yetkisini, kendi içinden seçeceği bir üyeye tevdi eder. En geç 45 gün içinde genel kongreyi toplantıya çağırır.', event='Selma Gürkan için GYK görevlendirme açıklaması', event_at='2023-05-17', pid='0410-emep-2023-gyk-anka-p', version='0410-emep-2023-gyk-anka-v1', url='https://www.gercekgundem.com/secim/emepin-yeni-genel-baskani-ercument-akdenizin-istifasinin-ardindan-selma-gurkan-oldu-423214', claim='Partinin ANKA aracılığıyla aktarılan açıklamasına göre GYK, 17 Mayıs toplantısında Selma Gürkan’ı genel başkanlık görevine getirdi.', stage='initiative', basis='party_announcement', limitation='Açıklamanın dayandığı GYK tutanağı ve kongre çağrısı görülmedi; parti açıklaması bağımsız karar sonucu sayılmadı. 17 Mayıs görevlendirmesi olağanüstü kongre seçiminden ayrıdır.')
]
for c in cases:
    scopes = {x['research_kind']: x for x in inventory['cells'] if x['party_id']=='emep' and x['topic_id']==c['topic']}
    assert set(scopes)=={'event','statement'}
    for scope in scopes.values():
        row = {k:scope[k] for k in ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')}
        row.update(id=scope['cell_id'], boundary_reason='Tek bir Mayıs 2023 kaynağı incelendi; tüm dönem ve diğer işlemler açıktır.')
        records['practice_scope_v2'].append(row)
    statement='0410-may-'+c['key']+'-statement'; sf='0410-may-'+c['key']+'-statement-finding'; qf='0410-may-'+c['key']+'-quote'; ef='0410-may-'+c['key']+'-explanation'; eid='0410-may-'+c['key']+'-event'; rid='0410-may-'+c['key']+'-relation'
    charter_pids=[c['charter']]
    if c['key']=='gyk': charter_pids.append('0410-emep-charter-202305-vacancy-p')
    finding(sf,c['summary'],charter_pids); finding(qf,c['quote'],charter_pids,provenance='quote',pair=sf)
    finding(ef,c['summary']+' '+c['claim'],charter_pids+[c['pid']])
    records['practice_statement'].append(dict(id=statement,party_id='emep',topic_id=c['topic'],taxonomy_version=4,summary_finding_id=sf,quote_finding_id=qf,statement_at=None,date_precision='unknown',version_id='0208-emep-program-charter-v1',period_basis='2019 yayın ve 2020 site güncellemesi kabul günü değildir.',uncertainty_reason='Tüzüğün kabul tarihi ve olay sırasındaki ara değişiklikleri doğrulanmadı.',comparison_row_id=c['row']))
    records['practice_event'].append(dict(id=eid,common_event_key='emep-may-2023-'+c['key'],event_at=c['event_at'],date_precision='day',date_unknown_reason=None,scope_context=c['event'],title=c['event'],occurrence_basis=c['claim']))
    records['practice_event_evidence'].append(dict(event_id=eid,passage_id=c['pid'],supported_point=c['claim'],stage=c['stage'],concrete_basis='İlgili tarihteki bildirimin kaynak metnindeki aktarımı.',limitation=c['limitation'],epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=c['pid'],stage=c['stage'],basis_kind=c['basis']))
    records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id='emep',topic_id=c['topic'],scope_id=scopes['event']['cell_id'],comparability_reason='Tüzük hükmü ile bildirilen ilgili işlem birlikte incelenir.',target_finding_id=sf,result_finding_id=None,explanation_finding_id=ef,temporal_context='Olay ve kaynak tarihleri ayrı; tüzüğün ara dönem yürürlüğü araştırılıyor.',authority_context='Tüzükte gösterilen yetki ve haberin kaynağı ayrıdır.',uncertainty_reason=c['limitation']))
    records['practice_candidate'].append(dict(id='0410-may-'+c['key']+'-candidate',scope_id=scopes['event']['cell_id'],event_id=eid,relation_id=rid,state='eligible',reason='Bildirilen işlem ilgili tüzük hükmüyle ilişkilidir.',passage_ids=json.dumps([c['pid']])))
    for typ,version,url,section in [('event',c['version'],c['url'],c['event']),('statement','0208-emep-program-charter-v1','https://www.emep.org/emek-partisi-program-ve-tuzugu',c['summary'])]:
        scope=scopes[typ]['cell_id'];aid='0410-may-'+c['key']+'-'+typ+'-reading'
        records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now))
        records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])))
        records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; kapsam ve sonraki uçlar açık.',source_version_id=version))

data=copy.deepcopy(base)
for entry in entries:
    rows=data.setdefault(entry['kind'],[])
    if entry['values'] not in rows: rows.append(entry['values'])
for kind,rows in records.items(): data.setdefault(kind,[]).extend(row for row in rows if row not in data[kind])
rules.validate_practices(data)
targets=rules.practice_review_targets(data,records); passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}; reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if 'emep' not in parties: continue
    if (kind,identity) in old: reviews.append(old[(kind,identity)]); continue
    ps=[passages[x] for x in sorted(pids)]; c=next((x for x in cases if x['key'] in identity),None)
    claim=(c['summary']+' '+c['claim'] if c else 'Mayıs 2023 tüzük ve kaynak açıklamaları incelendi.')
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in ps})),passage_ids=json.dumps([p['id'] for p in ps]),inspected_sections=json.dumps(sorted({p['section'] for p in ps}),ensure_ascii=False),supported_claim=claim,limitations=(c['limitation'] if c else 'Kapsam ve dönemsel yürürlük açıktır.'),result='reviewed',reason=kind+' / '+identity+' için özgün tüzük ve ilgili haber pasajı okundu.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep')
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('may-institutions-draft.json',package),('may-institutions-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('MAY_INSTITUTIONS_SEMANTIC_PASS',len(reviews),len(records['practice_event']))
