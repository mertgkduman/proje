---
phase: 04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas
plan: "01"
status: complete
subsystem: practice-archive
tags: [sqlite, source-policy, tracing, immutable-release, renderer]
requires: ["03-15"]
provides: ["schema7-practice-tracer", "renderer25", "practice-check-load-audit"]
affects: ["04-02", "04-03", "04-13", "04-15"]
tech-stack:
  added: []
  patterns: ["locked workspace and isolated transactional copy", "versioned immutable renderers", "source-linked claim and evidence"]
key-files:
  created:
    - src/uygulamalar.py
    - src/rapor_v24.py
    - tests/test_practice_tracer.py
    - tests/test_practice_legacy.py
    - data/practices/04-tracer.json
    - data/releases/53b24e6740104cb5be5d3419491bd735/records.sqlite3
    - data/releases/53b24e6740104cb5be5d3419491bd735/records.json
    - data/releases/53b24e6740104cb5be5d3419491bd735/index.html
    - data/releases/53b24e6740104cb5be5d3419491bd735/manifest.json
  modified:
    - src/arsiv.py
    - src/dosyalar.py
    - src/rapor.py
    - tests/test_comparisons.py
    - data/current.json
key-decisions:
  - "Çeşme ön seçim haberi atıflı claim olarak, tespit yöntemi ve kaynak içi oran çelişkisi açıklanarak kullanıldı; nihai kongre sonucu doldurulmadı."
  - "Şema 7 SQLite user_version işareti, practice tabloları ve manifest alanları birlikte doğrulanır; şema 6 ve renderer 24 tarihsel üretimi korunur."
  - "Kapsam yalnız arşivli Çeşme tracer olayıdır; dokuz parti araştırması veya Faz 4 tamamlandı iddiası değildir."
metrics:
  duration: "3h 35m 52s"
  completed: "2026-11-17"
  tasks: 2
  files: 14
plan_head_before: b9bb3a0586e9c76dd4191b2e9f421545845ec26a
actuals:
  tokens: 28617143
  tasks: 2
  commits: 5
---

# Phase 4 Plan 01: Kaynaklı Söylem–Uygulama Tracer Summary

Mevcut arşivdeki Çeşme ön seçimi, ayrı dönemsel söylem ve oluş kanıtıyla şema 7 üzerinden parti ve karşılaştırma görünümlerine taşındı; eski renderer 24 korunarak yeni yerel renderer 25 sürümü üretildi.

## Sonuç ve kapsam

