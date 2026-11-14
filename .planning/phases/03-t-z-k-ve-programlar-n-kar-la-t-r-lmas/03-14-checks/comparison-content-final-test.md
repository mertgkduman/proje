# Son GREEN comparison-content modül testi

- Komut: `python3 tests/run.py --pattern test_comparison_content.py`
- Kod ve testlerin Git HEAD'i: `7076a9392fa556af10c176892a4e071808fb5e45`
- `src/arsiv.py` SHA-256: `72a15137b0d8e4b7890aefd95ae5f61574393dd57383fdfca6630f4f1d0f552b`
- `tests/test_comparison_content.py` SHA-256: `e3061c430356095f079f0149a5bba494936b610ac0ecb08c2457cccae4caf9ba`
- Sonuç: 27 test, 129.141 saniye, çıkış 0. R17 ve R18 eski snapshot byte eşitliği ve sabit v2/sonraki sürüm testleri dahildir.
- Kalıcı yerel süreç kaydı: `/tmp/gsd-0314-content-final.run.json`; çıktı: `/tmp/gsd-0314-content-final.log`; çıkış: `/tmp/gsd-0314-content-final.exit`. Girdi ve kod hash'leri süreç başlatılmadan kaydedildi.
- Önceki 27 testlik koşuda dört fixture varsayımı başarısız olmuştu; `da2c1c6` yalnız ilgili sabit sürüm ve sıralama varsayımlarını düzeltti. Bu sonuç önceki başarısız koşunun üzerine yazılmadı.
