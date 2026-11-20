# Faz 4 orkestrasyon kurtarma kaydı

Gözlem zamanı: 2026-11-20 01:42:46 UTC. Bu dosya bir kurtarma anlık görüntüsüdür; sonraki gerçek sonuçlar için `fresh-gate-events.jsonl` ve çıkış dosyaları otoritedir.

## Amaç ve yürütüm

Kullanıcının `$gsd-execute-phase 4` isteği devam ediyor. Faz 4'te 15 plan / 7 dalga var; 04-01 ve 04-02 tamamlandı, 04-03 Task 2 birleşik kabulü açık. Parti araştırma planları 04-04–12 henüz başlamadı. Bu teknik çalışmalardan siyasi araştırma veya insan kabulü sonucu çıkarılmaz.

Kök: `/hpc/group/pfisterlab/mg551/storage/proje`; dal: `gsd/phase-01-kapsam-yontem-pilot`. Her değişiklikten önce ve her commit'ten önce `/tmp/gsd-phase04-root-pin.sh` çalıştırılır. Yürütüm bütün faz için `ISOLATION=none`; elle worktree veya paralel test yazıcısı açılmaz. Geçerli GSD yürütücüsü GPT-6.1 Terra/high; ağır araştırma/verifier için kullanıcının son tercihi yapılandırılmış GPT-6.2 Sol/xhigh. Otomatik Astra yok.

Daemon yeniden başladıktan sonra eski native ajanlar kayboldu, ayrılmış test süreçleri kaldı. Yeni `/root/phase04_gate_recovery` typed executor mevcut koşuyu devraldı; yeniden başlatma yapılmadı. Ajan kimliği de yeniden kaybolursa önce süreçleri ve dosyaları kontrol edin.

## Yaşayan koşu: tekrar başlatmayın

- Gözetici sarmalayıcı PID `3848481`, ana gözetici `3848487`, ilk test `3848527` gözlemde canlıydı.
- Batch: `9551972f3b8b4c9e9e8b5b6d9543c9bd`.
- Test: `test_practice_pending_integration.PracticePendingIntegration.test_public_merge_preserves_accepted_r1_as_pending`.
- Son gözlem yaklaşık 86 dakika; henüz test sonucu veya batch sonu yoktu. Bu anlık görüntüde yeni kapı kredisi **0/287**.
- Sözleşme: `fresh-gate-contract.json`; fingerprint `dd9dbcf91142854bd5a98ae4fe39528c904a3ede9194f8a8ffd4b6af49f5cc85`.
- Keşif: 287 benzersiz ID / 295 ham görünüm. Sekiz imported MergeEngine sınıfı tekrarı açıkça kaydedildi; çift sonuç kredisi yok.
- Canlı kanıt: `fresh-gate-events.jsonl`, `fresh-supervisor-v3.log`, `fresh-9551972f3b8b4c9e9e8b5b6d9543c9bd.log`; süreç yöneticileri `fresh_gate.py`, `fresh_wrapper.py`.
- Her batch 10.800 saniyeyle sınırlı; gerçek sıfır çıkış ve eşleşen önce/sonra kimlik olmadan kredi yok. Ayrılmış sarmalayıcı gerçek gözetici çıkışını bekleyip diske yazar. Eski native exec oturum ID'leriyle yeni ajandan poll yapılamaz.

Önceki `deaff...` fingerprint'ine ait 163 başarı güncel kapıya kredi değildir. Çok partili içerik fixture başlığını düzelten `8638c1b` test dosyasını değiştirdi; yeni kapı sıfırdan başladı. Eski sonuçlar `fresh-pre-content-fix-evidence/` altında tutulur. Önceki timeout/kesinti kanıtlarını silmeyin.

## Bekleyen Slurm işi

Kendi işimiz `62173687`: `common`, 2 CPU / 8 GiB, test çocuk süresi 10.800 saniye; scheduler kapanış payıyla 03:10. Gözlemde `PENDING (JobHeldUser)`; önce `AssocGrpCpuLimit` nedeniyle beklediğinden seri koşuyla aniden eşzamanlı başlamaması için tutuldu.

İş `taxonomy_slurm.py` ile tam `test_completion_coverage.CompletionCoverageTest.test_same_taxonomy_sourced_revision_round_trip` ID'sini değiştirilmeden çalıştıracak. Paylaşılan app-server cgroup'unda iki deneme `-9` ile kesildi; ikincisinin aralığında `oom_kill` 7→8 arttı, fakat sayaç tek başına PID kanıtı değildir. Kesintiler başarı veya timeout değildir. Test kaldırılmadı; açık external-pending olarak sona bırakıldı.

