import copy
import datetime
import json
from pathlib import Path

import uygulamalar

D = Path(__file__).parent
load = lambda name: json.loads((D / name).read_text())
package = load('package-germencik-102-union-draft.json')
reviews = load('germencik-102-union-checked-review-draft.json')
base = json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text())
template = load('germencik-congress-slice-draft.json')
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
statement_id = '0404-il-kongresi-statement'
scope_statement = 'practice-4c73f1c4d6cd47b05cbd76ba64982511224ab937f16b03bd4d6433eaf6869ec1'
scope_event = 'practice-790baa79e1338940818139e781c2d090ed3a2d2db65f0b5549e81f5736c8e45d'
summary = '0303-epm-extra-orgut-il-kongre-summary'
quote = '0303-epm-extra-orgut-il-kongre-quote'
charter_passages = ['0303-epm-extra-orgut-il-kongre-p', '0303-epm-extra-gecici-orgut-olusumu-p']
records = {k: [] for k in template['practice_records']}
statement = copy.deepcopy(template['practice_records']['practice_statement'][0])
statement.update(id=statement_id, topic_id='orgut-il-kongre', summary_finding_id=summary,
                 quote_finding_id=quote, comparison_row_id='04-03-v3-0303-epm-extra-orgut-il-kongre-row')
records['practice_statement'].append(statement)
for item in template['practice_records']['practice_scope_v2']:
    x = copy.deepcopy(item)
    x.update(id=scope_statement if x['research_kind'] == 'statement' else scope_event,
             topic_id='orgut-il-kongre', boundary_reason='Yozgat ve Manisa kongreleri; diğer il kongreleri ve resmî tutanaklar açıktır.')
    records['practice_scope_v2'].append(x)

entries = []
for name in ('yozgat-4379-source-records-draft.json', 'manisa-kongre-f5-source-records-draft.json'):
    entries.extend(load(name)['entries'])
for f in (summary, quote):
    for ev in base['finding_evidence']:
        if ev['finding_id'] == f:
            entries.append({'kind':'verification', 'values':{'finding_id':f, 'passage_id':ev['passage_id'],
                'checked_at':now, 'result':'confirmed', 'reason':'Kurucu tüzüğün il kongresi ve geçici örgütlenme hükümleri yeniden okundu.'}})

specs = [
    ('yozgat', 'Abdullah Yaşar', '0404-yozgat-4379-v1', '0404-yozgat-4379-kongre-p',
     'Yozgat Çamlık Gazetesi', 'Yozgat il kongresinde başkan seçimi',
     'Gazete 25 Ekim il kongresinde Abdullah Yaşar’ın yeniden il başkanı seçildiğini bildirir.'),
    ('manisa', 'İlksen Özalper', '0404-manisa-kongre-f5-v1', '0404-manisa-kongre-f5-p',
     'F5Haber', 'Manisa il kongresinde başkan seçimi',
     'F5Haber 25 Ekim il kongresinde İlksen Özalper’in delegelerin 470 geçerli oyunun tamamıyla yeniden il başkanı seçildiğini bildirir.'),
]
for city, person, version, passage, publisher, title, observed in specs:
    key = '0404-' + city + '-il-kongresi'
    event, relation, finding = key+'-event', key+'-relation', key+'-explanation'
    entries += [
        {'kind':'finding','values':{'id':finding,'party_id':'yeni-parti','heading':'Söylem ve uygulama',
         'pair_id':finding,'text':'Tüzük il kongresinin il başkanını seçmesini düzenler. '+observed,
         'provenance':'summary','epistemic_type':'claim'}},
        {'kind':'review','values':{'id':'review-'+finding,'kind':'finding','subject_id':finding,
         'reviewer_kind':'agent','reviewed_at':now,'result':'reviewed',
         'reason':'Kurucu tüzük ve '+publisher+' kongre haberi okundu; üye önseçimi ile il kongresi ayrıdır.'}},
    ]
    for pid in [charter_passages[0], passage]:
        entries.append({'kind':'finding_evidence','values':{'finding_id':finding,'passage_id':pid,'role':'support'}})
        entries.append({'kind':'verification','values':{'finding_id':finding,'passage_id':pid,'checked_at':now,
                        'result':'confirmed','reason':'Kurucu tüzük ve '+publisher+' kongre kaynağı ayrı incelendi.'}})
    records['practice_event'].append({'id':event,'common_event_key':'yeni-parti-'+city+'-il-kongresi-2026-10-25',
        'event_at':'2026-10-25','date_precision':'day','date_unknown_reason':None,
        'scope_context':city.title()+' birinci olağan il kongresi delege seçimi','title':title,
        'occurrence_basis':publisher+' tarihli haberinin kongre seçimini bildiren pasajı.'})
    records['practice_event_evidence'].append({'event_id':event,'passage_id':passage,'supported_point':observed,
        'stage':'action','concrete_basis':publisher+' olağan il kongresinin başkan seçimini aktarıyor.',
        'limitation':'Resmî seçim tutanağı görülmedi; önseçim ayrı aşamadır.','epistemic_type':'claim'})
    records['practice_evidence_assessment'].append({'event_id':event,'passage_id':passage,'stage':'action','basis_kind':'document'})
    records['practice_relation'].append({'id':relation,'statement_id':statement_id,'event_id':event,
        'party_id':'yeni-parti','topic_id':'orgut-il-kongre','scope_id':scope_event,
        'comparability_reason':'Her ikisi il kongresinde il başkanı seçimi aşamasına ilişkindir.',
        'target_finding_id':summary,'result_finding_id':None,'explanation_finding_id':finding,
        'temporal_context':'Kurucu tüzükten sonra 25 Ekim 2026 il kongresi.',
        'authority_context':'Tüzük il kongresini düzenler; haber başkan seçimini aktarır.',
        'uncertainty_reason':'Resmî seçim tutanağı görülmedi; önseçim ve il kongresi ayrı aşamalardır.'})
    records['practice_candidate'].append({'id':key+'-candidate','scope_id':scope_event,'event_id':event,
        'relation_id':relation,'state':'eligible','reason':'İl kongresi başkan seçimi tüzük hükmüyle doğrudan ilgilidir.',
        'passage_ids':json.dumps([passage],ensure_ascii=False)})
    records['practice_scope_source'].append({'scope_id':scope_event,'version_id':version,
        'inspected_sections':json.dumps([title],ensure_ascii=False),'inspected_at':now})
    doc = next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==version)
    attempt = key+'-reading'
    reason = publisher+' il kongresinde '+person+' seçimini bildirir; tutanak açıktır.'
    records['practice_lead'].append({'id':'lead-'+attempt,'scope_id':scope_event,'url':doc['original_url'],
        'relevance_reason':reason,'state':'examined','attempt_ids':json.dumps([attempt])})
    records['practice_attempt_v2'].append({'id':attempt,'scope_id':scope_event,'attempted_at':now,
        'query':doc['original_url'],'url':doc['original_url'],'result':'examined','reason':reason,'source_version_id':version})
