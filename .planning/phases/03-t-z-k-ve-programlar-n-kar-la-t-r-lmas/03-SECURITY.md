---
phase: "03"
slug: "t-z-k-ve-programlar-n-kar-la-t-r-lmas"
status: verified
threats_open: 0
asvs_level: 1
created: "2026-11-15T20:06:18.545669+00:00"
---

# Faz 03 — Güvenlik

Plan zamanında yazılmış 51 tehdit, bağımsız kod incelemesinin güncel kanıtlarıyla eşleştirildi. ASVS L1 ve `high` engelleme eşiğinde açık tehdit yoktur. Güvenlik doğrulaması, insan içerik kabulü değildir.

## Trust Boundaries

| Sınır | Açıklama | Aktarılan veri |
|---|---|---|
| Dış kaynak → yerel kayıt | Parti/sürüm/pasaj, sahiplik, kaynak türü ve açık atıf denetlenir; kaynak talimatları çalıştırılmaz. | Kaynak metni, belge ve kanıt |
| SQLite çalışma alanı → kapalı yayın | Tek yerel yazıcı, transaction/yedek, kaynaklı değişiklik geçmişi ve denetimli atomik işaretçi. | Kayıtlar, sürüm, manifest |
| Kayıt → HTML/arşiv | Escape, URL/path denetimi, pasif yerel arşiv ve etkin/tarihsel görünüm ayrımı. | Okur metni ve kaynak bağlantıları |

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation | Status |
|---|---|---|---|---|---|---|
| T-03-01 | Tampering | comparison alanı/kanıt | high | mitigate | Aynı parti, sürüm, konu ve alan doğrulaması yazma/export/audit'te ortak; yanlış sahiplik testi. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:47` | closed |
| T-03-02 | Tampering | renderer15/migration/publish | high | mitigate | Renderer15'i önce dondur; transaction/yedek; eski dosya hashleri ve hata-pointer testi. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-03 | Information Disclosure | HTML/URL/path | high | mitigate | Mevcut esc/web_url/safe_path; parametreli SQL ve pasif arşiv, saldırgan metin fixture'ı. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-04 | Denial of Service | kaynak okuma | medium | accept | Mevcut 20MiB kaynak sınırı ve yerel test zaman aşımı korunur; yeni ağ servisi yok. `src/arsiv.py:53`; `src/arsiv.py:329`; `tests/test_comparison_navigation.py:87` | closed |
| T-03-05 | Spoofing | source_role/party | high | mitigate | DEM/DBP ek metni program veya başka tüzel kişilik diye yükleme fixture'ı reddedilir. `src/arsiv.py:1932`; `tests/test_comparison_content.py:719`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:71` | closed |
| T-03-06 | Tampering | hierarchy/scope/state | high | mitigate | Döngü, geçersiz parent, kaynaksız yokluk ve eksik alternatives validate_comparisons'ta reddedilir. `src/arsiv.py:1982`; `tests/test_comparison_content.py:556`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:45` | closed |
| T-03-07 | Tampering | tarihsel renderer | high | mitigate | Her kalıcı yayın sonrası renderer değişikliğinde önce freeze/dispatch/version; eski HTML hash karşılaştırması. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-08 | Information Disclosure | kaynak metni/URL | high | mitigate | Mevcut escape/safe_url/safe_path ve pasif arşiv, yeni alanlarda aynen uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-03-A | Spoofing | parti/sürüm/alan | high | mitigate | Aynı partiye ait version_id ve passage zinciri comparison-check, yükleme ve audit'te doğrulanır. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:47` | closed |
| T-03-03-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-03-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-04-A | Spoofing | HTML/PDF sürümü ve dosya adının tarih sanılması | high | mitigate | HTML/PDF hükümleri kendi version_id'leriyle; belirsiz sıra ana alternatiflerde; dosya adı kabul tarihi olmaz. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:60` | closed |
| T-03-04-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-04-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-05-A | Spoofing | Belirsiz sıranın uydurulması ve kongre metninin bağımsız program yapılması | high | mitigate | uncertain ana alternatifler; supplement türü ve bağımsız program missing bağı korunur. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:59` | closed |
| T-03-05-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-05-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-06-A | Spoofing | parti/sürüm/alan | high | mitigate | Aynı partiye ait version_id ve passage zinciri comparison-check, yükleme ve audit'te doğrulanır. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:47` | closed |
| T-03-06-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-06-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-07-A | Spoofing | Ortak grup/başka parti belgesinin Yeni Yol'a mal edilmesi | high | mitigate | yargitay-331 ayrı kimliği ve source party zinciri; gerçek belge yokluğu tek attempt/missing kanıtıyla ortak konulara bağlı. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:80` | closed |
| T-03-07-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-07-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-08-A | Spoofing | Tarihsel BDP programının güncel bağımsız DBP programı yapılması | high | mitigate | Kaynakla belgelenmiş ad değişikliği ilişkisinin sınırı, historical source_role ve güncel program missing birlikte korunur. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:71` | closed |
| T-03-08-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-08-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-09-A | Spoofing | Birleşik HTML tüzük/programı ve kabul edilmemiş öneri paketi | high | mitigate | Bölüm scope'u, source_role ve kabul durumu ayrı; öneri güncel hüküm yapılmaz. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:72` | closed |
| T-03-09-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-09-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-10-A | Spoofing | parti/sürüm/alan | high | mitigate | Aynı partiye ait version_id ve passage zinciri comparison-check, yükleme ve audit'te doğrulanır. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:47` | closed |
| T-03-10-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-10-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-11-A | Spoofing | parti/sürüm/alan | high | mitigate | Aynı partiye ait version_id ve passage zinciri comparison-check, yükleme ve audit'te doğrulanır. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:47` | closed |
| T-03-11-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-11-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-12-A | Spoofing | DYP/1946 DP/ayrı güncel DYP kimliğinin karışması | high | mitigate | yargitay-3 ve kaynaklı1983/2007 ilişki sınırı; diğer tüzel partilerin metni ayrı kalır. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:78` | closed |
| T-03-12-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-12-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-13-A | Spoofing | parti/sürüm/alan | high | mitigate | Aynı partiye ait version_id ve passage zinciri comparison-check, yükleme ve audit'te doğrulanır. `src/arsiv.py:2004`; `tests/test_comparisons.py:56`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-precheck/source-second-reading.md:47` | closed |
| T-03-13-B | Tampering | scratch/yayın | high | mitigate | Salt okunur tabandan yerel scratch; tek yazıcı; refresh audit; eski prefix/receipt ve baytlar korunur. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-13-C | Information Disclosure | alıntı/URL/asset | high | mitigate | esc/web_url/safe_path ve policy2 atıf/pasif arşiv yolu bütün yeni alanlara uygulanır. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-14-A | Tampering | taxonomy/reconcile | high | mitigate | Tam eşleme, rollback, eski satır ve snapshot koruma testleri; export/audit ortak seçili sürüm. `src/arsiv.py:1547`; `src/arsiv.py:1716`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-fix/taxonomy-synthesis/README.md` | closed |
| T-03-14-B | Spoofing | synthesis_evidence | high | mitigate | Her karşılaştırılan tarafın gerçek pasajı; sahte çok-partili kanıtı validate_comparisons reddeder. `src/arsiv.py:1740`; `tests/test_completion_coverage.py:343`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-fix/synthesis-chain/README.md` | closed |
| T-03-14-C | Information Disclosure | HTML/URL/SQL | high | mitigate | Mevcut escape/safe_path ve parametreli sorgular yeni eşleme/sentez alanlarında korunur. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-15-A | Tampering | HTML/hash/URL | high | mitigate | Mevcut esc/web_url/safe_path; kaçışlı/geçersiz hash ve saldırgan metin fixture'ı. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |
| T-03-15-B | Tampering | tarihsel renderer/stil | high | mitigate | Önce17 freeze+dispatch; yeni CSS18; önceki HTML/hash yeniden üretimi. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-15-C | Denial of Service | tarayıcı testi | medium | mitigate | Yerel fixture, alt süreç zaman sınırı ve gerçek hata; Chromium yokluğunu skip saymama. `tests/test_comparison_navigation.py:83`; `tests/test_comparison_navigation.py:126`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/navigation-evidence.json` | closed |
| T-03-16-A | Tampering | complete validation | high | mitigate | Her açık substantive hücre ve eksik kapsam için olumsuz test; tek shared validate_phase_three. `src/arsiv.py:1474`; `tests/test_completion_coverage.py:178`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-fix/second-review-green/README.md` | closed |
| T-03-16-B | Repudiation | review/acceptance/probe kayıtları | high | mitigate | Gerçek reviewer_kind/tarih/gerekçe/release; ham tanılar korunur, sahte insan pass yazılmaz. `src/arsiv.py:984`; `tests/test_completion_coverage.py:216`; `data/comparisons/03-probe-record.json` | closed |
| T-03-16-C | Tampering | history/source/receipts | high | mitigate | Başlangıç hash karşılaştırması, sürüme bağlı yeniden üretim, phase2/prefix kontrolü. `src/arsiv.py:3155`; `tests/test_audit_memory.py:44`; `.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-16-checks/completion-v2-memory/STATUS.md` | closed |
| T-03-16-D | Information Disclosure | kaynak/HTML/yerel yol | high | mitigate | Mevcut parametreli SQL, esc/web_url/safe_path ve pasif arşiv korunur; yeni dış servis yok. `src/arsiv.py:220`; `tests/test_publication.py:108`; `src/arsiv_gorunum.py:150` | closed |

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---|---|---|---|---|
| R-03-01 | T-03-04 | Mevcut 20 MiB kaynak sınırı ve yerel test zaman aşımıyla sınırlı kaynak okuma; yeni ağ servisi yok. | 03-01-PLAN.md içindeki önceden kabul edilmiş `accept` kararı; bu denetimde yeni kabul yok. | Plan kaydı |

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|---|---|---|---|---|
| 2026-11-15T20:06:18.545669+00:00 | 51 | 51 | 0 | GSD root; bağımsız code-review kanıtlarıyla ASVS L1 sınıflandırması |

