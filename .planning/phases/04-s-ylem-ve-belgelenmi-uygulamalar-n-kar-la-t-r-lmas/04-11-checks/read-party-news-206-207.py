from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from pathlib import Path
import json, re

here = Path(__file__).resolve().parent
catalog = json.loads((here/'party-news-catalog.json').read_bytes())
posts = {int(p['id']):p for p in catalog['posts']}
cases = [
    (206,373,3686,'Altı partinin anayasa teklifi ve Demokrat Parti ev sahipliği.',
     'Temel Karamollaoğlu anayasa değişikliği teklifinin kamuoyuna sunulduğunu ve ardından Gültekin Uysal ev sahipliğinde ikinci turun üçüncü toplantısının yapıldığını söylüyor.',
     '30 Kasım 2022 Türkiye yerel günlü parti yayımı, pazartesi sunumu ile ardından gerçekleştiği belirtilen toplantıyı ayırıyor.',
     'Pazartesi 28 Kasım 2022’ye işaret eder. Toplantı günü ve kapsamı ile ortak teklifin özgün metni başka bir tarihli kaynaktan henüz doğrulanmadı. Parti anlatımı tek başına teklifin Meclise sunulmasını veya kabulünü göstermez.',
     "Ardından da Demokrat Parti Genel Başkanı Gültekin Uysal'ın ev sahipliğinde, 2. turun 3. toplantısını gerçekleştirdik."),
    (207,372,4599,'Öğretmen kariyeri, ücret ve emeklilik hedefleri.',
     'Temel Karamollaoğlu öğretmenlerin kariyer sınavının kaldırılması, kariyerin kıdeme bağlanması ve kariyer ödemesinin artırılarak emekliliğe yansıtılmasını savunuyor.',
     '23 Kasım 2022 Türkiye yerel günlü parti yayımı 7354 sayılı Öğretmenlik Meslek Kanununu eleştiriyor ve bu cümleleri Saadet iktidarının icraatları olarak niteliyor.',
     'Metin bunların mevcut iktidardan talep değil Saadet iktidarı için icraat cümleleri olduğunu açıkça belirtiyor. Sonraki mevzuat, fiilî ödeme ve parti yetkisi ayrıca incelenmedi.',
     'Sınav kalkmalı, kariyer kıdeme bağlanmalıdır. Kariyer kaynaklı ödeme miktarı hem artırılmalı hem de emekliliğe yansıtılmalıdır.'),
]
for tranche,pid,tokens,point,statement,evidence,uncertainty,selected in cases:
    source=Path('/tmp/gsd0411-body'+str(pid)+'.json')
    raw=source.read_bytes(); item=json.loads(raw)['veri']['haber']; assert int(item['id'])==pid
    body=re.sub(r'\s+',' ',re.sub(r'<[^>]+>',' ',unescape(unescape(item['detay'])))).strip()
    start=body.index(selected); dest=here/'party-news-bodies'/f'{pid}.json'; assert not dest.exists(); dest.write_bytes(raw); p=posts[pid]
    read=dict(post_id=pid,publisher=p['publisher'],public_url=p['public_url'],source_url=p['body_url'],final_url=p['body_url'],http_status=200,published_at=p['published_at'],updated_at=None,accessed_at=datetime.fromtimestamp(source.stat().st_mtime,timezone.utc).isoformat(),original_path=f'party-news-bodies/{pid}.json',original_bytes=len(raw),sha256=sha256(raw).hexdigest(),normalized_body_sha256=sha256(body.encode()).hexdigest(),source_section_range=[0,len(body)],state='examined',reading=statement,selected_passages=[dict(start=start,end=start+len(selected),exact=selected)],point=point,statement=statement,concrete_evidence=evidence,open_provenance=uncertainty)
    receipt=dict(tranche_id=f'saadet-party-news-{tranche}',party_id='saadet',reviewer_kind='agent',processed_at=datetime.now(timezone.utc).isoformat(),reads=[read],completed_pre_cut_bodies=292+(tranche-205),remaining_pre_cut_bodies=357-(tranche-205),closure_refs=[],source_token_observation=f'Tam tekil gövdenin okuma çıktısı araç tarafından yaklaşık {tokens} token olarak raporlandı ve 12.000 token sınırının altında.',normalization='HTML varlıkları iki kez çözüldü. Etiketler kaldırıldı ve boşluklar birleştirildi. Erişim zamanı indirme dosyasının ilk yazılma zamanıdır.')
    (here/f'party-news-{tranche}-reading.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(pid,read['sha256'],len(body))
