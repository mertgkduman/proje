# Faz 4 orkestrasyon kurtarma kaydı

## Önizleme testleri tamamlandı — 2026-11-21 08:12:52 UTC

62261875 aynı kaynak/test/yayın kimliğinde çalışıyor. Kapanış denetçisi gerçek çıkış dosyaları, günlükler ve önce/sonra kimlikleriyle genel **55/287** sonucunu doğruladı. `test_practice_preview` modülünde **18/18** gerçek başarı var. Modül ayrı süreçlerde tam keşfedilmiş ID kümesiyle çalıştı. 232 genel ID, tracer CLI ve Faz 2/3 kapanış denetimleri bekliyor.

- Fiziksel parti kökleri testi e74c8179581e44d2a0cb3fc2180fff2d, 2026-11-21T03:43:47.632621+00:00 zamanında exit 0 ve eşleşen kimlikle kapandı. Diğer üç önizleme testi ardından geçerek modülü tamamladı.
- Replay negatifleri şu ana dek kaynak yol sınırı, kabul edilmiş katkı değişikliği, geçersiz hedefli alias ve sahte okuma kökeni için exit 0 / kimlik eşleşmesi verdi. Doğrulayan kaynağın kendisi `fresh-gate-events.jsonl` ve batch log/exit dosyalarıdır.
- Açık batch 13cabc2023994f62b99318170e3f42cf, `test_lost_alias_rejected`, 08:06:42 UTC başladı. Slurm 62173687 ve 62262262 bağımlılık sırasını bekliyor. Plan/faz 2/15 ve 04-03 SUMMARY bekliyor.

## Slurm koşusunda doğrulanan sonuçlar — 2026-11-21 02:12:05 UTC

62261875 etkin. Geçerli 083475eeaf93e3b034722e3bf702e41598952e29144ce19b376d3cf116bff8e4 kimliğinde 47/287 gerçek başarı var. Kapanış denetçisi bütün mevcut sıfır çıkışları, günlükleri ve before/after kimliklerini okudu; kalan 240 ID nedeniyle kapanışı reddetti.

- Kesintiden sonraki `test_new_source_end_to_end` batch 09713561827049fba28e05516e350f6e, 22:35:24 UTC test başarı kaydı, exit 0 ve eşleşen kimlik. Ardından dört kısa preview kontrolü aynı koşuda geçti.
- `test_public_merge_distinct_and_unresolved_preserve_references` batch 0337e9409b5244e99320d12864069052, 00:06:46 UTC exit 0 ve eşleşen kimlik.
- `test_public_merge_rejects_bad_digest_and_conflicting_decisions` batch db4dcb0c7a0b4d2fa34e172f81bdc72c, 01:14:54 UTC exit 0 ve eşleşen kimlik.
- Açık batch e74c8179581e44d2a0cb3fc2180fff2d, `test_public_merge_separate_party_physical_roots`, 01:14:55 UTC başladı. Yeni durum için canlı JSONL ve Slurm kayıtlarına bakın.
- 62173687 ve 62262262 önceki bölümdeki sıra ile bağlı. Kapanış betiği denetlenmiş tracer kopyasını Faz 2/Faz 3 denetimlerinden önce kalıcı olarak saklar (3ef0e60). Üretim/test dosyaları, plan ilerlemesi ve kanonik yayın kimliği aynı kalır.

## Slurm iş sırası — 2026-11-20 21:05:22 UTC

