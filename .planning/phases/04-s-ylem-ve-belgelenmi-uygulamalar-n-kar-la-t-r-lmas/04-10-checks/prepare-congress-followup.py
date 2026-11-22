import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent
read=lambda p:json.loads(Path(p).read_text())
package=read('data/practices/04-emep.json'); old_review=read('data/practices/04-emep-review.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json')
records=package['practice_records'];entries=package['entries'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for name in ('ninth-congress-source-draft.json','extraordinary-congress-source-draft.json'):
    entries.extend(read(D/name)['entries'])
for pid,version,exact,section in [
    ('0410-emep-2020-indy-full-p','0410-emep-2020-indy-v1','Emek Partisinin 9. olağan kongresinde genel başkanlık görevine Ercüment Akdeniz seçildi.','9. kongre genel başkan seçimi'),
    ('0410-emep-2023-extra-full-p','0410-emep-2023-olaganustu-v1','Seçim gündemiyle toplanan kongrede Selma Gürkan parti genel başkanlığına seçildi.','Olağanüstü kongre genel başkan seçimi'),
]:
    entries.append(dict(kind='passage',values=dict(id=pid,version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)))
scope=next(x['id'] for x in records['practice_scope_v2'] if x['research_kind']=='event' and x['topic_id']=='genel-kongre-gorev')
charter='0208-emep-charter-governance';statement='0410-kongre-statement';target='0410-kongre-statement-finding'
def add(table,**v):entries.append(dict(kind=table,values=v))
def finding(fid,text,pids):
    add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=fid,text=text,provenance='summary',epistemic_type='claim')
    add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Tarih, aktör ve özgün kaynak bağlamı okundu.')
    for pid in pids:
        add('finding_evidence',finding_id=fid,passage_id=pid,role='support')
        add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Bulgu ve kaynak pasajı anlam bakımından eşleştirildi.')
cases=[dict(key='2020-ninth',eid='0410-2020-ninth-event',rid='0410-2020-ninth-relation',candidate='0410-2020-ninth-candidate',event_at='2020-11-22',precision='day',unknown=None,title='9. Genel Kongrede başkan seçimi',context='EMEP 9. Olağan Genel Kongresi',common='emep-2020-11-22-9-kongre-genel-baskan',pid='0410-emep-2020-indy-full-p',version='0410-emep-2020-indy-v1',url='https://www.indyturk.com/node/275861/haber/emep%E2%80%99-yeni-genel-ba%C5%9Fkan%C4%B1-erc%C3%BCment-akdeniz-oldu',claim='Independent Türkçe, 9. kongrede Ercüment Akdeniz’in genel başkan seçildiğini bildirir.',limitation='Haberin bazı kısımları Evrensel kaynaklıdır; seçim tutanağı görülmedi.'),
 dict(key='2023-extra',eid='0410-2023-extra-event',rid='0410-2023-extra-relation',candidate='0410-2023-extra-candidate',event_at=None,precision='unknown',unknown='Olağanüstü kongrenin tam günü haber metninde belirtilmiyor; 16 Mayıs istifasından sonra, 25 Haziran 2023 tarihli yayından önce gerçekleşti.',title='Olağanüstü kongrede başkan seçimi',context='EMEP olağanüstü genel kongresi',common='emep-2023-olaganustu-kongre-selma-gurkan',pid='0410-emep-2023-extra-full-p',version='0410-emep-2023-olaganustu-v1',url='https://www.evrensel.net/haber/493279/emep-olaganustu-genel-kongresini-topladi',claim='Evrensel, olağanüstü kongrede Selma Gürkan’ın genel başkan seçildiğini bildirir.',limitation='Kongrenin tam günü ve seçim tutanağı görülmedi; 17 Mayıs GYK görevlendirmesi ayrı işlemdir.')]
for c in cases:
    result='0410-'+c['key']+'-result';relfind='0410-'+c['key']+'-relation-finding'
    finding(result,c['claim'],[c['pid']])
    finding(relfind,'Parti tüzüğü metni genel başkan seçimini genel kongrenin görevleri arasında sayar. '+c['claim'],[charter,c['pid']])
    records['practice_event'].append(dict(id=c['eid'],common_event_key=c['common'],event_at=c['event_at'],date_precision=c['precision'],date_unknown_reason=c['unknown'],scope_context=c['context'],title=c['title'],occurrence_basis=c['claim']))
    for stage in ('action','result'):
        records['practice_event_evidence'].append(dict(event_id=c['eid'],passage_id=c['pid'],supported_point=c['claim'],stage=stage,concrete_basis='İsim, seçilen görev ve kongre haberin ilgili bölümünde birlikte yer alır.',limitation=c['limitation'],epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=c['eid'],passage_id=c['pid'],stage=stage,basis_kind='independent_report'))
    records['practice_relation'].append(dict(id=c['rid'],statement_id=statement,event_id=c['eid'],party_id='emep',topic_id='genel-kongre-gorev',scope_id=scope,comparability_reason='Genel kongrenin başkan seçimi yetkisi ile kongrede bildirilen başkan seçimi aynı konudadır.',target_finding_id=target,result_finding_id=result,explanation_finding_id=relfind,temporal_context='2019/2020 tarihli tüzük yayını ve kongre olayı farklı tarihlerdir.',authority_context='Tüzük metni genel başkan seçimini genel kongreye verir.',uncertainty_reason=c['limitation']+' Ara tüzük değişiklikleri araştırılmaktadır.'))
    records['practice_candidate'].append(dict(id=c['candidate'],scope_id=scope,event_id=c['eid'],relation_id=c['rid'],state='eligible',reason='Genel kongredeki genel başkan seçimi ilgili tüzük hükmü kapsamındadır.',passage_ids=json.dumps([c['pid']])))
    aid='0410-'+c['key']+'-reading'
    records['practice_scope_source'].append(dict(scope_id=scope,version_id=c['version'],inspected_sections=json.dumps([c['context']],ensure_ascii=False),inspected_at=now))
    records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=c['url'],relevance_reason=c['context'],state='examined',attempt_ids=json.dumps([aid])))
    records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=c['url'],url=c['url'],result='examined',reason=c['context']+' haber metni okundu; diğer kaynaklar ve kapsam açıktır.',source_version_id=c['version']))
data=copy.deepcopy(base)
for e in entries:
    target_rows=data.setdefault(e['kind'],[])
    if e['values'] not in target_rows:target_rows.append(e['values'])
for k,rows in records.items():
    target_rows=data.setdefault(k,[])
    target_rows.extend(x for x in rows if x not in target_rows)
rules.validate_practices(data)
targets=rules.practice_review_targets(data,records);ps={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in old_review['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if 'emep' not in parties:continue
    key=(kind,identity)
    if key in old:reviews.append(old[key]);continue
    selected=[ps[x] for x in sorted(pids)]
    case=next(c for c in cases if c['eid'] in identity or c['rid'] in identity)
    claim=case['claim']
    if kind in ('practice_relation','practice_relation.target_finding_id'):
        claim='Parti tüzüğü genel başkan seçimini genel kongrenin görevleri arasında sayar; olay bu konuya ilişkindir.'
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in selected})),passage_ids=json.dumps([p['id'] for p in selected]),inspected_sections=json.dumps(sorted({p['section'] for p in selected}),ensure_ascii=False),supported_claim=claim,limitations=case['limitation'],result='reviewed',reason=identity+' için kaynak metni, olay ve yetki ayrımı incelendi.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep')
refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('congress-followup-v2-draft.json',package),('congress-followup-v2-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
