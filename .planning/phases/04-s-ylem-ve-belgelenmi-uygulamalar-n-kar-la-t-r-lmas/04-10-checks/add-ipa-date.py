import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text())
package=read(D/'congress-followup-v2-draft.json'); review=read(D/'congress-followup-v2-review-draft.json')
package['entries'].extend(read(D/'ipa-event-date-source-draft.json')['entries'])
records=package['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
scope=next(x['id'] for x in records['practice_scope_v2'] if x['research_kind']=='event' and x['topic_id']=='genel-kongre-gorev')
eid='0410-2020-ninth-event';pid='0410-ipa-2020-congress-date-p';version='0410-ipa-2020-congress-date-v1'
url='https://ipa.istanbul/uploads/guvencesizlik-yeni-esitsizlikler-ve-cozum-yollari-konferansi-ozet-kitabi-95811-c45b3b4c.pdf'
records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point='İPA konferans kitabındaki Ercüment Akdeniz biyografisi 9. Genel Kongrenin 22 Kasım 2020 tarihinde yapıldığını bildirir.',stage='action',concrete_basis='Biyografide tarih ve genel başkan seçimi aynı cümlede yer alır.',limitation='Kitabın kesin yayın günü ve seçim tutanağı görülmedi.',epistemic_type='claim'))
records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='independent_report'))
records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps(['Ercüment Akdeniz biyografisi'],ensure_ascii=False),inspected_at=now))
aid='0410-ipa-ninth-date-reading';records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason='9. kongre tarihi ve genel başkan biyografisi',state='examined',attempt_ids=json.dumps([aid])))
records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='İPA kitabında biyografi ve kongre günü okundu; diğer kapsam açık.',source_version_id=version))
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');data=copy.deepcopy(base)
for e in package['entries']:
    rows=data.setdefault(e['kind'],[])
    if e['values'] not in rows:rows.append(e['values'])
for k,rs in records.items():
    rows=data.setdefault(k,[]);rows.extend(r for r in rs if r not in rows)
rules.validate_practices(data)
targets=rules.practice_review_targets(data,records);passages={p['id']:p for p in data['passage']}; old={(r['subject_kind'],r['subject_id']):r for r in review['practice_source_review']}; reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if 'emep' not in parties:continue
    key=(kind,identity)
    if key in old:
        existing=copy.deepcopy(old[key])
        if set(json.loads(existing['passage_ids'])) != set(pids):
            inspected=[passages[x] for x in sorted(pids)]
            existing.update(source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),reason=existing['reason']+' İPA biyografisindeki 22 Kasım tarihi ayrıca okundu.')
        reviews.append(existing);continue
    inspected=[passages[x] for x in sorted(pids)]
    assert pid in pids
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='İPA konferans kitabı Ercüment Akdeniz biyografisinde EMEP 9. Genel Kongresinin 22 Kasım 2020 günü gerçekleştiğini ve genel başkan seçimini belirtir.',limitations='Kesin yayın günü ve resmî seçim tutanağı görülmedi.',result='reviewed',reason='Biyografi sayfasında tarih, görev ve kongre bağlamı incelendi.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep')
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('congress-followup-v3-draft.json',package),('congress-followup-v3-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(reviews))
