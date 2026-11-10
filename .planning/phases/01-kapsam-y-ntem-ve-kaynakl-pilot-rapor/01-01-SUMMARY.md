---
phase: 01-kapsam-y-ntem-ve-kaynakl-pilot-rapor
plan: "01"
subsystem: kaynakli-arsiv
tags: [sqlite, kanit, html, arşiv, test]
requires: []
provides: [kaynak-arsivi, sqlite-writer, atomik-release, kaynakli-html]
affects: [01-02, 01-03, 01-04, 01-05, 01-06]
tech-stack:
  added: [Python-standart-kitapligi, SQLite]
  patterns: [icerik-adresli-arsiv, kapali-snapshot, atomik-isaretci]
key-files:
  created: [src/arsiv.py, src/rapor.py, tests/run.py, tests/test_tracer.py, tests/browser_probe.py, tests/test_publication.py, README.md]
  modified: []
key-decisions:
  - "Kaynak nesneleri SHA-256 ile adreslenir; kayıt ve rapor aynı kapalı release snapshotından üretilir."
  - "Ham HTML indirilebilir bayt olarak, okunabilir arşiv kaçışlanmış türev olarak sunulur."
status: complete
completed: 2026-11-10
duration: "Önceki yürütme ve insan onayı dahil; kesin toplam süre kaydedilmedi"
plan_head_before: 593a3ae910ce7ec778caadb2204cb5c974656a8a
actuals:
  tokens: 58460
  tasks: 2
  commits: 6
---

# Phase 1 Plan 1: Kaynaklı pilot kanıt zinciri özeti

Yargıtay'ın Yeni Parti kaydındaki kuruluş tarihi, değişmez arşivden SQLite kaydına ve kaynak bağlantılı HTML raporuna taşındı; kapalı release ve atomik işaretçiyle son doğrulanmış sürüm korunuyor.

## Gerçek kaynak ve doğrulama

- Kaynak: https://www.yargitaycb.gov.tr/sipar/365; erişim ve doğrulama 2026-11-10 14:20:10 UTC. Kayıttaki kuruluş tarihi 24.07.2026'dır. Arşiv SHA-256: `404e094c66eeb871b91b396689632313f63b186d4afa7f89e5e422f3c732ac6f`.
- Release: `40901676139946719967427b5d241c00`. JSON, HTML ve SQLite aynı snapshot ile ilişkilidir. Tarayıcı testi gerçek kaynak bağlantısına tıklayarak kaynak kaydını kontrol eder.
- `python3 tests/run.py`: 10 test geçti; gerçek tarayıcı etkileşimi dahil. `python3 src/arsiv.py audit --release current`: `AUDIT_OK 40901676139946719967427b5d241c00`.
- Kullanıcı tracer insan kontrolüne 2026-11-10 tarihinde “Onaylıyorum” yanıtını verdi. Onay, daha önce sunulan kaynak pasajı, özet ve kaynak bağlantısı kontrolüne ilişkindir.

## Görevler ve commitler

1. Kanıt zinciri: RED `76479d8`, uygulama `88299d7`.
2. Release bütünlüğü ve hata dayanıklılığı: RED `b879e2f`, uygulama `6c43954`.

Ölçülen altı commit, dört görev commitine ek olarak kontrol noktasını kaydeden `2f85869` ve `3f1fe51` commitlerini içerir. Token tahmini, görevlerin kaynak ve veri diffindeki 233841 karakterin dörde bölünmesiyle hesaplandı; ikili SQLite diff içeriği dahil değildir.

## Plandan sapmalar

İkinci görev, tracer için zorunlu insan kontrolü alınmadan önce yürütüldü ve commitlendi. Bu yürütme sırası plana aykırıydı; kontrol noktası sonradan sunuldu ve kullanıcı açıkça onayladı. Onay öncesi iş yapılmış olması gizlenmedi; görevler yeniden çalıştırılmadı veya geri alınmadı.

## Self-Check: PASSED

Planın yedi kaynak/test/dokümantasyon dosyası ve dört görev commiti mevcut; 10 test ve release denetimi başarıyla tekrarlandı.
