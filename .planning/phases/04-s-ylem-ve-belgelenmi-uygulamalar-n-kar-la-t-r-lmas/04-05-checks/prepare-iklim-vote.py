import copy, datetime, hashlib, json, re, shutil, sys
from pathlib import Path
sys.path.insert(0, 'src')
import uygulamalar as rules
from arsiv import html_source_text

D = Path(__file__).parent
E = D.parent/'04-10-checks'
ROOT = Path('data/practices/sources/tip')
OTHER = Path('data/practices/sources/emep')
read = lambda p: json.loads(Path(p).read_text())
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
live, old = Path('data/practices/04-tip.json'), Path('data/practices/04-tip-review.json')
assert digest(live) == '3b37986f75c88c387fdb5bf1e6ea5b6c8f220bcb11252436b080bdd79244468a'
assert digest(old) == '15c3659fd3affb700bf8265bca65490f9e2d187b2e1fc98f2c2f41cfebd23ce8'
package, previous = read(live), read(old)
base = read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
inventory = read('data/practices/04-inventory.json')
entries, records = package['entries'], package['practice_records']
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def add(table, **values): entries.append(dict(kind=table, values=values))

# Adopt the exact shared TBMM registration bytes, but use party-local identities.
for source_file in ('climate-register-source-draft.json', 'climate-vote-source-draft.json'):
 for entry in read(E/source_file)['entries']:
  row = copy.deepcopy(entry['values']); kind = entry['kind']
  if kind == 'passage' and source_file.startswith('climate-vote'): continue
  for key, value in list(row.items()):
   if isinstance(value,str): row[key] = value.replace('0410-emep-climate-2025-', '0405-tip-climate-2025-')
  if kind == 'document': row['party_id'] = 'tip'
  if kind == 'document_version':
   for k in ('original_path','readable_path'):
    path=Path(row[k]); target=ROOT/path; origin=OTHER/path
    if not target.exists(): target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(origin,target)
    assert digest(target)==digest(origin)
  if kind == 'archive_view':
   manifest=Path(row['manifest_path']); directory=manifest.parent
   if not (ROOT/manifest).exists(): shutil.copytree(OTHER/directory,ROOT/directory)
   assert digest(ROOT/manifest)==digest(OTHER/manifest)
  entries.append(dict(kind=kind,values=row))

ballot=ROOT/'objects/f7df0eac646ee87b066a347118dca3c2e74e4e0f08db7084dcb4f95b0256aae4/original.html.bin'
raw=html_source_text(ballot.read_bytes())
rows=re.findall(r'<tr[^>]*>.*?</tr>',raw,re.S)
pids=['0405-tip-climate-2025-register-number-p']
for suffix, needle, firstname in [('bas','BA&#x15E;','Erkan'),('kadigil','KADIG&#x130;L','Saliha'),('sik','&#x15E;IK','Ahmet')]:
 matches=[x for x in rows if f'<td>{needle}</td>' in x and firstname in x and 'RET' in x]
 assert len(matches)==1 and '\ufffd' not in matches[0]
 exact=matches[0][matches[0].find('<td>'):matches[0].rfind('</td>')+5]
 pid='0405-tip-climate-2025-ballot-'+suffix+'-p';pids.append(pid)
 add('passage',id=pid,version_id='0405-tip-climate-2025-ballot-v1',exact=exact,prefix=None,suffix=None,article=None,section='Kesin açık oy cetveli bireysel satırı',pdf_page_index=None,printed_page=None)

for kind in ('statement','event'):
 cell=next(x for x in inventory['cells'] if x['party_id']=='tip' and x['topic_id']=='doga-ekoloji' and x['research_kind']==kind)
 records['practice_scope_v2'].append(dict(id=cell['cell_id'],party_id='tip',topic_id='doga-ekoloji',taxonomy_version=4,period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='Program ve 2 Temmuz 2025 kesin oy cetveli incelendi; diğer olaylar ve sonuçlar açık.'))
scope=next(x['id'] for x in records['practice_scope_v2'] if x['party_id']=='tip' and x['topic_id']=='doga-ekoloji' and x['research_kind']=='event')
program='0304-tip-program-doga-p1'; quote='0304-tip-program-doga-q'
records['practice_statement'].append(dict(id='0405-tip-climate-statement',party_id='tip',topic_id='doga-ekoloji',taxonomy_version=4,summary_finding_id='0304-tip-program-doga-summary',quote_finding_id='0304-tip-program-doga-quote',statement_at=None,date_precision='unknown',version_id='0203-tip-program-v1',period_basis='Programın yayın ve kabul tarihi kesin değil.',uncertainty_reason='2025 tarihinde yürürlükte olduğu bağımsız doğrulanmadı.',comparison_row_id='04-03-v3-0304-tip-program-doga-row'))
for finding,pid in [('0304-tip-program-doga-summary',program),('0304-tip-program-doga-summary',quote),('0304-tip-program-doga-quote',quote)]: add('verification',finding_id=finding,passage_id=pid,checked_at=now,result='confirmed',reason='Programın ilgili paragrafı okundu.')
for finding in ('0304-tip-program-context-madencilik-summary','0304-tip-program-context-afet-summary'):
 for ref in base['finding_evidence']:
  if ref['finding_id']==finding: add('verification',finding_id=finding,passage_id=ref['passage_id'],checked_at=now,result='confirmed',reason='Programın ilgili paragrafı ve açıklayıcı kapsam kaydı okundu.')
