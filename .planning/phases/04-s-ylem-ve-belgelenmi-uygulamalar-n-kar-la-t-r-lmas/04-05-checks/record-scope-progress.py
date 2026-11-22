import json
from datetime import datetime,timezone
from pathlib import Path
path=Path('data/practices/04-tip-tranches.json'); data=json.loads(path.read_text())
items={
 'sendika-grev':dict(note='Arşivli Faz3 sendika satırı ile TBMM 27. dönem 2/4390 metni ve 2 Haziran 2023 hükümsüz listesi okundu. Programın 2022 tarihindeki sürümü bilinmiyor; başka olaylar ve uçlar araştırılmalı.',source_ids=['0203-tip-program-v1','0405-tip-sendika-274390-pdf-v1','0405-tip-sendika-hukumsuz-v1'],links=['https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y5/T2/WebOnergeMetni/9c60b46f-6665-479a-aa0f-9025c059f4e9.pdf','https://www5.tbmm.gov.tr/tutanaklar/TUTANAK/TBMM/d28/c001/tbmm28001001.pdf']),
 'calisma-sureleri':dict(note='Faz3 programın genel çalışma süreleri pasajı, 6–7 Nisan 2024 Parti Meclisi 35 saat beyanı ve TBMM 28. dönem 2/2121 yedi sayfa okundu; programın tarihsel yürürlüğü ve teklifin kesim anındaki tüm aşamaları ayrı araştırılmalı.',source_ids=['0203-tip-program-v1','0405-tip-pm-nisan-v1','0405-tip-282121-v1'],links=['https://tip.org.tr/myk-ve-parti-meclisi/parti-meclisi-degerlendirmesi-6-7-nisan-2024','https://www.tbmm.gov.tr/Yasama/KanunTeklifi/c3422565-793b-4f23-90d9-018f0fd3796b']),
 'ic-tartisma-elestiri':dict(note='2022 adlandırılmış tüzük PDF basılı 18–19. sayfalar; Nisan PM öz değerlendirmesi ve Temmuz açıklama, parti yanıtı ve gazetecinin ilgili takibi okundu. İhraç ve üyelik durumu ihtilaflı; 2024 tüzük yürürlüğü ve kalan olay uçları açık.',source_ids=['0203-tip-charter2022-v1','0405-tip-pm-nisan-v1','0405-tip-istifa-cumhuriyet-v1','0405-tip-gazeteci-yanit-v1'],links=['https://www.cumhuriyet.com.tr/siyaset/tipin-uc-il-yonetimi-istifa-etti-statukocu-bir-anlayisla-yol-2229384','https://cagdassamsun.com/kose-yazilari/umit_ozcelik_tipnin_seni_26_haziranda_ihrac_etmedigini_ispatla_-238']),
 'parti-ici-itiraz':dict(note='PDF basılı 18. sayfada üst organa itiraz hükmü ve Tire sevk/tedbir hakkındaki iki parti açıklaması ile ilgili kişinin ayrı beyanı okundu. Somut itiraz ve nihai disiplin işlemi görülmedi; tarihsel tüzük sürümü ve ilgili uçlar açık.',source_ids=['0203-tip-charter2022-v1','0405-tip-tire-sevk-v1','0405-tip-tire-yanit-v1','0405-tip-tire-ozturk-v1'],links=['https://www.habertire.com/tip-ilce-baskanligi-ali-haydar-ozturku-disipline-sevk-etti','https://www.habertire.com/tip-tire-ilce-baskanligi-ozturkun-iddialarina-yanit-verdi','https://egeyebakis.com/siyaset/tipin-vekil-adayindan-tipe-agir-elestiri-iktidarin-ekmegine-yag-suren-bir-parti-84934'])}
count=0
for t in data['tranches']:
 if t['topic_id'] in items:
  item=items[t['topic_id']]; t['research_progress']=dict(recorded_at=datetime.now(timezone.utc).isoformat(),note=item['note'],source_ids=item['source_ids'],urls=item['links'],status='partial');count+=1
  assert t['state']=='pending' and t['processed_at'] is None and not t['closure_refs']
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('PARTIAL_SCOPE_LINKS',count)