- Yerel sürüm: `53b24e6740104cb5be5d3419491bd735`; rapor: `data/releases/53b24e6740104cb5be5d3419491bd735/index.html`. `data/current.json` bu sürüme işaret eder. Kamuya yayın veya dağıtım yapılmadı.
- Paket `data/practices/04-tracer.json` yalnız Yeni Parti–Çeşme ön seçimi tracer kapsamını açıklar. Eski `0105-action-cesme` ve `0105-match-cesme` satırları değiştirilmedi; yeni ilişkiye açık köprülerle bağlandı. Faz 4 ve dokuz partinin uygulama araştırması tamamlanmış değildir.
- Olayın kaynaklı haberi `0105-cesme-v1` / `0105-cesme-p`, söylem kaynağı `0105-speech-v1` / `0105-speech-p` ve ilgili seçili Faz 3 satırı `04-03-v3-0303-epm-detail2-organ-secim-yontemi-ilce-yonetim-kurulu-secimi-row`'dur. Bağlantılı tüzük satırının ilçe yönetim kuruluna, olayın ilçe başkanlığı ön seçimine ilişkin olduğu açıklanır.
- Arşivlenmiş Alaçatı İnternet Gazetesi haberi yer, gün, oy veren üye sayısı ve aktörün sözlerini bildirir; tespit yöntemi açıklanmaz. Haberdeki 630/1.113 sayıları ile yaklaşık %86 ifadesi uyuşmaz. Haber atıflı `claim` olarak kullanıldı; bağımsız gözlem veya tutanak uydurulmadı. Ön seçim, daha sonraki nihai kongre seçimi değildir; sonuç bulgusu boş ve sınırı açıktır. Euronews haberinin yayıncısı, yazarı Sait Burak Utucu ve yayın tarihi kaydedildi. Bu maddi kaynak okuması hash kontrolünden ayrıdır ve insan kabulü olarak sunulmaz.
- Yeni yükleme/check/export/audit zinciri kaynak ve parti kapsamını, doğrulama ve ajan incelemesini, tarih ve aktörü kontrol eder. Yükleme kilitli çalışma alanındaki geçici kopyayı doğruladıktan sonra değiştirir; SQLite `user_version=7`, tablo ve manifest kontrolleri eksiltmeyle eski şemaya sessiz dönüşü engeller. [SQLite user_version belgesi](https://sqlite.org/pragma.html#pragma_user_version).

## Görev Commit'leri ve TDD

| Commit | İş |
| --- | --- |
| `de09318` | Gerçek arşiv zinciri için RED test; `practice-check` yokluğunda beklenen assertion hatası. |
| `2fc4a96` | Şema 7, renderer 25, dondurulmuş renderer 24 ve ilk gerçek tracer yolu. |
| `9d1584c` | Yerel tracer ve geçmiş koruması için RED test; başlangıçtaki current şema 6 olduğu için beklenen assertion hataları. |
| `7d9ba91` | Önceden eski kalmış karşılaştırma stil testini tarihsel üreticileri ayrıca koruyacak şekilde düzeltme. |
| `d34dcd5` | Doğrulanmış yerel tracer sürümü, incelemeler ve son koruma düzeltmeleri. |

Tracer geri bildirim kapısı, ilk GREEN commit'inden sonra `python3 tests/run.py --pattern test_practice_tracer.py` ile yeniden çalıştırıldı ve geçti. Son sürüm üzerinde testler tekrarlandı.

## Doğrulama

- `python3 src/arsiv.py practice-check --input data/practices/04-tracer.json` — exit 0, `PRACTICE_INPUT_OK`.
- `python3 src/arsiv.py audit --release current --phase 4 --stage tracer` — exit 0, `PHASE4_AUDIT_OK 53b24e6740104cb5be5d3419491bd735`.
- `python3 src/arsiv.py audit --release current --phase 2` — exit 0, `PHASE2_AUDIT_OK` aynı sürüm.
- `python3 src/arsiv.py audit --release current --phase 3 --stage complete` — exit 0, `PHASE3_AUDIT_OK` aynı sürüm.
- `python3 tests/run.py --pattern test_practice_tracer.py` — 3/3, `TESTS_OK`; gerçek arşivden DB→JSON→iki HTML görünümü, yanlış pasaj/parti ve eksik incelemede rollback, açık kaynak-parti kapsamı ve XSS sınırı.
- `python3 tests/run.py --pattern test_practice_legacy.py` — 6/6, `TESTS_OK`; migration rollback, marker/manifest kaybı, tüm practice tablolarının kaldırılması, policy 2, Faz 2 öneki, Faz 3 seçimi, şema 6 export ve renderer 24 byte eşitliği.
- `python3 tests/run.py --pattern test_matches.py` — 7/7, `TESTS_OK`.
- `python3 tests/run.py --pattern test_comparisons.py` — düzeltilmiş tam koşu 10/10, `TESTS_OK`. İlk koşu, aşağıdaki tarihsel stil testi nedeniyle 9/10 idi.

## Hash ve tarihsel koruma

Önceki `9003e475ee5d49b29a1310c0bfe2007d` snapshot dosyaları başlangıç ve kapanışta aynı SHA-256 değerlerini taşıdı: SQLite `74e7f42f2a5c5001cd994375774b54b506f04898c6bd34856b5971d820a21945`, JSON `438568ba29d796d54b43b8f169dffba71a93c0fe3995eaf01ca224a017f3b7db`, HTML `ef4b5a20e3bfb031f7cd655cfda7e834df105b216abc611cfef00f6568de658b`, manifest `0d78f4fe319ab7ed857ebddbf56ee8ff8144d580bfb5e7ebe5d6199616e3622c`. Dondurulan `src/rapor_v24.py` SHA-256 `adbc002bc4b2c39077ba9e908c01bc56e5133f896d66c9636a0d84682f6d053b`, başlangıçtaki renderer 24 kaynağıyla aynıdır.

Yeni SQLite `9151c3055f2d53572b9b116ac6799b0a6cfa10d0ca9d7431dc6787ad15c68f5b`, JSON `81845ee333b31fa8bf890465e4a5afb239499923d74a5be66c49de0adf07a704`, HTML `96b87ce3daf43c10e5f48514daec89d98b82c5824bfb9439f5effe4121f54238`, manifest `3f6b918b33656ec0a292dd6f45227a762290f090a090fc8362ca5eec72193264` SHA-256 değerlerini taşır.

Kaynak özgünlerinin SHA-256 değerleri Çeşme için `68df17792083dfbc02c435dbd1235222c1b8434c4dc54a364d02062fa76a3c83`, Euronews için `f5835650645352957fe402920529476d9f763868ba1cbd176ca46f85da638389`; tracer paketinin SHA-256 değeri `966c6681635ee1bb915263a5840dd6dda3bb05528705e33bb03ca98d03f597b8`.

## Deviations from Plan

1. **[Rule 2/3 — Eksik kaynak incelemesi ve doğrulama sırası]** İlk yerel yayın denemesi yeni bulgular için mevcut Faz 1 ajan incelemelerini eksik bulup current değişmeden durdu. Gerçek kaynak okumasına dayalı dört ajan review eklendi; aynı koşul check/load/export/audit yoluna taşındı. Yalnız bu başarısız denemenin geçici staging dosyaları kaldırıldı.
2. **[Rule 3 — Şema 7 Faz 2 uyumu]** `src/dosyalar.py` Faz 2 doğrulamasının şema 7 snapshot'ını kabul etmesi için güncellendi; eski şema kuralları ve teslim öneki korundu.
3. **[Rule 1/3 — Önceden eskimiş regresyon beklentisi]** Başlangıç `b9bb3a0` testinde aktif stil 16 beklenirken aynı başlangıç üreticisi zaten 24 kullanıyordu. `7d9ba91`, tarihsel 14/16/24 stil ve 16/24 üretici hash/bağlantılarını ve güncel 25→24 stil seçimini ayrı doğrular; tam test tekrarında 10/10 geçti.
4. SQLite sürüm işareti ve manifest karşılaştırmaları, marker veya tüm yeni tablolar kaldırılarak oluşabilecek sessiz şema düşürmeye karşı eklendi. Şema 6 snapshot'larının baytları değiştirilmedi.

## Sonraki İş

`deferred-items.md`, 04-02 genişletmesinde renderer 25'in ve varlığının dondurulmasını, Çeşme'ye özgü boş-sonuç cümlesinin diğer olaylara genellenmemesini ve bireysel milletvekili katkılarının kurumsal tutum sayılmadan desteklenmesini açık izler. Faz 4 için insan kabulü veya kamu yayını yapılmadı.

## Self-Check: PASSED

Oluşturulan temel dosyalar ve yukarıdaki beş commit disk/git üzerinde doğrulandı; current kimliği, eski ve yeni snapshot hash'leri ve test/audit çıktıları kontrol edildi. `actuals.tokens` değerinin ölçeği gerçekleşen `git diff` karakter sayısının dörde bölünmesidir; `actuals.commits` plan başlangıcından SUMMARY öncesi HEAD'e `git rev-list --count` ile ölçülmüştür.
