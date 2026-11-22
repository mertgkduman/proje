import json
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-national-primary-party-draft.json').read_text());review=json.loads((p/'national-primary-party-review-draft.json').read_text());versions={'0404-yeni-parti-haber-'+n+'-v1' for n in ('49','50','289','291')};changed=set()
for entry in pkg['entries']:
    if entry['kind']=='source_attribution' and entry['values']['version_id'] in versions:
        v=entry['values'];v['published_at']=None;v['date_precision']='unknown';v['basis']='Parti JSON içeriği ve created_at zamanı okundu; created_at oluşturulma zamanıdır, ayrı yayın tarihi belirlenmedi.';changed.add(v['version_id'])
assert changed==versions
for row in review['practice_source_review']:
    for field in ('supported_claim','limitations','reason','inspected_sections'):
        row[field]=row[field].replace('291 yayın günü Türkiye saatinde 9 Kasımdır','291 kayıt oluşturma günü Türkiye saatinde 9 Kasımdır')
(p/'package-creation-date-distinction-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n');(p/'creation-date-distinction-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('document creation retained; unknown publication',sorted(changed))
