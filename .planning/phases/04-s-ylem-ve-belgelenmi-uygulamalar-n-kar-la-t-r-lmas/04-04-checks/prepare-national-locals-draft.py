import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-usak-draft.json').read_text()); extra=json.loads((p/'october-referral-records-draft.json').read_text())['entries']; ids=('0404-edirne-genel-onsecim','0404-eskisehir-genel-onsecim')
pkg['entries'] += [e for e in extra if any(str(e['values'].get(k,'')).startswith(i) for k in ('id','version_id','document_id') for i in ids)]
pid='0404-eskisehir-genel-baslama-p'; pkg['entries'].append(dict(kind='passage',values=dict(id=pid,version_id='0404-eskisehir-genel-onsecim-v1',exact="genel başkan adayını belirlemek için Türkiye genelinde ve Eskişehir'de ön seçimler başladı.",prefix=None,suffix=None,article=None,section='8 Kasım Eskişehir genel başkan ön seçiminin başlaması',pdf_page_index=None,printed_page=None)))
r=pkg['practice_records'];ev='0404-genelbaskan-onsecim'
for ref,point in [('0404-edirne-genel-onsecim-p','Edirne merkezinde genel başkan adaylığı ön seçimi sandıkları'),(pid,'Eskişehirde genel başkan adaylığı ön seçiminin başlaması')]:
 r['practice_event_evidence'].append(dict(event_id=ev,passage_id=ref,supported_point=point,stage='action',concrete_basis='8 Kasım yerel haber ulusal ön seçimin ilgili ildeki uygulamasını bildiriyor.',limitation='Yerel örnek ulusal genel ön seçimle örtüşür, ayrı ulusal oy sayısı değildir; kurultaydan da ayrıdır.',epistemic_type='claim'))
 r['practice_evidence_assessment'].append(dict(event_id=ev,passage_id=ref,stage='action',basis_kind='independent_report'))
(p/'package-national-locals-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n');print('NATIONAL_LOCALS_DRAFT pending checks')
