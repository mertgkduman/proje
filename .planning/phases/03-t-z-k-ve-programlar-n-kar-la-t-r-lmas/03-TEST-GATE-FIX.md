---
phase: 03
fixed_at: 2026-11-15T10:29:48Z
review_path: .planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-TEST-GATE-REVIEW.md
iteration: 1
findings_in_scope: 1
fixed: 1
skipped: 0
status: all_fixed
---

# Faz 03: Test kapısı düzeltme raporu

## TG-01: Amaçlı birim fixture'larını sabitle

**Durum:** fixed: requires human verification  
**Commit:** `858fc59`  
**Dosyalar:** `tests/fixture_data.py`, `tests/test_acceptance.py`, `tests/test_chain.py`, `tests/test_documents.py`, `tests/test_finance.py`, `tests/test_matches.py`, `tests/test_missing.py`, `tests/test_topics.py`

Bağımsız amaçlı çalışma alanları gerçek kabul edilmiş `7f816c5afd704cf3a88f2cfd8638528f` sürümünü, dört sürümlük ata zincirini ve kayıtlarda belirtilen gerçek kaynak/görünüm dizinlerini kopyalar. Gerçek denetim ve migration korunur. Güncel mali veri testi ayrı, fixture'sız sınıfa taşındı; diğer canlı entegrasyonlar korunur.

## Doğrulama

Ana checkout'ta standart unittest ile 19 hedefli test geçti (45.219 saniye, çıkış 0); bunlara canlı güncel mali veri testi dahildir. Yedi dosyada test sayıları sırasıyla 4, 1, 11, 4, 7, 2, 3 olarak değişmedi. Python derleme ve `git diff --check` geçti. Ayrı yalıtılmış denemede gerçek `audit_release` sabit sürümü kabul etti ve `open_workspace` sonrası export şema 5 verdi; bir özgün kaynak veya arşiv görünümü indeksi kaldırıldığında gerçek denetim reddetti. Süreç PID/oturum, girdi özeti, log ve çıkış kanıtları `03-15-checks/tg-01/` altındadır.

Tam root test kapısı ve bağımsız yeniden kaynak incelemesi henüz çalıştırılmadı; bunlar orkestratörün sonraki işleridir. Önceki durdurulmuş root test koşusu exit 143 ile başarısızdır, geçiş değildir.
