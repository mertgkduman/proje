---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
reviewed: 2026-11-15T05:54:15Z
depth: standard
files_reviewed: 23
files_reviewed_list:
  - README.md
  - src/arsiv.py
  - src/dosyalar.py
  - src/kaynaklar.py
  - src/rapor.py
  - src/rapor_v15.py
  - src/rapor_v16.css
  - src/rapor_v16.py
  - src/rapor_v17.py
  - src/rapor_v18.py
  - src/rapor_v19.css
  - src/rapor_v19.py
  - src/rapor_v20.css
  - tests/comparison_navigation.cjs
  - tests/test_comparison_content.py
  - tests/test_comparison_navigation.py
  - tests/test_comparison_synthesis_contract.py
  - tests/test_comparisons.py
  - tests/test_dossiers.py
  - tests/test_phase2_cli_audit.py
  - tests/test_phase3_stage_compatibility.py
  - tests/test_source_labels.py
  - tests/test_source_policy.py
findings:
  critical: 4
  warning: 0
  info: 0
  total: 4
status: issues_found
---

# Phase 03: Kod İnceleme Raporu

**İncelenen an:** 2026-11-15T05:54:15Z  
**Derinlik:** standard  
**Kapsam:** Plan 01–15 kaynakları; plan 16 kabulü ve kaynak anlamı incelemesi bu raporun kapsamı değildir.

## Summary

Seçili konu eşlemesi, rapor gezinmesi ve regresyon testlerinde dört somut sorun bulundu. İnceleme statiktir; eşzamanlı tam regresyonu etkilememek için test, audit veya yayın çalıştırılmadı. Tarihsel renderer ve stiller değiştirilmemelidir.

## Narrative Findings (AI reviewer)

### CR-01: Konular arası satır taşıma yeni anlam incelemesini atlıyor — BLOCKER

**File:** `src/arsiv.py:447`, `src/arsiv.py:463`, `src/arsiv.py:1632`

**Issue:** `changed` yalnız aynı kimlikteki hedef konunun alanlarını eski sürümle karşılaştırıyor. Buna karşılık `comparison_reconcile`, bir eski satırın `mapping['topic_id']` değerinin kendi eski `topic_id` değerinden farklı olmasını yasaklamadan pasaj, özet ve alıntısını yeni hedefe kopyalıyor. Yeni sözlükte başka bir konu gerçekten değişmişse zorunlu `changed` koşulu karşılanabilir; değişmemiş bir hedefe taşınan satırlar `changed_rows` dışında kalır ve yeni `row_reviews` istenmez. Snapshot audit'i de `validate_changed_topic_reviews` içinde değişmemiş hedef için hemen devam eder. Aynı türden iki ayrı mevcut konu arasında böyle bir taşıma, kaynakları yeni anlam bakımından yeniden incelemeden yayınlayabilir ve kullanıcıya alakasız bir parti pozisyonu gösterebilir.

**Fix:** Eski ve yeni konu kimlikleri farklı olan her taşınmış satırı anlam değişikliği sayın; hedef için dokuz parti kapsamını ve her etkilenen satırın yeni tanım, koşul ve kendi kanıtına bağlı incelemesini zorunlu tutun. Kalıcı, yapılandırılmış satır soyunu snapshot'a kaydedip audit yolunda da aynı kuralı doğrulayın. Değişmemiş hedefe farklı konudan taşımayı reddeden negatif testi ekleyin.

### CR-02: Program kayıtlarının parti dosyasındaki hedefi Tüzük bölümünde — BLOCKER

**File:** `src/rapor.py:453`

**Issue:** `key == 'tuzuk'` dalı bütün parti karşılaştırma satırlarını alanlarına bakmaksızın basıyor. Dolayısıyla örneğin mevcut İYİ Parti program satırının karşılaştırmadaki “Parti dosyasına git” bağlantısı Program yerine Tüzük başlığı altındaki kayda götürüyor; Program bölümünde aynı satır bulunmuyor. Bağlantı kimliği ve odak çalışsa da okur yanlış belge bağlamına yönlendiriliyor. Mevcut tarayıcı testi yalnız doğru parti panelini kontrol ettiği için bunu kaçırıyor.

**Fix:** Satırın seçili `comparison_topic.domain` değerini esas alarak charter konularını Tüzük, program konularını Program bölümüne yerleştirin; ek ve tarihsel kaynaklarda da belge rolü yerine konu alanını kullanın. Gidiş/dönüş kimliklerini koruyun ve program ile tüzük satırlarının gerçek bölüm atalarını tarayıcı testinde doğrulayın. Eski rendererları değiştirmeyin; yeni renderer sürümüyle yayınlayın.

### CR-03: Geçerli URL kodlu fragmentler reddediliyor — BLOCKER

**File:** `src/rapor.py:646`

**Issue:** `hashTarget` ve `openHash` içinde yüzde işareti içeren her fragment reddediliyor. Kimliklerin veritabanı ve paket doğrulaması ASCII ile sınırlandırılmadığından Türkçe karakter, boşluk veya başka URL kodlu karakter içeren geçerli bir satır ya da pasaj kimliği kabul edilebilir. Tarayıcı bu kimliği fragmentte `%...` biçiminde kodladığında doğrudan bağlantı ve kaynağa/parti dosyasına geçiş, gizli paneli açma ve hedefe odaklama davranışını çalıştırmaz. Bozuk `%ZZ` girdisini reddetmek geçerli kodlamaları da reddetmeyi gerektirmez.

**Fix:** `decodeURIComponent` işlemini `try/catch` içinde uygulayıp yalnız hatalı kodlamayı reddedin; tıklama ve `hashchange` aynı çözümleyiciyi kullansın. Geçerli Türkçe karakterli ve boşluklu kimliklerle iki yönlü gezinmenin yanı sıra bozuk `%ZZ` durumunu test edin. Düzeltmeyi yeni renderer sürümüne taşıyın.

### CR-04: Kaynak etiketi testi eski etkin renderer sürümünü zorunlu tutuyor — BLOCKER

**File:** `tests/test_source_labels.py:49`, `src/rapor.py:11`

**Issue:** `test_same_document_two_publishers_keep_source_and_archive_in_both_views`, etkin `rapor.RENDERER_VERSION` değerinin 18 olduğunu koşulsuz bekliyor; mevcut değer 20. Test kaynak etiketi ve arşiv kontrollerine ulaşmadan başarısız olur, dolayısıyla tam regresyonu ve bu kontrollerin güvenilirliğini bozar.

**Fix:** Güncel renderer için sabit 18 beklentisini kaldırın veya güncel sürüm sözleşmesine güncelleyin; tarihsel 18'in byte uyumluluğunu zaten ayrı tarihsel renderer testiyle doğrulamaya devam edin.

---

_Reviewed: 2026-11-15T05:54:15Z_  
_Reviewer: gsd-code-reviewer_  
_Depth: standard_
