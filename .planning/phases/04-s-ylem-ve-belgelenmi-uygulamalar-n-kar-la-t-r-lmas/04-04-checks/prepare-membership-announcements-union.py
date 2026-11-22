import json
from datetime import datetime,timezone
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-membership-union-draft.json').read_text());review=json.loads((p/'membership-union-review-draft.json').read_text());pkg['entries']+=json.loads((p/'membership-party-records-draft.json').read_text())['entries'];now=datetime.now(timezone.utc).isoformat(timespec='seconds')
ev='0404-cevrimici-uyelik-cesme-event';rel='0404-cevrimici-uyelik-cesme-iliski-id';program='0303-epm-detail-uyelik-kabul-itiraz-basvuru-sekli-p';news='0404-cevrimici-uyelik-cesme-p';p49='0404-yeni-parti-haber-49-uyelik-p';p50='0404-yeni-parti-haber-50-uyelik-p'
for ref,point in ((p49,'Partinin üyelik sistemi duyurusu'),(p50,'Partinin dijital üyelik çağrısı')):
    pkg['practice_records']['practice_event_evidence'].append(dict(event_id=ev,passage_id=ref,supported_point=point,stage='initiative',concrete_basis='Partinin kamuya açık tarihli JSON duyurusu.',limitation='Duyuru açılışın kesin gününü ve tekil üyeliğe kabulü belirtmez.',epistemic_type='claim'))
    pkg['practice_records']['practice_evidence_assessment'].append(dict(event_id=ev,passage_id=ref,stage='initiative',basis_kind='party_announcement'))
    num='49' if ref==p49 else '50'
    review['practice_source_review'].append(dict(subject_kind='practice_event_evidence',subject_id=ev+'|'+ref+'|initiative',reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(['0404-yeni-parti-haber-'+num+'-v1'],ensure_ascii=False),passage_ids=json.dumps([ref],ensure_ascii=False),inspected_sections=json.dumps(['Partinin '+num+' numaralı üyelik duyurusu'],ensure_ascii=False),supported_claim=point+' metinde yer alır.',limitations='Duyuru açılışın kesin gününü veya tekil başvuruların kabulünü bildirmez.',result='reviewed',reason='Kamuya açık JSON içeriği ve UTC oluşturma zamanı Türkiye saatine çevrilerek okundu.'))
section={program:'Tüzük üyelik başvuru biçimi',news:'Çeşme haberi sistem ve rehber',p49:'Parti 49 numaralı üyelik duyurusu',p50:'Parti 50 numaralı dijital üyelik çağrısı'}
for row in review['practice_source_review']:
    if (row['subject_kind'],row['subject_id']) in (('practice_event',ev),('practice_relation',rel)):
        refs=([news,p49,p50] if row['subject_kind']=='practice_event' else [program,news,p49,p50]);versions=['epm-charter-v1' if x==program else '0404-cevrimici-uyelik-cesme-v1' if x==news else '0404-yeni-parti-haber-49-v1' if x==p49 else '0404-yeni-parti-haber-50-v1' for x in refs]
        row['source_version_ids']=json.dumps(list(dict.fromkeys(versions)),ensure_ascii=False);row['passage_ids']=json.dumps(refs,ensure_ascii=False);row['inspected_sections']=json.dumps([section[x] for x in refs],ensure_ascii=False);row['reviewed_at']=now
        row['supported_claim']='Yerel haber ve iki parti duyurusu sistemin varlığını tarihleriyle bildirir.' if row['subject_kind']=='practice_event' else 'Tüzükteki elektronik başvuru hükmü, yerel haber ve sonraki duyurular ilişkilidir.'
        row['limitations']='Haber ve duyurular açılışın kesin gününü veya tekil başvuruların kabulünü belirlemiyor.';row['reason']='Tüzük, 12 Ağustos yerel haber ve Türkiye saatleriyle 13–14 Ağustos parti duyuruları ayrı okundu.'
keys=[(x['subject_kind'],x['subject_id']) for x in review['practice_source_review']];assert len(keys)==len(set(keys));review['source_review_refs']=[dict(subject_kind=x['subject_kind'],subject_id=x['subject_id']) for x in review['practice_source_review']]
(p/'package-membership-announcements-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n');(p/'membership-announcements-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('entries',len(pkg['entries']),'reviews',len(keys),'closures',len(pkg['practice_records']['practice_closure']))
