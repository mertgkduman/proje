import json
from datetime import datetime,timezone
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-membership-source-layout-draft.json').read_text());review=json.loads((p/'membership-announcements-review-draft.json').read_text());pkg['entries']+=json.loads((p/'national-party-primaries-draft.json').read_text())['entries'];now=datetime.now(timezone.utc).isoformat(timespec='seconds');ev='0404-genelbaskan-onsecim';refs=['0404-yeni-parti-haber-289-onsecim-p','0404-yeni-parti-haber-291-onsecim-p']
assert len([x for x in pkg['practice_records']['practice_event'] if x['id']==ev])==1
for num,ref,point in [('289',refs[0],'Parti açıklamasında Özel’in Ankara’da ön seçimde oy kullanması'),('291',refs[1],'Parti açıklamasında ulusal yüzde 81,3 katılım beyanı')]:
    pkg['practice_records']['practice_event_evidence'].append(dict(event_id=ev,passage_id=ref,supported_point=point,stage='initiative',concrete_basis='Partinin kamuya açık tarihli JSON yayını.',limitation='Parti beyanı bağımsız sandık tutanakları veya kurultay seçimi değildir.',epistemic_type='claim'))
    pkg['practice_records']['practice_evidence_assessment'].append(dict(event_id=ev,passage_id=ref,stage='initiative',basis_kind='party_announcement'))
    review['practice_source_review'].append(dict(subject_kind='practice_event_evidence',subject_id=ev+'|'+ref+'|initiative',reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(['0404-yeni-parti-haber-'+num+'-v1'],ensure_ascii=False),passage_ids=json.dumps([ref],ensure_ascii=False),inspected_sections=json.dumps(['Partinin '+num+' numaralı ön seçim yayını'],ensure_ascii=False),supported_claim=point+' yayında yer alır.',limitations='Parti açıklaması sandık tutanağı veya kurultay seçim sonucu değildir.',result='reviewed',reason='Parti JSON içeriği ve oluşturma zamanı Türkiye saatine çevrilerek okundu.'))
targets={('practice_event',ev),('practice_relation','0404-genelbaskan-onsecim-iliski-id'),('practice_relation','0404-tbmm-onsecim-iliski-id')};updated=set()
for row in review['practice_source_review']:
    key=(row['subject_kind'],row['subject_id'])
    if key in targets:
        for field,added in [('source_version_ids',['0404-yeni-parti-haber-289-v1','0404-yeni-parti-haber-291-v1']),('passage_ids',refs),('inspected_sections',['Parti 289 ön seçimde oy kullanma anlatımı','Parti 291 katılım oranı beyanı'])]:
            values=json.loads(row[field]);assert not set(values)&set(added);row[field]=json.dumps(values+added,ensure_ascii=False)
        row['reviewed_at']=now;row['limitations']+=' Parti oranı ulusal beyan olup yerel ön seçimlerle toplanmaz; 291 yayın günü Türkiye saatinde 9 Kasımdır.';row['reason']+=' Parti JSON 289 ve 291 ayrı okunup kaynak zincirine eklendi.';updated.add(key)
assert updated==targets
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']];assert len(keys)==len(set(keys));review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
(p/'package-national-primary-party-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n');(p/'national-primary-party-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('entries',len(pkg['entries']),'reviews',len(keys),'closures',len(pkg['practice_records']['practice_closure']))