- 62261875 çalışan seri regresyondur. 40/287 gerçek başarıdan devam etti. Konak değişiminde kesilen test yeni batch 09713561827049fba28e05516e350f6e altında tekrar başladı. Önbellekler isteğe bağlı çalıştırma girdileridir ve eski sonuçların kaydedilmiş fixture bağları korunur.
- Önceden tutulan 62173687 işi aynı taksonomi testini kendi geçici DATA ağacında çalıştırır. Betiği doğrulandı. İş 62261875 sona erdikten sonra başlayacak şekilde `afterany` bağımlılığıyla serbest bırakıldı; alttaki eski held bilgisi tarihsel gözlemdir. Başarı ölçütü kendi gerçek test günlüğü, sıfır çıkış ve kaynak/yayın kimliğidir.
- 62262262 (`gsd04-closeout`) yalnız 62173687 sıfır çıkışla bitince çalışır. `fresh_slurm_closeout.py` 287 benzersiz başarıyı gerçek batch çıkışları ve değişmez kaynak/yayın kimliğiyle doğrular. Seri iş dış test açıkken `coverage incomplete` ile çıkabilir; bu tek başına başarılı bir suite değildir. Kapanış betiği eksik veya yinelenen test sonucuyla denetimlere geçmez.
- Regresyon tam ise sırayla sözdizimi kontrolü, gerçek tracer CLI, Faz 2 audit ve Faz 3 complete audit çalışır. Tracer üretiminin normal DB/JSON/HTML/manifest denetimine ek olarak iki görünümün tracer bağlantıları ve yerel kaynak dosyaları kontrol edilir. Çıkışlar ve günlükler `closeout-62262262-*`, sonuç `closeout-62262262.json`; başarılı preview kopyası `data/.staging/gsd-04-03-tracer-preview-62262262`. Bu işler plan veya faz sayaçlarını veya SUMMARY'yi kendiliğinden ilerletmez.
- Kapanışın eksik kanıtı reddetme yolu canlı 40/287 ledger üzerinde doğrulandı. Test kimliği 083475eeaf93e3b034722e3bf702e41598952e29144ce19b376d3cf116bff8e4. Yeni başarılı sonuç bulunmadan 04-03 tamamlanmış sayılmaz.

## Güncel kurtarma — 2026-11-20 21:00 UTC

- Yeni makinede önceki gözetici, test ve `fd0afd4cd1ea4ded872bc86118b9dd2c` batch çıkışı yoktu; bu batch `batch_abandoned` olarak kaydedildi ve kredi verilmedi. 16 başarılı batch'in her birinin gerçek `OK` günlüğü, sıfır çıkış dosyası ve kaynak/yayın kimliği kontrol edildi: 40/287 ID. R1 merge fixture SHA `444aecf81f9c0f33033f45eb16a95adcb8ecd6085d8c4db7a3c233c5d1bed601`; eski accepted manifest ve replay fixture kimlikleri eski olaylarda korunur, yeniden üretilmiş gibi gösterilmez.
- `fresh_gate.py` kurtarma uyarlaması geçmiş batch'lerin tam kimliğini doğrular; yeni testlerde mevcut kaynak/test/yayın kimliğiyle çalışır ve artık kayıp, yalnızca isteğe bağlı `/tmp` fixture dosyalarını zorunlu kılmaz. Testlerin desteklediği önbelleksiz yollar ve özgün assertion'lar kullanılır. Kanonik manifestin DB/JSON/HTML özetleri, DB baseline ve kilit yokluğu her batch öncesi/sonrasında kontrol edilir. Kaynak/test fingerprint'i değişmedi; keşif doğrulandı ve 10.800 saniyelik batch sınırı korunuyor.
- Slurm **62261875** `gsd04-gate-resume`, common, 2 CPU/8 GiB, 2 gün üst sınırla **RUNNING**; `fresh_slurm_resume.py` gerçek supervisor çıkışını `fresh-slurm-62261875.exit` dosyasına kaydeder. Başlangıçta 40/287 kredi saptandı; yeni batch `09713561827049fba28e05516e350f6e`, `test_new_source_end_to_end`, 20:59:59 UTC'de gerçekten başladı. Job, batch ve olay durumunu kontrol etmeden tekrar başlatmayın. Gözetici çalışırken aynı dosyaları değiştirmeyin ve başka kanonik test yazıcısı açmayın.
- Ayrı tutulmuş taksonomi işi **62173687** `JobHeldUser`; diğer seri testler bittikten ve gerçek Slurm betiği/kimliği yeniden incelendikten sonra ele alınacak. İşi şimdi serbest bırakmayın. Genel gate tek dış ID beklerken tamamlanmış sayılmaz; tracer, Faz 2/Faz 3 audit ve son kanonik özetler de bekler. 04-03 SUMMARY/sayaç henüz güncellenmedi. Test fixture değişiklikleri korunuyor; commit yapılmadı.

## Güncel gözlem — 2026-11-20 17:39:03 UTC

Bu bölüm önceki gözlemlerden yenidir; canlı JSONL/çıkış dosyaları sonraki sonuçlar için otoritedir.

