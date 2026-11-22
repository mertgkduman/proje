import copy, hashlib, json, sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
import uygulamalar as rules
D=Path(__file__).parent
base=json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text())
raw=Path('data/practices/sources/emep/objects/4652802c6a033afbb51a35e4048f24d11f81cd482fbe778e2820123985e59dab/original.html.bin').read_bytes()
t=html_source_text(raw)
name='<td>BAYHAN</td>'
assert t.count(name)==1 and name.encode() in raw
i=t.index(name); j=t.index('<td style="text-align:left">Emek Partisi</td>',i); k=t.index('</td>',t.index('19:33:43',j))+5
vote=t[j:k]
assert vote.encode() in raw and '\ufffd' not in vote and 'RET' in vote
oldid='0410-emep-tezkere-3761-ballot-emep-p';newid='0410-emep-tezkere-3761-ballot-vote-p'
specs=[('mandate-3761-union-draft.json','mandate-3761-union-review-draft.json','mandate-3761-source-faithful'),('gebze-congress-union-draft.json','gebze-congress-union-review-draft.json','gebze-congress-source-faithful'),('izmit-congress-union-draft.json','izmit-congress-union-review-draft.json','izmit-congress-source-faithful'),('kocaeli-congress-union-draft.json','kocaeli-congress-union-review-draft.json','kocaeli-congress-source-faithful'),('luleburgaz-congress-branch-draft.json','luleburgaz-congress-branch-review-draft.json','luleburgaz-congress-source-faithful')]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=[]
for pn,rn,out in specs:
 p=json.loads((D/pn).read_text());oldreview=json.loads((D/rn).read_text());entries=p['entries'];records=p['practice_records'];changed=[]
 passage=next(e['values'] for e in entries if e['kind']=='passage' and e['values']['id']==oldid)
 passage['exact']=name;passage['section']='Açık oy cetvelinde Bayhan soyadı'
 second=dict(passage,id=newid,exact=vote,section='Aynı Bayhan satırında parti, ret oyu ve zaman')
 entries.append(dict(kind='passage',values=second))
 for e in list(entries):
  if e['kind'] in ('finding_evidence','verification') and e['values'].get('passage_id')==oldid:
   v=copy.deepcopy(e['values']);v['passage_id']=newid;entries.append(dict(kind=e['kind'],values=v))
  if e['kind']=='source_attribution' and e['values'].get('version_id')=='0410-emep-gebze-2026-party-v1':
   assert e['values']['kind']=='party';e['values']['kind']='party_publication';changed.append('Gebze parti atfı: party_publication')
 for table in ('practice_event_evidence','practice_evidence_assessment'):
  old=next(x for x in records[table] if x['passage_id']==oldid);v=copy.deepcopy(old);v['passage_id']=newid
  if table=='practice_event_evidence':v['supported_point']='Aynı açık oy cetveli satırı Emek Partisi, RET ve 19:33:43 kaydını gösterir.';v['limitation']='İsim ve oy alanları, aradaki CP1254 karakter kaybını önlemek için aynı satırdan iki özgün ASCII pasajla birlikte okunur.'
  records[table].append(v)
 for x in records['practice_candidate']:
  ids=json.loads(x['passage_ids'])
  if oldid in ids:ids.append(newid);x['passage_ids']=json.dumps(ids)
 data=copy.deepcopy(base)
 for entry in entries:
  if entry['values'] not in data.setdefault(entry['kind'],[]):data[entry['kind']].append(entry['values'])
 for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
 rules.validate_practices(data)
 targets=rules.practice_review_targets(data,records);passages={x['id']:x for x in data['passage']};reviews=copy.deepcopy(oldreview['practice_source_review']);review_changed=[]
 for r in reviews:
  key=(r['subject_kind'],r['subject_id']);pids=targets[key][0]
  if newid in pids:
   before=set(json.loads(r['passage_ids']));assert oldid in before and before.issubset(pids)
   r['passage_ids']=json.dumps(sorted(pids));r['source_version_ids']=json.dumps(sorted({passages[x]['version_id'] for x in pids}));r['inspected_sections']=json.dumps(sorted({passages[x]['section'] for x in pids}),ensure_ascii=False)
   r['limitations']+=' Oy cetveli adı ve oy alanı aynı satırın iki özgün ASCII parçası olarak birlikte kontrol edildi.'
   review_changed.append(key)
 rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep')
 refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];p['source_review_refs']=refs
 for name_,obj in [(out+'-draft.json',p),(out+'-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
  with (D/name_).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
 receipt.append(dict(old_package=pn,old_package_sha256=sha(D/pn),old_review=rn,old_review_sha256=sha(D/rn),new_package=out+'-draft.json',new_package_sha256=sha(D/(out+'-draft.json')),new_review=out+'-review-draft.json',new_review_sha256=sha(D/(out+'-review-draft.json')),modified_review_subjects=review_changed,other_changes=changed,old_passage_ids_are_subset=True))
with (D/'mandate-source-faithful-receipt.json').open('x') as f:json.dump(dict(explanation='İki ASCII pasaj özgün baytta ve aynı HTML satırında birebir bulundu; yerel pasif kaynak görünümündeki tam satır insan tarafından da okundu. Bayhan adı ve RET/zaman birlikte değerlendirilir. Özgün bayt ve önceki başarısız paketler değişmedi.',candidates=receipt),f,ensure_ascii=False,indent=2);f.write('\n')
print('SOURCE_FAITHFUL_SEMANTIC_PASS',len(receipt))
