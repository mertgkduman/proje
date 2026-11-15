---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
fixed_at: 2026-11-15T08:37:35Z
review_path: .planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas/03-REVIEW.md
original_review_commit: b53ed3161787205f592f9aaaffe3b347c7887fac
followup_review_commit: 5face6b
followup_fixed: 1
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 03: Code Review Fix Report

**Durum:** Dört kaynak düzeltmesi ve bağımsız incelemenin temiz checkout fixture bulgusu kapandı. Final22 P2/P3 bağımsız auditleri exit 0; son kaynak incelemesi `clean`. Tam global regresyon, 03-16 ve insan UAT ayrı açık kapılardır.

## Düzeltilen bulgular

### CR-01: Konular arası satır taşımanın yeni anlam incelemesi

**Durum:** fixed: requires human verification  
**Commit:** `7535b06`, `24edad7`  
**Dosyalar:** `src/arsiv.py`, `tests/test_comparison_content.py`, `README.md`

Sözleşme 3/lineage 1, yapılandırılmış satır soyunu, tanım/koşul/öz kaynak kararlarını ve ilk sözlük sürümünün gerçek tabana bağlanmasını doğrular. Farklı konuya taşınan her satır için inceleme ve hedefte dokuz parti kapsamı gereklidir. Önceki snapshotlar değişmez. Ayrı DATA üzerindeki gerçek kaynaklı fixture export, publish, bağımsız audit ve bozulmuş manifest reddinden geçti; soy kenarı silinip hash yenilendiğinde gerçek audit ve import reddetti, başarısız import workspace'i değiştirmedi. Kanıtlar `03-15-checks/lineage-contract-v3-result.json` ve `lineage-tamper-result.json`. Final22 mevcut veri sözleşmesini **2**, taxonomy sürümünü **4** olarak korur; izole fixture'daki sözleşme 3 bu yayına geriye dönük uygulanmamıştır.

### CR-02: Parti dosyasında Tüzük/Program hedefi

**Durum:** fixed: requires human verification  
**Commit:** `b8581a4`  
**Dosyalar:** `src/rapor.py`, `src/arsiv.py`, `src/rapor_v20.py`, `src/rapor_v21.css`, `tests/test_comparison_navigation.py`, `tests/comparison_navigation.cjs`

Satırlar kaynak rolü yerine seçili konu alanına göre bölüm altında gösterilir; gerçek tarayıcı testi hem Tüzük hem Program atalarını doğrular. Renderer 20 donduruldu ve eski HTML byte-byte yeniden üretildi.

### CR-03: URL kodlu fragmentler ve ayrılmış karakterler

**Durum:** fixed: requires human verification  
**Commit:** `5c1c55e`, `40c31a8`, `6af739b`  
**Dosyalar:** `src/rapor.py`, `src/arsiv.py`, `src/rapor_v21.py`, `src/rapor_v22.css`, `tests/test_comparison_navigation.py`, `tests/comparison_navigation.cjs`

Hedef ID bir kez URL kodlanır ve güvenle çözülür; bozuk fragment güvenli kalır, geçmişten kaynakça odağı korunur. Gerçek kaynaklı izole fixture `%`, `%20`, `%ZZ`, Türkçe, boşluk, `#`, `?`, `/`, `&` ve tırnaklı teknik kimlikleri doğrudan ve karşılıklı bağlantılarda sınar. İlk literal `%` hatası `03-15-checks/percent-preview-red.log` içinde korunur. Renderer 21 frozen modülü gerçek HTML'yi byte-byte yeniden üretir.

### CR-04: Eski renderer sabiti

**Durum:** fixed  
**Commit:** `4d51cb1`  
**Dosya:** `tests/test_source_labels.py`

Aktif renderer için eski 18 sabiti kaldırıldı; kaynak/sürüm/atıf/arşiv davranışı ve ayrı tarihsel byte testleri korunur. Sentez downgrade testinin eski complete-stage fixture'ı `8f79e00` ile amaçlanan partial aşamaya sabitlendi.

## Bağımsız yeniden inceleme: temiz checkout fixture teslimi

5face6b incelemesinin yeni CR-01 bulgusu, 2fa77a4 ile kapalı altı yayın zinciri ve current işaretçisinin depoya alınmasıyla düzeltildi. Runtime, test veya araştırma içeriği değişmedi. Manifestteki tüm dosya özetleri teslim öncesi doğrulandı. Aynı `git ls-files` kapsamından açılan temiz Git arşivinde önce gerçek dosya eksikliği görüldü (`clean-fixtures-red-valid.json`), teslim sonrasında renderer 20/21 byte ve alan bazlı bölüm testi geçti (`clean-fixtures-green.json`). İlk RED kapsamı fixture dizinlerini açıkça istemediği için `clean-fixtures-red.json` superseded olarak işaretlendi; geçerli RED/GREEN ayrı korunur.

## Doğrulama ve devredilen işler

Tüm kontroller ana checkout'ta yapıldı. Final local release `27033583248b4951b3fe8e5fd6d77b9f`, renderer 22, HTML SHA-256 `60bafd3b384e020800a01b00a0c58beaf0392d1587d69e372c44667e4186cf3f`: publisher exit 0. Eski renderer 20/21 HTML hashleri ve veri sürekliliği `03-15-checks/continuity-v22.json` içindedir. `pre22-regressions.log`: 26 test geçti; final `navigation-v22.log`: 4 test geçti, gerçek file/HTTP × 360/1365 üzerinde 19'ar kontrol ve kaynak/arşiv başarılı. `screenshots-v22.json`: dört gerçek ekran, exit 0.

**Son bağımsız auditler geçti:** P2 ve P3 partial komutları gerçek `27033583248b4951b3fe8e5fd6d77b9f` sürümünde exit 0 ve `PHASE2_AUDIT_OK` / `PHASE3_AUDIT_OK` verdi. P3 partial, complete snapshot'ın complete korumalarını çalıştırdı. Immutable girdi özetleri değişmedi; kalıcı log/exit ve sonuç `03-15-checks/phase2-v22.*`, `phase3-v22.*`, `audits-v22-result.json` içindedir. Bağımsız kaynak incelemesi `6475e3b` ile clean olarak kaydedildi.

03-16 kaynak anlamı incelemesi, root tam global regresyonu, sekiz küresel gereksinim ve UAT/faz kapanışı tamamlanmamıştır. Durdurulan eski global regresyon geçiş olarak sunulmaz.
