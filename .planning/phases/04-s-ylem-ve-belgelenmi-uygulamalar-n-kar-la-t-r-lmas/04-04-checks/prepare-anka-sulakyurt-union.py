import copy
import datetime
import json
from pathlib import Path

import uygulamalar

D = Path(__file__).parent
load = lambda n: json.loads((D/n).read_text())
p = load('package-province-congress-103-union-draft.json')
r = load('province-congress-103-union-review-draft.json')
before = copy.deepcopy(p)
now = datetime.datetime.now(datetime.timezone.utc).isoformat()
anka = load('manisa-anka-verified-view-source-draft.json')
sul = load('sulakyurt-kongre-source-records-draft.json')
new_entries = anka['entries'] + sul['entries']
manisa = '0404-manisa-il-kongresi'
anka_passages = ['0404-manisa-kongre-anka-p','0404-manisa-kongre-anka-divan-p']
for pid in anka_passages:
    new_entries.extend([
        {'kind':'finding_evidence','values':{'finding_id':manisa+'-explanation','passage_id':pid,'role':'support'}},
        {'kind':'verification','values':{'finding_id':manisa+'-explanation','passage_id':pid,'checked_at':now,
         'result':'confirmed','reason':'ANKA özgün haberinde il kongresi seçimi ve divan başkanının sonuç açıklaması incelendi.'}},
    ])
for e in new_entries:
    if e not in p['entries']: p['entries'].append(e)
records = {k:[] for k in p['practice_records']}
for pid in anka_passages:
    records['practice_event_evidence'].append({'event_id':manisa+'-event','passage_id':pid,'stage':'action',
        'supported_point':'ANKA 25 Ekim Manisa kongresinin seçimini ve divanın açıkladığı sonucu aktarır.',
        'concrete_basis':'ANKA özgün haberinin kongre sonucu ve divan açıklaması.',
        'limitation':'F5 ile aynı olay ve haber aktarımıdır; bağımsız iki sayım değildir.', 'epistemic_type':'claim'})
    records['practice_evidence_assessment'].append({'event_id':manisa+'-event','passage_id':pid,'stage':'action','basis_kind':'document'})
scope='practice-52a7ef45c066031308e757065bea9964e24ea87f09113ab929b3c69fc8863a92'
key='0404-sulakyurt-kongre'; event=key+'-event'; relation=key+'-relation'; finding=key+'-explanation'
charter='0303-epm-detail8-orgut-ilce-kongre-ilce-kongresindeki-secimler-p'; passage='0404-sulakyurt-kongre-p'
new_entries=[
    {'kind':'finding','values':{'id':finding,'party_id':'yeni-parti','heading':'Söylem ve uygulama','pair_id':finding,
     'text':'Tüzük ilçe kongresinde ilçe başkanının seçilmesini düzenler. İl Gazetesi, Sulakyurt olağan ilçe kongresinde delegelerin Erdal Özkan’ı ilçe başkanı seçtiğini bildirir.',
     'provenance':'summary','epistemic_type':'claim'}},
    {'kind':'review','values':{'id':'review-'+finding,'kind':'finding','subject_id':finding,'reviewer_kind':'agent',
     'reviewed_at':now,'result':'reviewed','reason':'Kurucu tüzük ve İl Gazetesi Sulakyurt kongre haberi ayrı incelendi.'}},
]
for pid in (charter,passage):
    new_entries.extend([{'kind':'finding_evidence','values':{'finding_id':finding,'passage_id':pid,'role':'support'}},
      {'kind':'verification','values':{'finding_id':finding,'passage_id':pid,'checked_at':now,'result':'confirmed',
       'reason':'Kurucu tüzük ve Sulakyurt ilçe kongresindeki delege seçimi haberi okundu.'}}])
for e in new_entries:p['entries'].append(e)
records['practice_event'].append({'id':event,'common_event_key':'yeni-parti-sulakyurt-ilce-kongresi-2026',
    'event_at':None,'date_precision':'unknown','date_unknown_reason':'4 Ekim haberinde gerçekleşmiş kongrenin kesin günü belirtilmiyor.',
    'scope_context':'Sulakyurt olağan ilçe kongresi delege seçimi','title':'Sulakyurt ilçe kongresinde başkan seçimi',
    'occurrence_basis':'4 Ekim İl Gazetesi haberinde tamamlanan kongrenin delege seçimi aktarılıyor.'})
records['practice_event_evidence'].append({'event_id':event,'passage_id':passage,'stage':'action',
    'supported_point':'Erdal Özkan’ın Sulakyurt ilçe kongresinde delegelerce seçilmesi.',
    'concrete_basis':'İl Gazetesi ilçe kongresinde delege seçimini bildiriyor.',
    'limitation':'Resmî tutanak, oy sayısı ve kesin kongre günü görülmedi.','epistemic_type':'claim'})
