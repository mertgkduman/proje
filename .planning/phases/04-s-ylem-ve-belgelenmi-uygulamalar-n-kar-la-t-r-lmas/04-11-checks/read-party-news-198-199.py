from datetime import datetime,timezone
from hashlib import sha256
from html import unescape
from pathlib import Path
import json,re
here=Path(__file__).resolve().parent
posts={int(p['id']):p for p in json.loads((here/'party-news-catalog.json').read_bytes())['posts']}
cases=[
 (198,382,'Deprem sonrasında koordinasyon ve tahliye çağrısı.','Karamollaoğlu depremin üçüncü günündeki koordinasyon eksikliklerini eleştiriyor ve acil ihtiyaçlarla tahliye çağrısı yapıyor.','Parti yayımı üçüncü gün ve ilk 72 saatin önemine ilişkin açıklamayı genel başkana atfediyor.','İleri sürülen müdahale ve iletişim eksiklikleri bu parti gövdesiyle bağımsız olarak doğrulanmış olay sonucu sayılmaz.','Bölgeden öncelikle kadın, çocuk ve yaşlıların acilen tahliye edilmesi gerekiyor.'),
 (199,381,'Deprem sonrasında acil kurtarma ve tahliye çağrısı.','Karamollaoğlu acil tahliye koridorları ve ekipman sevki çağrısı yapıyor.','Parti yayımında kriz masası oluşturulduğu, taleplerin resmî kurumlarla paylaşıldığı ve OHAL kararının takip edileceği aktarılıyor.','Partinin kriz masası ve resmî kurumlara bilgi paylaşımı parti beyanıdır. OHAL ilanı, Meclis onayı ve fiilî tahliye ayrı belgelerdir.','Acilen her noktada ‘tahliye koridorları’ açılmalı ve talep eden tüm vatandaşlarımız bölgeden çıkarılmalıdır.')]
for tranche,pid,point,statement,evidence,uncertainty,selected in cases:
    f=Path('/tmp/gsd0411-body'+str(pid)+'.json'); raw=f.read_bytes(); body=json.loads(raw)['veri']['haber']; assert int(body['id'])==pid
    text=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',unescape(unescape(body['detay'])))).strip(); start=text.index(selected)
    accessed=datetime.fromtimestamp(f.stat().st_mtime,timezone.utc).isoformat(); dest=here/'party-news-bodies'/f'{pid}.json'; assert not dest.exists(); dest.write_bytes(raw); p=posts[pid]
    read=dict(post_id=pid,publisher=p['publisher'],public_url=p['public_url'],source_url=p['body_url'],published_at=p['published_at'],updated_at=None,accessed_at=accessed,original_path=f'party-news-bodies/{pid}.json',sha256=sha256(raw).hexdigest(),normalized_body_sha256=sha256(text.encode()).hexdigest(),source_section_range=[0,len(text)],state='examined',reading=statement,selected_passages=[dict(start=start,end=start+len(selected),exact=selected)],point=point,statement=statement,concrete_evidence=evidence,open_provenance=uncertainty)
    record=dict(tranche_id=f'saadet-party-news-{tranche}',party_id='saadet',reviewer_kind='agent',processed_at=datetime.now(timezone.utc).isoformat(),reads=[read],completed_pre_cut_bodies=283+(tranche-197),remaining_pre_cut_bodies=366-(tranche-197),closure_refs=[],normalization='HTML varlıkları iki kez çözüldü. Etiketler kaldırıldı ve boşluklar birleştirildi. Erişim zamanı indirme dosyasının ilk yazılma zamanıdır.')
    (here/f'party-news-{tranche}-reading.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n'); print(pid,len(text),read['sha256'])