Diğer seri testler ve ağır denetimler bitmeden işi bırakmayın veya ikinci bir iş göndermeyin. Sonrasında kendi tutulan işini release edip gerçek sonucu, süreç çıkışını, kaynak/test/yayın kimliğini ve DB/JSON/HTML byte özetlerini önce/sonra bağlayın. Taksonomi testi hesap düğümünde kendi yerel temp ağacını üretir; ilgisiz app-server `/tmp` fixture'larının varlığını varsaymaz. Eksik tek ID varken genel kapı tamamlanmış değildir.

## Devralınacak değişiklikler ve kalan kontroller

`tests/test_practice_pending_integration.py` henüz commit edilmemiş test altyapısı düzenlemesidir. Gerçek public merge ve public replay ayrı, provenance/digest ile bağlı aşamalardır. Gerçek ordinary audit, DB→JSON, R1 korunumu/pending, strict kaynak kontrolü ve complete reddi dahil özgün assertion'lar korunur. Geçici accepted S1 tam audit edildikten sonra yalnız geçici arşiv current=S1 yapılır; kanonik current değişmez. Üretim bypass'ı veya yeni production API yok. Replay ve birleşik kapı geçmeden bu düzenlemeyi tamamlandı saymayın veya geri almayın.

Tam yeni kapı, bütün preview/source-review/merge/coverage ve diğer keşfedilmiş ID'leri kapsar. Kaynak/test dosyası değişirse önceki fingerprint kredisi geçersiz olur. `.planning` içindeki yalnız orkestrasyon notları kaynak/test fingerprint'ini değiştirmez. Ortak fixture yeniden kullanımı sonuç kredisi değildir; gerçek public çağrıdan üretim ve tekrar doğrulama şartları korunur.

Sonrasında planın gerçek tracer komutu, current Faz 2 audit ve current Faz 3 complete audit'i gerekir. Tracer hedefi `/tmp/gsd-04-03-tracer-preview` eski görev çıktısıysa başarılı yeniden koşudan önce benzersiz yedeğe taşınır; eski çıktı veya ilgisiz dosya silinmez. Bütün kontroller gerçekten geçince 04-03 SUMMARY ve sıralı SDK takibi 3/15'e ilerler; fazın bütünü veya araştırma gereksinimleri tamamlanmış sayılmaz.

**Dalga kapısı düzeltmesi:** `54f2699` / `b7b17c1`, ardışık dalgaların genel regresyondan muaf olduğu eski yanlış yorumu düzeltti. `04-WAVE-TESTING.md` ve ana execute-phase workflow uyarınca seri son plandan sonra da genel test kapısı gerekir. Wave 2 `regression_pending`; güncel kapı Wave 2/3 açığını Wave 4 öncesi kapatır. Geçmişte Wave 2 genel paketi çalışmış gibi yazılmaz. Faz sonunda ayrıca yeni genel regresyon ve workflow doğrulamaları gerekir.

## Kanonik durum ve korunacak dosyalar

Kurtarmada 95 kaynak/test dosyasının sözleşmeye eşitliği ve şu gerçek dosya özetleri doğrulandı; yazıcı kilidi yoktu:

| Dosya | SHA256 |
|---|---|
| current pointer | `5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7` |
| DB | `9151c3055f2d53572b9b116ac6799b0a6cfa10d0ca9d7431dc6787ad15c68f5b` |
| JSON | `2dbd097af27060cdb5818570faa9620bbcf492465734294d1633c07fcc9aa617` |
| HTML | `96b87ce3daf43c10e5f48514daec89d98b82c5824bfb9439f5effe4121f54238` |
| manifest | `fb954f92e57ffe768c3cc63c065c8b7dc55a788af9f91dd5c56a8ff02172eb6b` |

Release `f67ca0a35e634035bf3aa83a46571f50`. Frozen renderer 24/25/26, CSS24 ve özgün baytlar değişmez; active renderer27/CSS25. Eski per-batch sözleşme ayrıca her DB/JSON/HTML hash'ini tutmuyordu; kaydedilmemiş ara hash'ler varmış gibi gösterilmez. Slurm helper gerçek üç hash'i kaydeder.

`.gsd/`, `.planning/milestone.lock`, Faz3 `ROOT-ACTIVE-HANDOFF.md`, `.planning/ui-reviews/`, `data/.staging/` ve bütün güncel test/timeout/kesinti dosyaları korunur. Stash/reset/clean yapılmaz. Yeni kanonik yayın, push veya deploy yok. Testler sırayla yazıcı kilidi alabilir; bitişte gerçek kanonik özetler ve kilit yokluğu yeniden doğrulanır.
