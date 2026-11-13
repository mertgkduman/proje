---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "06"
subsystem: kaynakli-karsilastirma
tags: [iyi-parti, tuzuk, program, semantik-inceleme]
requires:
  - phase: 03-05
    provides: Denetlenmiş ortak konu sözlüğü ve önceki yerel karşılaştırma sürümü
provides:
  - İYİ Parti'nin iki değişiklik notlu tüzüğünün kaynaklı organ ve konu karşılaştırması
  - İYİ Parti'nin erişilebilir tam HTML programının ortak konulara ve incelenmiş kapsamlara ayrılması
affects: [03-14, 03-15, 03-16]
actuals:
  tokens: 11218527
  tasks: 2
  commits: 2
plan_head_before: b34dbbf626bcf48086ed0b5fc79e0d4dcff1b14b
tech-stack:
  added: []
  patterns: [degismez-yerel-yayin, kaynakli-degisiklik-tarihcesi, sinirli-inceleme-kapsami]
key-files:
  created:
    - data/comparisons/03-iyi-charter.json
    - data/comparisons/03-iyi-semantic.json
    - data/comparisons/03-iyi-program.json
  modified:
    - data/current.json
key-decisions:
  - "2020 ve 2026 kapaklarındaki değişiklik notları her hükmün ayrı yürürlük tarihi sayılmadı."
  - "Kayıt iptali ve yeniden yazım, disiplin yoluyla üyelikten çıkarmayla özdeşleştirilmedi."
  - "Alınamayan PDF biçimi, erişilmiş tam HTML programın yokluğu olarak gösterilmedi."
requirements-completed: []
requirements-addressed: [TUZ-01, TUZ-02, TUZ-03, TUZ-04, PRG-01, KAR-01, KAR-02, RAP-02]
duration: 95min
started: 2026-11-13T18:23:52Z
completed: 2026-11-13
status: complete
---

# Phase 03 Plan 06: İYİ Parti Tüzük ve Program Karşılaştırması Özeti

**İYİ Parti'nin iki tüzük nüshası ve tam HTML programı, kaynak pasajları, açıklamalı değişiklikler ve soru sınırı belirtilmiş incelemelerle iki yerel rapor görünümüne işlendi.**

## Teslimler ve kaynak kapsamı

- 2020 değişiklik notlu `0205-iyi-charter-istanbul-v1` ile 2026 değişiklik notlu `0205-iyi-charter-download-v1` tüzüklerinin 1–91. maddeleri ve geçici hükümleri incelendi. Paket 166 ortak tüzük konusu, 249 satır, 213 kaynaklı alan, 37 somut kapsam ve 66 iki pasajlı tarihçe kaydı içerir. Mevcut 48. madde tracer pasajları ve tarihçesi yeniden kullanıldı. 343 pasajın kaynak eşleşmesi kontrol edildi; metin katmanının sözcük sırasını bozduğu basılı 46. sayfadaki bir pasaj ayrıca görsel olarak doğrulandı.
- 2020 m.3 toplu üyelikten çıkarma veya toplu disipline sevk yasağı ile 2026 m.8 gerekçeli kayıt iptali ve yeniden yazım yetkisi kendi kapsamlarında karşılaştırıldı. Yeni hükümde eşitlik ve demokrasi esasları, kanun ve tüzüğe aykırı olmayan neden ve gerekçe koşulları korundu; kayıt işlemi disiplinle ihraç olarak adlandırılmadı. Belge değişiklik notları tekil hükümlerin kesin hukuki yürürlük tarihi olarak sunulmadı.
- Tüzük sürümü `8916515f456d479e8b55011533c22db1`, rapor `data/releases/8916515f456d479e8b55011533c22db1/index.html`, görev commiti `e2402de`.
- Tam HTML programı `0205-iyi-program-page-v1` sekiz bölümde incelendi; 135 ortak program konusu, 157 birebir kaynak pasajı, 157 program alanı ve 39 somut soru/sürüm kapsamı üretildi. Ayrıca eski il disiplin yer tutucusu önceki tüzük bulgusuna bağlandı. Programın PDF aktarımına erişilememesi `0205-iyi-missing-program-pdf` kaydında biçime özgü kalır; HTML içerik eksik sayılmadı. Programın bilinmeyen kabul tarihi uydurulmadı.
- Önceki demokrasi, temel yurttaşlık geliri ve il disiplin kurulu `not_researched` kayıtları aynı kimliklerle gerçek kanıt veya sınırlı kapsam sonucuna yükseltildi. Son çalışma alanında İYİ için araştırılmamış karşılaştırma satırı kalmadı. Program sürümü `a828140c2fb649b5b8d0cef32b42769e`, rapor `data/releases/a828140c2fb649b5b8d0cef32b42769e/index.html`, görev commiti `b0e3ad7`.

