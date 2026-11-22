"""Yalnızca doğrulanmış Aliağa adayı canlıya alındıktan sonra çalıştırılır."""
import hashlib,json,sqlite3,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from uygulamalar import practice_review_targets
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks');live=Path('data/practices/04-tip.json');rev=Path('data/practices/04-tip-review.json')
assert hashlib.sha256(Path('data/practices/sources/tip/objects/f41542187d09f436ac0af5be886c417f9fcd983401c6b86d2dfa722fef341e07/readable.html').read_bytes()).hexdigest()=='2374b87000c871c696d85f044150e93507cb443176a0d0b1f10a5e4e84202219'
assert hashlib.sha256(live.read_bytes()).hexdigest()=='b38b4625cf600a8e035601783840dcfbbc6c51443f3eb666e113c5b43a016547','Aliağa tam kapıdan geçip canlıya alınmamış'
assert hashlib.sha256(rev.read_bytes()).hexdigest()=='fcf88d34f5737196000201d0373fae78d8708f696529dcc490d46ddd6cf66da2'
pkg=json.loads(live.read_text());review=json.loads(rev.read_text());now=datetime.now(timezone.utc).isoformat();entries=json.loads((p/'tezkere-3761-source-records.json').read_text())['entries'];records={}
def add(k,v):entries.append(dict(kind=k,values=v))
def rec(k,v):records.setdefault(k,[]).append(v)
prefix='0405-tip-tezkere-3761';t='0405-tip-20231017-tezkere-tutanak';v='0405-tip-20231017-tezkere-oy';a=t+'-authority-full-p';q=t+'-statement-p';spoken=t+'-ballot-p';name=v+'-name-p';vote=v+'-vote-p';ev=prefix+'-event';statement=prefix+'-statement';con=prefix+'-contribution';rel=prefix+'-relation'
add('actor',dict(id=prefix+'-kadigil',kind='authorized_representative',party_id='tip',person_id='0405-tip-sera-kadigil',authorization_passage_id=a))
fs=[(prefix+'-summary','Kadıgil, TİP adına başka ülke topraklarında askerî operasyonlara karşı olduklarını açıkladı.','summary',[a,q]),(prefix+'-quote','Başka ülkelerin topraklarında askerî operasyon yürütülmesine “hayır” diyoruz.','quote',[q]),(prefix+'-action','Kadıgil, 17 Ekim 2023’te Irak ve Suriye tezkeresi 3/761 için açık oylamada ret oyu kullandı.','summary',[name,vote,spoken]),(prefix+'-explanation','Kadıgil’in TİP adına belirttiği sınır ötesi askerî operasyonlara karşı tutumu ile aynı gün 3/761 tezkeresinde kullandığı ret oyu ilişkilidir. Konuşma tutanakta oylamadan önce yer alır; tek milletvekilinin oyu tüm milletvekillerinin katıldığını göstermez.','summary',[a,q,spoken,name,vote])]
for fid,text,prov,refs in fs:
 add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=statement if fid in (prefix+'-summary',prefix+'-quote') else fid,text=text,provenance=prov,epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='quotation' if prov=='quote' else 'support'));add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='TBMM özgün tutanak ve oy cetvelinin ilgili sırası okundu.'))
 add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Parti adına açıklama ile kişisel oy ve oturum sırası ayrıldı.'))
inv=json.loads(Path('data/practices/04-inventory.json').read_text())
for kind in ('statement','event'):
 cell=next(x for x in inv['cells'] if x['party_id']=='tip' and x['topic_id']=='dis-guvenlik' and x['research_kind']==kind)
 rec('practice_scope_v2',dict(id=cell['cell_id'],party_id='tip',topic_id='dis-guvenlik',taxonomy_version=cell['taxonomy_version'],period_start=cell['period_start'],cutoff_at=cell['cutoff_at'],research_kind=kind,boundary_reason='17 Ekim 2023 tezkeresi incelendi; diğer dönem ve uçlar açık.'))
 if kind=='event':scope=cell['cell_id']
