import copy,datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;E=D.parent/'04-08-checks';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
live=Path('data/practices/04-yeni-parti.json');review=Path('data/practices/04-yeni-parti-review.json');assert sha(live)=='7dd0e9d53922d65a4940b169aeca52b71ce16693bc6eadc4696d8d41ba6bb667' and sha(review)=='cfab87e0a39814413640d4a9ccabf062d5e27794bc8058e29a90f418f7bf0bc8'
v1=D/'nov03-genelgorusme-yeniparti-draft.json';assert sha(v1)=='d1baaa2cc5001c3fa6ce5848775fd1470333c9f502b429d869854a9d5ad5d17b'
pkg=read(v1);previous=read(review);base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');entries=pkg['entries'];records=pkg['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds');prefix='0404-nov03-genelgorusme-yeniparti';eid=prefix+'-event';candidate=prefix+'-unmatched'
allowed={'0408-nov03-genelgorusme-register-number','0408-nov03-genelgorusme-register-date','0408-nov03-genelgorusme-signed-number','0408-nov03-genelgorusme-signed-scope','0408-nov03-genelgorusme-signed-date','0408-nov03-genelgorusme-signed-role'}
for entry in read(E/'nov03-genelgorusme-source-records.json')['entries']:
 kind=entry['kind'];row=copy.deepcopy(entry['values']);vs=str(row.get('version_id',''));ident=str(row.get('id',''));passage=str(row.get('passage_id',''))
 if kind in ('document','document_version'): include=('-register' in ident or '-signed' in ident)
 elif kind in ('archive_view','source_attribution'):include=('-register' in vs or '-signed' in vs)
 elif kind=='passage':include=ident in allowed
 elif kind=='manual_passage':include=passage in allowed
 else:include=False
 if not include:continue
 for k,v in row.items():
  if isinstance(v,str):row[k]=v.replace('0408-nov03-genelgorusme-',prefix+'-')
 if kind=='document':row['party_id']='yeni-parti'
 entries.append(dict(kind=kind,values=row))
limit='8/153 esas genel görüşme dosyası ile 3 Kasım ön görüşmenin aynı gün yapılması gündem talebi ayrı işlemlerdir; kişisel oy ve kesim anındaki esas dosya sonucu bilinmiyor.'
for suffix,point in [('register-number','TBMM sicili esas numarasını 8/153 gösterir.'),('register-date','TBMM sicili Başkanlığa geliş tarihini 3 Kasım olarak kaydeder.'),('signed-scope','İmzalı metin ekonomik etkiler ve kamu denetimi üzerine genel görüşme ister.'),('signed-date','İmzalı metin 3 Kasım tarihini taşır.')]:
 p=prefix+'-'+suffix;records['practice_event_evidence'].append(dict(event_id=eid,passage_id=p,stage='initiative',supported_point=point,concrete_basis='8/153 TBMM sicili veya görsel okunan imzalı önerge.',limitation=limit,epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=p,stage='initiative',basis_kind='document'))
fid=prefix+'-finding'
for e in entries:
 if e['kind']=='finding' and e['values']['id']==fid:e['values']['text']='Aşkın Genç, Yeni Parti Grubu adına Yeni Yol’un 8/153 genel görüşme önergesinin ön görüşmesinin aynı gün yapılması talebini destekledi. Başkan talebin kabul edilmediğini açıkladı.'
for suffix in ('register-number','register-date','signed-scope','signed-date'):
 p=prefix+'-'+suffix;entries.append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=p,role='support')));entries.append(dict(kind='verification',values=dict(finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='8/153 sicili ve iki sayfa imzalı metin görsel olarak karşılaştırıldı.')))
scope=next(x['id'] for x in records['practice_scope_v2'] if x['topic_id']=='seffaflik-yolsuzluk' and x['research_kind']=='event');
for role in ('register','signed'):
 vid=prefix+'-'+role+'-v1';v=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==vid);url=v['original_url'];sections=sorted({e['values']['section'] for e in entries if e['kind']=='passage' and e['values']['version_id']==vid});aid=prefix+'-v2-'+role
 records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='8/153 sicili ve imzalı dosyanın ilgili bölümü okundu; esas durumun kesim tarihi açık.',source_version_id=vid));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason='8/153 esas dosyası',state='examined',attempt_ids=json.dumps([aid])))
for row in records['practice_candidate']:
 if row['id']==candidate:row['passage_ids']=json.dumps(json.loads(row['passage_ids'])+[prefix+'-register-number',prefix+'-register-date',prefix+'-signed-scope',prefix+'-signed-date'],ensure_ascii=False)
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():
 if table in ('practice_contract','practice_coverage_contract','practice_variant_contract','practice_evidence_contract'):data[table]=copy.deepcopy(rows)
 else:data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='yeni-parti');passages={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']):x for x in previous['practice_source_review']};reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 rows=[passages[x] for x in sorted(ids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({x['version_id'] for x in rows})),passage_ids=json.dumps([x['id'] for x in rows]),inspected_sections=json.dumps(sorted({x['section'] for x in rows}),ensure_ascii=False),supported_claim='8/153 sicili, imzalı önerge ve ilk gündem görüşmesi okundu.',limitations=limit,result='reviewed',reason=kind+' / '+identity+' birincil kayıtları ayrı incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='yeni-parti',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];pkg['source_review_refs']=refs
for name,obj in [('nov03-genelgorusme-yeniparti-v2-draft.json',pkg),('nov03-genelgorusme-yeniparti-v2-review.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('NOV03_V2_SEMANTIC_PASS',len(reviews),eid)