Planların tümündeki tehdit kimlikleri kayıtla bire bir eşleşti; kanıt dosyaları ve satırları mevcut. SUMMARY dosyalarında ayrı yapılandırılmış `Threat Flags` bölümü yoktur. L1 kısa yolu uygulandı: plan zamanında yazılmış kayıt + 0 açık tehdit; ek güvenlik ajanı gerekli değildir.

Kaynak kodu inceleme sınırı `6ef0b5d`; temiz bağımsız rapor `62f7b09` kaydındadır. Son kaynaklı geçişlerin gerçek API yayını ve genel regresyonu bu rapor yazılırken sürmektedir; onların sonucu ayrıca kabul dosyasına eklenecektir. Önceki `554db20` çalışması yeni kodun kanıtı sayılmamıştır. Tam taxonomy 5 import/yayın/audit bu kapıda kanıtlanmış sayılmaz.

## Sign-Off

- [x] Bütün tehditlerin disposition kaydı var.
- [x] Önceden kabul edilmiş risk açıkça kaydedildi.
- [x] `threats_open: 0` doğrulandı.
- [x] `status: verified` ayarlandı.

**Approval:** verified 2026-11-15T20:06:18.545669+00:00 — ASVS L1 teknik güvenlik kapısı.

## Bellek düzeltmesi sonrası devamlılık

