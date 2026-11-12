---
phase: "02"
slug: b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
status: verified
threats_open: 0
threats_total: 42
threats_closed: 42
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-11-12"
---

# Faz 02 — Yazılım güvenliği

Planlarda yazılı 42 tekil tehdit için uygulama ve mevcut kontrol kanıtları bulundu. ASVS 1 ve sıfır açık tehdit nedeniyle secure-phase iş akışının L1 kısa yolu uygulandı; yeni bir geniş tehdit taraması veya kaynak kabul koşulu üretilmedi.

## Güven sınırları

| Sınır | Koruma |
|---|---|
| Dış metin/URL → kayıt | İzlenebilir atıf, doğru parti/pasaj sahipliği; beyanın kaynağa atfı |
| Workspace → değişmez yayın | Transaction, rollback, hash/FK, atomik pointer ve eski sürüm koruması |
| Kayıt/HTML → okur | Metin kaçışı, güvenli yollar, pasif CSP, scriptsiz yerel varlıklar |
| Yayın → teslim | Gerçek sürüm/hash, kesim, sıralı prefix ve bağlı makbuz |

D-13–D-16 uygulanır: alan adı için bağımsız sicil kanıtı, her yayına insan kabulü veya kesin tarihsel yürürlük kanıtı aranmaz. Sicil kimliği kendi kaynağıyla tutarlı kalır; bilinmeyen dönem açıkça belirtilir. Güvenlik sonucu kaynakta yazan siyasi iddianın bağımsız doğruluğu veya insan kabulü anlamına gelmez.

## Tehdit kaydı