records['practice_evidence_assessment'].append({'event_id':event,'passage_id':passage,'stage':'action','basis_kind':'document'})
records['practice_relation'].append({'id':relation,'statement_id':'0404-germencik-kongre-statement','event_id':event,
    'party_id':'yeni-parti','topic_id':'orgut-ilce-kongre','scope_id':scope,
    'comparability_reason':'Her ikisi ilçe kongresinde başkan seçimi aşamasına ilişkindir.',
    'target_finding_id':'0303-epm-detail8-orgut-ilce-kongre-ilce-kongresindeki-secimler-summary',
    'result_finding_id':None,'explanation_finding_id':finding,'temporal_context':'Kurucu tüzükten sonra 4 Ekim tarihli haber.',
    'authority_context':'Tüzük ilçe kongresini düzenler; yerel haber delege seçimini aktarır.',
    'uncertainty_reason':'Resmî tutanak, oy sayısı ve kesin kongre günü görülmedi.'})
records['practice_candidate'].append({'id':key+'-candidate','scope_id':scope,'event_id':event,'relation_id':relation,
    'state':'eligible','reason':'İlçe kongresindeki başkan seçimi tüzük hükmüyle doğrudan ilgilidir.',
    'passage_ids':json.dumps([passage])})
version='0404-sulakyurt-kongre-v1'; url=next(e['values']['original_url'] for e in sul['entries'] if e['kind']=='document_version')
records['practice_scope_source'].append({'scope_id':scope,'version_id':version,'inspected_sections':json.dumps(['Sulakyurt kongresi delege seçimi'],ensure_ascii=False),'inspected_at':now})
reason='İl Gazetesi Sulakyurt kongresindeki delege seçimini bildiriyor; tutanak açık.'
records['practice_lead'].append({'id':'lead-'+key+'-reading','scope_id':scope,'url':url,'relevance_reason':reason,
    'state':'examined','attempt_ids':json.dumps([key+'-reading'])})
records['practice_attempt_v2'].append({'id':key+'-reading','scope_id':scope,'attempted_at':now,'query':url,
    'url':url,'result':'examined','reason':reason,'source_version_id':version})
for k, rows in records.items():
    for x in rows:
        if x not in p['practice_records'][k]:p['practice_records'][k].append(x)
assert p['entries'][:len(before['entries'])]==before['entries']
for k, rows in before['practice_records'].items():assert p['practice_records'][k][:len(rows)]==rows
base=json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text())
for e in p['entries']:
    a=base.setdefault(e['kind'],[])
    if e['values'] not in a:a.append(e['values'])
for k,rows in p['practice_records'].items():
    a=base.setdefault(k,[])
    for x in rows:
        if x not in a:a.append(x)
targets=uygulamalar.practice_review_targets(base)
passages={x['id']:x for x in base['passage']}
affected={('practice_event',manisa+'-event'),('practice_relation',manisa+'-relation'),
          ('practice_relation.explanation_finding_id',manisa+'-relation')}
for row in r['practice_source_review']:
    k=(row['subject_kind'],row['subject_id'])
    if k in affected:
        ids=sorted(targets[k][0]); row['passage_ids']=json.dumps(ids,ensure_ascii=False)
        row['source_version_ids']=json.dumps(sorted({passages[x]['version_id'] for x in ids}),ensure_ascii=False)
        row['reason']+=' ANKA özgün sonucu ve divan açıklaması da okundu; F5 aynı olaydır.'
new_targets=uygulamalar.practice_review_targets(base,records)
for (kind,identity),(pids,_) in new_targets.items():
    ids=sorted(pids)
    r['practice_source_review'].append({'subject_kind':kind,'subject_id':identity,'reviewer_kind':'agent','reviewed_at':now,
        'source_version_ids':json.dumps(sorted({passages[x]['version_id'] for x in ids}),ensure_ascii=False),
        'passage_ids':json.dumps(ids,ensure_ascii=False),'inspected_sections':json.dumps(['Sulakyurt veya Manisa kaynakları: '+kind],ensure_ascii=False),
        'supported_claim':identity+' için ilgili tüzük veya yerel kongre haberi okunup kaynak aşaması belirlendi.',
        'limitations':'Resmî tutanaklar görülmedi; ANKA ve F5 aynı Manisa olayı için bağımsız sayım değildir.',
        'result':'reviewed','reason':identity+' hedefinin belirli pasajları gerçek kaynaklarda incelendi.'})
    r['source_review_refs'].append({'subject_kind':kind,'subject_id':identity})
uygulamalar.validate_practice_source_review(base,r['practice_source_review'],party_id='yeni-parti')
for n,obj in [('package-anka-sulakyurt-105-union-draft.json',p),('anka-sulakyurt-105-union-review-draft.json',r)]:
    (D/n).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(r['practice_source_review']),len(p['practice_records']['practice_event']),len(p['practice_records']['practice_relation']))