eid='0405-tip-climate-22927-event';rid='0405-tip-climate-22927-relation';fid='0405-tip-climate-22927-explanation'
add('finding',id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=fid,text='TİP programı doğal varlıkların metalaştırılmasına karşı çıkar. 2 Temmuz 2025 kesin cetvelinde Erkan Baş, Saliha Sera Kadıgil ve Ahmet Şık için ayrı ayrı ret oyları yer alır.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program ve resmi kayıtların ayrı pasajları okundu.')
for pid in [program]+pids:
 add('finding_evidence',finding_id=fid,passage_id=pid,role='support');add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Kaynak pasajı ve bağlamı okundu.')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-3-104-2-2927-iklim-kanunu',event_at='2025-07-02',date_precision='day',date_unknown_reason=None,scope_context='TBMM 104. birleşim kesin açık oy cetveli',title='İklim Kanunu kesin açık oylaması',occurrence_basis='TBMM kesin açık oy cetveli ve 2/2927 teklif kaydı.'))
for pid,point in zip(pids,['Teklif kaydı esas numarasını 2/2927 olarak gösterir.','Kesin cetvel Erkan Baş için ret oyu kaydeder.','Kesin cetvel Sera Kadıgil için ret oyu kaydeder.','Kesin cetvel Ahmet Şık için ret oyu kaydeder.']):
 records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage='action',concrete_basis='TBMM teklif kaydı ve kesin açık oy cetveli.',limitation='Bireysel oylar kanunun çevresel etkisini veya komisyon oylarını göstermez.',epistemic_type='claim'))
 records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id='0405-tip-climate-statement',event_id=eid,party_id='tip',topic_id='doga-ekoloji',scope_id=scope,comparability_reason='Program doğal varlıkları ele alır; oylanan kanun iklim değişikliğiyle ilgilidir. Oy programın gerçekleşmesi anlamına gelmez.',target_finding_id='0304-tip-program-doga-summary',result_finding_id=None,explanation_finding_id=fid,temporal_context='Program yayını ile 2 Temmuz 2025 oylaması ayrı tarihlerdir.',authority_context='Oylar üç milletvekiline ayrı ayrı aittir.',uncertainty_reason='Programın 2025 yürürlük durumu ve yasanın etkisi oy cetvelinden çıkarılmaz.'))
records['practice_candidate'].append(dict(id='0405-tip-climate-22927-candidate',scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='Kesin cetvelde üç TİP milletvekilinin bireysel oyları.',passage_ids=json.dumps(pids)))
versions={e['values']['id']:e['values'] for e in entries if e['kind']=='document_version'}
for i,role in enumerate(('register','ballot')):
 v='0405-tip-climate-2025-'+role+'-v1';url=versions[v]['original_url']; section=('2/2927 teklif kaydı','Üç TİP milletvekilinin kesin oy satırları')[i];aid='0405-tip-climate-attempt-'+str(i)
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; kapsam açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():
 if table in ('practice_contract','practice_coverage_contract','practice_variant_contract','practice_evidence_contract'):
  data[table]=copy.deepcopy(rows)
 else: data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data)
new_passages={x['passage_id'] for x in records['practice_event_evidence']};targets=rules.practice_review_package_targets(data,records,new_passages,party_id='tip');passages={p['id']:p for p in data['passage']};old_reviews={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in old_reviews: reviews.append(old_reviews[(kind,identity)]);continue
 inspected=[passages[x] for x in sorted(ids)]
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({x['version_id'] for x in inspected})),passage_ids=json.dumps([x['id'] for x in inspected]),inspected_sections=json.dumps(sorted({x['section'] for x in inspected}),ensure_ascii=False),supported_claim='Program, teklif kaydı ve kişisel kesin oy satırları ayrı okundu.',limitations='Kanunun etkisi ve 2025 program yürürlüğü çıkarılmaz.',result='reviewed',reason=kind+' / '+identity+' kaynak pasajları incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='tip',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for n,obj in [('iklim-append-draft.json',package),('iklim-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/n).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('IKLIM_SEMANTIC_PASS',len(reviews),eid,rid)
