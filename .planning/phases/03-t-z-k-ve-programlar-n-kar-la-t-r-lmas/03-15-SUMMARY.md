---
phase: 03-t-z-k-ve-programlar-n-kar-la-t-r-lmas
plan: "15"
subsystem: report
tags: [navigation, chromium, accessibility, immutable-releases]
requires:
  - phase: 03-14
    provides: Seçili v4 karşılaştırma, tipli sentez ve dokuz parti tabanı
provides:
  - Kaynak ve kapsam kanıtına erişen iki yönlü odaklı karşılaştırma gezintisi
  - Renderer 20 ile doğrulanmış yerel immutable rapor ve gerçek tarayıcı kanıtı
affects: [03-16, source-semantics, uat]
tech-stack:
  added: []
  patterns: [frozen-renderer-dispatch, chromium-devtools-viewport]
key-files:
  created: [src/rapor_v18.py, src/rapor_v19.py, src/rapor_v19.css, src/rapor_v20.css, tests/test_comparison_navigation.py, tests/test_phase3_stage_compatibility.py, tests/test_phase2_cli_audit.py, data/comparisons/03-navigation-checks.json]
  modified: [src/arsiv.py, src/rapor.py, README.md]
key-decisions:
  - Önceki 18 ve ara 19 rendererları ayrı dosyalarda byte-exact donduruldu; canlı sürüm 20 kullanıldı.
  - Partial audit isteği complete snapshot için complete kontrollerini uygular; Faz 2 CLI kendi tam auditini yapan doğrulayıcıya doğrudan gider.
requirements-completed: []
requirements-contributed: [KAR-01, KAR-02, RAP-02]
coverage:
  - id: D1
    description: Gerçek yerel yayında iki yönlü gezinme, odak, kaynak ve kapsam kanıtı
    verification:
      - kind: automated_ui
        ref: tests/test_comparison_navigation.py
        status: pass
    human_judgment: true
    rationale: Görsel ve kaynak anlamı değerlendirmesi 03-16 kapsamında sürer.
  - id: D2
    description: Geçmiş renderer korunumu ve final Faz 2/Faz 3 kısmi auditleri
    verification:
      - kind: integration
        ref: data/comparisons/03-navigation-checks.json
        status: pass
    human_judgment: false
actuals:
  tokens: 323281
  tasks: 2
  commits: 10
plan_head_before: 717df861ae50a32e43534c4df6754fb51d2c4885
duration: yaklaşık 3 saat
completed: 2026-11-15
status: complete
---

# Phase 03 Plan 15: Karşılaştırma Gezintisi Summary

**Sabit kaynaklı karşılaştırma, parti dosyası ve belge arşivi arasında odak ve geçmişi koruyan gezinme; renderer 20 ile yerel immutable rapor.**

## Accomplishments

- Final yerel release `ef353c40c60b400eb1c52b3245e9a65b`, renderer 20, schema 6, taxonomy 4, sentez sözleşmesi 2 ve complete karşılaştırma aşamasındadır. Okur yolu `data/releases/ef353c40c60b400eb1c52b3245e9a65b/index.html`; HTML SHA-256 `78e74311816f7b9903f11a49fc9b096487c8333f026c7e535654d2a8886ae014`.
- Aynı row kimliğiyle iki yönlü gezinti, doğrudan hash, odak, kaynak sürümü/konumu/arşivi, kapsam kanıtı ve geçmiş geri/ileri davranışı gerçek Chromium ile file ve loopback HTTP üzerinde 360 ve 1365 CSS piksel genişliklerinde sınandı. Her koşul 19 assertion geçti. Final görüntüler `03-15-checks/screenshots-final/` içindedir.
- Final `PHASE2_AUDIT_OK` ve `PHASE3_AUDIT_OK` kısmi istekle gerçek release üzerinde exit 0 verdi; kanıt, sonuç logları ve dört tarihsel HTML yeniden üretim hash'i `data/comparisons/03-navigation-checks.json` içindedir. `test_report.py` 11/11; aşama uyumluluğu 2/2; Faz 2 CLI 3/3 geçti.
- README yerel rapor, comparison komutları, kısmi/tam ayrımı ve kaynak incelemesinin sınırını açıklar. Kamuya yayın yapılmadı.

## Task Commits

- RED kanıtları: `87b1a6c`, `90a1518`, `efc6b10`; ilk iki RED kaydı seçili olmayan kimlik kullandığından geçersizdir, `efc6b10` seçili v4 row varlığını ve gerçek odak hatasını doğrular. Python unittest çıkışı gerçek çalışmadan Node yerleşik TAP sarmalayıcısıyla GSD kanıt biçimine taşındı; geçerli kanıt `03-15-checks/red.json`.
- Görev 1: `7a09b4e`, kapsam/citation odak düzeltmesi ve 19 freeze/20 sürümü `a1a8678`.
- Audit uyumluluğu RED/GREEN: `a8222aa`, `fe115e7`. Faz 2 yinelenen audit RED/GREEN: `c20cf3b`, `51f3b24`.
- Görev 2 gerçek yayın ve kanıt: `966b3bb`.