## Doğrulama

- Her iki paket `COMPARISON_INPUT_OK` ve ayrı current tabanlı workspace yüklemesinde `COMPARISON_LOAD_OK` verdi. Pasaj eşleşmesi ve 513 alan, kapsam ve tarihçe için ajan semantik kararları ayrı kontrol edildi; bu kararlar bağımsız insan kabulü değildir.
- Tüzük sürümünde `PHASE3_AUDIT_OK 8916515f456d479e8b55011533c22db1`; son sürümde `PHASE3_AUDIT_OK a828140c2fb649b5b8d0cef32b42769e` ve `PHASE2_AUDIT_OK a828140c2fb649b5b8d0cef32b42769e` alındı. Son manifestte Faz 2 `phase2_delivery` önceki `6090bfda16a14ce99a1b6c9d3ff47d71` ile eşittir.
- Tüzük paketindeki 249 ve program paketindeki 175 etkin satırın iki görünümdeki kimlik ve karşılıklı bağlantıları kontrol edildi. Alanlarda sırasıyla 852 ve 632 kaynak başvurusu doğrulandı; tüzük değişikliklerinin eski ve yeni kaynak hedefleri iki görünümde kontrol edildi.
- Önceki planda doğrulanan 124 testlik kod tabanı bu veri planında değiştirilmedi. Burada paket, kaynak, anlam, rapor bağlantısı, yayın ve belirtilen audit kontrolleri yapıldı. Sürümler yereldir.
- `actuals.tokens`, plan başlangıcından iki görev commitine ölçülen 44.874.109 karakterlik git farkının dörde bölünmesidir; model token tüketimi değildir. Başlangıç zamanı ve plan öncesi HEAD yürütme defterinden alınmıştır.

## 03-14, 03-15 ve 03-16 aktarımı

- Kayıtların gerekçeli iptali ve yeniden yazımı ile 24–60 aylıkları kapsayan erken çocukluk bakım ve eğitim programı, kaynaklı yeni konu adayları olarak 03-14 tüm parti geri tarama kuyruğuna kaydedildi.
- Renderer 17 kapsam satırlarında inceleme sürümü ve somut soruyu tek başına göstermediğinden, kaynaklı bağlam satırı bunları görünür açıklamada korur. Satır içi sunum ve tüm faz kabulü 03-15/03-16 kapsamındadır.
- Sekiz ortak gereksinim bu planla ele alındı; diğer parti planları, geri tarama ve son faz doğrulaması tamamlanana kadar tamamlanmış işaretlenmez.

## Sapmalar ve sorunlar

Mimari, şema veya üretici kodu değiştirilmedi. PDF erişim sınırı mevcut gerçek araştırma kaydına bağlıdır; kapsamda açık ifade bulunmaması yalnız belirtilen kaynak sürümü ve somut soruyla sınırlıdır.

## Self-Check: PASSED

Üç paket, iki yerel rapor ve iki görev commiti doğrulandı; iki son audit başarılı ve yazıcı kilidi serbesttir.
