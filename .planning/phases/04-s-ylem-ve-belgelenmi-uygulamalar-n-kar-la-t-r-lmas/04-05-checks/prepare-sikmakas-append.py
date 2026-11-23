import copy,datetime,hashlib,json,shutil,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
import uygulamalar as rules
D=Path(__file__).parent; E=D.parent/'04-10-checks'; ROOT=Path('data/practices/sources/tip'); OTHER=Path('data/practices/sources/emep')
read=lambda p:json.loads(Path(p).read_text()); sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
live=Path('data/practices/04-tip.json'); rev=Path('data/practices/04-tip-review.json')
assert sha(live)=='e7c25b0daea6273fbe19dc1f7daf643590625cbd3ae72b01ecf6b8807aa80ea2' and sha(rev)=='7f567c7db246a6faa793d1017cad5a12f2f97d7a5443c93e4211e73ed9497581'
pkg=read(live); previous=read(rev); base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json'); entries=pkg['entries']; records=pkg['practice_records']; now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def add(table,**v):entries.append(dict(kind=table,values=v))
for entry in read(E/'sik-makas-source-draft.json')['entries']:
 row=copy.deepcopy(entry['values']); kind=entry['kind']
 if '0410-emep-sik-makas-party' in json.dumps(row,ensure_ascii=False):continue
 for key,value in row.items():
  if isinstance(value,str):row[key]=value.replace('0410-emep-sik-makas-','0405-tip-sik-makas-')
 if kind=='document':row['party_id']='tip'
 if kind=='document_version':
  for k in ('original_path','readable_path'):
   src=OTHER/row[k]; dest=ROOT/row[k]; dest.parent.mkdir(parents=True,exist_ok=True)
   if not dest.exists():shutil.copyfile(src,dest)
   assert sha(src)==sha(dest)
 if kind=='archive_view':
  path=Path(row['manifest_path']);src=OTHER/path.parent;dest=ROOT/path.parent
  if not dest.exists():shutil.copytree(src,dest)
  for f in src.rglob('*'):
   if f.is_file():assert sha(f)==sha(dest/f.relative_to(src))
 entries.append(dict(kind=kind,values=row))
news='0405-tip-sik-makas-anka-v1'; raw=(ROOT/'objects/2629ffa4231dfcf20c359916cb7f32a7543b3cedbb50359caffe90c00809d042/original.html.bin').read_bytes();text=html_source_text(raw)
for suffix,exact in [('identity','TİP Genel Başkanı Erkan Baş'),('commitment','Bu bilin&ccedil;le bu direnişe yaklaşmak ve arkadaşların m&uuml;cadelesinin sonuna kadar yanında durmak gerekiyor')]:
 assert exact in text
 add('passage',id='0405-tip-sik-makas-'+suffix+'-p',version_id=news,exact=exact,prefix=None,suffix=None,article=None,section='Baş’ın toplantıda desteği',pdf_page_index=None,printed_page=None)
eid='0405-tip-sik-makas-event'; rid='0405-tip-sik-makas-relation'; fid='0405-tip-sik-makas-explanation'; con='0405-tip-sik-makas-contribution'; candidate='0405-tip-sik-makas-candidate';aid='0405-tip-sik-makas-anka-meeting-p'; identity='0405-tip-sik-makas-identity-p'; statement='0405-tip-sik-makas-commitment-p'; program='0304-tip-program-sendika-p1';scope=next(x['id'] for x in records['practice_scope_v2'] if x['topic_id']=='sendika-grev' and x['research_kind']=='event')
add('finding',id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=fid,text='TİP programı sendikal örgütlenme hakkını savunur. ANKA yayınına göre Erkan Baş, Şık Makas işçileriyle TBMM basın toplantısına katıldı ve işçilerin mücadelesinin yanında durulması gerektiğini söyledi.',provenance='summary',epistemic_type='claim')
add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, toplantı ve Baş’ın ayrı sözleri okundu; toplantı günü ve sonuç açık.')
for p in (program,aid,identity,statement):
 add('finding_evidence',finding_id=fid,passage_id=p,role='support');add('verification',finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='Program ve iki yayın ilgili aktörleriyle incelendi.')
