---
phase: "01"
slug: "kapsam-y-ntem-ve-kaynakl-pilot-rapor"
status: verified
threats_open: 0
asvs_level: 1
block_on: high
register_authored_at_plan_time: true
created: "2026-11-10T17:24:57.392381+00:00"
---

# Faz 1 — Güvenlik incelemesi

## Trust Boundaries

Dış belge → değişmez arşiv → yerel SQLite scratch → kapalı snapshot → JSON/HTML → okur; loopback sunucusu yalnız yayımlanmış yerel release/objects yollarını sunar. Kamuya yayın yoktur.

## Threat Register

| Threat ID | Category | Component | Severity | Disposition | Mitigation evidence | Status |
|---|---|---|---|---|---|---|
| T-01-01 | Tampering | capture_source/render_report | high | mitigate | src/arsiv.py:93; src/rapor.py:6; tests/test_report.py | closed |
| T-01-02 | Tampering | publish_release | high | mitigate | src/arsiv.py:714; src/arsiv.py:880; tests/test_publication.py | closed |
| T-01-03 | Denial of Service | capture_source | medium | mitigate | src/arsiv.py:185 (30 s timeout, 20 MiB sınırı) | closed |
| T-01-04 | Tampering | yerel dosya yolları/serve | high | mitigate | src/arsiv.py:100; tests/test_publication.py | closed |
| T-02-01 | Spoofing | record_identity | high | mitigate | src/arsiv.py:113; tests/test_scope.py; 0fd27e1 | closed |
| T-02-02 | Tampering | record_scope/freeze_cutoff | high | mitigate | src/arsiv.py:687; tests/test_scope.py; tests/test_dates.py | closed |
| T-02-03 | Repudiation | dönem ve kaynak gözlemi | medium | mitigate | src/arsiv.py:666; tests/test_dates.py | closed |
| T-03-01 | Denial of Service | enqueue_lead/close_topic | medium | mitigate | src/arsiv.py:368; src/arsiv.py:558; tests/test_chain.py | closed |
| T-03-02 | Repudiation | record_attempt/record_missing | high | mitigate | src/arsiv.py:404; src/arsiv.py:643; tests/test_missing.py | closed |
| T-03-03 | Tampering | belge sürümü | high | mitigate | src/arsiv.py:329; tests/test_chain.py; 3df7994 | closed |
| T-04-01 | Spoofing | verify_document_authority | high | mitigate | src/arsiv.py:437; tests/test_documents.py; tests/test_topics.py | closed |
| T-04-02 | Tampering | validate_evidence | high | mitigate | src/arsiv.py:550; src/arsiv.py:742; tests/test_documents.py | closed |
| T-04-03 | Repudiation | topic_basis/verification | medium | mitigate | src/arsiv.py:441; tests/test_topics.py | closed |
| T-05-01 | Spoofing | actor/record_financial | high | mitigate | src/arsiv.py:448; src/arsiv.py:585; tests/test_matches.py; tests/test_finance.py | closed |
| T-05-02 | Tampering | record_match/render_report | high | mitigate | src/arsiv.py:779; tests/test_matches.py | closed |
| T-05-03 | Repudiation | occurrence/financial evidence | high | mitigate | src/arsiv.py:448; src/arsiv.py:585; tests/test_finance.py; 5d159b8 | closed |
| T-06-01 | Tampering | render_report/kaynak bağlantısı | high | mitigate | src/rapor.py:6; tests/test_report.py | closed |
| T-06-02 | Tampering | validate_phase_one | high | mitigate | src/arsiv.py:815; src/arsiv.py:880; tests/test_acceptance.py | closed |
| T-06-03 | Information Disclosure | serve/arşiv | medium | mitigate | src/arsiv.py:978; tests/test_acceptance.py; tests/test_publication.py | closed |

## İnceleme yöntemi ve sınırları

Plan aşamasında yazılmış 19 tehdit için ASVS 1 düzeyinde önlem varlığı incelendi. Kaynak/işlev referansları ve ilgili negatif testler eşlendi; bağımsız kod incelemesinin tekrarlanabilir bulguları düzeltildi ve son teyit `01-REVIEW.md` içinde clean olarak kaydedildi. `secure-phase` kısa devre kuralı uyarınca planlanmış kayıt + L1 + sıfır açık eşik tehdidi koşulunda ek derin denetçi çalıştırılmadı. Bu kayıt güvenlik sertifikası veya bütün ağ hata kiplerinin sınanması değildir.

Eski snapshot'lar değişmez; yeni yazma/yayın işlemleri sıkı kimlik ve faz kontrollerini kullanır. Tarihsel sürümlerin daha eski kimlik denetim sınırı README ve REVIEW-FIX içinde korunur. HTML kontrolü kayıt kimliği, güvenli render ve deterministik türev bütünlüğünü denetler; kaynak cümlelerinin maddi anlamını otomatik kanıtlamaz.

Kaynak anlamı, hukuki kimlik/tarih yorumu, mali kapsam ve tarafsızlık insan incelemesi bekler. Yazılım tehdidinin önleminin bulunması bu insan yargılarını çözmüş sayılmaz.

## Accepted Risks Log

Kullanıcı adına kabul edilmiş risk yoktur.

## Security Audit Trail

| Tarih | Toplam | Kapalı | Açık eşik tehdidi | İnceleyen |
|---|---|---|---|---|
| 2026-11-10T17:24:57.392381+00:00 | 19 | 19 | 0 | Orkestratör; bağımsız gsd-code-reviewer kanıtlarıyla |

## Sign-Off

- [x] Her plan tehdidinin disposition ve önlem referansı var.
- [x] Kaynaklı negatif testler ve bağımsız kod düzeltme teyidi kayıtlı.
- [x] ASVS 1 yazılım önlemi kapsamı için threats_open: 0.
- [ ] İnsan kaynak/kimlik/tarafsızlık incelemesi — ayrı UAT kapısı.
