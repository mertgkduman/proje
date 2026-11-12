# Faz 02 — Tamamlanmış teslimin yerel yenilemesi

**Tarih:** 2026-11-12  
**Önceki sürüm:** `bcc67d04d9d741e191589d0f5ac173ca` (üretici 13)  
**Yeni sürüm:** `1d6b49b307f04a258c1a11d90978fe7c` (üretici 14)  
**Kod commit:** `353a5ee`  
**Yerel yayın commit:** `72b6908`

Tamamlanmış teslim sırası korunarak okuyucu raporu açık `--refresh` yoluyla yeniden üretildi. Manifestin `phase2_refresh` alanı `true`; `phase2_delivery` önceki sürümle birebir aynı ve son parti Demokrat, aşama `complete`. Yeni parti teslimi veya makbuz oluşturulmadı.

## Çalıştırılan komutlar ve sonuçlar

- `PYTHONPATH=src:tests python -m unittest -v test_dossiers.DossierTracer.test_refresh_requires_unchanged_completed_delivery test_dossiers.DossierTracer.test_publish_refresh_and_party_are_exclusive test_dossiers.DossierTracer.test_real_tip_publish_audit_html_and_receipt_in_isolated_data` — 3 test geçti; eksik/değişmiş sıra, değişmiş parti/aşama, işaretin kaldırılması ve `--party` ile `--refresh` birlikteliği reddedildi; olağan TİP teslim yolu geçti.
- `python src/arsiv.py workspace --scratch /tmp` — `/tmp/proje-work-rtgai83e`; taban sürüm önce uygulamanın kendi denetiminden geçti.
- `python src/arsiv.py publish --workspace /tmp/proje-work-rtgai83e --refresh` — `1d6b49b307f04a258c1a11d90978fe7c`. Yayın yolu faz 1 ve dokuz dosya doğrulamasını, politika ve geçmiş teslim denetimlerini işaretçiden önce uyguladı.
- `python src/arsiv.py audit --release 1d6b49b307f04a258c1a11d90978fe7c --phase 2` — `PHASE2_AUDIT_OK 1d6b49b307f04a258c1a11d90978fe7c`.
- Eski ve yeni `records.json` nesneleri `release_id` çıkarılarak karşılaştırıldı; tam eşit. Manifestlerde `phase2_delivery` tam eşit, `phase2_refresh=true`, `renderer_version=14` ve `base_release=bcc67d04d9d741e191589d0f5ac173ca` doğrulandı: `RECORDS_AND_DELIVERY_IDENTICAL`.
- `git diff -- data/objects data/views data/deliveries data/releases/bcc67d04d9d741e191589d0f5ac173ca` — boş; eski nesneler, görünümler, teslim makbuzları ve yayın değiştirilmedi. Önceden geçen sekiz makbuz denetimi tekrarlanmadı.

`data/current.json` yeni yerel sürümü gösterir. Bu işlem ağ yayını veya GitHub Pages dağıtımı içermez. `CR-09` için yalnız HTTP başlığında kalan UTF-8 dışı charset desteği hâlâ açık sınırlamadır; ayrıntı `02-REVIEW-FIX.md` içindedir.