- Aynı `/root/phase04_gate_recovery` etkin; kaynak/test fingerprint'i `083475eeaf93e3b034722e3bf702e41598952e29144ce19b376d3cf116bff8e4` değişmedi. 287 benzersiz ID / 295 ham görünüm içinde tam sıfır çıkışlı, kimliği eşleşen batch kredisi **40/287**.
- `test_inherited_reading_is_pending_after_partial_merge` bu güncel kapıda gerçek exit 0 ile geçti; önceki hedefli sonucu yerine kredi edilmedi. Önizleme kontrolleri ilerledi; `test_merge_same_event_preserves_base_event_and_is_order_independent` batch `b170987664e6418c92d45b955b4f99bc`, `2026-11-20T17:00:51.468959+00:00` zamanında exit 0 / identity_ok true ile bitti.
- Şimdi `test_practice_preview.PracticePreview.test_new_source_end_to_end` çalışıyor. Batch `fd0afd4cd1ea4ded872bc86118b9dd2c`, başlangıç `2026-11-20T17:00:51.671626+00:00`. Son yürütücü gözleminde test PID `704815`, gerçek `practice-merge` çocuk PID `708139` canlıydı; bu gözlemde sonuç veya batch sonu yok. Bu testi tekrar başlatmayın.
- Wrapper `389626` / supervisor `389629` aynı koşuyu sürdürüyor. Güncel kanıt `fresh-gate-events.jsonl`, `fresh-fd0afd4cd1ea4ded872bc86118b9dd2c.log`, `fresh-supervisor-v3.log`; sözleşme `fresh-gate-contract.json`. Eski parmak izi sayıları veya hedefli loglar bu kapıya kredi olmaz.
- Plan/faz hâlâ **2/15**. Kalan bütün ID'ler, dış Slurm taksonomi ID'si (`62173687`, eylem öncesi gerçek durumu yeniden kontrol edin), tracer, Faz2/Faz3 audit'leri ve değişmez kanonik özetler kapanmadan 04-03 SUMMARY/sayaç ilerletilmez. Parti araştırma planları başlamadı.
- Kök yalnız bu devam notunu güncelledi. Diğer kaynak/test, ham arşiv, kanonik yayın ve canlı süreçlere müdahale edilmedi.

## Güncel gözlem — 2026-11-20 14:56:12 UTC

Bu bölüm önceki anlık görüntülerin yerini alır; yeni sonuçlar için canlı JSONL ve gerçek çıkış dosyaları otoritedir.

- Aynı `/root/phase04_gate_recovery` typed yürütücüsü etkin. Genel kapının güncel fingerprint'i `083475eeaf93e3b034722e3bf702e41598952e29144ce19b376d3cf116bff8e4`: 287 benzersiz ID / 295 ham görünüm. Tam bitmiş, sıfır çıkışlı ve kimliği eşleşen batch'lerden kredi **32/287**. Eski fingerprint sonuçları taşınmadı.
- Riskli gerçek R1 merge ve digest/provenance ile bağlı replay ilk iki batch olarak geçti. Ardından content 3, contract 4, coverage 6, legacy 6, merge-engine 8 ve persistence 3 ID geçti; ilk iki ID ile toplam 32.
- Canlı batch `a01b1c6241054047aa0066e264aa060c`: `test_practice_pending_integration.PracticePendingIntegration.test_inherited_reading_is_pending_after_partial_merge`. Çocuk PID `664983`; başlangıç `2026-11-20T14:31:44.253644+00:00`. Bu gözlemde sonuç veya batch sonu yok; başarı sayılmaz ve tekrar başlatılmaz.
- Ayrılmış wrapper PID `389626`, supervisor PID `389629`. Sözleşme `fresh-gate-contract.json`, kanıt `fresh-gate-events.jsonl` / `fresh-supervisor-v3.log` / `fresh-a01b1c6241054047aa0066e264aa060c.log`. Native oturum kaybolsa da önce bu süreçleri ve kalıcı çıktıları kontrol edin.
- `tests/test_practice_pending_integration.py` ve `tests/test_practice_merge_persistence.py` teknik fixture düzeltmeleri hâlâ korunacak değişikliklerdir. Persistence tek hedefli v2 gerçek exit 0 (3704.998 s), inherited tek hedefli v2 gerçek exit 0 (5124.366 s) verdi; bunlar fresh gate yerine kredi edilmedi. Persistence bu güncel gate'te ayrıca 3/3 geçti; inherited şu anda yeniden çalışıyor. Üretim denetimleri ve assertion'lar korunuyor.
- Slurm `62173687` kendi tutulmuş taksonomi işi olarak sonraya bırakılmıştır; koşu/ağır denetimler bitmeden bırakılmaz veya kopyası gönderilmez. Son gerçek durumunu eylem öncesi yeniden kontrol edin.
- Kök yalnız bu orkestrasyon notunu güncelledi; kaynak/test dosyalarına veya canlı testlere müdahale etmedi. Plan ve faz ilerlemesi hâlâ **2/15**; 04-03 birleşik kapısı, tracer ve Faz2/Faz3 audit'leri bitmeden SUMMARY/sayaç ilerletilmez.