rec('practice_event',dict(id=ev,common_event_key='tbmm-28-2-008-3-761-tezkere',event_at='2023-10-17',date_precision='day',date_unknown_reason=None,scope_context='28. dönem 8. birleşim açık oylama',title='Irak ve Suriye tezkeresi 3/761 açık oylaması',occurrence_basis='TBMM 8. birleşim tutanağı ve açık oy cetveli.'))
for pid,point in [(name,'Saliha Sera Kadıgil oy cetveli ad hücresi'),(vote,'Aynı satırdaki ret oyu ve saat'),(spoken,'Tutanaktaki oylamanın başlatılması')]:
 rec('practice_event_evidence',dict(event_id=ev,passage_id=pid,supported_point=point,stage='action',concrete_basis='TBMM resmî tutanağı ve kişisel oy cetveli.',limitation='Kişisel ret oyu diğer milletvekillerinin oyu değildir; ilan ve kesin cetvel sayıları farklı aşamalardır.',epistemic_type='claim'));rec('practice_evidence_assessment',dict(event_id=ev,passage_id=pid,stage='action',basis_kind='document'))
rec('practice_contribution',dict(id=con,event_id=ev,party_id='tip',actor_id=prefix+'-kadigil',contribution_kind='objection',finding_id=prefix+'-action',authority_passage_id=a,membership_passage_id=None,responsibility_limit='Kadıgil’in kişisel oyudur; Baş ve Şık cetvelde katılmadı.'))
rec('practice_actor_period',dict(contribution_id=con,valid_from='2023-10-17',valid_to='2023-10-17',identity_passage_id=a))
rec('practice_statement',dict(id=statement,party_id='tip',topic_id='dis-guvenlik',taxonomy_version=4,summary_finding_id=prefix+'-summary',quote_finding_id=prefix+'-quote',statement_at='2023-10-17',date_precision='day',version_id=t+'-v1',period_basis='Aynı birleşimde oylama öncesi parti adına açıklama.',uncertainty_reason='Oturum konuşması belirli oylama bağlamındadır.',comparison_row_id='04-03-v3-0304-tip-program-sosyalist-dis-silah-row'))
rec('practice_relation',dict(id=rel,statement_id=statement,event_id=ev,party_id='tip',topic_id='dis-guvenlik',scope_id=scope,comparability_reason='Açıklama sınır ötesi askerî operasyonlara karşıdır; tezkere de sınır ötesi yetkiyi uzatır.',target_finding_id=prefix+'-summary',result_finding_id=None,explanation_finding_id=prefix+'-explanation',temporal_context='Açıklama ve oy aynı gün; tutanakta konuşma oylamadan öncedir.',authority_context='Kadıgil kişisel oy kullanmıştır; tezkerenin kabulüne Meclis karar verir.',uncertainty_reason='Diğer vekillerin katılmama durumu parti ret oyu sayılmaz.'))
pkg['entries'].extend(entries)
for k,rows in records.items():pkg['practice_records'].setdefault(k,[]).extend(rows)
data={k:list(v) for k,v in pkg['practice_records'].items()}
for x in pkg['entries']:data.setdefault(x['kind'],[]).append(x['values'])
db=sqlite3.connect('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.sqlite3');db.row_factory=sqlite3.Row
for table in ('finding_evidence','passage'):data.setdefault(table,[]).extend(dict(x) for x in db.execute('SELECT * FROM '+table))
versions={x['id']:x['version_id'] for x in data['passage']};targets=practice_review_targets(data,records)
for (kind,identity),(refs,parties) in targets.items():
 review['practice_source_review'].append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({versions[x] for x in refs})),passage_ids=json.dumps(sorted(refs)),inspected_sections=json.dumps(['TBMM parti adına konuşma ve açık oylama sırası','Windows-1254 özgün cetvelde Kadıgil kişisel oy satırı'],ensure_ascii=False),supported_claim='Tarihli söylem ve kişisel oy kaynak bağlamında okundu: '+identity,limitations='İki TBMM belgesi bağımsız yayıncı değildir; ilan ve kesin oy cetveli farklı sayılardır.',result='reviewed',reason='Özgün pasajlar ve satır bağlamı incelendi: '+kind+' '+identity));review['source_review_refs'].append(dict(subject_kind=kind,subject_id=identity))
for name,obj in [('3761-append-draft.json',pkg),('3761-review-draft.json',review)]:(p/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY',len(entries),len(targets))
