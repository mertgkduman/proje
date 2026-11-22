"""Dar Hakkâri fragmenti için gerçek kaynak okuma kayıtları; henüz doğrulanmadı."""
import datetime,json
from pathlib import Path
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
event='0406-hakkari-2024-selection'; st='0406-hakkari-charter-statement';rel='0406-hakkari-selection-relation';con='0406-hakkari-selection-contribution';dis='0406-hakkari-selection-dispute'
a='0406-hakkari-round1-alt-p';b='0406-hakkari-round2-p';c='0406-calli-p';d='0406-calli-list-p';e='0406-calli-reply-p';s='0305-dem-secim-yontem-to-yerel-aday-dem-passage'
versions={a:'0406-hakkari-round1-alt-v1',b:'0406-hakkari-round2-v1',c:'0406-calli-v1',d:'0406-calli-v1',e:'0406-calli-reply-v1',s:'0204-dem-charter-v1'}
sections={a:'Yüksekova Haber 13 Ocak ilk tur sonucu',b:'Yüksekova Halkın Sesi 14 Ocak ikinci tur sonucu',c:'Hakkari İl Sesi 24 Ocak Çallı itirazı',d:'Hakkari İl Sesi 24 Ocak Çallı delege listesi iddiası',e:'Hakkari İl Sesi 26 Ocak il örgütü yanıtı',s:'DEM adlı tüzük PDF indeksi 31, Madde 59'}
limited='Tüzüğün o tarihteki yürürlüğü, seçim yönergesi, oy tutanakları ve itiraz kararı bu kaynaklarla doğrulanmadı; 10/16 oy farkı çelişkili.'
items=[
 ('practice_event_evidence',event+'|'+a+'|action',[a],'İlk tur için Çallı ve Akış oyları gazetede belirtilir.'),
 ('practice_event_evidence',event+'|'+b+'|result',[b],'İkinci tur sonucu Akış ve Tekçe adayları olarak bildirilir.'),
 ('practice_event',event,[a,b],'İki tarihli Hakkâri yerel aday ön seçimi haberlerde yer ve sonuçla anlatılır.'),
 ('practice_statement',st,[s],'Nüsha Madde 59 yerel aday ön seçimi veya merkez yoklamasını ve PM kararını düzenler.'),
 ('practice_statement.summary_finding_id',st,[s],'Tüzük özeti iki yöntemi ve PM yetkisini korur.'),
 ('practice_statement.quote_finding_id',st,[s],'Alıntı Madde 59 yerel ve genel seçim aday yöntemidir.'),
 ('practice_relation',rel,[s,a,b],'Ön seçim ile tüzükteki yerel aday yöntemi aynı konuya ilişkindir; yürürlük bağı açık.'),
 ('practice_relation.target_finding_id',rel,[s],'İlişkinin hedef bulgusu tüzükte yerel aday belirleme yöntemidir.'),
 ('practice_relation.result_finding_id',rel,[a,b],'Sonuç bulgusu ilk tur haberini ikinci tur aday sonucundan ayırır.'),
 ('practice_relation.explanation_finding_id',rel,[s,a,b],'İlişki cümlesi seçim yönergesi ve tüzük dönemi belirsizliğini korur.'),
 ('practice_contribution',con,[a,b],'Partinin yerel aday ön seçimi iki haberin kapsamıyla sınırlıdır.'),
 ('practice_contribution.finding_id',con,[a,b],'Katkı bulgusu iki tura ait aktarılan sonuçları birlikte gösterir.'),
 ('practice_dispute',dis,[a,b,c,d,e],'Çallı itirazı ve delege iddiası ile il örgütünün yanıtı ayrıdır.'),
 ('practice_dispute.summary_finding_id',dis,[c,d,e],'İhtilaf özeti iki tarafın iddiasını kaynağa atfeder.'),
 ('practice_dispute_evidence',dis+'|'+d+'|İkinci tur listesine 44 kişi eklendiği iddiası|conflict',[d],'Çallı ikinci tur listesine 44 kişinin eklendiğini ileri sürer.'),
 ('practice_dispute_evidence',dis+'|'+e+'|İtiraza ilişkin parti yanıtı|reply',[e],'İl örgütü itirazı dayanıksız bulduğunu ve tebliğ ettiğini savunur.'),
]
now=datetime.datetime.now(datetime.timezone.utc).isoformat();reviews=[]
for kind,identity,ps,claim in items:
 reviews.append(dict(subject_kind=kind,subject_id=identity,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(list(dict.fromkeys(versions[p] for p in ps)),ensure_ascii=False),passage_ids=json.dumps(ps,ensure_ascii=False),inspected_sections=json.dumps([sections[p] for p in ps],ensure_ascii=False),supported_claim=claim,limitations=limited,result='reviewed',reason='İlgili kaynak bölümleri okundu; '+claim))
(checks/'hakkari-event-review-draft.json').write_text(json.dumps(dict(practice_source_review=reviews,source_review_refs=[dict(subject_kind=r['subject_kind'],subject_id=r['subject_id']) for r in reviews]),ensure_ascii=False,indent=2)+'\n')
print('HAKKARI_EVENT_REVIEW_DRAFT',len(reviews))
