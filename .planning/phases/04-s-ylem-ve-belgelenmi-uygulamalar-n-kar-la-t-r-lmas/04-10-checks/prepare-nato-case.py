import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text
import uygulamalar as rules

D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D/'kirsehir2026-union-draft.json')
previous = read(D/'kirsehir2026-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records = package['entries'], package['practice_records']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
entries.extend(read(D/'nato-case-source-draft.json')['entries'])
pid = '0410-emep-nato-case-party-full-p'
exact = 'EMEP adına Av. Sevil Aracı ve Av. Tugay Bek tarafından Ankara Nöbetçi İdare Mahkemesi Başkanlığına sunulan dilekçede yasaklama kararının hukuki dayanaklardan yoksun olduğu, temel hak ve özgürlükleri kısıtladığı ve telafisi zor zararlara neden olacağı gerekçesiyle valilik kararının yürütmesinin durdurulması ve iptali talep edildi.'
raw = Path('data/practices/sources/emep/objects/ed286860d3699409567a8fa59a9d5e3259c8f3a6002712ace4c1ea4e19b71cff/original.html.bin').read_bytes()
assert exact in html_source_text(raw)
entries.append(dict(kind='passage', values=dict(id=pid, version_id='0410-emep-nato-case-party-v1', exact=exact, prefix=None, suffix=None, article=None, section='Davanın açılması', pdf_page_index=None, printed_page=None)))
scope = next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='emep' and x['topic_id']=='ifade-basin-ozgurlugu' and x['research_kind']=='event')
eid, rid, fid = '0410-nato-yasak-dava-event', '0410-nato-yasak-dava-relation', '0410-nato-yasak-dava-explanation'
def add(k, **v): entries.append(dict(kind=k, values=v))
add('finding', id=fid, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=fid, text='Program toplantı, gösteri ve yürüyüş hakkının önündeki engellerin kaldırılmasını savunur. Parti ve ANKA yayınları, Ankara’daki NATO zirvesi öncesi valilik kararına karşı EMEP adına dava açıldığını ve yürütmenin durdurulması istendiğini aktarır.', provenance='summary', epistemic_type='claim')
add('review', id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program, parti yayını ve ANKA aktarımı okundu; karar ve dava günü bilinmiyor.')
for p in ('0309-emep-program-006-0-passage', pid, '0410-emep-nato-case-anka-filing-p'):
    add('finding_evidence', finding_id=fid, passage_id=p, role='support')
    add('verification', finding_id=fid, passage_id=p, checked_at=now, result='confirmed', reason='Program veya dava yayını okundu.')
records['practice_event'].append(dict(id=eid, common_event_key='emep-ankara-nato-etkinlik-yasagi-iptal-davasi-2026', event_at=None, date_precision='unknown', date_unknown_reason='10 Haziran yayınları dava açıldığını aktarır ancak dilekçenin teslim gününü belirtmez.', scope_context='Ankara valiliği zirve öncesi etkinlik tedbirlerine karşı idari dava', title='NATO zirvesi öncesi etkinlik kararına karşı EMEP davası', occurrence_basis='Parti ve ANKA yayınlarında avukatların mahkemeye sunduğu dilekçe aktarılır; resmi dosya görülmedi.'))
records['practice_event_evidence'].append(dict(event_id=eid, passage_id=pid, supported_point='Parti adına sunulan dilekçede valilik kararının yürütmesinin durdurulması ve iptali istendi.', stage='initiative', concrete_basis='Parti yayınında dava dilekçesi aktarılır.', limitation='Dilekçenin teslim günü ve mahkeme sonucu bilinmiyor.', epistemic_type='claim'))
records['practice_evidence_assessment'].append(dict(event_id=eid, passage_id=pid, stage='initiative', basis_kind='party_announcement'))
records['practice_relation'].append(dict(id=rid, statement_id='0410-expression-statement', event_id=eid, party_id='emep', topic_id='ifade-basin-ozgurlugu', scope_id=scope, comparability_reason='Program toplantı ve gösteri hakkını savunur; dava etkinlikleri sınırlayan valilik kararına yöneliktir.', target_finding_id='0410-expression-statement-finding', result_finding_id=None, explanation_finding_id=fid, temporal_context='2019/2020 program yayını ile 10 Haziran 2026 dava haberleri farklı tarihlerdir.', authority_context='Dilekçe parti adına avukatlar tarafından sunuldu; karar verme yetkisi idare mahkemesindedir.', uncertainty_reason='Dava günü, mahkeme sonucu ve 2026 programının kesintisiz yürürlüğü gösterilmedi.'))
records['practice_candidate'].append(dict(id='0410-nato-yasak-dava-candidate', scope_id=scope, event_id=eid, relation_id=rid, state='eligible', reason='Parti ve ANKA yayınları dava girişimini aktarıyor.', passage_ids=json.dumps([pid,'0410-emep-nato-case-anka-filing-p'])))
for role in ('party', 'anka'):
    v = '0410-emep-nato-case-'+role+'-v1'; section='Davanın açılması'; aid='0410-nato-case-'+role+'-attempt'
    version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==v); url=version['original_url']
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='Yayın ve dilekçe aktarımı okundu; dava sonucu açık.',source_version_id=v))
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
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Program ve dava haberi pasajları incelendi.',limitations='Yayın tarihi dava günü değildir; talep sonuç değildir.',result='reviewed',reason=kind+' / '+identity+' için kaynak pasajları okundu.'))
rules.validate_practice_source_review(data,reviews,party_id='emep',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]; package['source_review_refs']=refs
for name,obj in [('nato-case-union-draft.json',package),('nato-case-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
print('NATO_CASE_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']),'RELATIONS',len(records['practice_relation']))