| Threat ID | Category | Component | Severity | Disposition | Uygulama/kontrol kanıtı | Status |
|---|---|---|---|---|---|---|
| T-02-01 | Tampering | migrate_workspace/export_db | high | mitigate | src/dosyalar.py:30; test_migration_rollback_and_invalid_records_leave_pointer; 1791 eski dosya korunması | closed |
| T-02-02 | Spoofing | identity_confirmation/dossier_field | high | mitigate | src/dosyalar.py:96; src/kaynaklar.py:77; test_dossiers; test_source_policy | closed |
| T-02-03 | Elevation | render_report/receipt path | high | mitigate | src/rapor.py esc/web_url; src/arsiv.py safe_path; src/arsiv_gorunum.py validate_view; 20 odaklı test ve CR-01 düzeltmesi | closed |
| T-02-04 | Repudiation | phase2_delivery/receipt | medium | mitigate | data/deliveries/02-03-tip.json–02-10-demokrat.json; 02-10-CHECKS.json operations: sekiz son receipt-check exit0 | closed |
| T-02-05 | Denial | source capture | medium | mitigate | src/arsiv.py:216 capture_source: timeout30/MAX_SOURCE; gerçek erişim girişimleri | closed |
| T-02-SC | Tampering | Bağımlılıklar | low | accept | Yeni paket/bağımlılık bildirimi eklenmedi; Python stdlib/SQLite/sistem Poppler; planlarda önceden yazılı sınırlı accept | closed |
| T-02-06 | Tampering | version_relation/version_context | high | mitigate | src/dosyalar.py validate_dossier version_context/version_relation; cycle/period negatifleri | closed |
| T-02-07 | Spoofing | Kart/kronoloji/kimlik notu | high | mitigate | src/dosyalar.py validate_dossier dossier_field/dossier_event/dossier_identity_note; ayrı pasaj sahipliği | closed |
| T-02-08 | Elevation | details/source/history DOM | high | mitigate | src/rapor.py esc/web_url; src/arsiv.py safe_path; src/arsiv_gorunum.py validate_view; 20 odaklı test ve CR-01 düzeltmesi | closed |
| T-02-09 | Repudiation | Sürüm açıklaması | medium | mitigate | src/kaynaklar.py check_evidence_attribution; provenance/epistemic_type; gerekçeli bilinmeyen dönem (D-13) | closed |
| T-02-10 | Spoofing | TİP/site/tüzük ve pilot kart | high | mitigate | src/dosyalar.py:96; src/kaynaklar.py:77; test_dossiers; test_source_policy | closed |
| T-02-11 | Tampering | Versiyon/kesim/makbuz | high | mitigate | src/arsiv.py:775; src/dosyalar.py:75; 02-10-CHECKS.json preservation/operations | closed |
| T-02-12 | Repudiation | Özet/alıntı ve araştırma kaydı | medium | mitigate | Kaynaklı summary/quote çiftleri; gerçek attempt/closure; agent review insan onayı olarak sunulmaz | closed |
| T-02-13 | Denial | Belge edinimi | medium | mitigate | src/arsiv.py capture_source timeout30/20MiB; gerçek başarısız girişimler | closed |
| T-02-04-S | Spoofing | dem kimlik/site | high | mitigate | src/dosyalar.py:96; src/kaynaklar.py:77; test_dossiers; test_source_policy | closed |
| T-02-04-T | Tampering | dem kaynak/sürüm/kesim | high | mitigate | src/arsiv.py:775; src/dosyalar.py:75; 02-10-CHECKS.json preservation/operations | closed |
| T-02-04-E | Elevation | HTML/kaynak yolları | high | mitigate | src/rapor.py esc/web_url; src/arsiv.py safe_path; src/arsiv_gorunum.py validate_view; 20 odaklı test ve CR-01 düzeltmesi | closed |
| T-02-04-R | Repudiation | 02-04-dem.json | medium | mitigate | data/deliveries/02-03-tip.json–02-10-demokrat.json; 02-10-CHECKS.json operations: sekiz son receipt-check exit0 | closed |
| T-02-05-S | Spoofing | iyi kimlik/site | high | mitigate | src/dosyalar.py:96; src/kaynaklar.py:77; test_dossiers; test_source_policy | closed |
| T-02-05-T | Tampering | iyi kaynak/sürüm/kesim | high | mitigate | src/arsiv.py:775; src/dosyalar.py:75; 02-10-CHECKS.json preservation/operations | closed |
| T-02-05-E | Elevation | HTML/kaynak yolları | high | mitigate | src/rapor.py esc/web_url; src/arsiv.py safe_path; src/arsiv_gorunum.py validate_view; 20 odaklı test ve CR-01 düzeltmesi | closed |
| T-02-05-R | Repudiation | 02-05-iyi.json | medium | mitigate | data/deliveries/02-03-tip.json–02-10-demokrat.json; 02-10-CHECKS.json operations: sekiz son receipt-check exit0 | closed |
| T-02-06-S | Spoofing | yeni-yol kimlik/site | high | mitigate | src/dosyalar.py:96; src/kaynaklar.py:77; test_dossiers; test_source_policy | closed |
| T-02-06-T | Tampering | yeni-yol kaynak/sürüm/kesim | high | mitigate | src/arsiv.py:775; src/dosyalar.py:75; 02-10-CHECKS.json preservation/operations | closed |
| T-02-06-E | Elevation | HTML/kaynak yolları | high | mitigate | src/rapor.py esc/web_url; src/arsiv.py safe_path; src/arsiv_gorunum.py validate_view; 20 odaklı test ve CR-01 düzeltmesi | closed |
| T-02-06-R | Repudiation | 02-06-yeni-yol.json | medium | mitigate | data/deliveries/02-03-tip.json–02-10-demokrat.json; 02-10-CHECKS.json operations: sekiz son receipt-check exit0 | closed |
| T-02-07-S | Spoofing | dbp kimlik/site | high | mitigate | src/dosyalar.py:96; src/kaynaklar.py:77; test_dossiers; test_source_policy | closed |
| T-02-07-T | Tampering | dbp kaynak/sürüm/kesim | high | mitigate | src/arsiv.py:775; src/dosyalar.py:75; 02-10-CHECKS.json preservation/operations | closed |
| T-02-07-E | Elevation | HTML/kaynak yolları | high | mitigate | src/rapor.py esc/web_url; src/arsiv.py safe_path; src/arsiv_gorunum.py validate_view; 20 odaklı test ve CR-01 düzeltmesi | closed |
| T-02-07-R | Repudiation | 02-07-dbp.json | medium | mitigate | data/deliveries/02-03-tip.json–02-10-demokrat.json; 02-10-CHECKS.json operations: sekiz son receipt-check exit0 | closed |
| T-02-08-S | Spoofing | emep kimlik/site | high | mitigate | src/dosyalar.py:96; src/kaynaklar.py:77; test_dossiers; test_source_policy | closed |
| T-02-08-T | Tampering | emep kaynak/sürüm/kesim | high | mitigate | src/arsiv.py:775; src/dosyalar.py:75; 02-10-CHECKS.json preservation/operations | closed |
| T-02-08-E | Elevation | HTML/kaynak yolları | high | mitigate | src/rapor.py esc/web_url; src/arsiv.py safe_path; src/arsiv_gorunum.py validate_view; 20 odaklı test ve CR-01 düzeltmesi | closed |
| T-02-08-R | Repudiation | 02-08-emep.json | medium | mitigate | data/deliveries/02-03-tip.json–02-10-demokrat.json; 02-10-CHECKS.json operations: sekiz son receipt-check exit0 | closed |
| T-02-09-S | Spoofing | saadet kimlik/site | high | mitigate | src/dosyalar.py:96; src/kaynaklar.py:77; test_dossiers; test_source_policy | closed |
| T-02-09-T | Tampering | saadet kaynak/sürüm/kesim | high | mitigate | src/arsiv.py:775; src/dosyalar.py:75; 02-10-CHECKS.json preservation/operations | closed |
| T-02-09-E | Elevation | HTML/kaynak yolları | high | mitigate | src/rapor.py esc/web_url; src/arsiv.py safe_path; src/arsiv_gorunum.py validate_view; 20 odaklı test ve CR-01 düzeltmesi | closed |
| T-02-09-R | Repudiation | 02-09-saadet.json | medium | mitigate | data/deliveries/02-03-tip.json–02-10-demokrat.json; 02-10-CHECKS.json operations: sekiz son receipt-check exit0 | closed |
| T-02-10-S | Spoofing | demokrat kimlik/site | high | mitigate | src/dosyalar.py:96; src/kaynaklar.py:77; test_dossiers; test_source_policy | closed |
| T-02-10-T | Tampering | demokrat kaynak/sürüm/kesim | high | mitigate | src/arsiv.py:775; src/dosyalar.py:75; 02-10-CHECKS.json preservation/operations | closed |
| T-02-10-E | Elevation | HTML/kaynak yolları | high | mitigate | src/rapor.py esc/web_url; src/arsiv.py safe_path; src/arsiv_gorunum.py validate_view; 20 odaklı test ve CR-01 düzeltmesi | closed |
| T-02-10-R | Repudiation | 02-10-demokrat.json | medium | mitigate | data/deliveries/02-03-tip.json–02-10-demokrat.json; 02-10-CHECKS.json operations: sekiz son receipt-check exit0 | closed |

