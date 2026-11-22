import datetime,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent
base=json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text())
names=['mandate-3761','gebze-congress','izmit-congress','kocaeli-congress','luleburgaz-congress']
pid='0410-emep-tezkere-3761-ballot-vote-p'
subject='0410-mandate-3761-event|'+pid+'|action'
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
receipt=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in names:
 pp=D/(name+'-source-faithful-draft.json');rp=D/(name+'-source-faithful-review-draft.json')
 p=json.loads(pp.read_text());r=json.loads(rp.read_text());data=json.loads(json.dumps(base))
 for e in p['entries']:
  if e['values'] not in data.setdefault(e['kind'],[]):data[e['kind']].append(e['values'])
 for table,rows in p['practice_records'].items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
 passages={v['passage_id'] for v in p['practice_records']['practice_event_evidence']}
 targets=rules.practice_review_package_targets(data,p['practice_records'],passages,party_id='emep')
 seen={(x['subject_kind'],x['subject_id']) for x in r['practice_source_review']}
 assert set(targets)-seen=={('practice_event_evidence',subject)}
 assert targets[('practice_event_evidence',subject)][0]=={pid}
 r['practice_source_review'].append(dict(subject_kind='practice_event_evidence',subject_id=subject,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(['0410-emep-tezkere-3761-ballot-v1']),passage_ids=json.dumps([pid]),inspected_sections=json.dumps(['Aynı Bayhan satırında parti, ret oyu ve zaman'],ensure_ascii=False),supported_claim='Kesin açık oy cetvelinin Bayhan satırındaki ikinci özgün parça Emek Partisi, RET ve 19:33:43 alanlarını gösterir.',limitations='Soyad ve oy alanı aynı satırdaki iki ayrı ASCII pasajla birlikte okunmalıdır; oylama genel toplamı ayrıca değerlendirilir.',result='reviewed',reason='Olay kanıtı '+subject+' için özgün TBMM cetvelindeki parti, oy ve saat alanları okundu.'))
 refs=[{k:x[k] for k in ('subject_kind','subject_id')} for x in r['practice_source_review']];r['source_review_refs']=refs;p['source_review_refs']=refs
 rules.validate_practice_source_review(data,r['practice_source_review'],party_id='emep',target_keys=set(targets))
 np=D/(name+'-source-faithful-v2-draft.json');nr=D/(name+'-source-faithful-v2-review-draft.json')
 for path,obj in [(np,p),(nr,r)]:
  with path.open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
 receipt.append(dict(old_package=str(pp.name),old_package_sha256=sha(pp),old_review=str(rp.name),old_review_sha256=sha(rp),new_package=str(np.name),new_package_sha256=sha(np),new_review=str(nr.name),new_review_sha256=sha(nr),added_review_subject=['practice_event_evidence',subject],old_reviews_preserved=True))
with (D/'mandate-source-faithful-v2-receipt.json').open('x') as f:json.dump(dict(failure='62425222: Kaynak inceleme hedef kapsamı eksik',added_target=subject,candidates=receipt),f,ensure_ascii=False,indent=2);f.write('\n')
print('PACKAGE_TARGET_COVERAGE_PASS',len(receipt))
