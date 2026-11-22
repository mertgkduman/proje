"""İki 2025 olayı ve bağımsız esas numarası kaynaklarıyla kapı öncesi taslak."""
import datetime
import hashlib
import json
from pathlib import Path
from arsiv import html_source_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
first=(p/'103465-combined-draft.json').read_bytes(); first_review=(p/'103465-combined-review-draft.json').read_bytes()
assert hashlib.sha256(first).hexdigest()=='79180081aaee4df4778eb15e9468c1b7f7571ff4e7ecbca49f75709264db6c31'
assert hashlib.sha256(first_review).hexdigest()=='2add4592356617c7be50f84c2d6fe1575aab12147cacffdc3e418b4b73ff9c3c'
package,review=json.loads(first),json.loads(first_review)
fragment=json.loads((p/'103464-unmatched-fragment-draft.json').read_text())
package['entries']+=fragment['entries']+json.loads((p/'2025-detail-source-slices-draft.json').read_text())['entries']
local_text='Toplumsal meselelerin ilk şahidi olan yerel medya organları, yerel medya gazeteleri, televizyonları ise Basın İlan Kurumunun esirgediği ilanlar sebebiyle yoksulluk sınırında hatta daha da altında faaliyet yürütmeye ve var olmaya çalışıyorlar.'
body=html_source_text(Path('data/practices/sources/dem/objects/c3eb7e2855a1d26b1ee984f002583d706b7dcd4adc42bc1feaf8eba2a7ac603f/original.html.bin').read_bytes())
assert body.count(local_text)==1
local_id='0406-tbmm-2025-24-yerel-medya-p'
package['entries'].append(dict(kind='passage',values=dict(id=local_id,version_id='0406-tbmm-2025-24-v1',exact=local_text,prefix=None,suffix=None,article=None,section='Cupolo’nun yerel medya ve ilanlar hakkındaki açıklaması',pdf_page_index=None,printed_page=None)))
for table,rows in fragment['practice_records'].items(): package['practice_records'].setdefault(table,[]).extend(rows)
review['practice_source_review']+=fragment['practice_source_review']
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
package['practice_records']['practice_event_evidence'].append(dict(event_id='0406-2025-103465-gundem',passage_id=local_id,supported_point='Yerel medya ve ilanlara ilişkin grup görüşü',stage='initiative',concrete_basis='Cupolo yerel medya kuruluşları ve ilanlar hakkında görüş bildirir.',limitation='Bu, konuşmacıya ait değerlendirmedir; yerel medyanın mali sonucu bağımsız olarak doğrulanmaz.',epistemic_type='claim'))
package['practice_records']['practice_evidence_assessment'].append(dict(event_id='0406-2025-103465-gundem',passage_id=local_id,stage='initiative',basis_kind='document'))
review['practice_source_review'].append(dict(subject_kind='practice_event_evidence',subject_id='0406-2025-103465-gundem|'+local_id+'|initiative',reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(['0406-tbmm-2025-24-v1']),passage_ids=json.dumps([local_id]),inspected_sections=json.dumps(['Cupolo’nun yerel medya hakkındaki açıklaması'],ensure_ascii=False),supported_claim='Konuşmacı yerel medya ve ilanlara ilişkin görüşünü açıkladı.',limitations='İddia konuşmacıya aittir; yerel medya gelirleri bağımsız doğrulanmadı.',result='reviewed',reason='TBMM tutanağında Cupolo’nun yerel medya cümlesi okundu.'))
for number,event in [('103464','0406-2025-103464-gundem'),('103465','0406-2025-103465-gundem')]:
    version='0406-tbmm-'+number+'-detail-v1'
    for suffix,point in [('number','Araştırma önergesinin esas numarası'),('received','Başkanlığa geliş tarihi')]:
        passage='0406-tbmm-'+number+'-detail-'+suffix+'-p'; stage='initiative'
        package['practice_records']['practice_event_evidence'].append(dict(event_id=event,passage_id=passage,supported_point=point,stage=stage,concrete_basis='TBMM resmî ayrıntı sayfası '+point.lower()+' bilgisini gösterir.',limitation='Erişimde görülen sayfa durumu yöntem kesimine taşınmaz; ön görüşme takvimi asıl araştırma önergesinden ayrıdır.',epistemic_type='claim'))
        package['practice_records']['practice_evidence_assessment'].append(dict(event_id=event,passage_id=passage,stage=stage,basis_kind='document'))
        review['practice_source_review'].append(dict(subject_kind='practice_event_evidence',subject_id=event+'|'+passage+'|'+stage,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps([version]),passage_ids=json.dumps([passage]),inspected_sections=json.dumps([point],ensure_ascii=False),supported_claim='Resmî detay sayfasındaki '+point.lower()+'.',limitations='Ayrıntı sayfasının erişimdeki durum bilgisi kesim tarihi durumu olarak kabul edilmez.',result='reviewed',reason='Özgün '+number+' detay sayfası incelendi.'))
for number,event in [('103464','0406-2025-103464-gundem'),('103465','0406-2025-103465-gundem')]:
    row=next(x for x in review['practice_source_review'] if x['subject_kind']=='practice_event' and x['subject_id']==event)
    row['source_version_ids']=json.dumps(json.loads(row['source_version_ids'])+['0406-tbmm-'+number+'-detail-v1'],ensure_ascii=False)
    row['passage_ids']=json.dumps(json.loads(row['passage_ids'])+['0406-tbmm-'+number+'-detail-number-p','0406-tbmm-'+number+'-detail-received-p'],ensure_ascii=False)
    row['inspected_sections']=json.dumps(json.loads(row['inspected_sections'])+['Resmî esas numarası','Başkanlığa geliş tarihi'],ensure_ascii=False)
    if number=='103465':
        row['passage_ids']=json.dumps(json.loads(row['passage_ids'])+[local_id],ensure_ascii=False)
        row['inspected_sections']=json.dumps(json.loads(row['inspected_sections'])+['Yerel medya ve ilanlar'],ensure_ascii=False)
review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']]
assert len(keys)==len(set(keys))
(p/'two-2025-combined-draft.json').write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n')
(p/'two-2025-combined-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('TWO_2025_COMBINED_DRAFT',len(package['practice_records']['practice_event']),len(keys))