## Deviations from Plan

1. **[Rule 3 - Sürüm uyarlaması]** Planın eski 17→18 numaralandırması yerine mevcut 18 donduruldu. Ara 19 yayını `61b127ba1cb1479e9e6f55e6a6f40f5e` kabul edildikten sonra gerçek kapsam odağı hatası bulundu; 19 ve CSS19 korundu, düzeltme ayrı 20/CSS20 ile yayımlandı. Renderer 17 ve CSS16 değişmedi; 17, 18 ve 19 release HTML'leri byte eşitliğiyle yeniden üretildi.
2. **[Rule 1 - Odak]** Kaynaktan farklı kapsam kaydına geçiş eski citation odağını yanlış geri alıyordu. Dört gerçek tarayıcı başarısızlığı `03-15-checks/status-navigation-fail.log` içinde; renderer 20 hedef odağını korurken kaynak geçmişi dönüşünü de sınar.
3. **[Rule 3 - Audit uyumluluğu]** Complete sözleşmeli final release için partial isteği aşama eşitliğinde reddediliyordu. Önce gerçek hata/negatif test kaydedildi; fix complete kontrollerini aynen uygular ve complete isteğinde partial/tracer'ı reddeder. İlk başarısız ve düzeltilmiş loglar korunur.
4. **[Rule 3 - Mükerrer audit]** Faz 2 CLI, doğrulayıcının kendi tam auditinden önce aynı audit'i yeniden çalıştırıyordu. Yalnız ek `--check` bulunmayan Faz 2 yolu doğrudan tam audit ve tüm P2 kontrollerini yapan doğrulayıcıya yönlendirildi; diğer yollar değişmedi. Gerçek önce/sonra auditleri ve negatif çağrı testleri kaydedildi.

## Verification and Limits

- `python3 tests/run.py --pattern test_comparison_navigation.py`: final release, dört gerçek Chromium/viewport koşulu, exit 0.
- `python3 tests/run.py --pattern test_report.py`: son kodla 11/11, exit 0.
- `python3 tests/run.py --pattern test_phase3_stage_compatibility.py`: 2/2; `test_phase2_cli_audit.py`: 3/3.
- Final release `--phase 2`: hem önceki hem optimize CLI `PHASE2_AUDIT_OK`; `--phase 3 --stage partial`: düzeltilmiş kodla `PHASE3_AUDIT_OK`. İlk P3 başarısızlığı ve P2 eski/yeni kod snapshot ilişkileri checks dizininde korunur.
- 03-14 tam global paket 1800 saniyede zaman aşımına uğradı; bu bir tam geçiş değildir. Son global regresyon, kaynak anlamı/UAT ve faz kapanışı 03-16/root sorumluluğundadır. Bu özetin frontmatter gereksinimleri planın katkı alanlarını kopyalar; küresel gereksinimler burada tamamlandı işaretlenmedi.

## Self-Check: PASSED

Önemli dosyalar ve listelenen commitler mevcut; final release manifesti, gerçek tarayıcı sonucu, audit logları ve tarihsel renderer eşitlikleri doğrulandı.

## Exact-file acceptance correction

Önceki dört ortam testi release HTML'inin script eklenmiş geçici kopyasını açmıştı; bu sonuçlar gerçek etkileşim kanıtı olarak korunur ancak değişmez dosyanın doğrudan açıldığını kanıtlamak için geçersizdir. Önceki kanıt `03-15-checks/instrumented-navigation-checks.json` içinde saklandı. Yeni test, kapalı HTML'yi değiştirmeden CDP `Runtime.evaluate` kullanır ve kalıcı yardımcısı `tests/comparison_navigation.cjs` altındadır. Aktif taxonomy içindeki İYİ demokrasi ve yardım kampanyası kapsam satırları parti, konu, durum ve gerçek kaynak sürümü ölçütleriyle seçilir.

Yeni koşu `03-15-checks/exact-browser-run.json` ve `exact-browser.log` içinde: 2 test, dört gerçek viewport/protokol koşulu ve 19'ar kontrol exit 0. Tarayıcı doğrudan `file:///hpc/group/pfisterlab/mg551/storage/proje/data/releases/ef353c40c60b400eb1c52b3245e9a65b/index.html` ve o koşuda `http://127.0.0.1:44361/releases/ef353c40c60b400eb1c52b3245e9a65b/index.html` adreslerini açtı; istenen ve gerçekten açılan adresler kanıttadır. Her koşulda aynı browser gerçek yerel İYİ program arşivine giderek beklenen pasajı okudu; arşiv SHA ilişkisi de kontrol edildi. HTTP sunucusu yalnız test süresince çalıştı. Önceden geçen P2/P3, tarihsel renderer ve görsel kanıtları korundu; audit veya yayın tekrarlanmadı. `requirements-completed` boştur; üç kimlik yalnız katkı alanıdır, küresel koşullar 03-16 sonrasına açıktır.
