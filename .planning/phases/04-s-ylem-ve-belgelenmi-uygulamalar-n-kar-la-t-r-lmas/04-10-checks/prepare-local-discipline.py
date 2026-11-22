import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;read=lambda p:json.loads(Path(p).read_text())
package=read(D/'congress-followup-v3-draft.json');previous=read(D/'congress-followup-v3-review-draft.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');inventory=read('data/practices/04-inventory.json')
entries=package['entries'];records=package['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for name in ('bolu-congress-source-draft.json','corum-congress-source-draft.json'):
    entries.extend(read(D/name)['entries'])
entries.append(dict(kind='passage',values=dict(id='0410-emep-2020-bolu-discipline-full-p',version_id='0410-emep-2020-bolu-v1',exact='Disiplin Kurulu ise </strong>Süreyya Demir, Burakcan Akpınar, Hasan Metin Taşkıran olarak belirlendi.',prefix=None,suffix=None,article=None,section='İl disiplin kurulu belirlenmesi',pdf_page_index=None,printed_page=None)))
topic='il-disiplin-kurulu';scopes={c['research_kind']:c for c in inventory['cells'] if c['party_id']=='emep' and c['topic_id']==topic}
assert set(scopes)=={'event','statement'}
for c in scopes.values():
    row={k:c[k] for k in ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')};row.update(id=c['cell_id'],boundary_reason='Bolu ve Çorum il kongrelerinde kurulların belirlendiğine dair dar inceleme; diğer il ve dönemler açıktır.');records['practice_scope_v2'].append(row)
def add(table,**values):entries.append(dict(kind=table,values=values))
def finding(fid,text,pids,provenance='summary',pair=None):
    add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=pair or fid,text=text,provenance=provenance,epistemic_type='claim')
    add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='İl düzeyi ve haberin doğrudan belirttiği sınırlar incelendi.')
    for p in pids:
        add('finding_evidence',finding_id=fid,passage_id=p,role='support');add('verification',finding_id=fid,passage_id=p,checked_at=now,result='confirmed',reason='İl kongresi, organ ve kaynak pasajı eşleştirildi.')
charter='0309-emep-html-019-0-passage';statement='0410-il-disiplin-statement';summary='0410-il-disiplin-finding';quote='0410-il-disiplin-quote'
finding(summary,'Parti tüzüğü metni il disiplin kurulunun il kongresince gizli oyla seçilen üç üyeden oluşmasını öngörür.',[charter])
finding(quote,'İl disiplin kurulu, il kongresi tarafından gizli oyla seçilen 3 üyeden oluşur.',[charter],provenance='quote',pair=summary)
records['practice_statement'].append(dict(id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at=None,date_precision='unknown',version_id='0208-emep-program-charter-v1',period_basis='Parti metni 2019 yayın ve 2020 site güncellemesi taşır; tüzük kabul günü bilinmiyor.',uncertainty_reason='İlgili olaylarda yürürlükteki ara tüzük değişiklikleri ve seçim tutanakları açık.',comparison_row_id='04-03-v3-03-v2-emep-il-disiplin-kurulu'))
cases=[dict(key='bolu',eid='0410-bolu-il-kongre-event',rid='0410-bolu-disiplin-relation',version='0410-emep-2020-bolu-v1',pid='0410-emep-2020-bolu-discipline-full-p',url='https://www.koroglugazetesi.com/emek-partisi-bolu-il-kongresi-yapildi',context='EMEP Bolu il kongresi',date_reason='Köroğlu 24 Aralık 2020 tarihinde yayımladı; kongrenin kesin günü haberde belirtilmedi.',claim='Köroğlu, Bolu il kongresinde Süreyya Demir, Burakcan Akpınar ve Hasan Metin Taşkıran’ın disiplin kurulunda belirlendiğini aktardı.',limit='Haber oylama biçimi ve kongrenin tam gününü belirtmez; seçim tutanağı görülmedi.'),
 dict(key='corum',eid='0410-corum-il-kongre-event',rid='0410-corum-disiplin-relation',version='0410-emep-2023-corum-v1',pid='0410-emep-2023-corum-discipline-p',url='https://www.evrensel.net/haber/504486/emep-corum-il-orgutu-kongre-surecini-tamamladi-bu-baski-rejimini-birlikte-puskurtecegiz',context='EMEP Çorum 10. Olağan İl Kongresi',date_reason='Evrensel haberi 27 Kasım 2023 tarihlidir; kongrenin kesin günü haberde belirtilmedi.',claim='Evrensel, Çorum il kongresinde disiplin kurulu üyelerinin de belirlendiğini aktardı.',limit='Haber disiplin kurulu üyelerinin sayısını ve oylama biçimini belirtmez; sekiz sayısı genel merkez delegelerine aittir.')]
