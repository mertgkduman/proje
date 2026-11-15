---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
reviewed: 2026-11-15T08:47:39Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - README.md
  - src/arsiv.py
  - src/rapor.py
  - src/rapor_v20.py
  - src/rapor_v21.css
  - src/rapor_v21.py
  - src/rapor_v22.css
  - tests/comparison_navigation.cjs
  - tests/test_comparison_content.py
  - tests/test_comparison_navigation.py
  - tests/test_comparison_synthesis_contract.py
  - tests/test_source_labels.py
findings:
  critical: 1
  warning: 0
  info: 0
  total: 1
status: issues_found
---

# Phase 03: Kod İnceleme Raporu

**İncelenen an:** 2026-11-15T08:47:39Z  
**Derinlik:** standard  
**Durum:** issues_found

## Summary

On iki dosya ve önceki dört bulgunun düzeltme yolları statik olarak incelendi. Önceki CR-01, CR-02, CR-03 ve CR-04 kaynak düzeyinde kapandı; bununla birlikte yeni bir temiz checkout test bağımlılığı bulundu. Bu inceleme test, audit veya yayın çalıştırmadı. Bağımsız P2/P3 auditleri ve kullanıcı kabulü bu raporun sonucu değildir.

Önceki CR-01 için farklı konuya taşınan ve yerine geçirilen satırların kararları ile etkilenen hedeflerin dokuz parti kapsamı kalıcı sözleşme 3 soyundan denetleniyor; ilk soy başlangıcı tabanın bir sonraki sözlüğüne bağlanıyor ve sonraki yayınlarda eski soy kayıtları korunuyor. CR-02 için aktif renderer satırı kaynak rolü yerine seçili konunun alanına göre dosya bölümüne koyuyor. CR-03 için üretilen fragment bir kez kodlanıyor, çözme bir kez yapılıyor ve bozuk kodlama güvenle bırakılıyor; statik test kapsamı geçerli ayrılmış karakterler, kaynak ve geçmiş odağını içeriyor. CR-04 için eski etkin sürüm sabiti kaldırılmış, gerçek kaynak etiketi kontrolleri ve ayrı geçmiş renderer byte karşılaştırmaları korunmuş. Önceki sözleşme 2 snapshotlarının korunması hata sayılmadı.

## Narrative Findings (AI reviewer)

### CR-01: Geçmiş renderer regresyon testi Git'te bulunmayan yayınlara bağlı — BLOCKER

**File:** `tests/test_comparison_navigation.py:60`, `tests/test_comparison_navigation.py:64`

**Issue:** `test_preview_places_rows_by_topic_domain_and_frozen_20_is_exact` aşağıdaki dört dosyayı koşulsuz okuyor, fakat her iki release dizini de mevcut Git ağacında izlenmiyor. Temiz checkout'ta ilk `records.json` okuması `FileNotFoundError` ile sonlanır; böylece hem renderer 20/21 için byte uyumluluğu hem de aynı testteki Tüzük/Program bölüm yerleşimi doğrulanamaz. Yerel çalışma alanında mevcut olmaları bunları depo fixture'ı yapmaz.

- `data/releases/ef353c40c60b400eb1c52b3245e9a65b/records.json`
- `data/releases/ef353c40c60b400eb1c52b3245e9a65b/index.html`
- `data/releases/d8d06dbe3a794d2fb92459391af5a549/records.json`
- `data/releases/d8d06dbe3a794d2fb92459391af5a549/index.html`

**Fix:** Tarihsel byte karşılaştırmalarının ve bölüm yerleşimi kontrolünün ihtiyaç duyduğu bu değişmez kayıt ve HTML çiftlerini uygun teslim kapsamına alın veya aynı gerçek snapshotları içeren, Git'te izlenen kendi kendine yeterli fixture'lar sağlayın. Testi atlamayın ve beklenen HTML'yi test sırasında test edilen renderer ile yeniden üretmeyin; bağımsız byte kanıtı korunmalı. Temiz checkout'ta dosyaların bulunmasını ve testin bu kontrolleri yürütmesini doğrulayın.

---

_Reviewed: 2026-11-15T08:47:39Z_  
_Reviewer: gsd-code-reviewer_  
_Depth: standard_