## Sonraki güncelleme — 2026-11-20 04:28:47 UTC

Bu bölüm aşağıdaki ilk kurtarma anlık görüntüsünden daha yenidir; canlı JSONL/çıkış dosyaları yine otoritedir.

- İlk kurtarma koşusu `dd9...5cc85` fingerprint'inde 190 gerçek ID'yi tam batch olarak doğruladıktan sonra `test_practice_merge_persistence` grubunda exit 1 ile durdu. Bu gruptaki iki kısmi başarı kredi değildir. Eski 57 dosya / 26 batch kanıtı `fresh-dd9-persistence-failure/` altında korunuyor.
- Hata teknik fixture'dadır: R2 gerekçesi R1'den aynen kopyalıydı ve paket normal doğrulayıcısının istediği bütün seçilmiş/etkilenmiş okuma hedeflerini sağlamıyordu. Yürütücü yalnız `tests/test_practice_merge_persistence.py` örneğini, gerçek snapshot'tan gereken hedef/pasaj/sürüm kümelerini türetecek ve olay R2 gerekçesini ayıracak şekilde düzeltiyor. Üretim denetimleri ve assertion'lar kaldırılmadı. Değişiklik henüz doğrulanmış veya commit edilmiş değildir; önceki 190 sonuç gelecekteki yeni fingerprint'e kredi olmaz.
- Mevcut tek hedefli gerçek koşu: `/tmp/gsd-04-persistence-revision-v2.log` ve `.exit`; Python sarmalayıcı PID `3906750`, timeout PID `3906751`. Son gözlem 39m16s, süreçler canlı, yalnız test başlangıç satırı var; sonuç/exit dosyası yok. Sarmalayıcı gerçek çıkışı bekleyip kaydeder. Bu koşuyu tekrar başlatmayın.
- Önceki hedefli v1'in kabuğu kesildi; süreç daha sonra unittest ERROR verdi, güvenilir dış çıkışı olmadığından yalnız tanıdır ve başarı kredisi yoktur. Yeni v2 gerçek gözeticiyle çalışıyor.
- `tests/test_practice_pending_integration.py` içindeki önceki test-only aşamalama düzenlemesi de hâlâ commit edilmemiştir. Yeni kapıda gerçek R1 merge ve ona digest/provenance ile bağlı R1 replay **ilk iki batch** olarak ardışık koşulacak; sonra diğer ID'ler. Geçerli ilk merge sonucu kaydedilmeden replay çıktısı varsayılmaz.
- Slurm `62173687` aynı kendi işimizdir ve tutulmuştur; başka iş gönderilmedi veya ek test yazıcısı başlatılmadı. Bütün kontroller, yeni tam regresyon, gerçek tracer ve Faz2/Faz3 audit'leri bitmeden 04-03 SUMMARY/sayaç ilerletilmez. Faz hâlâ 2/15'tir.
- Yeni native yürütücü `/root/phase04_gate_recovery` çalışıyor. Ajan yine kaybolursa süreç/kanıt durumunu yeniden kontrol edin. Aşağıdaki ilk snapshot'taki PID'ler ve sıfır kredi bilgisi artık tarihsel gözlemdir; onları otomatik yeniden başlatma talimatı saymayın.

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
