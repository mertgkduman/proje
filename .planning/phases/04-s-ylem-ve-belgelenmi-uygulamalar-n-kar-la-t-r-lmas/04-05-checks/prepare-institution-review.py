import json
from pathlib import Path
from datetime import datetime, timezone
p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
c='0304-tip-pdf-uye-tartisma-q'; a='0405-tip-istifa-cumhuriyet-announcement-p'; x='0405-tip-istifa-cumhuriyet-criticism-p'; b='0405-tip-istifa-cumhuriyet-rebuttal-mdk-p'; z='0405-tip-gazeteci-yanit-denial-p'
event='0405-tip-2024-istifa-aciklama'; st='0405-tip-ic-tartisma-statement'; rel='0405-tip-istifa-iliski'; dispute='0405-tip-istifa-ihtilaf'
specs=[
 ('practice_event',event,[a,b],'Basın açıklaması ve buna parti yanıtı haberde yer alır.'),
 ('practice_event_evidence',event+'|'+a+'|action',[a],'İmzacıların istifa beyanı yayımlanmıştır; üyelik statüleri ihtilaflıdır.'),
 ('practice_event_evidence',event+'|'+b+'|action',[b],'Parti basın bürosu önceden ihraç iddiasıyla cevap verdi.'),
 ('practice_statement',st,[c],'PDF üyelerin bağlı organlarda tartışabilmesini düzenler.'),
 ('practice_statement.summary_finding_id',st,[c],'Özet tartışma yolunu korur.'),
 ('practice_statement.quote_finding_id',st,[c],'Alıntı PDF sayfasındaki cümledir.'),
 ('practice_relation',rel,[c,a,x,b,z],'Yazılı iç tartışma ile kamuya açıklanan eleştiri aynı konunun farklı kapsamlarıdır.'),
 ('practice_relation.target_finding_id',rel,[c],'Hedef PDF kopyasının üyelere ilişkin tartışma hükmüdür.'),
 ('practice_relation.explanation_finding_id',rel,[c,a,x,b,z],'İlişki iki tarafın iddialarını ve çözümlenmemiş statüyü birlikte korur.'),
 ('practice_contribution','0405-tip-istifa-parti-katki',[b],'Parti basın bürosu önceki ihraç iddiası ile karşı çıktı.'),
 ('practice_contribution.finding_id','0405-tip-istifa-parti-katki',[b],'Katkı bulgusu haberin kuruma atfettiği cevapla sınırlıdır.'),
 ('practice_dispute',dispute,[c,a,x,b,z],'Partinin ihraç beyanı ve kişinin reddi aynı meselede çekişmelidir.'),
 ('practice_dispute.summary_finding_id',dispute,[c,a,x,b,z],'İhtilaf özeti karşı tarafları ve kanıt sınırını açıkça belirtir.'),
 ('practice_dispute_evidence',dispute+'|'+b+'|Önceki ihraç|conflict',[b],'Parti daha önce ihraç kararı verildiğini bildirir.'),
 ('practice_dispute_evidence',dispute+'|'+z+'|Önceki ihraç|reply',[z],'Gazeteci kişinin ihraç edildiği iddiasını reddettiğini aktarır.')]
now=datetime.now(timezone.utc).isoformat(); reviews=[]
for kind,ident,refs,claim in specs:
 versions=sorted({'0203-tip-charter2022-v1' if v==c else '0405-tip-istifa-cumhuriyet-v1' if v in (a,x,b) else '0405-tip-gazeteci-yanit-v1' for v in refs})
 reviews.append(dict(subject_kind=kind,subject_id=ident,reviewer_kind='agent',reviewed_at=now,source_version_ids=json.dumps(versions),passage_ids=json.dumps(refs),inspected_sections=json.dumps(['PDF sayfa 18–19; yerel açıklama; parti cevabı ve gazeteci takip yazısı'],ensure_ascii=False),supported_claim=claim,limitations='PDF’nin 2024 yürürlük sırası bilinmiyor; üyelik ve disiplin evrakı görülmedi.',result='reviewed',reason='Bu alanın kaynak içeriği ve ayrı aktörleri incelendi: '+kind))
(p/'institution-review-draft.json').write_text(json.dumps(dict(practice_source_review=reviews),ensure_ascii=False,indent=2)+'\n')
print('DRAFT ONLY',len(reviews))
