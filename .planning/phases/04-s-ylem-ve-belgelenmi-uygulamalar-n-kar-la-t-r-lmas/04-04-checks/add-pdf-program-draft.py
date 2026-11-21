"""Add the actual TBMM proposal first-page authority passage to v2."""
import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg=json.loads((p/'package-program-draft-v2.json').read_text()); pkg['entries']+=json.loads((p/'tbmm-pdf-records-draft.json').read_text())['entries']; ref='0404-tbmm-3790-pdf-p'; fid='0404-asgari-iliski'; event='0404-asgari-ucret-teklif'
pkg['entries'] += [dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=ref,role='support')),dict(kind='verification',values=dict(finding_id=fid,passage_id=ref,checked_at='2026-11-21T19:53:01+00:00',result='confirmed',reason='TBMM teklif PDF ilk sayfasındaki Özel ve Yeni Parti genel başkanı unvanı yerel sayfa metninde okundu; OCR hatası korunmuştur.'))]
pkg['practice_records']['practice_event_evidence'].append(dict(event_id=event,passage_id=ref,supported_point='Teklifin ilk sayfasında Özel için Yeni Parti genel başkanı unvanı',stage='initiative',concrete_basis='Özgün TBMM PDF ilk sayfası Özel imzası altında unvanı gösteriyor.',limitation='Yerel PDF metin çıkarımı seçim çevresini hatalı OCR ile gösterir; iddia edilen kanun kabulüne kanıt değildir.',epistemic_type='claim'))
pkg['practice_records']['practice_evidence_assessment'].append(dict(event_id=event,passage_id=ref,stage='initiative',basis_kind='document'))
(p/'package-program-draft-v3.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
r=json.loads((p/'program-review-draft-v2.json').read_text()); ver='0404-tbmm-3790-pdf-v1'
for x in r['practice_source_review']:
 if x['subject_id'] in (event,'0404-asgari-iliski-id') and x['subject_kind'] in ('practice_event','practice_relation','practice_relation.explanation_finding_id'):
  for key,value in [('source_version_ids',ver),('passage_ids',ref),('inspected_sections','TBMM 2/3790 PDF, ilk sayfa, Özel imza ve unvanı')]:
   a=json.loads(x[key]);a.append(value);x[key]=json.dumps(a,ensure_ascii=False)
  x['reason']+=' TBMM PDF ilk sayfası da yerelde incelendi.'
r['practice_source_review'].append(dict(subject_kind='practice_event_evidence',subject_id=event+'|'+ref+'|initiative',reviewer_kind='agent',reviewed_at='2026-11-21T19:53:01+00:00',source_version_ids=json.dumps([ver]),passage_ids=json.dumps([ref]),inspected_sections=json.dumps(['TBMM 2/3790 PDF, ilk sayfa, Özel imza ve unvanı'],ensure_ascii=False),supported_claim='Teklifin ilk sayfasında Özel Yeni Parti genel başkanı olarak belirtiliyor.',limitations='PDF metin çıkarımında seçim çevresi OCR hatalıdır; CHP unvanı taşıyan internet transkripsiyonu ayrıdır.',result='reviewed',reason='İlk sayfa yerel pdf_page_text çıktısı ile TBMM sayfası karşılaştırıldı.'))
r['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in r['practice_source_review']]
(p/'program-review-draft-v3.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('PROGRAM_PDF_DRAFT',len(r['practice_source_review']))