## Önceden belgelenmiş risk kararı

| Risk ID | Threat Ref | Gerekçe | Kararın dayanağı | Tarih |
|---|---|---|---|---|
| R-02-SC | T-02-SC | Yeni bağımlılık eklenmedi; mevcut sistem araçları kullanıldı | On planın ortak, önceden yazılı low/accept satırı; yeni genel risk kabulü verilmedi | Plan kayıtları |

## Denetim izi

| Tarih | Tekil tehdit | Kapalı | Açık | Yöntem |
|---|---:|---:|---:|---|
| 2026-11-12 | 42 | 42 | 0 | Root L1 kaynak/kanıt incelemesi; planların tamamı, üretim CHECKS, kod incelemesi ve 20 başarılı odaklı düzeltme testi |

- Plan-time threat_model blokları ve SUMMARY belgeleri okundu; ayrı Threat Flags başlığı bulunmadı.
- 02-10-CHECKS.json dokuz dosyalı PHASE2_AUDIT_OK, PHASE1_AUDIT_OK, sekiz son makbuz kontrolü, 32 test ve önceki 1791 değişmez dosyanın korunmasını kaydeder.
- CR-01 için DNS/IP sabitleme, istek öncesi yönlendirme kontrolü ve özel ağ reddi 15b5e99 ile uygulanıp ağ göndermeyen odaklı testlerde doğrulandı.
- Kod incelemesindeki CR-07/CR-08 sunum künyesi/HTML entity sorunları ve CR-09 eski capture kodlama sınırı ayrıca açık tutulur; bunlar bu kayıt için yeni bir güvenlik kabulü sayılmadı. Yeni üretici 14 yayını bu sorunlar giderilene kadar bekler.
- Tam faz regresyonu bu belgenin yazımı sırasında çalışmaktadır; sonucu bu belgeyle başarılı ilan edilmez. Faz kapanışı ayrıca regresyon ve hedef doğrulamasını bekler.

## Sonuç

- [x] Bütün plan tehditlerinin disposition değeri ve kanıtı var.
- [x] Önceden yazılı sınırlı bağımlılık kararı kaydedildi.
- [x] threats_open: 0 (high/critical açık yok).
- [x] status: verified; ASVS 1 kısa yol koşulları sağlandı.

Teknik doğrulama: 2026-11-12 — kaynak içeriği için insan onayı verilmedi.

## Sonraki doğrulamalar

CR-07 ve CR-08 ikinci turda düzeltildi; 25 arşiv/rapor ve iki ilgili atıf testi geçti. CR-09 yalnız HTTP başlığında kalan UTF-8 dışı charset için açık destek sınırı olarak kaydedildi; çözülemeyen yeni kaynaklar açık hata verir. `353a5ee` tamamlanmış sırayı, parti kimliğini ve aşamayı değiştirmeden yalnız tam teslimin açık --refresh yoluyla yeniden yayımlanmasını sağlar; üç olumlu/olumsuz kontrol ve yeni `1d6b49b307f04a258c1a11d90978fe7c` için PHASE2_AUDIT_OK geçti. Önceki belgeler, kaynak atıfları ve sekiz makbuz değişmedi; yeni açık güvenlik tehdidi veya risk kabulü eklenmedi. Regresyon sonucu 02-REGRESSION.md içinde çözülmüş tek eski beklenti hatasıyla belgelenmiştir.

Son SC3/KAY-01 açıklaması üretici15 (c2415da) ile yalnız kapalı yöntem metnine eklendi. ac4b8fdec02f4a9ebb666036ed251683 resmî yenilemesi mevcut güvenlik sınırlarını ve eski teslim kayıtlarını korur; yeni yetki veya kaynak kabul koşulu eklemez.


## UAT kapanışında kayıt kontrolü — 2026-11-12T04:32:29.265609Z

Planların threat_model tablolarındaki 42 tekil tehdit mevcut güvenlik kaydıyla eşleştirildi: 42/42 closed, threats_open: 0. ASVS 1 ve plan zamanında yazılmış kayıt için kısa yol uygulandı; mevcut somut kod/test kanıtı yeniden kullanıldı. Bu oturumda uygulama, veri veya rapor değişmedi; yalnız kullanıcı UAT sonuçları ve kapanış kayıtları güncelleniyor. Yeni tehdit taraması, test koşusu veya risk kabulü yapılmadı.
