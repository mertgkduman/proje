---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
reviewed: 2026-11-12T00:13:01Z
depth: standard
files_reviewed: 27
files_reviewed_list:
  - .gitignore
  - README.md
  - src/arsiv.py
  - src/arsiv_gorunum.py
  - src/dosyalar.py
  - src/kaynaklar.py
  - src/rapor.py
  - src/rapor_v10.py
  - src/rapor_v11.css
  - src/rapor_v11.py
  - src/rapor_v12.py
  - src/rapor_v13.py
  - src/rapor_v8.py
  - src/rapor_v9.py
  - tests/archive_browser.cjs
  - tests/browser_probe.py
  - tests/test_acceptance.py
  - tests/test_archive_views.py
  - tests/test_dates.py
  - tests/test_documents.py
  - tests/test_dossiers.py
  - tests/test_finance.py
  - tests/test_matches.py
  - tests/test_publication.py
  - tests/test_report.py
  - tests/test_scope.py
  - tests/test_source_policy.py
findings:
  critical: 3
  warning: 0
  info: 0
  total: 3
status: issues_found
---

# Faz 02: Kod Yeniden İnceleme Raporu

**İnceleme zamanı:** 2026-11-12T00:13:01Z  
**Derinlik:** standard  
**İncelenen dosya:** 27  
**Durum:** issues_found

## Özet

İlk incelemedeki altı düzeltme, `e6c2b92..f08bb25` kaynak farkı ve ilgili testler üzerinden yeniden incelendi. Altı özgün örnek giderilmiş; iki düzeltmede içerik kaybına neden olan yeni durumlar ve kodlama zincirinde önceden var olan ayrı bir eksik bulundu. Önceki kimlikler ve çözüm kanıtları aşağıda korunmuştur. Tam regresyon bu rapor yazılırken çalışıyor; sonuç henüz alınmadı.

## Narrative Findings (AI reviewer)

### CR-07: Yazar aktarımının kaldırılması mevcut üç bilinen yazarı görünmez kılıyor

**Sınıflandırma:** BLOCKER  
**Dosya:** `src/rapor.py:160`, `src/rapor.py:84-110`  
**Sorun:** CR-05'in yanlış tarih/yayıncı aktarımı giderilmiş; ancak önceki sürüme bağlı bulgular gösterilirken aynı belgenin yazarı doğrulanmış sonraki sürümü sadece tarih ve sürüm etiketi olarak listeleniyor, yazar ve atıf dayanağı hiçbir yerde gösterilmiyor. Mevcut `bcc67d04d9d741e191589d0f5ac173ca` verisi üretici 14 ile tekrar oluşturulduğunda Ekonomim'in iki haberinden “Haber Merkezi”, Kocaeli TV haberinden “Bugün Kocaeli” kayboluyor. Sonraki üç kayıtta yazar ve özgün HTML metadata dayanağı kayıtlıdır. Bu, bilinen yazar atfını okura ulaştırma gereğini bozar.

**Düzeltme:** Her sürümün kendi tarih, yayıncı ve dayanağını koruyarak sonraki sürümün yazarını ve kanıtını açık sürüm atfıyla gösterin. Alternatif olarak yalnız açıkça desteklenen yazarı, kaynak sürüm ve gerekçesine bağlantıyla tamamlayın; yayıncıyı, tarihi veya dayanağı topluca aktarmayın. Gerçek üç kaynakta yazarın görünür kalmasını ve farklı tarih/yayıncıların eski sürüme taşınmamasını birlikte test edin.

### CR-08: Kimlik notu alıntılarında HTML entity çözümlemesi atlanıyor

**Sınıflandırma:** BLOCKER  
**Dosya:** `src/rapor.py:137-139`, `src/rapor.py:158-164`  
**Sorun:** CR-06 için eklenen `format_finding`, kaynak türünü yalnız `finding_evidence` satırlarından belirliyor. `dossier_identity_note` kayıtları ise kanıta `own_passage_id` ve `related_passage_id` ile bağlanıyor; bu nedenle HTML kaynaklı alıntı notunda eşleşme bulunamıyor ve entity çözümlemesi yapılmıyor. Mevcut kimlik notunun bellek içi kopyasında alıntı ve HTML pasajı `SAADET &amp; PARTİSİ` olduğunda çıktı `SAADET &amp;amp; PARTİSİ` oluyor; tarayıcı okura `&amp;` gösteriyor. Bu metin alıntı ve pasaj eşitliği koşulunu karşılayan bir girdi için birebir aktarımı bozuyor.

