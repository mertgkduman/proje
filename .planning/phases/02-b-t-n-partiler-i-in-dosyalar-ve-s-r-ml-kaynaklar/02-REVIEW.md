---
phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar
reviewed: 2026-11-12T00:58:31Z
depth: standard
files_reviewed: 28
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
  - src/rapor_v14.css
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
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Faz 02: Son Kod İnceleme Raporu

**İnceleme zamanı:** 2026-11-12T00:58:31Z  
**Derinlik:** standard; son tur önceki bulgular ve değişen kodla sınırlı  
**İncelenen dosya:** 28  
**Durum:** clean

## Özet

Önceki CR-01–CR-08 bulgularının örnekleri ve tamamlanmış teslimin yenilenmesi düzeltildi. CR-09'un meta/BOM bildirimli kaynak zinciri düzeltildi; yalnız HTTP başlığında kalan ve baytlardan yeniden üretilemeyen UTF-8 dışı kodlama için açıkça reddedilen, aşağıda belirtilen destek sınırı devam ediyor. Bu sınırlı son incelemede seviyesi açık BLOCKER veya WARNING bulgu kalmadı.

## Narrative Findings (AI reviewer)

Bu turda açık sınıflandırılmış bulgu yoktur. Aşağıdaki geçmiş tablosu önceki bulguların ve kısmi kodlama desteğinin kanıtını korur.

## Bulguların geçmişi ve düzeltme kanıtı

| Kimlik | Durum | Kanıt |
|---|---|---|
| CR-01 | Düzeltildi | `src/arsiv_gorunum.py:34` her yönlendirmeden önce izinli ana makineyi ve DNS adreslerini denetleyerek doğrulanmış genel IP'ye bağlanır; yönlendirme ve karma DNS testleri `tests/test_archive_views.py` içindedir. |
| CR-02 | Düzeltildi | `DROP_VOID` içindeki `embed` blok yığınına alınmaz; `test_void_embed_does_not_hide_following_content` sonrasındaki metni denetler. |
| CR-03 | Düzeltildi | Pasif görünüm BOM, HTML meta ve uygun HTTP charset bilgisini çözer; `test_declared_charsets_and_bom_preserve_turkish_text_and_original` özgün hash'i ve Türkçe metni sınar. |
| CR-04 | Düzeltildi | Biçim 2 kimliği manifest alanlarından üretilir ve doğrulanır; biçim 1 görünümleri kabul edilir. `test_view_identity_covers_source_url_and_limitations` farklı kaynak URL'lerini ve sınırları denetler. |
| CR-05 | Düzeltildi | Farklı sürümün tüm künyesi artık aktarılmaz; `test_attribution_is_never_copied_from_same_hash_sibling` tarih/yayıncı karışmasını denetler. Yazar görünürlüğü CR-07 altında ayrıca düzeltildi. |
| CR-06 | Düzeltildi | PDF kaynaklı bulgu ve pasajlardaki literal entity korunur; `test_pdf_quote_entities_are_literal_and_html_entities_decode` PDF ve HTML kökenlerini sınar. Kimlik notu CR-08 altında ayrıca düzeltildi. |
| CR-07 | Düzeltildi | `src/rapor.py:84` her kardeş sürümün kendi yazarını ve atıf dayanağını o sürümün geçmişinde gösterir; farklı sürümün yayıncısı/tarihi aktarılmaz. Üç gerçek yazar kaydı ve farklı künyeler ilgili rapor testlerinde denetlenmiştir (`4610441`). |
| CR-08 | Düzeltildi | `src/rapor.py:140` kimlik notunun kendi ve ilişkili pasajlarını biçimleyiciye verir; `src/rapor.py:161` eşleşen pasajın HTML/PDF kökenini kullanır. Her iki köken ilgili rapor testlerinde denetlenmiştir (`acef9a2`). |
| CR-09 | Kısmen düzeltildi; aşağıdaki destek sınırı sürüyor | `src/arsiv.py:125` ve `src/kaynaklar.py:45` meta/BOM üzerinden çözümlemeyi kullanır; `test_declared_non_utf8_capture_passage_and_export` Windows-1254 kaynağı yakalama, atıf ve export boyunca sınar ve eski türev baytlarının korunmasını denetler (`d56106c`). |
| CR-10 | Düzeltildi | `src/dosyalar.py:75` refresh için sekiz partilik tam ve değişmemiş prefix'i, aynı son parti ve `complete` aşamasını şart koşar. `src/arsiv.py:1029` refresh'i `--party`/tracer ile dışlar ve normal parti teslimi korumasını tutar. Üç odaklı test ve gerçek yerel yayın kaydı `02-REFRESH.md` içindedir (`353a5ee`). |

## Kalan destek sınırı

Önceden var olan kayıt şeması, yalnız HTTP başlığında bulunan ve HTML baytlarında meta/BOM ile belirtilmeyen UTF-8 dışı karakter kümesini kalıcı olarak saklamaz. `src/arsiv.py:235` yeni yakalamada HTTP çözümlemesi ile baytlardan bağımsız yeniden üretilebilen çözümleme uyuşmazsa açık hata verir; sessizce bozuk kayıt üretmez. Meta/BOM bildirimli kaynaklar desteklenir ve önceki özgün ve türev baytları yerinde değiştirilmez. Bilinen mevcut üretim girdileri bu sınırla engellenmemiştir. Bu sınır, genel HTTP charset desteği için ileride sürümlü metadata gerektirebilecek, yayın engeli sayılmayan belgeli kapsamdır.

## Yayın ve doğrulama kanıtı

Yerel `1d6b49b307f04a258c1a11d90978fe7c` sürümü üretici 14 ve `phase2_refresh=true` ile oluşturulmuş, `PHASE2_AUDIT_OK` almıştır. `02-REFRESH.md` uyarınca önceki sürümle kayıtlar `release_id` dışında aynıdır; önceki makbuzlar, nesneler, görünümler ve yayınlar korunmuştur. Bu yerel yenileme ağ yayını değildir.

`02-REGRESSION.md` ve `02-REVIEW-FIX.md` kayıtlarına göre tam koşuda 91 testin 90'ı geçti; tek hata üretici 13'e sabitlenmiş test beklentisiydi. Beklenti düzeltildikten sonra ilgili entegrasyon testi 1/1 geçti. Değişen arşiv/rapor testleri 25/25, ilgili kaynak politikası testleri 2/2 ve yenileme testleri 3/3 geçti. Tam paketin tek çalıştırmada bütünüyle başarılı olduğu iddia edilmez. Bu son sınırlı incelemede testler yeniden çalıştırılmadı.

---

_İnceleyen: gsd-code-reviewer_  
_Derinlik: standard; son tur sınırlı doğrulama_