`7ea9376` tarihsel denetimleri önce çalıştırarak çağrı zincirinde tutulan tam snapshot sayısını sınırlar; hiçbir tehdit önlemi kaldırılmaz. Gerçek 53 sürümlük adayın denetimi 891.893 saniyede, 1,297,632 KiB tepe RSS ile 4 GiB adres alanı sınırında geçti. Dört dosya, işaretçi ve 2.251 ilk girdi değişmedi. Kaynak ve test değişikliklerinin bağımsız artımlı incelemesi temizdir; 51 tehdit için açık sayısı yine 0. Genel regresyon ve üretim v2 kabulü henüz bekleniyor. Ayrıntı: `03-16-checks/completion-v2-memory/STATUS.md`.


## Root final publication continuity — 2026-11-16T04:29:51.226758+00:00

Final local release `3a3021c8e81749c3834462d1a0d81231` passed ordinary/P2/P3 complete audits. Product source is unchanged from the reviewed memory fix; 202 pre-production tests and 91 actual-current focused tests across documented epochs passed. The later navigation change affects test-fixture construction only and has an independent clean review and four passing current-release tests. No new risk acceptance is implied; all 51 planned threats remain closed. See `03-16-checks/root-final-continuity.json` and `completion-v2-final/STATUS.md`.
