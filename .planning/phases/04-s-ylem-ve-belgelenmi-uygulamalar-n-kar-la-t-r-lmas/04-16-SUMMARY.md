---
phase: 04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas
plan: "16"
status: complete
completed: 2026-11-26
subsystem: archive
requires:
  - phase: 04-03
    provides: Kapsam envanteri ve kaynaklı olay birleşimi
provides:
  - Dokuz partinin incelenen söylem ve uygulama kayıtları
  - Yerel HTML, SQLite, JSON ve özgün kaynak arşivi
requirements-completed: [UYG-01, UYG-02, KAR-03]
plan_head_before: 33e5f04401130ad915168142a96ba95c3be6692b
key-files:
  created: [.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-16-checks/first-delivery.json]
---

# Faz 4 ilk teslimi

[HTML raporunu aç](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html). Aynı sürümün [SQLite veritabanı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/records.sqlite3),
[JSON kaydı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/records.json) ve [manifesti](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/manifest.json).

İlk teslim dokuz partide kaynakları incelenmiş 625 olay ve 428
ilişkiyi kapsıyor. Tek olaya yönlendirilen 22 ortak olay kararı
ve çözülemeyen 13 aday kendi kaynakları ve gerekçeleriyle kayıtta.
Araştırma kesimi 10 Kasım 2026. 5.490 kapsam hücresinden
1’i kapalı, 355’i araştırılmış ve açık,
5134’ü henüz araştırılmamış. TİP’in eski amblem
araştırmasının önceki kapanışı ve yeniden açılışı görünür.

## Dokuz partiden örnekler

| Parti | Kaynakların gösterdiği | Kanıt sınırı |
|---|---|---|
| Yeni Parti | 14 Ekim 2026 komisyonu, 2/3895 ile 2/3939’u birlikte görüşme önergesini reddetti ve 2/3939’u kabul etti. [Komisyon kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0404-fon-komisyon-1014-relation) | 2/3895 dosyasının sonraki işlemi ve belirli bir yazılı soruya cevap ayrı izleniyor. |
| TİP | İstanbul Sözleşmesi davasında TİP temyiz eden davacıydı. Danıştay İDDK, 19 Aralık 2022’de ilk derece ret kararını onadı. [Temyiz kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0405-tip-istanbul-sozlesmesi-court-final-relation) | Sonraki AYM başvurusunun inceleme sonucu açık. |
| DEM Parti | 2/1716’nın HEDEP antetli, imzalı nüshası 24 Ekim 2023 geliş kaydı ve 27 Ekim havalesiyle eşleşiyor. [Antet kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0406-dem-kimlik-21716-relation) | Belge bu evraktaki kullanımı gösteriyor. Tescil günü ayrı bir araştırma konusu. |
| İYİ Parti | 8 Ağustos 2023’te Metin Ergun, Akbelen ön görüşmesinde İYİ Parti Grubu adına konuştu. Genel Kurul genel görüşme açılmasını kabul etmedi. [Akbelen kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0407-akbelen-2023-relation) | Kişi oyları ve maden izinlerinin durumu açık. |
| Yeni Yol Partisi | 8/134, 17 Haziran 2026’da Meclise sunulan ve emekli aylığı hesabı için genel görüşme isteyen imzalı önerge. [Önerge kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0408-inquiry-8134-relation) | Ön görüşme oyu ve önerilen tedbirlerin yürürlüğe girip girmediği açık. |
| DBP | Bağlar Belediye Meclisinin, CEMR Eşitlik Şartı konulu 6 Şubat 2015 tarihli 2015/48 sayılı kararı kayda geçirildi. [Belediye kararı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0409-dbp-baglar-2015-cemr-relation) | Karar belediye meclisine ait. 2015 imza nüshası ve uygulama açık. |
| EMEP | 19 Mart 2021 tarihli 3718 sayılı karar karşısında EMEP’in 20 Mart açıklaması yayımlanmış bir itirazı belgeliyor. [Sözleşme kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0410-emep-istanbul-sozlesmesi-relation) | Kararı Cumhurbaşkanı verdi. Uygulamanın fiilî etkileri ayrı kaynak gerektiriyor. |
| Saadet Partisi | 27 Ocak 2021 tarihli 7/35779 Bakanlık yanıtı, Karaduman’ın bireysel yazılı sorusuyla eşleşiyor. [Yanıt kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0411-saadet-mine-inquiry-35779-relation) | İşçilerin ücret veya kıdem ödemesi alıp almadığı ayrı kanıt gerektiriyor. |
| Demokrat Parti | Altı partinin 28 Kasım 2022’de anayasa değişikliği önerisini tanıttığı toplantıda Demokrat Parti, genel başkanı Gültekin Uysal ile temsil edildi. [Tanıtım kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0412-six-leaders-2022-11-28-presentation-relation) | Haber, tanıtımı belgeliyor. Nihai yasama işlemi ayrı bir aşama. |

## Aynı olayda farklı parti rolleri

İstanbul Sözleşmesi için 3718 sayılı fesih kararı iki parti
bağlamında aynı olay kimliğini kullanıyor. 19 Mart karar günü ve
20 Mart yayımı, 3928 sayılı sonraki kararın belirlediği 1 Temmuz
sona erme gününden ayrı. EMEP’in yayımlanmış itirazı ile TİP’in
Danıştay’da davacı sıfatıyla yürüttüğü süreç farklı eylemler.
Temyizin reddi Danıştay’a ait ve iki parti bağlamında fesih
kararını kimin verdiği ayrıca gösteriliyor. [TİP kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0405-tip-istanbul-sozlesmesi-withdrawal-relation) · [EMEP kartı](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0410-emep-istanbul-sozlesmesi-relation) · [Temyiz sonucu](/work/mg551/gsd-phase04-previews.sgFrq4/gsd-phase04-first-delivery-62742674/releases/9079b7fa5bcb4af29ed4c552e38a5eeb/index.html#comparison-practice-0405-tip-istanbul-sozlesmesi-court-final-relation)

## Doğrulama ve devam kapsamı

Arşiv işi 62742674 ve bağımsız denetim SQLite, veri, dosya özeti
ve iki okuyucu görünümünde geçti. Dokuz partinin kaynak zincirleri
iki görünümde denetlendi. Tarayıcıda 360 ve 1.365 pikselde dosya ve
yerel HTTP üzerindeki dört senaryo doğrulandı. [Denetim kaydı](04-16-checks/first-delivery.json).

Faz 4, kullanıcı tarafından daraltılan ilk teslim kapsamıyla tamamlandı.
Veri arşivi tam tarihsel tarama için `partial` durumunu koruyor.
04-04–15’in devam araştırması açık. İnsan okuyucu kabulü için bu
teslimde bir yanıt kaydedilmedi. Kanonik önceki arşiv ve bu yerel arşiv
ayrı dizinlerde.
