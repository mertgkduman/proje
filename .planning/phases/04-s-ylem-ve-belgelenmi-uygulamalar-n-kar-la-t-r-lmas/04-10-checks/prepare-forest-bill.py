import copy,datetime,json,sys
from pathlib import Path
sys.path.insert(0,'src')
import uygulamalar as rules
D=Path(__file__).parent;read=lambda p:json.loads(Path(p).read_text())
package=read(D/'may-institutions-draft.json');previous=read(D/'may-institutions-review-draft.json')
base=read('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json');inventory=read('data/practices/04-inventory.json')
entries=package['entries'];records=package['practice_records'];now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
for name in ('forest-bill-source-draft.json','forest-bill-additional-passages.json'):entries.extend(read(D/name)['entries'])
topic='orman-su-yonetimi';scopes={c['research_kind']:c for c in inventory['cells'] if c['party_id']=='emep' and c['topic_id']==topic};assert set(scopes)=={'event','statement'}
for c in scopes.values():
 row={k:c[k] for k in ('party_id','topic_id','taxonomy_version','period_start','cutoff_at','research_kind')};row.update(id=c['cell_id'],boundary_reason='2/3804 teklifi ve programın orman koruma hükmü incelendi; diğer dönem ve uçlar açıktır.');records['practice_scope_v2'].append(row)
