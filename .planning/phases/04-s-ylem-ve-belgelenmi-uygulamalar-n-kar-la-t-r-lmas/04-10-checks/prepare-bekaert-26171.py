import copy, datetime, json, sys
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text
import uygulamalar as rules

D = Path(__file__).parent
read = lambda p: json.loads(Path(p).read_text())
package = read(D / 'ozka-27997-union-draft.json')
previous = read(D / 'ozka-27997-union-review-draft.json')
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
entries, records = package['entries'], package['practice_records']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
entries.extend(read(D / 'bekaert-26171-source-draft.json')['entries'])
raw = (D / 'bekaert-26171/detail.html').read_bytes()
owner = '0410-emep-bekaert-26171-detail-owner-p'
exact = '&#x130;skender BAYHAN'
assert exact in html_source_text(raw)
entries.append(dict(kind='passage', values=dict(id=owner, version_id='0410-emep-bekaert-26171-detail-v1', exact=exact, prefix=None, suffix=None, article=None, section='Soru ve yanıt bildirim kaydı', pdf_page_index=None, printed_page=None)))
question = '0410-emep-bekaert-26171-question-p'
exact = 'Birleşik Metal-İş Sendikası Bekaert’ta yaşanan işyeri birleşmesinin usulen hukuka aykırılıklar\niçerdiğini belirterek suç duyurusunda bulunmuştur.\nBu Bağlamda;\n1- Bekaert firmasmm gerçekleştirdiği birleşme süreci, işçilerin sendikal haklarım geriye\ngötürerek'
assert exact in pdf_page_text(D / 'bekaert-26171/question.pdf', 1)
entries.append(dict(kind='passage', values=dict(id=question, version_id='0410-emep-bekaert-26171-question-v1', exact=exact, prefix=None, suffix=None, article=None, section='İmzalı yazılı soru, ikinci sayfa', pdf_page_index=1, printed_page=None)))
scope = next(x['id'] for x in records['practice_scope_v2'] if x['party_id'] == 'emep' and x['topic_id'] == 'sendika-grev' and x['research_kind'] == 'event')
eid, rid, fid = '0410-bekaert-26171-event', '0410-bekaert-26171-relation', '0410-bekaert-26171-explanation'
def add(k, **v): entries.append(dict(kind=k, values=v))
add('finding', id=fid, party_id='emep', heading='Belgelenmiş uygulamalar', pair_id=fid, text='Program sendika ve grev hakkını savunur. İskender Bayhan Bekaert işyeri birleşmesi ve sendika hakları iddiaları hakkında yazılı soru verdi; TBMM kaydı bakanlık yanıtının bildirildiğini gösterir.', provenance='summary', epistemic_type='claim')
add('review', id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at=now, result='reviewed', reason='Program, resmi kayıt, imzalı soru ve taranmış yanıt incelendi; iddialar ve dava sonucu ayrı tutuldu.')
pids = ['0309-emep-program-006-1-passage', '0410-emep-bekaert-26171-detail-number-p', '0410-emep-bekaert-26171-detail-date-p', '0410-emep-bekaert-26171-detail-reply-p', owner, question]
for p in pids:
    add('finding_evidence', finding_id=fid, passage_id=p, role='support')
    add('verification', finding_id=fid, passage_id=p, checked_at=now, result='confirmed', reason='Program veya resmi soru ve yanıt kaydı okundu.')
records['practice_event'].append(dict(id=eid, common_event_key='tbmm-28-3-7-26171-bekaert-sendika-yetki', event_at='2025-03-24', date_precision='day', date_unknown_reason=None, scope_context='TBMM Bekaert işyeri birleşmesi ve sendika hakları iddiaları yazılı soru ve yanıt kaydı', title='Bekaert işyeri birleşmesi ve sendika hakları hakkında yazılı soru', occurrence_basis='TBMM soru kaydı Bayhanı, konuyu ve başkanlığa geliş gününü bildirir.'))
for p, point in [('0410-emep-bekaert-26171-detail-number-p', 'TBMM 7/26171 sayılı yazılı soru kaydıdır.'), ('0410-emep-bekaert-26171-detail-date-p', 'Soru 24 Mart 2025te başkanlığa geldi.'), (owner, 'Soru sahibi İstanbul Milletvekili İskender Bayhandır.'), (question, 'Soru işyeri birleşmesinin sendikal haklara etkisini gündeme getirir.'), ('0410-emep-bekaert-26171-detail-reply-p', 'TBMM kaydına göre yanıt 7 Eylül 2026da bildirildi.')]:
    records['practice_event_evidence'].append(dict(event_id=eid, passage_id=p, supported_point=point, stage='action', concrete_basis='TBMM resmi soru kaydı ve imzalı soru.', limitation='Soru ve genel yanıt iddiaların doğrulanmasını veya dava sonucunu göstermez.', epistemic_type='claim'))
    records['practice_evidence_assessment'].append(dict(event_id=eid, passage_id=p, stage='action', basis_kind='document'))
