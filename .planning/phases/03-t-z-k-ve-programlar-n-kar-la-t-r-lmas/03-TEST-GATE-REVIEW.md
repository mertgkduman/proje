---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
reviewed: 2026-11-15T10:25:23.566759+00:00
depth: standard
reviewer_kind: orchestrator
files_reviewed: 7
findings:
  critical: 0
  warning: 1
  info: 0
  total: 1
status: issues_found
---

# Test kapısı: sabit birim testi verisi

Bu değerlendirme orkestratörün gerçek test zamanları ve statik kaynak incelemesidir; bağımsız agent incelemesi olarak sunulmaz. Önceki dört runtime bulgusu kapalıdır.

## TG-01: Amaçlı birim fixture'ları büyüyen canlı yayın zincirine bağlı — WARNING

`tests/test_finance.py:12-17` ve `tests/test_matches.py:13-19` her testte canlı DATA'yı kopyalayıp `open_workspace` ile güncel yayın zincirinin tamamını yeniden denetliyor. Eksik bilgi/konu, belge ve bazı kabul/arama zinciri mutasyon testleri aynı örüntüyü kullanıyor. Özel test satırlarıyla temel sözleşme kuralları sınayan bu testler için üretim arşivinin değişen büyüklüğü gerekli fixture değildir. Önceki 03-14 kapısı 1800 saniyede tamamlanamadı; yeni koşu 90 dakikadan fazla sürede ancak 72 test geçerek bu tekrarlayan setuplara ulaştı. Kalan finans/eşleştirme/eksik/konu testleri de aynı maliyeti çoğaltıyor. Yapılandırılmış üç saatlik kapı için güvenilir, sabit kapsamlı birim verisi gerekir.

Düzeltme: mevcut `PublicationTest`/dossier fixture yaklaşımına uygun, Git'te izlenen gerçek sabit tarihsel baseline kullan. Küçük, source_policy2 taşıyan ve `tip-charter-v1` içeren `7f816c5afd704cf3a88f2cfd8638528f` kabul edilmiş bir adaydır (schema5, renderer11, SQLite684032 bayt,44 belge sürümü). Sahte inceleme veya downgrade yaratma. Gerekli kapalı ancestor manifest/JSON/SQLite/HTML ile bunların kayıtlarının istediği gerçek özgün/okunabilir dosya ve pasif arşiv varlıklarını kopyala; validator/audit fonksiyonunu mock'lama veya bypass etme. Sadece releases/current kapsamını sabitlemek yeterliyse en küçük doğru yaklaşımı seç; tüm büyüyen canlı releases/staging ağaçlarını tekrar kopyalamaktan kaçın.

Kaynak kodu `src/` ve araştırma verisi değişmemeli. Var olan davranış ve negatif assertionlar korunmalı; skip ekleme. Gerçek current anlık görüntü kabulü, gerçek current server/navigation, güncel finans pilotu, PublishedMatches ve gerçek kaynaklı sözlük testleri canlı current üzerinde kalmalı. Gerekirse güncel finans testi ayrı fixture'sız sınıfa taşınır; amaçlı birim fixture'ı ona uygulanmaz. Mutasyon testlerinin her biri bağımsız çalışma alanı kullanmalı. Bazda olmayan gerekli gerçek kayıt varsa doğru başka küçük sabit kabul edilmiş fixture seç; yapay metadata değişikliğiyle testi susturma.

Kapsam: tests/test_acceptance.py içindeki amaçlı mutasyonlar; test_chain.py; test_documents.py amaçlı mutasyonlar; test_finance.py; test_matches.py içindeki MatchContract (PublishedMatches canlı kalır); test_missing.py; test_topics.py amaçlı mutasyonlar; gerekirse tek ortak tests/fixture_data.py. Testlerin işlevsel gövdelerini koru. Doğrulama mevcut bu süitlerle ve gerçek current'ı ayrı tutan testlerle yapılır. Tam global süiti root tekrar çalıştırır. Sonrasında bağımsız kaynak re-review yapılacaktır.

Durdurulan koşu:03-15-checks/root-review-fixes/root-regression-abort.json; test exit143, root result1, geçiş değildir. Çalışan publisher kesilmedi, root writer lock yoktu, current270335 değişmedi.