for c in cases:
    result='0410-'+c['key']+'-disiplin-result';relfind='0410-'+c['key']+'-disiplin-finding';scope=scopes['event']['cell_id']
    finding(result,c['claim'],[c['pid']]);finding(relfind,'Tüzük metni il disiplin kurulunun il kongresinde seçilmesini düzenler. '+c['claim'],[charter,c['pid']])
    records['practice_event'].append(dict(id=c['eid'],common_event_key='emep-'+c['key']+'-il-kongre',event_at=None,date_precision='unknown',date_unknown_reason=c['date_reason'],scope_context=c['context'],title='İl kongresinde disiplin kurulu',occurrence_basis=c['claim']))
    for stage in ('action','result'):
        records['practice_event_evidence'].append(dict(event_id=c['eid'],passage_id=c['pid'],supported_point=c['claim'],stage=stage,concrete_basis='Yerel kongre ve kurulun belirlendiği ilgili haber bölümünde bildirilir.',limitation=c['limit'],epistemic_type='claim'))
        records['practice_evidence_assessment'].append(dict(event_id=c['eid'],passage_id=c['pid'],stage=stage,basis_kind='independent_report'))
    records['practice_relation'].append(dict(id=c['rid'],statement_id=statement,event_id=c['eid'],party_id='emep',topic_id=topic,scope_id=scope,comparability_reason='Tüzükte il disiplin kurulu oluşumu ve haberlerde il kongresindeki kurul belirlenmesi inceleniyor.',target_finding_id=summary,result_finding_id=result,explanation_finding_id=relfind,temporal_context='Tüzükteki tarih belirsiz; kongre günleri haber tarihinden çıkarılmadı.',authority_context='Tüzük il kongresini kurul seçimiyle görevlendirir.',uncertainty_reason=c['limit']+' Dönemsel tüzük ara değişiklikleri araştırılmaktadır.'))
    records['practice_candidate'].append(dict(id='0410-'+c['key']+'-disiplin-candidate',scope_id=scope,event_id=c['eid'],relation_id=c['rid'],state='eligible',reason='İl kongresinde disiplin kuruluna ilişkin haber ilgili hükümle bağlantılıdır.',passage_ids=json.dumps([c['pid']])))
    aid='0410-'+c['key']+'-disiplin-reading';records['practice_scope_source'].append(dict(scope_id=scope,version_id=c['version'],inspected_sections=json.dumps([c['context']],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=c['url'],relevance_reason=c['context'],state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=c['url'],url=c['url'],result='examined',reason=c['context']+' kaynağı okundu; diğer il ve dönemler açık.',source_version_id=c['version']))
c=scopes['statement'];version='0208-emep-program-charter-v1';url='https://www.emep.org/emek-partisi-program-ve-tuzugu';aid='0410-il-disiplin-charter-reading';records['practice_scope_source'].append(dict(scope_id=c['cell_id'],version_id=version,inspected_sections=json.dumps(['Tüzük Madde 48'],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=c['cell_id'],url=url,relevance_reason='İl disiplin kurulunun kuruluşu',state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=c['cell_id'],attempted_at=now,query=url,url=url,result='examined',reason='Tüzük Madde 48 okundu; kaynak dönemi ve kapsam açıktır.',source_version_id=version))
data=copy.deepcopy(base)
for e in entries:
    rows=data.setdefault(e['kind'],[])
    if e['values'] not in rows:rows.append(e['values'])
for k,rs in records.items():
    rows=data.setdefault(k,[]);rows.extend(r for r in rs if r not in rows)
rules.validate_practices(data);targets=rules.practice_review_targets(data,records);passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
    if 'emep' not in parties:continue
    if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
    inspected=[passages[x] for x in sorted(pids)]
    case=next((c for c in cases if c['eid'] in identity or c['rid'] in identity),None)
    claim=(case['claim'] if case else 'Tüzük Madde 48 il disiplin kurulunun il kongresince gizli oyla seçilen üç üyeden oluşmasını öngörür.')
    if case and kind in ('practice_relation','practice_relation.target_finding_id'):claim='Tüzükte il disiplin kurulu seçimi ile haberde il kurulunun belirlenmesi aynı düzeyde ilişkilidir; oylama usulü haberden çıkarılmadı.'
    reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim=claim,limitations=(case['limit'] if case else 'Tüzük kabul ve geçerlilik dönemi tam doğrulanmadı.'),result='reviewed',reason=kind+' / '+identity+' için kaynakta il, kurul, üye ve haberin tarih sınırı okundu.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep');refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('local-discipline-v2-draft.json',package),('local-discipline-v2-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
    with (D/name).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
