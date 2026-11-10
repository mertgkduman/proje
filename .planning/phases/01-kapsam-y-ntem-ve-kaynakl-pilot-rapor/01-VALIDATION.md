---
phase: "01"
slug: "kapsam-y-ntem-ve-kaynakl-pilot-rapor"
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-11-10"
---

# Faz 1 — Doğrulama stratejisi

Altı plan ve on iki görevin normal yazılım kabul koşulları mevcut ve çalıştırılmış testlere eşlenmiştir. Otomatik kapsam uyumu; kaynak anlamı, tarafsızlık ve 13 uç varsayımı/dört prohibition için insan onayı değildir. Bu manuel maddeler açık kalır.

## Test Infrastructure

| Özellik | Değer |
|---|---|
| Framework | Python standart kitaplığı `unittest` |
| Yapılandırma | 01-01-01 tracer içinde Wave 0: `tests/run.py`, gerçek kaynak capture'ı, geçici yerel fixture ve scratch DB |
| Hızlı komut | `python3 tests/run.py --pattern test_tracer.py` (her görevde aşağıdaki hedefli pattern kullanılır) |
| Tam paket | `python3 tests/run.py`; ardından `python3 src/arsiv.py audit --release current --phase 1` (son komut 01-06-02'de genişler) |
| Sıfır-test kapısı | Runner `unittest` keşfi 0 ise çıkış 2; test hatası çıkış 1; başarı `TESTS_OK count=N`. Atlanan tarayıcı başarı sayılmaz. |
| Süre hedefi | Tam paket 44 test: 32,275 sn (<60 sn); hızlı komutun bağımsız son süresi ölçülmedi |

## Sampling Rate

- Her görev commit'inden önce hedefli test; yeni test ilgili görevin ilk adımıdır. Ortak runner/scratch/browser altyapısının sahibi 01-01-01'dir; ayrı yatay scaffold görevi yoktur.
- Her plan dalgasından sonra `python3 tests/run.py` ve `python3 src/arsiv.py audit --release current`; çıkış 0 ve TESTS_OK/AUDIT_OK gerekir. Son dalgada `--phase 1` ve PHASE1_AUDIT_OK gerekir.
- `$gsd-verify-work` öncesi tam paket yeşil olmalıdır; önemli pasajların, tarafsızlığın ve gerçek okuma davranışının insan incelemesi bu UAT akışında yapılır.
- Sıfır test, çalıştırılmamış test veya eksik tarayıcı kontrolü başarı değildir.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---|---|---|---|---|---|---|---|---|---|
| 01-01-01 | 01-01 | 1 (Wave 0 içerir) | KAY-02, KAY-03, MET-01–03, VER-01 | T-01-01, T-01-03 | Gerçek arşiv/hash, write-close-reopen, güvenli kaynak tıklama | Integration/browser | `python3 tests/run.py --pattern test_tracer.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-01-02 | 01-01 | 1 | KAY-03, VER-01 | T-01-02, T-01-04 | Tek-yazıcı/staging/pointer, traversal reddi, hata kurtarma | Integration | `python3 tests/run.py --pattern test_publication.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-02-01 | 01-02 | 2 | KAPS-01–03, KAY-02, KAY-03, VER-01 | T-02-01, T-02-02 | Dokuz ad, dışlama, registry/üye/grup ayrımı | Contract/data | `python3 tests/run.py --pattern test_scope.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-02-02 | 01-02 | 2 | KAPS-04, KAY-02, VER-01 | T-02-02, T-02-03 | Ayrı tarih ve yeniden üretilebilir kesim | Contract | `python3 tests/run.py --pattern test_dates.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-03-01 | 01-03 | 3 | KAPS-04, KAY-02, VER-01 | T-03-01, T-03-03 | Döngü/yeni sürüm, pending kapanma reddi ve reopen | State/integration | `python3 tests/run.py --pattern test_chain.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-03-02 | 01-03 | 3 | EKS-01, EKS-02, VER-01 | T-03-02 | Girişim/tür/parti/konu uyumu; not_researched ayrı | Contract/data | `python3 tests/run.py --pattern test_missing.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-04-01 | 01-04 | 4 | KAY-02, KAY-03, MET-01–04, EKS-01, EKS-02, VER-01 | T-04-01, T-04-02 | Belge otoritesi, sürüm/hash ve gerçek pasaj | Contract/data | `python3 tests/run.py --pattern test_documents.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-04-02 | 01-04 | 4 | KAPS-04, KAY-02, VER-01 | T-04-03 | Konu dayanağı ve sürüm, aday/doğrulanmış ayrımı | Contract/data | `python3 tests/run.py --pattern test_topics.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-05-01 | 01-05 | 5 | KAPS-04, KAY-02, MET-01–04, EKS-01, EKS-02, VER-01 | T-05-01–T-05-03 | Aktör/oluş kanıtı; bütün uygun kayıtların küme eşitliği | Contract/data | `python3 tests/run.py --pattern test_matches.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-05-02 | 01-05 | 5 | KAY-02, KAY-03, MET-01–04, EKS-01, EKS-02, VER-01 | T-05-01, T-05-03 | Güncel tüzel kimlik, gerçek dönem/kapsam, NULL/0 | Contract/data | `python3 tests/run.py --pattern test_finance.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-06-01 | 01-06 | 6 | KAY-02, KAY-03, MET-01–04, EKS-01, EKS-02 | T-06-01, T-06-03 | Güvenli DOM/URL/yol, hash/geri/fokus ve offline arşiv | Integration/browser | `python3 tests/run.py --pattern test_report.py` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |
| 01-06-02 | 01-06 | 6 | Faz 1'in 13 gereksinimi | T-06-02; bütün high tehditler | Gerçek release/FK/hash/kanıt/export eşitliği | Acceptance/data | `python3 tests/run.py --pattern test_acceptance.py`; `python3 src/arsiv.py audit --release current --phase 1` | Evet; ilgili test dosyası mevcut | COVERED — tam pakette geçti |

Her hedefli komutun failing direction'ı: sıfır olmayan çıkış, sıfır test veya TESTS_OK count= yokluğu. Faz audit'i sıfır olmayan çıkış veya PHASE1_AUDIT_OK yokluğunda başarısızdır. Bütün PLAN görevlerinde `<automated>` öğesinin hemen ardından `<fails_when>` vardır. Yalnız planlama yapısal kontrolü bu testlerin çalıştırılması sayılmaz.

## Wave 0 Requirements

- [x] 01-01-01: `tests/run.py` sıfır keşfi reddeder, hedef pattern ve tam discovery çalışır; test verileri geçici dizinde kalır.
- [x] 01-01-01: gerçek capture ve yerel scratch DB yazma–kapatma–yeniden okuma düzeneği.
- [x] 01-01-01: `tests/test_tracer.py`, kaynak/pasaj/hash ve yerel HTML/arşiv bağlantısı denetimi.
- [x] 01-01-01: `tests/browser_probe.py`, paket kurmadan tarayıcı keşfi ve gerçek citation.click(); tarayıcı bulunamaması başarı değildir.
- [x] Sonraki 11 görev: kendi adlandırılmış test dosyasını verify'dan önce yaratır; ortak runner 01-01-01 bağımlılığıyla hazırdır. Test dosyası yaratılmadan verify geçemez.

## Manual-Only Verifications

| Davranış | Gereksinim | Neden insan incelemesi | Adımlar |
|---|---|---|---|
| Alıntı/özet/pasaj doğruluğu | KAY-02, MET-01–04 | Metnin kaynak sınırını aşması salt şemayla anlaşılamaz | Her önemli bulguyu özgün pasajla karşılaştır; alıntıyı ve özetin anlamını kontrol et |
| Kapsam, kimlik, tarafsız yöntem | KAPS-01–04 | Hukuki kimlik ve aktör bağlamı yargı gerektirir | Arşiv TBMM/Yargıtay kayıtlarını aç; ad/grup/üyelik ve dışlama gerekçelerini karşılaştır |
| Okunabilirlik ve kaynak etkileşimi | MET-01–03, KAY-03, EKS-02 | DOM kontrolleri gerçek okuma incelemesini tamamlamaz | Kaynak bağlantısı, geri/fokus, klavye, dar ekran ve çevrimdışı arşivi dene; özet ve alıntıyı birlikte gör |
| Belgesiz niyet ve uç varsayımları | Bütün 13 gereksinim | Edge motoru 13 satırı unclassified/unresolved bıraktı; dört prohibition descriptor-less ve flagged-unverified | COVERAGE.md'deki her flagged satırı ve 01-06 must_haves.prohibitions maddelerini incele; test yeşiliyle otomatik resolved verme |

## Validation Sign-Off

- [x] Her görevde planlanmış `<automated>` + hemen sonra `<fails_when>` ve test sahipliği var.
- [x] Üç ardışık doğrulamasız görev yok; 12/12 görev hedefli kontrolde örnekleniyor.
- [x] Wave 0 ortak altyapıyı; her sonraki görev kendi yeni test yolunu açıkça sahipleniyor.
- [x] Watch kipinde veya sınırsız test komutu yok; unittest sonlu çalışıyor.
- [x] Son görev eşlemesi ve tehdit referansları altı planla eşit.
- [x] Tam paket gecikmesi son çalışmada 32,275 sn ölçüldü; hızlı kontrolün son bağımsız süresi ayrıca ölçülmedi.
- [x] Gerçek otomatik testlerden sonra mekanik kapsam için `nyquist_compliant` ve `wave_0_complete` güncellendi; insan incelemesi ayrı ve bekliyor.

**Automated approval:** validated — 12/12 görev, 13/13 normal gereksinim koşulu için test yolu var.

**Human approval:** pending — Manual-Only tablosu, 13 unresolved uç ve dört flagged-unverified prohibition değişmedi. İlk 01-01 tracer için kullanıcının önceki onayı diğer bu maddelere aktarılmadı.

## Validation Audit 2026-11-10T17:26:03.391023+00:00

| Ölçüt | Sonuç |
|---|---|
| Otomatik eşlemesi eksik görev | 0 / 12 |
| Otomatik normal kabul koşulu olmayan gereksinim | 0 / 13 |
| Son tam paket | TESTS_OK count=44; 32,275 sn |
| Gerçek sürüm kabulü | PHASE1_AUDIT_OK 6fd06aa1a6c643ed99b2b1c95f32822d |
| Kod incelemesi sonrası regresyonlar | Kimlik, belge sahipliği, aynı/değişen hash, mali sayı biçimi, atomik yayın ve aday çözümü testleri |
| İnsan/probe yargıları | 13 uç ve 4 prohibition açık; kaynak/UI/tarafsızlık incelemesi bekliyor |

Test dosyaları ve test adları, görev komutları ile çapraz kontrol edildi. Yeni otomatik test açığı bulunmadığından validate-phase adım 3→6 kısa yolu kullanıldı; ek Nyquist denetçisi veya yapay kapsama testi üretilmedi. Süre sonucu kaynak doğruluğunun insan onayı sayılmaz.

## UI repair verification 2026-11-10T17:35:20.374044+00:00

UI-FIX ve 3e4f7ad commitinden sonra tam paket: TESTS_OK count=44; 34,546 sn. PHASE1_AUDIT_OK 7b69e39259214749b36bd655e60c7e66. Kapsam/girişim hash bağlantısı, viewport meta ve Türkçe okuyucu etiketleri gerçek Chromium file/loopback probuyla kontrol edildi. Dar/geniş ekran görüntüleri masaüstü pencereleridir; gerçek mobil ve insan erişilebilirliği incelemesi bekliyor.
