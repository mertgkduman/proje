# 04-03 devam: Task 1 tamamlandı, Task 2 bekliyor

## Konum ve kanıt

- `04-03-01` tamamlandı: RED `72bbf93`, uygulama `55bf41f`. `04-03-SUMMARY.md` oluşturulmadı; plan sayacı ilerletilmedi.
- Görev sonrası tracer kapısı: `python3 tests/run.py --pattern test_practice_coverage.py`, 5/5, çıkış 0, 282 saniye; `/tmp/gsd-04-03-01-tracer-feedback.log` ve `.exit`. Öncesindeki gerçek DB → JSON dosyası → iki HTML görünümü kabul koşusu da 5/5, çıkış 0: `/tmp/gsd-04-03-01-precommit-json.log` ve `.exit`. Tracer verified end-to-end.
- `python3 src/arsiv.py audit --release current --phase 2`: `PHASE2_AUDIT_OK f67ca0a35e634035bf3aa83a46571f50`, çıkış 0; `/tmp/gsd-04-03-01-phase2-audit.log` ve `.exit`.
- `python3 src/arsiv.py audit --release current --phase 3 --stage complete`: `PHASE3_AUDIT_OK f67ca0a35e634035bf3aa83a46571f50`, çıkış 0; `/tmp/gsd-04-03-01-phase3-audit.log` ve `.exit`.
- `practice-coverage --inventory data/practices/04-inventory.json --input data/practices/04-coverage-tracer.json --party yeni-parti`: `PRACTICE_COVERAGE_OK`, çıkış 0; `/tmp/gsd-04-03-01-cli-final.log` ve `.exit`. 610 hücrede `organ-secim-yontemi` olay hücresi `open`, söylem hücresi `not_researched`.
- Current `f67ca0a35e634035bf3aa83a46571f50`; global `data/.write.lock` yok. Yeni public release, insan kabulü veya tamamlanmış parti araştırması üretilmedi.

## Kapsam ve sürüm sözleşmesi

Envanter current snapshot'ın son tamamlanmış seçimi, `scope_party`, doğrulanmış kuruluş gözlemleri ve yöntem kesiminden türetilir: 305 seçili konu, dokuz parti, 5.490 statement/event hücresi, 1.729 seçili kaynak koleksiyonu ve `2026-11-10T14:38:46.154751+00:00` kesimi. Bu sayılar sabit kod değildir. `data/practices/04-inventory.json` başlangıç durumlarını taşır; durumlar kanıt geçmişinden hesaplanır. Uzantı konuları için dokuz partiye iki türde geri tarama hücresi açılır; Faz 3 taxonomy/selection değiştirilmez.

`04-03-PLAN.md` Kural 3 düzeltmesi geçerlidir: gerçek `0105-organ-closure` yalnız ilan edilen eski sorguları kapsar, artık belirsizlikler taşır ve eski konu sonra yeniden açılmıştır. `0105-cesme-access` / `0105-cesme-v1` ve kaynaklı olay ilişkisi köprüyle saklanır; daha geniş Yeni Parti hücresi **açık** kalır. Eski kapanış tam kapsamlı `practice_closure` sayılmaz. Diğer partilerin tarandığı varsayılmaz. Çeşme haberindeki 630/1113 ve yüzde 86 çelişkisi ile ön seçim / nihai kongre sınırı önceki kayıtlardaki atıfla korunur.

`src/uygulamalar.py` içindeki `PRACTICE_COVERAGE_TABLES`, önceki variant-v1 tablolarını değiştirmeden append-only `practice_scope_v2`, lead/candidate revizyonları, `practice_closure`, `practice_reopen`, kaynaklar, topic extension, inventory revision ve kaynaklı legacy köprüleri ekler. `build_practice_inventory`, `validate_practice_coverage`, `validate_practice_closure`, `practice_coverage_states`, `practice_manifest_fields` ve `validate_practice_descent` ortak kurallardır. `practice-inventory` ve `practice-coverage` `src/arsiv.py` içindeki gerçek parser/handler'dır. `practice-check --inventory` yeni markerı veya eski paket biçimini uygun sözleşmeyle denetler. Yeni kaynak, kapanıştan sonra gerçek reopen kaydı olmadan kapalı kalamaz; eski kapanış değişmez. `no_result`, mevcut attempt/missing zincirine bağlıdır. Legacy köprülü kapsam kapanırken ilgili aynı-parti eski uç ve adaylar atlanamaz. `--complete` bütün kanonik hücreleri gerektirir.

`data/practices/04-coverage-tracer.json` var olan gerçek satırları ve yalnız gerçek sınırlı köprüyü taşıyan yeni pakettir. Tarihsel `data/practices/04-tracer.json` değiştirilmedi. `practice_scope_v2.id` envanter cell_id'sidir; array alanları SQLite kayıtlarında JSON metnidir. Rapor scope durumunu, geçmişi, uç ve aday gerekçelerini ve yetkili pasaj bağlantılarını iki görünümde gösterir. Tam kapanış, yanlış parti, sahte `no_result`, pending uç, daraltılmış evren, marker kaybı, yeni sürümle reopen ve dokuz-parti uzantısı testleri geçici teknik örneklerle sınanır; bunlar siyasi araştırma değildir.

## Sıradaki görev: 04-03-02

`04-03-PLAN.md` Task 2'yi yeni bağlamla yürüt: bağımsız `practice-preview`, `practice-merge`, `practice-source-check`; explicit storage-root izolasyonu, source-review ve kaynaklı event decision/alias/merge provenance; deterministik merge ve bütün ilişki/katkı/pasaj başvuruları; negatif digest/alias/karar ve global current/lock testleri. Task 2 kapsamını Task 1'den türetme.

Planın gerçek preview komutu tarihsel `04-tracer.json` girdisini adlandırır; bu paket eski tabana ve eski dar tracer biçimine sahiptir. Onu değiştirmeden destekle ve 04-inventory'nin kanonik kapsam doğrulamasını gevşetme; gerektiğinde `04-coverage-tracer.json` ile kaynaklı sürüm geçişini açık ve denetlenebilir biçimde bağla. Önizlemeyi global current/lock/DB yazmadan geçici kökte üret. Task 2 tamamlandıktan sonra tam plan SUMMARY, STATE/ROADMAP güncellemesi ve metadata commit yapılır. Geniş faz regresyonu yalnız faz sonunda orkestratörün `04-WAVE-TESTING.md` protokolündedir.
