---
phase: 04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas
plan: "03"
subsystem: archive
tags: [coverage, provenance, preview, source-review, merge, sqlite]
requires:
  - phase: 04-02
    provides: Sürümlü uygulama kayıtları ve kaynaklı olay zinciri
provides:
  - Dokuz partilik kanonik kapsam envanteri ve kaynak bağlı arama/kapanış geçmişi
  - İzole kaynak önizlemesi, okuma denetimi ve kökeni korunmuş deterministik olay birleşimi
affects: [04-04, 04-05, 04-06, 04-07, 04-08, 04-09, 04-10, 04-11, 04-12, 04-13, 04-14, 04-15]
tech-stack:
  added: []
  patterns: [append-only kayıtlar, explicit storage root, doğrulanabilir merge provenance]
key-files:
  created: [data/practices/04-inventory.json, data/practices/04-coverage-tracer.json, src/uygulama_birlestirme.py, src/uygulama_merge_kayit.py, tests/test_practice_coverage.py, tests/test_practice_preview.py]
  modified: [src/arsiv.py, src/kaynaklar.py, src/rapor.py, src/uygulamalar.py, tests/test_practice_merge_persistence.py, tests/test_practice_pending_integration.py]
key-decisions:
  - Çeşme eski kapanışı yalnız belgelenmiş dar sorgulara bağlanır; geniş kapsam hücresi açık kalır.
  - Birleşen olayların eski kaynak okumaları yeni genişletilmiş kanıt için otomatik kabul sayılmaz.
  - İzole önizleme aynı standart manifest ve audit sözleşmesini açık kaynak kökleriyle kullanır.
requirements-completed: []
plan_head_before: 3f85e3673447fc5024c6d6f57c7b8d2322616c8f
actuals:
  tokens: 2081368
  tasks: 2
  commits: 65
duration: yaklaşık 82 saat, kesintiler ve beklemeler dahil
completed: 2026-11-21
status: complete
---

# Phase 04 Plan 03: Kapsam ve izole uygulama önizlemesi özeti

**Kaynak bağlı parti-konu kapsamı, kapanış geçmişi ve doğrulanabilir olay birleşimi DB → JSON → HTML önizleme zincirine eklendi.**

## Sonuçlar

- Envanter gerçek seçili konulardan, dokuz partiden ve iki araştırma türünden türetilir; daraltılmış kapsam, sahte yokluk, bekleyen uçla kapanış ve kaynak gelince yeniden açılmanın atlanması reddedilir. Eski Çeşme kaydının dar kapsamı korunur; diğer partiler araştırılmış sayılmaz.
- Açık kaynak kökleri ve yerel SQLite denetimiyle izole preview, özgün/pasif kaynakları, standart manifesti ve bağımsız audit yolunu kullanır. Source-review geçmişi ve sürüm/pasaj kapsamı doğrulanır.
- Public merge; event kararlarını, alias ve provenance kayıtlarını, partiye ait kaynakları ve eski kabul edilmiş kayıtları korur. Genişletilen kanıt için önceki okuma otomatik onay oluşturmaz; pending kalır. CLI'lar `practice-inventory`, `practice-coverage`, `practice-preview`, `practice-merge` ve `practice-source-check` sunar.

## Doğrulama

- 287 benzersiz test kimliği, 64 gerçek sıfır çıkışlı batch ve aynı kaynak/test/yayın kimliğiyle doğrulandı. Olay defteri, gerçek günlükler ve çıkış dosyaları `04-03-checks/fresh-gate-*` ve ilgili `fresh-<batch>` dosyalarında korunur; denetleyici `fresh_slurm_closeout.py` ile yeniden okunabilir. Fingerprint `083475eeaf93e3b034722e3bf702e41598952e29144ce19b376d3cf116bff8e4`.
- Seri Slurm işi 62261875, 286/286 kendi testini geçirdi ve henüz sonuçlanmamış dış ID nedeniyle exit 1 verdi; ayrı 62173687 işi taksonomi testini 10601.023 saniyede exit 0 ile tamamladı. Kesilmiş `fd0afd4c…` denemesine kredi verilmedi.
- 62262262 işi build, gerçek tracer CLI, Faz 2 audit ve Faz 3 complete audit komutlarının tümünü exit 0 ile tamamladı; `PHASE2_AUDIT_OK` ve `PHASE3_AUDIT_OK` kanonik `f67ca0a35e634035bf3aa83a46571f50` için kaydedildi. Gerçek tracer preview `data/.staging/gsd-04-03-tracer-preview-62262262/releases/95a5a7c451f44d20b3d6fc77d1a44f47` altında; DB, JSON, HTML, manifest, iki görünüm ve 13.754 yerel bağlantı denetlendi. Manifest SHA256 `9dfcace69ba9d1e98b1bbee49aaf9f9adc2d9e23ec9bc7a593f0893642c920cd`. Kanıt `04-03-checks/closeout-62262262.json` ve eşleşen komut günlüklerindedir.
- Kanonik pointer, DB, JSON, HTML ve manifest özetleri başlangıçtaki değerlerle eşleşti; yazıcı kilidi yok. Preview geçici teknik teslimdir; kamu yayını, yeni parti araştırması veya insan kaynak incelemesi değildir.

## Görev commitleri ve sapmalar

- Task 1 RED `72bbf93`, uygulama `55bf41f`; gerçek kapsam tracer kapısı 5/5 geçti.
- Task 2, izole kök/audit (`1843961`, `4104ae3`), kaynak alımı (`c4d616f`), source-review (`cb5a213`, `a566fd7`), merge motoru ve public persistence (`011900b`, `ce3d504`, `ca067c0`) ile tamamlandı. `4b3570a` doğrulanmış iki teknik test fixture düzeltmesini, `627d475` tam regresyon kanıtını korur. Diğer ara RED/GREEN ve düzeltmeler git geçmişindedir.
- **[Rule 3]** Eski Çeşme kapanışının gerçekte dar olan kapsamı geniş hücreyi kapatacak biçimde yükseltilmedi; gerekçeli köprü ve açık hücre korundu.
- **[Rule 1]** Test fixture'larında kabul edilen kaynak okuma kapsamı ve geçici merge/replay bağları gerçek doğrulayıcıların gerektirdiği şekilde düzeltildi. Assertion'lar ve üretim denetimleri korunarak tam regresyon yeniden geçti.
- **[Rule 3]** Kaybolan geçici fixture ve uygulama oturumu nedeniyle gözetici, eski kanıtın fixture bağını koruyarak sonraki testlerin desteklenen önbelleksiz yollarını Slurm üzerinde sürdürdü. 10.800 saniyelik batch sınırı değişmedi.

## Sınırlar ve devam

Bu plan teknik altyapıyı tamamlar; UYG-01, UYG-02 ve KAR-03 faz gereksinimleri ve 04-04–04-15 araştırma/teslim çalışmaları açık kalır. Çıktı, seçili bütün partiler için araştırmanın tamamlandığı anlamına gelmez. Takip eden dalga kapıları orkestratör tarafından yürütülür.

## Self-Check: PASSED

Önemli oluşturulmuş dosyalar ve görev commitleri bulundu; 287 sonuç gerçek sıfır çıkış/durum ve kimliklerle yeniden sayıldı. Tracer manifest özeti, beş kanonik dosya özeti ve kilit yokluğu doğrulandı. Yeni güven sınırları için açık kök, kaynak sahibi, özet ve alias doğrulamaları plan kapsamındadır; bilinen hedefi engelleyen stub bulunmadı.
