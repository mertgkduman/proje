import json
from datetime import datetime,timezone
from pathlib import Path

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks');pkg=json.loads((p/'package-group-scoped-draft.json').read_text());review=json.loads((p/'group-scoped-review-draft.json').read_text());now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name in ('postcutoff-charter-pdf-draft.json','postcutoff-pm-news-draft.json'):
    pkg['entries']+=json.loads((p/name).read_text())['entries']
old='0404-pm-degisikligi-iliski';fid='0404-pm-degisikligi-tarihsel-baglam';rid='0404-pm-degisikligi-iliski-id'
refs=['0303-epm-extra-merkez-kurul-olusumu-p','0303-kurucular-secim-p','0404-tuzuk-degisikligi-haber-p','0404-charter-announcement-api-p','0404-pm-artis-amida-p','0404-sonraki-tuzuk-16kasim-gecici6-p']
pkg['entries'].append(dict(kind='finding',values=dict(id=fid,party_id='yeni-parti',heading='Söylem ve uygulama',pair_id=fid,text='Kuruluş tüzüğü Parti Meclisi için 80 seçilmiş asıl ve 20 yedek üyeden söz eder. Sözcünün 9 Kasım açıklaması, bir sonraki olağan kurultay takvimine kadar bir defalık 150 asıl ve 30 yedek öngörüldüğünü aktarır. Kesim sonrasındaki 15 Kasım Amida haberi sayının 150’den 160’a artırıldığını bildirir; 16 Kasımda üretilmiş tüzük PDF’si 9 Kasım kararına atıf yapan geçici maddede 160 asıl ve 30 yedek yazar. Kesim anındaki kararın tam metni ve sonraki artışın metne ne zaman işlendiği görülmediğinden 160 sayısı 9 Kasım sonucu olarak alınamaz.',provenance='summary',epistemic_type='claim')))
for ref in refs:
    pkg['entries'].append(dict(kind='finding_evidence',values=dict(finding_id=fid,passage_id=ref,role='support')))
    pkg['entries'].append(dict(kind='verification',values=dict(finding_id=fid,passage_id=ref,checked_at=now,result='confirmed',reason='Kuruluş hükmü, 9 Kasım açıklaması ve tarihleri ayrılmış sonraki haber ve PDF pasajları okundu.')))
pkg['entries'].append(dict(kind='review',values=dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='9 Kasım açıklaması ve kesim sonrası iki kaynağın tarihleri ve sayıları ayrı tutuldu.')))
rows=[x for x in pkg['practice_records']['practice_relation'] if x['id']==rid];assert len(rows)==1 and rows[0]['explanation_finding_id']==old
rows[0]['explanation_finding_id']=fid
rows[0]['uncertainty_reason']='9 Kasım kararının tam metni görülmedi; 15 Kasım haberi ve 16 Kasım PDF’sindeki 160 sayısının kesim anında geçerli olduğu varsayılmıyor.'
rows[0]['authority_context']='9 Kasım sözcü beyanı ve haber kararın açıklamasıdır; sonraki haber ve PDF farklı tarihlerdeki bağlamdır.'
versions=['epm-charter-v1','0404-tuzuk-degisikligi-haber-v1','0404-charter-announcement-api-v1','0404-pm-artis-amida-v1','0404-sonraki-tuzuk-16kasim-v1']
sections=['Kuruluş tüzüğü Parti Meclisi','Kuruluş tüzüğü kurucu seçim hükmü','Cumhuriyet 9 Kasım değişiklik haberi','9 Kasım sözcü açıklamasında 150 ve 30','Amida 15 Kasım sonraki artış haberi','16 Kasım üretilen PDF Geçici Madde 6']
for row in review['practice_source_review']:
    if row['subject_id']==rid and row['subject_kind'] in ('practice_relation','practice_relation.explanation_finding_id'):
        row['source_version_ids']=json.dumps(versions,ensure_ascii=False);row['passage_ids']=json.dumps(refs,ensure_ascii=False);row['inspected_sections']=json.dumps(sections,ensure_ascii=False);row['reviewed_at']=now
        row['supported_claim']='Tarih sırasıyla 9 Kasım açıklaması ve sonraki sayı anlatımları ayrıldı.' if row['subject_kind']=='practice_relation' else 'Açıklama sonraki 160 sayısını kesim içi karar diye sunmuyor.'
        row['limitations']='9 Kasım kararının tam metni ve sonraki artışın metne işlenme zamanı doğrulanmadı.'
        row['reason']='Kuruluş tüzüğü, 9 Kasım haber ve sözcü açıklaması ile sonraki Amida ve PDF pasajları okundu.'
assert sum(x['subject_id']==rid and x['subject_kind'] in ('practice_relation','practice_relation.explanation_finding_id') for x in review['practice_source_review'])==2
(p/'package-pm-context-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n');(p/'pm-context-review-draft.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
print('entries',len(pkg['entries']),'reviews',len(review['practice_source_review']))
