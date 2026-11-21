import json
from pathlib import Path
p=Path('data/practices/04-yeni-parti-tranches.json');q=json.loads(p.read_text())
notes={
 'organ-secim-yontemi':'4 Ağustos Euronews beyanı, Çeşme, Muğla ve 8 Kasım ulusal ön seçim kaynak zincirleri dar paketlerde denetlendi; Uşak, Bursa, Sakarya, İzmir ve Diyarbakır ek yerel taslakları gerçek CLI kontrollerini bekliyor. 69 il toplamı ile yerel kayıtlar ve ayrı kongreler toplanmaz; diğer iller ve itirazlar araştırılacak.',
 'barinma-konut':'Kurucu program barınma hükmü ve 7 Ağustos TBMM 122. birleşimde grup önerisinin öne alınmasına ilişkin oylama okundu; kapsam açık, asıl önergenin sonraki işlemleri ve başka uygulamalar araştırılacak. Taslak source-check ve preview sürüyor.',
 'asgari-ucret':'Kurucu program asgari ücret hükmü ile 3 Ağustos TBMM 2/3790 teklifi ve PDF metni okundu; sunum yasalaşma değildir. Teklifin kesim tarihindeki seyri ve başka uygulamalar araştırılacak.',
 'uyelik-kabul-itiraz':'Kurucu tüzük üyelik hükmü ile Kayseride kayıt iddiası ve karşı açıklama dar pakette incelendi; Edirne askı takvimi ayrı kaynaklarda okundu. Kayseri dosyasının asıl başvuru ve kararları ve diğer olgular aranacak.',
 'disiplin-yetki':'Kurucu tüzük ve Gaziantep Keleş sevk/ihracına ilişkin farklı haberler dar pakette incelendi; Oğuzeli Ergüleç dosyası ayrıca sevk aşamasında aktarıldı. Disiplin kurulu kararları ve diğer somut işlemler araştırılacak.',
}
for t in q['tranches']:
 if t['topic_id'] in notes:
  marker='2026-11-21 ara okuma: '+notes[t['topic_id']]
  if marker not in t['next_leads']:t['next_leads'].append(marker)
p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
