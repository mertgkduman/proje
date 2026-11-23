import copy,datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
import uygulamalar as rules
D=Path(__file__).parent;ROOT=Path('data/practices/sources/yeni-parti');read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
live=Path('data/practices/04-yeni-parti.json');review=Path('data/practices/04-yeni-parti-review.json')
assert sha(live)=='50eef2357332ff02a7073332ac3345a625bd2d112f837d73d6613c99be606ce1' and sha(review)=='02f29b840cc994cbd2807a644e7c05245f6678c8784635c00e308077906124d6'
pkg=read(live);previous=read(review);base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');entries=pkg['entries'];records=pkg['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def add(table,**v):entries.append(dict(kind=table,values=v))
vid='0404-tbmm-yemek-akdogan-1103-v1'; version=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==vid);assert version['sha256']=='43f76c014493808d974aed00ce23152667132f1862f387bde6f788524a17357b';raw=(ROOT/version['original_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==version['sha256'];text=html_source_text(raw)
begin='Grup Başkan Vekili Balıkesir Milletvekili Turhan Çömez tarafından, Türkiye Sigorta ve Türkiye Hayat ve Emeklilikin';end='görüşmelerin 3/11/2026 Salı günkü birleşimde yapılması önerilmiştir.';i=text.index(begin);j=text.index(end,i)+len(end);proposal=text[i:j];assert '<' not in proposal and len(proposal)<1000
identity='BAŞKAN - Yeni Parti Grubu adına Antalya Milletvekili Sayın Aykut Kaya.';support='Yeni Parti olarak İYİ Partinin araştırma önergesini destekliyoruz.';result='BAŞKAN - Öneriyi oylarınıza sunuyorum: Kabul edenler... Kabul etmeyenler... Kabul edilmemiştir.'
assert i<text.index(identity,i)<text.index(support,i)<text.index(result,text.index(support,i))<text.index('Cumhuriyet Halk Partisi Grubunun İç Tüzük',text.index(result,text.index(support,i)))
prefix='0404-nov03-genelgorusme-yeniparti-4961';sections={'proposal':'İYİ Parti 2. grup gündem önerisi','identity':'Yeni Parti grup temsilcisi','support':'Aykut Kaya grup adına destek','result':'2. önerinin açık oylama olmayan gündem sonucu'}
for suffix,exact in [('proposal',proposal),('identity',identity),('support',support),('result',result)]:
 add('passage',id=prefix+'-'+suffix+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=sections[suffix],pdf_page_index=None,printed_page=None)
entries.extend(read(D/'nov03-genelgorusme-yeniparti-4961-source-records.json')['entries'])
pid=prefix+'-person'; actor=prefix+'-actor'; ip=prefix+'-identity-p'; sp=prefix+'-support-p'; pp=prefix+'-proposal-p'; rp=prefix+'-result-p'; fid=prefix+'-finding';eid=prefix+'-event';candidate=prefix+'-unmatched';con=prefix+'-contribution'
add('person',id=pid,name='Aykut Kaya');add('actor',id=actor,kind='authorized_representative',party_id='yeni-parti',person_id=pid,authorization_passage_id=ip)
add('finding',id=fid,party_id='yeni-parti',heading='Belgelenmiş uygulamalar',pair_id=fid,text='Aykut Kaya, Yeni Parti Grubu adına İYİ Parti’nin 10/4961 sigorta ve emeklilik araştırma önergesinin ön görüşmesinin aynı gün yapılması talebini destekledi. Başkan talebin kabul edilmediğini açıkladı.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='İkinci grup önerisi, Yeni Parti adına söz ve başkanın talebe ilişkin sonucu kesintisiz bağlamıyla okundu.')
for p in (pp,ip,sp,rp,prefix+'-register-number',prefix+'-register-date',prefix+'-signed-number',prefix+'-signed-scope'):add('finding_evidence',finding_id=fid,passage_id=p,role='support');add('verification',finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='3 Kasım birleşimi, esas sicili ve imzalı önerge kaynak sınırlarında okundu.')
scope=next(x['id'] for x in records['practice_scope_v2'] if x['topic_id']=='seffaflik-yolsuzluk' and x['research_kind']=='event')
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-5-012-10-4961-gundem',event_at='2026-11-03',date_precision='day',date_unknown_reason=None,title='10/4961 sigorta ve emeklilik araştırmasının ön görüşme talebinin reddi',scope_context='İYİ Parti Grubu, Türkiye Sigorta ve Türkiye Hayat ve Emeklilik hakkında verdiği 10/4961 araştırma önergesinin ön görüşmesinin 3 Kasım 2026 birleşiminde yapılmasını istedi. Genel Kurul bu gündem talebini reddetti.',occurrence_basis='TBMM 28. Dönem 5. Yasama Yılı 12. Birleşim ham tutanağı, imzalı 10/4961 önergesi ve TBMM esas kaydı.'))
limit='Ret, araştırma ön görüşmesinin o birleşimde yapılması talebine aittir; esas araştırma dosyasının sonucu ve kişisel oy bilinmiyor.'
for p,stage,point in [(prefix+'-register-number','initiative','TBMM sicilinde 10/4961 esas numarası.'),(prefix+'-register-date','initiative','TBMM sicilinde 3 Kasım geliş tarihi.'),(prefix+'-signed-number','initiative','İmzalı dosyada 10/4961 numarası.'),(prefix+'-signed-scope','initiative','Önerge gerekçesinde şirketler ve gözetim kapsamı.'),(pp,'initiative','İYİ Parti’nin aynı gün ön görüşme önerisi.'),(ip,'action','Başkan Kaya’ya Yeni Parti Grubu adına söz verdi.'),(sp,'action','Kaya grup adına öneriyi destekledi.'),(rp,'result','Başkan gündem önerisinin kabul edilmediğini bildirdi.')]:
 records['practice_event_evidence'].append(dict(event_id=eid,passage_id=p,stage=stage,supported_point=point,concrete_basis='TBMM ham tutanağı, esas sicili veya imzalı önerge.',limitation=limit,epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=p,stage=stage,basis_kind='document'))
records['practice_contribution'].append(dict(id=con,event_id=eid,party_id='yeni-parti',actor_id=actor,contribution_kind='support',finding_id=fid,authority_passage_id=ip,membership_passage_id=None,responsibility_limit='Kaya grup adına sözlü destek açıkladı; kişisel açık oy kaydı gösterilmedi.'))
records['practice_actor_period'].append(dict(contribution_id=con,valid_from='2026-11-03',valid_to='2026-11-03',identity_passage_id=ip))
reason='Genel programdaki şeffaflık ifadesi bu özel araştırma ve gündem önerisiyle aynı ölçekte değil; daha önceki doğrudan söylem araştırması açık.'
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,relation_id=None,state='unmatched',reason=reason,passage_ids=json.dumps([pp,ip,sp,rp,prefix+'-register-number',prefix+'-register-date',prefix+'-signed-number',prefix+'-signed-scope'],ensure_ascii=False)))
prior=[x for x in records['practice_scope_source'] if x['scope_id']==scope and x['version_id']==vid];combined=set(sections.values())
for x in prior:combined.update(json.loads(x['inspected_sections']))
url=version['original_url'];aid=prefix+'-attempt';records['practice_scope_source'].append(dict(scope_id=scope,version_id=vid,inspected_sections=json.dumps(sorted(combined),ensure_ascii=False),inspected_at=now));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='İkinci grup önerisi, Kaya’nın grup adına desteği ve aynı önerinin reddi okundu; esas dosya ve kişisel oy açık.',source_version_id=vid))
if not any(x['scope_id']==scope and x['url']==url for x in records['practice_lead']):records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason='İYİ Parti araştırma gündemi ve Yeni Parti grup görüşü',state='examined',attempt_ids=json.dumps([aid])))
for role in ('register','signed'):
 v=next(e['values'] for e in entries if e['kind']=='document_version' and e['values']['id']==prefix+'-'+role+'-v1');u=v['original_url'];a=prefix+'-'+role+'-attempt';sec=[e['values']['section'] for e in entries if e['kind']=='passage' and e['values']['version_id']==v['id']];records['practice_scope_source'].append(dict(scope_id=scope,version_id=v['id'],inspected_sections=json.dumps(sec,ensure_ascii=False),inspected_at=now));records['practice_attempt_v2'].append(dict(id=a,scope_id=scope,attempted_at=now,query=u,url=u,result='examined',reason='10/4961 sicili ve üç sayfa imzalı önerge okundu.',source_version_id=v['id']));records['practice_lead'].append(dict(id='lead-'+a,scope_id=scope,url=u,relevance_reason='10/4961 esas dosyası',state='examined',attempt_ids=json.dumps([a])))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():
 if table in ('practice_contract','practice_coverage_contract','practice_variant_contract','practice_evidence_contract'):data[table]=copy.deepcopy(rows)
 else:data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='yeni-parti');passages={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']):x for x in previous['practice_source_review']};reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 rows=[passages[x] for x in sorted(ids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({x['version_id'] for x in rows})),passage_ids=json.dumps([x['id'] for x in rows]),inspected_sections=json.dumps(sorted({x['section'] for x in rows}),ensure_ascii=False),supported_claim='İkinci grup önerisi, Yeni Parti sözel desteği ve gündem sonucu okundu.',limitations=limit,result='reviewed',reason=kind+' / '+identity+' özgün tutanak bağlamı incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='yeni-parti',target_keys=set(targets));refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];pkg['source_review_refs']=refs
for name,obj in [('nov03-genelgorusme-yeniparti-4961-draft.json',pkg),('nov03-genelgorusme-yeniparti-4961-review.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('NOV03_SEMANTIC_PASS',len(reviews),eid,candidate)