shared=next(x for x in read(E/'sik-makas-union-draft.json')['practice_records']['practice_event'] if x['common_event_key']=='tbmm-sik-makas-karaca-isci-basin-toplantisi-2026'); shared=copy.deepcopy(shared); shared['id']=eid; records['practice_event'].append(shared)
for p,point,basis,stage in [(aid,'ANKA yayını Karaca ve işçilerle TBMM toplantısını aktarır.','document','action'),(statement,'ANKA yayını Baş’ın işçilerin mücadelesi yanında durma çağrısını aktarır.','document','action')]:
 records['practice_event_evidence'].append(dict(event_id=eid,passage_id=p,supported_point=point,stage=stage,concrete_basis='EMEP veya ANKA yayını.',limitation='Yayın tarihi kesin toplantı günü değildir; işçi alacaklarının sonucu gösterilmedi.',epistemic_type='claim'));records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=p,stage=stage,basis_kind=basis))
auth='0405-tip-20241106-bas-authority-p';records['practice_contribution'].append(dict(id=con,event_id=eid,party_id='tip',actor_id='0405-tip-kayyum-bas',contribution_kind='support',finding_id=fid,authority_passage_id=auth,membership_passage_id=None,responsibility_limit='Baş’ın haberde bildirilen toplantı katılımı ve destek açıklaması; alacaklara ilişkin karar veya ödeme yetkisi gösterilmedi. Kimlik döneminin günü haberin güncellemesidir, toplantı tarihi değildir.'));records['practice_actor_period'].append(dict(contribution_id=con,valid_from='2026-06-03',valid_to='2026-06-03',identity_passage_id=identity))
records['practice_relation'].append(dict(id=rid,statement_id='0405-tip-sendika-statement',event_id=eid,party_id='tip',topic_id='sendika-grev',scope_id=scope,comparability_reason='Program sendikal örgütlenmeyi savunur; toplantıda Baş işçilerin hak mücadelesine destek bildirir.',target_finding_id='0304-tip-program-sendika-summary',result_finding_id=None,explanation_finding_id=fid,temporal_context='Program tarihi bilinmiyor; ANKA ve EMEP yayınları Mart 2026 tarihlidir.',authority_context='Baş’ın katkısı toplantı ve destek sözüyle sınırlıdır; işveren veya idare adına karar yetkisi gösterilmedi.',uncertainty_reason='Programın 2026 yürürlük dönemi, toplantının kesin günü ve işçi taleplerinin sonucu doğrulanmadı.'))
records['practice_candidate'].append(dict(id=candidate,scope_id=scope,event_id=eid,relation_id=rid,state='eligible',reason='ANKA toplantıyı ve Baş’ın ayrı destek sözünü aktarıyor.',passage_ids=json.dumps([aid,identity,statement])))
for v in (news,):
 version=next(x['values'] for x in entries if x['kind']=='document_version' and x['values']['id']==v); url=version['original_url']; sections=sorted({x['values']['section'] for x in entries if x['kind']=='passage' and x['values']['version_id']==v});attempt='0405-tip-sik-makas-attempt-anka';records['practice_scope_source'].append(dict(scope_id=scope,version_id=v,inspected_sections=json.dumps(sections,ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+attempt,scope_id=scope,url=url,relevance_reason='Toplantı ve aktör sözleri',state='examined',attempt_ids=json.dumps([attempt])));records['practice_attempt_v2'].append(dict(id=attempt,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='Yayın okundu; olay tarihi ve sonucu açık.',source_version_id=v))
data=copy.deepcopy(base)
for e in entries:
 if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
for table,rows in records.items():
 if table in ('practice_contract','practice_coverage_contract','practice_variant_contract','practice_evidence_contract'):data[table]=copy.deepcopy(rows)
 else:data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_package_targets(data,records,{x['passage_id'] for x in records['practice_event_evidence']},party_id='tip');passages={x['id']:x for x in data['passage']};old={(x['subject_kind'],x['subject_id']):x for x in previous['practice_source_review']};reviews=[]
for (kind,identity),(ids,parties) in sorted(targets.items()):
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 rows=[passages[x] for x in sorted(ids)];reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({x['version_id'] for x in rows})),passage_ids=json.dumps([x['id'] for x in rows]),inspected_sections=json.dumps(sorted({x['section'] for x in rows}),ensure_ascii=False),supported_claim='Program, katılımcılar ve Baş’ın destek sözü kaynaklarıyla okundu.',limitations='Toplantı günü, programın 2026 yürürlük durumu ve işçi taleplerinin sonucu açık.',result='reviewed',reason=kind+' / '+identity+' kaynakları incelendi.'))
rules.validate_practice_source_review(data,reviews,party_id='tip',target_keys=set(targets)); refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];pkg['source_review_refs']=refs
for name,obj in [('sikmakas-append-draft.json',pkg),('sikmakas-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
print('SIKMAKAS_SEMANTIC_PASS',len(reviews),eid,rid)