records['practice_relation'].append(dict(id=rid, statement_id='0410-labor-statement', event_id=eid, party_id='emep', topic_id='sendika-grev', scope_id=scope, comparability_reason='Program sendikal hakları savunur; soru işyeri birleşmesi ve sendikal hakları konu alır.', target_finding_id='0410-labor-statement-finding', result_finding_id=None, explanation_finding_id=fid, temporal_context='Programın 2023 arşivi ile 2025 soru ve 2026 yanıtı ayrı tarihlerdir.', authority_context='Soru Bayhana; genel hukuki yanıt Çalışma ve Sosyal Güvenlik Bakanlığına aittir.', uncertainty_reason='Soru iddiaların doğruluğunu veya dava sonucunu göstermez; programın 2025te kesintisiz yürürlüğü kanıtlanmadı.'))
records['practice_candidate'].append(dict(id='0410-bekaert-26171-candidate', scope_id=scope, event_id=eid, relation_id=rid, state='eligible', reason='TBMM özgün soru ve yanıt kayıtları incelendi.', passage_ids=json.dumps(pids[1:])))
for role in ('detail', 'question', 'reply'):
    v = '0410-emep-bekaert-26171-' + role + '-v1'
    version = next(e['values'] for e in entries if e['kind'] == 'document_version' and e['values']['id'] == v)
    section = 'Soru ve yanıt bildirim kaydı' if role == 'detail' else 'İmzalı soru' if role == 'question' else 'Bakanlık yanıtı'
    aid = '0410-bekaert-26171-' + role + '-attempt'
    records['practice_scope_source'].append(dict(scope_id=scope, version_id=v, inspected_sections=json.dumps([section], ensure_ascii=False), inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid, scope_id=scope, url=version['original_url'], relevance_reason=section, state='examined', attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid, scope_id=scope, attempted_at=now, query=version['original_url'], url=version['original_url'], result='examined', reason='TBMM kayıt veya sayfaları okundu; fiilî sonuç ayrı.', source_version_id=v))
data = copy.deepcopy(base)
for e in entries:
    if e['values'] not in data.setdefault(e['kind'], []): data[e['kind']].append(e['values'])
for table, rows in records.items(): data.setdefault(table, []).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
targets = rules.practice_review_package_targets(data, records, {x['passage_id'] for x in records['practice_event_evidence']}, party_id='emep')
passages = {p['id']: p for p in data['passage']}
old = {(r['subject_kind'], r['subject_id']): r for r in previous['practice_source_review']}
reviews = []
for (kind, identity), (ids, parties) in sorted(targets.items()):
    if (kind, identity) in old:
        reviews.append(old[(kind, identity)])
        continue
    inspected = [passages[x] for x in sorted(ids)]
    reviews.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent', reviewed_at=now, source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})), passage_ids=json.dumps([p['id'] for p in inspected]), inspected_sections=json.dumps(sorted({p['section'] for p in inspected}), ensure_ascii=False), supported_claim='Program ve TBMM kayıt pasajları incelendi.', limitations='Soru ve genel yanıt iddiaların doğrulandığını veya dava sonucunu göstermez.', result='reviewed', reason=kind+' / '+identity+' için kaynak pasajları okundu.'))
rules.validate_practice_source_review(data, reviews, party_id='emep', target_keys=set(targets))
refs = [{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews]
package['source_review_refs'] = refs
for name, obj in [('bekaert-26171-union-draft.json', package), ('bekaert-26171-union-review-draft.json', dict(practice_source_review=reviews, source_review_refs=refs))]:
    with (D/name).open('x') as f: json.dump(obj, f, ensure_ascii=False, indent=2); f.write('\n')
print('BEKAERT_26171_SEMANTIC_PASS', len(reviews), 'EVENTS', len(records['practice_event']), 'RELATIONS', len(records['practice_relation']))