records['practice_scope_source'].append({'scope_id':scope_statement,'version_id':'epm-charter-v1',
    'inspected_sections':json.dumps(['İl kongresi seçimi ve geçici örgüt oluşumu'],ensure_ascii=False),'inspected_at':now})
charter_url = 'https://yenipartiyiz.biz/parti-tuzugu'
charter_reason = 'Kurucu tüzükte il kongresi seçim hükmü ve geçici örgüt oluşumu yeniden okundu.'
records['practice_lead'].append({'id':'lead-0404-il-kongresi-charter-reading','scope_id':scope_statement,
    'url':charter_url,'relevance_reason':charter_reason,'state':'examined',
    'attempt_ids':json.dumps(['0404-il-kongresi-charter-reading'])})
records['practice_attempt_v2'].append({'id':'0404-il-kongresi-charter-reading','scope_id':scope_statement,
    'attempted_at':now,'query':charter_url,'url':charter_url,'result':'examined',
    'reason':charter_reason,'source_version_id':'epm-charter-v1'})

before = copy.deepcopy(package)
for e in entries:
    if e not in package['entries']:
        package['entries'].append(e)
for k, rows in records.items():
    for row in rows:
        if row not in package['practice_records'].setdefault(k,[]):
            package['practice_records'][k].append(row)
assert package['entries'][:len(before['entries'])] == before['entries']
for k, rows in before['practice_records'].items():
    assert package['practice_records'][k][:len(rows)] == rows

data = copy.deepcopy(base)
for e in package['entries']:
    arr = data.setdefault(e['kind'], [])
    if e['values'] not in arr: arr.append(e['values'])
for k, rows in package['practice_records'].items():
    arr = data.setdefault(k, [])
    for row in rows:
        if row not in arr: arr.append(row)
targets = uygulamalar.practice_review_targets(data, records)
passages = {p['id']: p for p in data['passage']}
new_reviews = []
for (kind, identity), (pids, _) in targets.items():
    ids = sorted(pids)
    new_reviews.append({'subject_kind':kind,'subject_id':identity,'reviewer_kind':'agent','reviewed_at':now,
        'source_version_ids':json.dumps(sorted({passages[p]['version_id'] for p in ids}),ensure_ascii=False),
        'passage_ids':json.dumps(ids,ensure_ascii=False),
        'inspected_sections':json.dumps(['İl kongresi tüzük hükmü ve ilgili il kongresi haberi: '+kind],ensure_ascii=False),
        'supported_claim':'İlgili kaynak pasajları '+identity+' için tüzük hükmünü veya aktarılan il kongresi seçimini gösterir.',
        'limitations':'Resmî seçim tutanakları görülmedi; üye önseçimi ve delege kongresi ayrıdır.',
        'result':'reviewed','reason':identity+' hedefinin tüzük ve ilgili haber pasajları ayrı okundu.'})
uygulamalar.validate_practice_source_review(data, new_reviews, require_coverage=False, party_id='yeni-parti')
reviews['practice_source_review'].extend(new_reviews)
reviews['source_review_refs'].extend({'subject_kind':x['subject_kind'],'subject_id':x['subject_id']} for x in new_reviews)
uygulamalar.validate_practice_source_review(data, reviews['practice_source_review'], party_id='yeni-parti')
for name, obj in [('package-province-congress-103-union-draft.json',package),('province-congress-103-union-review-draft.json',reviews)]:
    (D/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(new_reviews),len(reviews['practice_source_review']),len(package['practice_records']['practice_event']),len(package['practice_records']['practice_relation']))