**Düzeltme:** Kimlik notu biçimleyicisine notun iki pasajını sağlayın; metinle eşleşen pasajın kaynak türünü kullanarak HTML entity çözümlemesini uygulayın ve PDF metnini literal koruyun. HTML ve PDF kaynaklı kimlik notlarında entity benzeri dizeleri test edin.

### CR-09: UTF-8 dışındaki kaynaklar genel kayıt ve pasaj zincirinde kullanılamıyor

**Sınıflandırma:** BLOCKER  
**Dosya:** `src/arsiv.py:124-126`, `src/arsiv.py:221-245`, `src/arsiv.py:823-835`, `src/kaynaklar.py:45-48`  
**Sorun:** CR-03'ün pasif görünüm örneği giderildi; bu ayrı genel kayıt zinciri kısıtı önceden de vardı. `capture_source` HTTP karakter kümesini artık sonuç alanı olarak veriyor, ancak `document_version` şemasında bunu koruyan alan yok. `readable_bytes`, atıf denetimi ve `export_db` pasaj kontrolü HTML baytlarını hâlâ UTF-8 replacement ile çözüyor. Bu nedenle Windows-1254 bildirimli ve “Türkiye İşçi Partisi” içeren bir belgenin doğru Türkçe pasajı export sırasında `Pasaj özgün belgede bulunamadı` hatasıyla reddedilir; okunabilir türev de bozuktur. Mevcut pasif görünüm testi bu uçtan uca yolu kapsamıyor.

**Düzeltme:** Yeni yakalamalar için karakter kümesini kalıcı ve sürümlü meta veride koruyup yeni kayıtların atıf/pasaj çözümlemesine aynı değeri aktarın. Önceki okunabilir türevlerin baytlarını ve eski denetim davranışını koruyacak geriye uyumlu bir yol kullanın; mevcut arşivleri yerinde değiştirmeyin. HTTP ve meta bildirimli Windows-1254 kaynakların yakalama → kayıt → pasaj → export akışını test edin.

## Önceki bulguların yeniden kontrolü

| Kimlik | Durum | Kanıt |
|---|---|---|
| CR-01 | Özgün hata giderildi | `fetch_asset` her yönlendirmeden önce izinli ana makine ve genel IP kontrolü yapıyor; doğrulanmış IP'ye bağlanıyor. Yönlendirme, karma DNS yanıtı ve yeniden çözümleme testleri `tests/test_archive_views.py:100-140`. |
| CR-02 | Giderildi | `DROP_VOID` içindeki `embed` yığına eklenmiyor; `test_void_embed_does_not_hide_following_content`. |
| CR-03 | Özgün pasif görünüm hatası giderildi | Görünüm BOM, HTTP charset ve meta kodlamayı çözüyor; `test_declared_charsets_and_bom_preserve_turkish_text_and_original`. Önceden var olan genel kayıt sorunu ayrı CR-09'da açıklanmıştır. |
| CR-04 | Giderildi | Biçim 2 kimliği manifest içeriğinden üretiliyor; biçim 1 kabul ediliyor. `test_view_identity_covers_source_url_and_limitations` ve mevcut görünüm testleri. |
| CR-05 | Özgün hata giderildi; yeni CR-07 açık | Başka sürümün tüm künyesi artık aktarılmıyor; `test_attribution_is_never_copied_from_same_hash_sibling`. Mevcut üç yazarlı künye görünmez oluyor. |
| CR-06 | Özgün PDF örneği giderildi; yeni CR-08 açık | PDF bulgu ve pasajlarında literal entity korunuyor; `test_pdf_quote_entities_are_literal_and_html_entities_decode`. Kimlik notları farklı kanıt yapısı nedeniyle bundan yararlanmıyor. |

## Sürüm ve regresyon

`src/rapor_v13.py`, `e6c2b92:src/rapor.py` ile bayt bayt aynıdır; `bcc67d04d9d741e191589d0f5ac173ca` HTML'i üretici 13 ile birebir yeniden üretilmiştir. Aynı kayıtlarda üretici 14 çıktısı farklıdır ve üç bilinen yazarı gizler. Kod düzeltmelerini rapora yansıtmak için yeni sürüm gerekir; bu açıklar giderilip doğrulanmadan üretici 14 ile yeni sürüm önerilmez. Mevcut sürüm değiştirilmedi.

Tam faz regresyonu `python3 tests/run.py` ile yapılandırılmış 1800 saniyelik sınır altında başlatıldı ve rapor yazılırken devam ediyordu. Sonuç ve test sayısı tamamlandığında `/tmp/phase02-regression-final.json`, ayrıntı `/tmp/phase02-regression-final.log` dosyasındadır; henüz başarılı sayılmamıştır.

---

_İnceleyen: gsd-code-reviewer_  
_Derinlik: standard_
