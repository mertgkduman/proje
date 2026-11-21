"""Connect the program to the actual TBMM proposal, without claiming adoption."""
import json
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg=json.loads((p/'package-mugla-draft-v4.json').read_text()); rec=pkg['practice_records']; entries=pkg['entries']
sources=json.loads((p/'tbmm-source-records-draft.json').read_text())['entries']
ids=('0404-tbmm-asgari-ucret','0404-tbmm-gelen-kagit')
entries += [e for e in sources if any(e['values'].get(k,'').startswith(i) for k in ('id','version_id','document_id') for i in ids)]
target='0303-epm-program-asgari-ucret-summary'; quote='0303-epm-program-asgari-ucret-quote'; program='0303-epm-program-asgari-ucret-p1'; proposal='0404-tbmm-asgari-ucret-p'; group='0404-tbmm-gelen-kagit-p'; fid='0404-asgari-iliski'; now='2026-11-21T19:32:00+00:00'
for x in (target,quote): entries.append(dict(kind='verification',values=dict(finding_id=x,passage_id=program,checked_at=now,result='confirmed',reason='Kurucu programın asgari ücret hükmü özgün belgeyle karşılaştırıldı.')))
entries.append(dict(kind='finding',values=dict(id=fid,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=fid,text='Program asgari ücretin insanca yaşamı sağlayacak düzeyde belirlenmesini hedefler. Genel başkan ve grup başkanvekilleri, net 45.800 lira öneren 2/3790 sayılı kanun teklifini sundu; teklifin sunulması önerinin yasalaştığını veya ücretin uygulandığını göstermez.',provenance='summary',epistemic_type='claim')))
for ref in (program,proposal,group):
 entries.append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=ref,role='support')))
 entries.append(dict(kind='verification',values=dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Program metni, TBMM teklif özeti ve gelen kâğıtlardaki imza sahipleri ayrı okundu; yasalaşma veya uygulama ileri sürülmedi.')))
entries.append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Kurucu program ve TBMM 2/3790 teklif kayıtları incelendi; teklif ile uygulama ayrıldı.')))
eid='0404-asgari-ucret-teklif'; rec['practice_event'].append(dict(id=eid,common_event_key='tbmm-2-3790',event_at='2026-08-03',date_precision='day',date_unknown_reason=None,scope_context='TBMM Başkanlığına 2/3790 kanun teklifinin gelişi',title='Asgari ücret kanun teklifi',occurrence_basis='TBMM gelen kâğıtları 2/3790 teklifini ve 3 Ağustos 2026 geliş tarihini kaydediyor.'))
for passage,point in [(proposal,'Aylık net 45.800 lira önerisi'),(group,'Genel başkan ve grup başkanvekillerinin teklif sahipliği')]:
 rec['practice_event_evidence'].append(dict(event_id=eid,passage_id=passage,supported_point=point,stage='initiative',concrete_basis='TBMM kaydı öneri ve teklif sahipleri hakkında bilgi veriyor.',limitation='Teklifin yasalaşması veya ücretin fiilen uygulanması bu kayıttan çıkarılamaz.',epistemic_type='claim'))
 rec['practice_evidence_assessment'].append(dict(event_id=eid,passage_id=passage,stage='initiative',basis_kind='document'))
sid='0404-asgari-program-statement'; rec['practice_statement'].append(dict(id=sid,party_id='yeni-parti',topic_id='asgari-ucret',taxonomy_version=4,summary_finding_id=target,quote_finding_id=quote,statement_at='2026-07-24',date_precision='day',version_id='epm-program-v1',period_basis='24 Temmuz 2026 kurucu programı.',uncertainty_reason='Program, insanca yaşam düzeyinin hesap yöntemini belirtmiyor.',comparison_row_id='04-03-v3-0303-epm-program-asgari-ucret-row'))
scope='practice-6587ea202bf33b5fa6a935c25ab08afad38c6bc8f55b7caac4e33afa11ad140e';rec['practice_scope_v2'].append(dict(id=scope,party_id='yeni-parti',topic_id='asgari-ucret',taxonomy_version=4,period_start='2026-07-24',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='2/3790 teklifinin evreleri ve başka somut uygulamalar araştırılıyor; kapsam açık.'))
rec['practice_relation'].append(dict(id='0404-asgari-iliski-id',statement_id=sid,event_id=eid,party_id='yeni-parti',topic_id='asgari-ucret',scope_id=scope,comparability_reason='Program ve kanun teklifi asgari ücretin düzeyi ile ilgilidir.',target_finding_id=target,result_finding_id=None,explanation_finding_id=fid,temporal_context='Program 24 Temmuz; teklif 3 Ağustos 2026 tarihinde kayda girmiştir.',authority_context='TBMM gelen kâğıtlarında genel başkan ve grup başkanvekilleri teklif sahipleri olarak gösterilir.',uncertainty_reason='Teklifin sunulması, yasanın kabul edildiğini veya önerilen ücretin uygulandığını göstermez; kesim tarihindeki aşama ve Günaydın sitesindeki kopyada farklı yazılan parti unvanları ayrıca araştırılıyor.'))
(p/'package-program-draft-v2.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
print('PROGRAM_DRAFT initiative only, scope open')
