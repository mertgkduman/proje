import json
from datetime import datetime,timezone
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
all_entries=json.loads((p/'institution-sources-draft.json').read_text())['entries']; doc='0405-tip-pm-nisan'; vid=doc+'-v1'; ps=doc+'-thirtyfive-p'; proposal='0405-tip-282121-pdf-workhour-p'; summary='0405-tip-pm35-summary'; quote='0405-tip-pm35-quote'; explanation='0405-tip-pm35-iliski-bulgu'; st='0405-tip-pm35-statement'; rel='0405-tip-pm35-iliski'; event='0405-tip-282121-event'; now=datetime.now(timezone.utc).isoformat()
entries=[]
for item in all_entries:
 v=item['values']; kind=item['kind']
 if (kind=='document' and v['id']==doc) or (kind=='document_version' and v['id']==vid) or (kind in ('archive_view','source_attribution','passage') and v.get('version_id')==vid):
  item=json.loads(json.dumps(item)); v=item['values']
  if kind=='document':v['source_kind']='party'
  if kind=='document_version':v.update(document_date='2024-04-09',date_precision='day',date_unknown_reason=None,version_label='9 Nisan 2024 tarihli Parti Meclisi değerlendirmesi')
  if kind=='source_attribution':v.update(published_at='2024-04-09',date_precision='day',basis='Sayfanın görünür 9 Nisan 2024 tarihi ve article:published_time künyesi okundu.')
  entries.append(item)
def add(k,v):entries.append(dict(kind=k,values=v))
for fid,text,prov,refs in [(summary,'Parti Meclisi değerlendirmesi 1 Mayıs için haftalık çalışma süresinin 35 saate indirilmesini talep eder.','summary',[ps]),(quote,'Çalışma Süresi Haftalık 35 Saate Düşürülsün','quote',[ps]),(explanation,'9 Nisan Parti Meclisi açıklaması haftalık 35 saat talebini dile getirir; 24 Nisan milletvekili teklifi aynı süreyi kanun değişikliği olarak önerir. Teklif, hedefin gerçekleştiğini göstermez.','summary',[ps,proposal])]:
 add('finding',dict(id=fid,party_id='tip',heading='Belgelenmiş uygulamalar',pair_id=st,text=text,provenance=prov,epistemic_type='claim'))
 for ref in refs:
  add('finding_evidence',dict(finding_id=fid,passage_id=ref,role='quotation' if prov=='quote' else 'support'));add('verification',dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Tarihli Parti Meclisi metni ve teklif maddesi kaynak bağlamında okundu.'))
 add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Söylem ve teklif tarihleri, özne ve uygulama sınırı karşılaştırıldı.'))
records={'practice_statement':[dict(id=st,party_id='tip',topic_id='calisma-sureleri',taxonomy_version=4,summary_finding_id=summary,quote_finding_id=quote,statement_at='2024-04-09',date_precision='day',version_id=vid,period_basis='Parti sayfası yayın tarihi 9 Nisan; değerlendirme toplantısı 6–7 Nisan 2024.',uncertainty_reason=None,comparison_row_id='04-03-v3-0304-tip-program-emek-talepleri-row')], 'practice_relation':[dict(id=rel,statement_id=st,event_id=event,party_id='tip',topic_id='calisma-sureleri',scope_id=None,comparability_reason='Her ikisi genel haftalık 35 saat hedefine ilişkindir.',target_finding_id=summary,result_finding_id=None,explanation_finding_id=explanation,temporal_context='Parti açıklaması 9 Nisan, teklif 24 Nisan 2024.',authority_context='Parti Meclisi hedef belirtir, milletvekili teklif verir, yasa kabulü TBMM yetkisidir.',uncertainty_reason='Teklifin sonucu ve ülke genelindeki çalışma süresi ayrıca incelenmelidir.')]}
(p/'policy-35h-statement-delta.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,practice_records=records),ensure_ascii=False,indent=2)+'\n');print('DRAFT ONLY',len(entries))
