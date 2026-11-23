import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text
import uygulamalar as rules

D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D/'tupras-norm-union-draft.json')
previous = read(D/'tupras-norm-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records = package['entries'], package['practice_records']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
entries.extend(read(D/'sik-makas-source-draft.json')['entries'])
pid = '0410-emep-sik-makas-party-full-p'
exact = 'EMEP Gaziantep Milletvekili Sevda Karaca, Çalışma ve Sosyal Güvenlik Bakanlığı ile görüşmek için Tokat, İstanbul ve Çorlu’dan birleşerek Ankara’ya gelen Şık Makas işçileri Meclis’te basın toplantısı düzenledi.'
raw = (D/'sik-makas-party-original.html').read_bytes()
assert exact in html_source_text(raw)
entries.append(dict(kind='passage', values=dict(id=pid, version_id='0410-emep-sik-makas-party-v1', exact=exact, prefix=None, suffix=None, article=None, section='TBMM basın toplantısı', pdf_page_index=None, printed_page=None)))
demand = '0410-emep-sik-makas-party-demand-p'
demand_exact = 'Kıdem tazminatı hakkı gerçek anlamda güvenceye alınsın.'
assert demand_exact in html_source_text(raw)
entries.append(dict(kind='passage', values=dict(id=demand, version_id='0410-emep-sik-makas-party-v1', exact=demand_exact, prefix=None, suffix=None, article=None, section='TBMM basın toplantısı', pdf_page_index=None, printed_page=None)))
scope = next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='sendika-grev' and x['research_kind']=='event')
eid, rid, fid = '0410-sik-makas-meclis-event', '0410-sik-makas-meclis-relation', '0410-sik-makas-meclis-explanation'
def add(k, **v): entries.append(dict(kind=k, values=v))
add('finding', id=fid, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=fid, text='Program işçi ve emekçilerin sendikal örgütlenme ve grev hakkını savunur. Parti ve ANKA yayınları, Sevda Karaca ile Şık Makas işçilerinin TBMM basın toplantısını ve işçilerin hak taleplerini aktarır.', provenance='summary', epistemic_type='claim')
add('review', id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program ve iki yayın okundu; yayın tarihi toplantının kesin tarihi olarak alınmadı.')
for p in ('0309-emep-program-006-1-passage', pid, demand, '0410-emep-sik-makas-anka-meeting-p'):
    add('finding_evidence', finding_id=fid, passage_id=p, role='support')
    add('verification', finding_id=fid, passage_id=p, checked_at=now, result='confirmed', reason='Program veya toplantıya dair yayın okundu.')
records['practice_event'].append(dict(id=eid, common_event_key='tbmm-sik-makas-karaca-isci-basin-toplantisi-2026', event_at=None, date_precision='unknown', date_unknown_reason='ANKA 4 Mart ve parti 6 Mart yayınları toplantıyı aktarır; kesin toplantı günü ayrıca doğrulanmadı.', scope_context='Şık Makas işçilerinin hak talepleri ve TBMM basın toplantısı', title='Şık Makas işçileriyle TBMM basın toplantısı', occurrence_basis='EMEP ve ANKA yayınları Sevda Karaca ile işçilerin toplantısını ve diğer konuşmacıları aktarır.'))
records['practice_event_evidence'].append(dict(event_id=eid, passage_id=pid, supported_point='Sevda Karaca ile Şık Makas işçileri Mecliste basın toplantısı düzenledi.', stage='initiative', concrete_basis='Parti yayını toplantıyı bildiriyor.', limitation='Toplantı günü ve işçi taleplerinin sonuçları ayrıca doğrulanmadı.', epistemic_type='claim'))
records['practice_evidence_assessment'].append(dict(event_id=eid, passage_id=pid, stage='initiative', basis_kind='party_announcement'))
records['practice_relation'].append(dict(id=rid, statement_id='0410-labor-statement', event_id=eid, party_id='emep', topic_id='sendika-grev', scope_id=scope, comparability_reason='Program işçilerin sendikal örgütlenme ve grev hakkını savunur; toplantıda işçi hak talepleri dile getirilir.', target_finding_id='0410-labor-statement-finding', result_finding_id=None, explanation_finding_id=fid, temporal_context='2019/2020 program yayını ve Mart 2026 toplantı haberleri farklı tarihlerdir.', authority_context='Karaca milletvekili olarak işçilerle basın toplantısına katıldı; işveren veya idare adına karar verme yetkisi gösterilmedi.', uncertainty_reason='Toplantının kesin günü, işçi taleplerinin sonucu ve programın 2026 tarihindeki kesintisiz yürürlüğü gösterilmedi.'))
records['practice_candidate'].append(dict(id='0410-sik-makas-meclis-candidate', scope_id=scope, event_id=eid, relation_id=rid, state='eligible', reason='Parti ve ANKA yayınları toplantıyı aktarıyor.', passage_ids=json.dumps([pid,'0410-emep-sik-makas-anka-meeting-p'])))
for role in ('party', 'anka'):
    v='0410-emep-sik-makas-'+role+'-v1'; section='TBMM basın toplantısı'; aid='0410-sik-makas-'+role+'-attempt'
    version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v); url=version['original_url']
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='Yayın ve toplantı aktarımı okundu; toplantı günü ve sonuç açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
    if e['values'] not in data.setdefault(e['kind'],[]): data[e['kind']].append(e['values'])
for table,rows in records.items(): data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='emep')
passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']}; reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if (kind,identity) in old: reviews.append(old[(kind,identity)]); continue
    inspected=[passages[x] for x in sorted(pids)]
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve toplantı yayını pasajları incelendi.',limitations='Yayın tarihi kesin toplantı günü değildir; işçi taleplerinin sonucu gösterilmedi.',result='reviewed',reason=kind+' / '+identity+' için kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for name,obj in [('sik-makas-union-draft.json',package),('sik-makas-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('SIK_MAKAS_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