def add(table,**values):entries.append(dict(kind=table,values=values))
def finding(fid,text,pids,provenance='summary',pair=None):
 add('finding',id=fid,party_id='emep',heading='Belgelenmiş uygulamalar',pair_id=pair or fid,text=text,provenance=provenance,epistemic_type='claim')
 add('review',id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Program, teklif ve kaynak niteliği ayrı okundu.')
 for pid in pids:
  add('finding_evidence',finding_id=fid,passage_id=pid,role='support');add('verification',finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Özgün program veya resmi teklif pasajı doğrulandı.')
charter='0309-emep-program-041-1-passage';filing='0410-emep-forest-23804-pdf-filing-p';aim='0410-emep-forest-23804-pdf-aim-p';karaca='0410-emep-forest-23804-register-karaca-p';bayhan='0410-emep-forest-23804-register-bayhan-p';filed='0410-emep-forest-23804-register-filed-p';sf='0410-forest-statement-finding';quote='0410-forest-statement-quote';ef='0410-forest-explanation';statement='0410-forest-statement';eid='0410-forest-23804-event';rid='0410-forest-23804-relation'
finding(sf,'Parti programı toprağın, ormanların, suların, bitkilerin ve hayvanların korunmasını savunur.',[charter]);finding(quote,'Toprağın, ormanların, suların,\nbitki ve hayvanların korunması.',[charter],provenance='quote',pair=sf)
finding(ef,'Program ormanların korunmasını savunur. Sevda Karaca Demir ve İskender Bayhan 11 Ağustos 2026’da orman mevzuatında değişiklik teklifi sundu; teklifin gerekçesi belirli ek maddelerin kaldırılmasını önerir.',[charter,filing,aim,karaca,bayhan,filed])
records['practice_statement'].append(dict(id=statement,party_id='emep',topic_id=topic,taxonomy_version=4,summary_finding_id=sf,quote_finding_id=quote,statement_at=None,date_precision='unknown',version_id='0208-emep-program-charter-v1',period_basis='Parti programı sayfası 2019 yayın ve 2020 site güncellemesi taşır; kabul günü bilinmiyor.',uncertainty_reason='2023 arşiv ve seçili metin boşluk normalleştirmesi sonrası eşittir; ara değişiklik ve 2026 hukuki yürürlük ayrıca doğrulanmadı.',comparison_row_id='04-03-v3-0309-emep-program-041-1-row'))
records['practice_event'].append(dict(id=eid,common_event_key='tbmm-28-5-2-3804-orman-kanunu',event_at='2026-08-11',date_precision='day',date_unknown_reason=None,scope_context='TBMM’ye sunulan 2/3804 orman kanunu değişiklik teklifi',title='Orman Kanunu değişiklik teklifi',occurrence_basis='İmzalı teklif ve TBMM teklif kaydı başkanlığa geliş gününü gösterir.'))
for pid,point in [(filing,'Orman Kanunu değişiklik teklifi TBMM Başkanlığına sunuldu.'),(filed,'TBMM kaydı başkanlığa geliş gününü 11 Ağustos 2026 olarak gösterir.')]:
 records['practice_event_evidence'].append(dict(event_id=eid,passage_id=pid,supported_point=point,stage='action',concrete_basis='Resmî teklif üst yazısı veya kayıt ekranındaki tarih.',limitation='Teklifin sunulması yasalaşma değildir; 1 Ekim komisyon sevki ayrı süreçtir.',epistemic_type='claim'))
 records['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=pid,stage='action',basis_kind='document'))
records['practice_relation'].append(dict(id=rid,statement_id=statement,event_id=eid,party_id='emep',topic_id=topic,scope_id=scopes['event']['cell_id'],comparability_reason='Programdaki orman koruma hedefi ve orman mevzuatını değiştirme teklifi aynı doğal varlık konusu bakımından ilişkilidir.',target_finding_id=sf,result_finding_id=None,explanation_finding_id=ef,temporal_context='Programın 2023 arşiv görüntüsü ve 2026 teklif ayrı tarihlerdedir.',authority_context='Program parti beyanıdır; teklif iki EMEP milletvekilinin TBMM girişimidir.',uncertainty_reason='Teklifin kesinleşmiş sonucu gösterilmedi; mevzuat değişikliği veya ekolojik etki çıkarılmaz.'))
records['practice_candidate'].append(dict(id='0410-forest-23804-candidate',scope_id=scopes['event']['cell_id'],event_id=eid,relation_id=rid,state='eligible',reason='Orman mevzuatı teklifi ilgili program ifadesiyle bağlantılıdır.',passage_ids=json.dumps([filing,filed])))
for typ,version,url,section in [('statement','0208-emep-program-charter-v1','https://www.emep.org/emek-partisi-program-ve-tuzugu','G/C/5-a ormanların korunması'),('event','0410-emep-forest-23804-pdf-v1','https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y4/T2/WebOnergeMetni/863fb3e5-63a0-432f-86f3-1f3ea3818a59.pdf','2/3804 teklif üst yazısı ve gerekçesi')]:
 scope=scopes[typ]['cell_id'];aid='0410-forest-23804-'+typ+'-reading';records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps([section],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason=section,state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason=section+' okundu; diğer orman olayları ve sonuç açık.',source_version_id=version))
scope=scopes['event']['cell_id'];version='0410-emep-forest-23804-register-v1';url='https://tbmm.gov.tr/Yasama/KanunTeklifi/a234c8c0-bc04-4dc6-8901-019ff10d27e2';aid='0410-forest-23804-register-reading';records['practice_scope_source'].append(dict(scope_id=scope,version_id=version,inspected_sections=json.dumps(['Başkanlığa geliş ve imza sahipleri'],ensure_ascii=False),inspected_at=now));records['practice_lead'].append(dict(id='lead-'+aid,scope_id=scope,url=url,relevance_reason='Teklifin TBMM kayıt tarihi ve imza sahipleri',state='examined',attempt_ids=json.dumps([aid])));records['practice_attempt_v2'].append(dict(id=aid,scope_id=scope,attempted_at=now,query=url,url=url,result='examined',reason='Kayıt tarihi ve iki imzacı okundu; nihai sonuç açık.',source_version_id=version))
data=copy.deepcopy(base)
for entry in entries:
 rows=data.setdefault(entry['kind'],[])
 if entry['values'] not in rows:rows.append(entry['values'])
for table,rows in records.items():data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
rules.validate_practices(data);targets=rules.practice_review_targets(data,records);passages={p['id']:p for p in data['passage']};old={(r['subject_kind'],r['subject_id']):r for r in previous['practice_source_review']};reviews=[]
for (kind,identity),(pids,parties) in sorted(targets.items()):
 if 'emep' not in parties:continue
 if (kind,identity) in old:reviews.append(old[(kind,identity)]);continue
 inspected=[passages[x] for x in sorted(pids)]
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(sorted({p['version_id'] for p in inspected})),passage_ids=json.dumps([p['id'] for p in inspected]),inspected_sections=json.dumps(sorted({p['section'] for p in inspected}),ensure_ascii=False),supported_claim='Parti programında orman koruma; iki EMEP milletvekilinin 11 Ağustos 2026 tarihli orman mevzuatı değişiklik teklifi ve gerekçesi.',limitations='Teklif kabulü veya çevresel sonuç kanıtlanmadı; program ara dönem yürürlüğü ayrıca araştırılacak.',result='reviewed',reason=kind+' / '+identity+' için özgün program, imzalı teklif ve TBMM kayıt pasajları incelendi.'))
rules.validate_practice_source_review(data,reviews,require_coverage=False,party_id='emep');refs=[{k:r[k] for k in ('subject_kind','subject_id')} for r in reviews];package['source_review_refs']=refs
for name,obj in [('forest-bill-union-draft.json',package),('forest-bill-union-review-draft.json',dict(practice_source_review=reviews,source_review_refs=refs))]:
 with (D/name).open('x') as f:f.write(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('FOREST_SEMANTIC_PASS',len(reviews),'EVENTS',len(records['practice_event']))
