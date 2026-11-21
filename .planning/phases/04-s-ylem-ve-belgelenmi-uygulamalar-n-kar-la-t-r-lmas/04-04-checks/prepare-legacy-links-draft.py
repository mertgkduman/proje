import json
from pathlib import Path
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
pkg=json.loads((p/'package-samsun-speech-draft.json').read_text())
rows=[
 ('afyon','0404-afyon-onsecim-event','0404-afyon-onsecim-iliski-id'),
 ('aydin','0404-aydin-onsecim-event','0404-aydin-onsecim-iliski-id'),
 ('bursa','0404-bursa-onsecim-event','0404-bursa-iliski-id'),
 ('diyarbakir','0404-diyarbakir-onsecim-event','0404-diyarbakir-iliski-id'),
 ('istanbul','0404-istanbul-onsecim-event','0404-istanbul-onsecim-iliski-id'),
 ('izmir','0404-izmir-onsecim-event','0404-izmir-onsecim-iliski-id'),
 ('sakarya','0404-sakarya-onsecim-event','0404-sakarya-iliski-id'),
 ('usak','0404-usak-onsecim-event','0404-usak-iliski-id'),
 ('national-edirne','0404-genelbaskan-onsecim','0404-genelbaskan-onsecim-iliski-id'),
 ('national-eskisehir','0404-genelbaskan-onsecim','0404-genelbaskan-onsecim-iliski-id'),
]
links=pkg['practice_records']['practice_legacy_link']
for suffix,event,relation in rows:
    reason=('Eski yerel sandık kaydı ile aynı 8 Kasım genel başkan ön seçimi; il sandıkları ulusal toplama ek olay sayılmaz.' if suffix.startswith('national-') else 'Eski 18 Ekim il ön seçimi kaydı ile kaynaklı yeni olay aynı yer ve aşamayı kapsar; sonraki kongre ayrı tutulur.')
    for kind in ('action','match'):
        links.append(dict(legacy_kind=kind,legacy_id='0105-'+kind+'-'+suffix,event_id=event,relation_id=relation,overlap_reason=reason))
(p/'package-legacy-links-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
