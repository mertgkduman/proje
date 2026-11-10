# Walking Skeleton — Türkiye Siyasi Partileri Araştırması

**Phase:** 1  
**Generated:** 2026-11-10  
**Durum:** Mimari yürütme sözleşmesi; uygulamanın çalıştığı henüz kanıtlanmadı.

## Capability Proven End-to-End

Kanıtlanacak yetenek: Okur Yeni Parti'nin gerçek Yargıtay kuruluş pasajından üretilen kısa özet ve alıntıyı görür; kaynak bağlantısını açıp özgün belgeye ve güvenli yerel kopyaya ulaşır. Yol, gerçek arşiv → SQLite yaz/commit/kapat/yeniden aç → JSON/HTML → tarayıcı tıklamasıdır. Kanıt sahibi `01-01-01` tracer görevidir.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Framework | Python standart kitaplığı, statik HTML/CSS/JavaScript | Kaynaklı arşiv/rapor için harici uygulama çerçevesi veya paket kurulumu gerekmiyor. |
| Data layer | `sqlite3`; yerel scratch'te tek yazıcı; kanonik kapalı SQLite release snapshot'ı | Depo NFS. Aktif DB yerel dosya sisteminde kalır; JSON ve HTML aynı kapalı DB'den türetilir. |
| Auth | Hesap/oturum servisi yok | Bu faz yerel dosya üretir; yerel önizleme yalnız `127.0.0.1` dinler. |
| Deployment target | Yalnız belgelenmiş yerel tam akış | Kamuya yayın/barındırma seçilmedi. |
| Directory layout | `src/arsiv.py`, `src/rapor.py`, `tests/`, `data/objects/`, `data/releases/` | İki küçük çekirdek modül, değişmez kaynaklar ve türetilmiş rapor ayrılır. |
| Source provenance | quote/summary ve fact/source_assertion/comment ayrı alanlar | Görünür üretim türü etiketi olmadan veri kökeni korunur. |
| UI route | `index.html`, `#party-{id}`, `#source-{id}`, `#scope-method` | Statik hash bağlantısı kaynak etkileşimini sağlar; HTTP uygulama endpoint'i gerekmiyor. |
| Test runner | `unittest` + sıfır testi reddeden `tests/run.py` + mevcut headless Chrome | Paket kurulumu yapmadan gerçek DB ve tarayıcı davranışı denetlenir. |

## Canonical Record and Recovery

`data/current.json` yalnız release işaretçisi taşır. Asıl düzenlenebilir kayıt, işaret edilen değişmez release'in `records.sqlite3` dosyasıdır; değişiklik için bu kapalı snapshot yerel scratch'e kopyalanır. Kalıcı JSON/HTML düzenlenmez. Tek-yazıcı kilidi ve base-release kontrolü ikinci yazıcının üstüne yazmayı önler.

Her işlem commit/close → aynı dosya sistemindeki staging'e snapshot → aynı snapshot'tan JSON/HTML → hash/FK/pasaj/link denetimi → değişmez release dizini → en son atomik current değişimi sırasını izler. Hata öncesi son doğrulanmış release tutulur. Pointer değişiminden sonra hata varsa manifest yeniden denetlenir. Bir release'in DB'si başka release'in raporuyla eşleştirilmez. Kurtarma son doğrulanmış kapalı snapshot'tan yeni scratch açar; çalışan süreç kontrol edilmeden kilit silinmez. NFS üzerinde WAL veya aktif eşzamanlı DB yoktur.

Özgün HTML `original.html.bin`, PDF `original.pdf` olarak korunur; `readable.html` kaynak metninin kaçışlanmış türevidir. Okur bu güvenli türevi açar; ham HTML yalnız indirilir. URL/protokol ve kök altı dosya yolları doğrulanır.

## Stack Touched in Phase 1

- [ ] Project scaffold — `01-01-01`: Python CLI, test runner ve yerel dizinler.
- [ ] Routing — `01-01-01`, `01-06-01`: gerçek `#source-{id}` yolu, doğru panel ve kaynak açılışı.
- [ ] Database — `01-01-01`: gerçek write/commit/close/reopen/read.
- [ ] UI — `01-01-01`: gerçek kaynak linki etkileşimi; statik DB türevi, harici API yok.
- [ ] Local full-stack run — `01-01-02`, `01-06-02`: workspace/record/publish/audit/serve akışı README'de; tracer ve tarayıcı testinde kanıt.

Yürütmeden sonra kullanılacak yerel komutlar: `python3 tests/run.py`, `python3 src/arsiv.py audit --release current --phase 1`, `python3 src/arsiv.py serve --host 127.0.0.1 --port 8000`. İlk komut sıfır testi reddeder; ikinci PHASE1_AUDIT_OK gerektirir; üçüncü yalnız geliştirme gösterimidir. İlk release üretme adımları görevlerde tanımlıdır ve uygulandığında README'ye yazılır.

## Out of Scope (Deferred to Later Slices)

Bu liste mevcut yol haritasının sınırıdır; Faz 1 kararlarını azaltmaz. Bütün partilerin gerçek beş başlıklı dosyaları Faz 2'de; partiler arası tüzük/program karşılaştırmaları Faz 3'te; geniş söylem/uygulama karşılaştırmaları Faz 4'te; bütün partilerin mali incelemesi Faz 5'te; tam güncelleme geçmişi ve nihai paylaşılabilirlik Faz 6'dadır. Kamuya yayın/barındırma kararı bu planlarda yoktur.

## Subsequent Slice Plan

- Faz 1 genişlemeleri: kapsam/kimlik/kesim → kaynak zinciri/eksikler → pilot belge/konu → pilot olay/mali → tam rapor kabulü.
- Faz 2: Aynı kanıt ve release protokolüyle dokuz partinin dosyaları.
- Faz 3–5: Aynı konu/aktör/dönem ve kanıt ilişkileriyle karşılaştırmalar.
- Faz 6: Sürüm/güncelleme geçmişi ve tam paylaşılabilir rapor.

Bu fazda dış tüketicisi/yayımlanmış şeması olmayan sürümlü yerel yapı kullanılır. Teknik seçimler geri alınabilir; gerçek bir one-way karar veya yeni onay kapısı yoktur. Model/effort eşlemeleri ve otomatik Astra yasağı korunur.
