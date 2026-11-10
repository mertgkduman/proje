---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
plan: "02"
subsystem: kapsam-ve-yontem
tags: [tbmm, yargitay, sqlite, kapsam, kesim]
requires: [01-01]
provides: [tarihli-kapsam, kimlik-ve-grup-ayrimi, dondurulmus-kesim]
affects: [01-03, 01-04, 01-05, 01-06]
tech-stack:
  added: []
  patterns: [surumlu-snapshot, kaynak-yabanci-anahtari, utc-kesim]
key-files:
  created: [tests/test_scope.py, tests/test_dates.py]
  modified: [src/arsiv.py, src/rapor.py, tests/browser_probe.py, README.md, data/current.json]
key-decisions:
  - "İlk doğrulanmış TBMM kapsam yakalamasının UTC erişim anı, kullanıcı seçimi olarak gösterilmeden ilk yöntem kesimidir."
  - "Onaylı kapsam, tarihli TBMM gözlemleri, parti kimliği, bireysel üyelik ve Meclis grubu ayrı kayıtlardır."
status: complete
completed: 2026-11-10
duration: "yaklaşık 18 dakika"
plan_head_before: 5240a86f4c5092e15a8698f13ab9662b46378c6a
actuals:
  tokens: 1111777
  tasks: 2
  commits: 4
---

# Phase 1 Plan 2: Kapsam ve yöntem özeti

Kullanıcının onayladığı dokuz partilik liste ve yedi dışlama kararı, TBMM'nin tarihli sandalye gözlemleri ile ayrı tutuldu; Yeni Parti pilotunun kesimi, gerçek TBMM arşiv nesnesinin erişim anına bağlandı.

## Kaynak ve dönem

- TBMM sandalye dağılımı: https://tbmm.gov.tr/sandalyedagilimi ; yakalama `2026-11-10T14:38:46.154751+00:00`, SHA-256 `2fc162c6e7fd3735bfcdaf6f1af89016419c51bffbabe5a9b433d3218e37de3a`. Dokuz ad tabloda bulundu; sayfanın kendi güncelleme tarihi bilinmiyor. Bu erişim anı ilk yöntem kesimidir.
- Yeni Parti için 01-01'deki https://www.yargitaycb.gov.tr/sipar/365 kaydı ve 24.07.2026 kuruluş pasajı kullanıldı. Diğer partilere verilen `tbmm-` anahtarları TBMM gözlem kimlikleridir; bağımsız Yargıtay sicil doğrulaması sayılmamalıdır.
- TBMM'nin bireysel konuşma listesinde Mehmet Emin Ekmen için 25.12.2024 tarihli Saadet parti satırı ve Yeni Yol listesinde Bülent Kaya için grup görevi ayrı kaynak ilişkileri olarak saklandı. Belirli bir tarihli parti kaydı genel ve süresiz üyelik iddiası değildir. Grup adı bireysel üyelikten çıkarılmaz.
- 2023 tarihi için [Anadolu Ajansı](https://www.aa.com.tr/tr/gundem/secimde-13-siyasi-parti-tek-basina-digerleri-ittifak-catisinda-yarisacak/2868155) kopyası destek/ortak liste ile ittifakı ayırır. [YSK 2023 faaliyet raporunun](https://www.ysk.gov.tr/doc/dosyalar/docs/Faaliyet_Raporlari/2023_Yili_Faaliyet_Raporu.pdf) 76. PDF sayfasındaki protokol açıklaması ayrıca okundu. PDF henüz arşive ve pasaj kaydına bağlanmadı; bu birincil kaynak zincirinin tamamlanması takip edilmelidir.
- `7f06c8880dde4093ab6db4b16c75fc1f` güncel yerel release'tir. Kuruluş günü ve kesin kesim anı dahildir; yalnız günü bilinen kesim günü olayı belirsizdir. Belge, olay, hesap dönemi, erişim ve doğrulama alanları ayrıdır.

## Doğrulama

- `python3 tests/run.py --pattern test_scope.py`: 3 test; `python3 tests/run.py --pattern test_dates.py`: 1 test.
- `python3 tests/run.py`: 14 test ve `TESTS_OK`; gerçek Chromium kaynak bağlantısı kontrolü dahil.
- `python3 src/arsiv.py audit --release current`: `AUDIT_OK`; önceki dört release de ayrıca denetlendi.
- Planın TBMM/Yargıtay kopyalarını ve grup/üyelik ayrımını insanın incelemesi, `human_verify_mode: end-of-phase` gereği faz sonu kontrolü için bekliyor; insan onayı alınmış gibi sayılmadı.

## Görevler ve commitler

1. Kapsam ve kimlikler: RED `bc3abcc`, GREEN `67bfec0`.
2. Kesim ve tarihler: RED `5137372`, GREEN `a67bacb`.

## Plandan sapmalar ve sınırlamalar

**[Rule 1 - Hata] Tarayıcı testi kaynak bağlantısının sıraya bağlı seçimini kullandı.** Yeni kapsam bağlantıları ilk sırayı alınca eski test yanlış kaynağa tıkladı. `tests/browser_probe.py` kuruluş kaydını kimliğiyle seçer; 14 test tekrar geçti.

**Birincil kaynak zinciri:** YSK faaliyet raporu okunmuş ancak PDF arşiv/pasaj zincirine bağlanmamıştır. AA tarihsel açıklaması güncel ittifak ortaklığı olarak sunulmaz; YSK belgesi bağımsız arşivlenip ilişkilendirilene kadar bu uç açık kalır.

**Teknik sınır:** Olay tarihi doğrulaması şu an yalnız kaynakla doğrulanmış Yeni Parti kuruluş tarihini uygular; diğer partiler için kuruluş tarihi doğrulanana kadar olay kaydı reddedilir. Kapsam gözlemi ile kaynağın anlamsal uygunluğu otomatik yabancı anahtar kontrolüne ek olarak faz sonunda insan incelemesi gerektirir.

Ölçülen token değeri, Git metin diff uzunluğunun dörde bölünmesidir; arşivlenmiş HTML bu değerin büyük kısmını oluşturur. İkili SQLite diff içeriği dahil değildir.

## Self-Check: PASSED

İki test dosyası, kaynak dosyaları, dört görev commiti ve yerel release mevcuttur; 14 test ve release denetimleri geçmiştir.
