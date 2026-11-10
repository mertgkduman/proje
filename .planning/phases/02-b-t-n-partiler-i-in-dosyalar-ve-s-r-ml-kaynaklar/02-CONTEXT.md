# Phase 2: Bütün partiler için dosyalar ve sürümlü kaynaklar - Context

**Gathered:** 2026-11-10 (America/New_York)
**Status:** Ready for planning

<domain>
## Phase Boundary

Okur, onaylanan dokuz partinin kuruluş ve temel bilgiler, tüzük, program, söylem–uygulama ve finansman–harcamalar başlıklarını aynı raporda açabilir. Temel kimlik bilgileri ve bulgular ilgili belge sürümüne kadar izlenir. Kaynak türleri ve erişilebilen belge geçmişi görünür. Faz 2, DOS-01, DOS-02, KAY-01 ve KAY-04 gereksinimlerini karşılar.

Faz 3 tüzük ve program karşılaştırmalarını, Faz 4 söylem–uygulama karşılaştırmalarını, Faz 5 mali araştırmayı, Faz 6 güncelleme akışı ve paylaşılabilir raporun tamamlanmasını kapsar.

</domain>

<decisions>
## Implementation Decisions

### Parti sırası ve ara teslimler

- **D-01** — İlk yeni dosya TİP için hazırlanır. Her parti bu fazın dosya ve kaynak doğrulama ölçütlerini karşıladığında yerel rapora ayrı bir teslim olarak eklenir ve sıradaki partiye geçilir. Yeni Parti dosyası için Faz 1 pilotu temel alınır.
- **D-02** — Yeni dosyaların hazırlanma sırası TİP → DEM Parti → İYİ Parti → Yeni Yol Partisi → Demokratik Bölgeler Partisi (DBP) → Emek Partisi (EMEP) → Saadet Partisi → Demokrat Parti.
- **D-03** — Raporun parti sekmeleri Yeni Parti → TİP → DEM Parti → İYİ Parti → Yeni Yol Partisi → DBP → EMEP → Saadet Partisi → Demokrat Parti sırasını izler. TİP ikinci sekmedir. Karşılaştırmalı Özet de ana sekmeler arasında yer alır. Bu sıra rapor sunumuna aittir.
- **D-04** — Her parti eklendiğinde kısa ara teslim, güncellenmiş rapor bağlantısını, eklenen içeriği ve önemli kaynak eksiklerini içerir.

### Belge sürümlerinin sunumu

- **D-05** — Bulgunun dayandığı belge sürümü önde görünür. Aynı belgenin erişilebilen diğer sürümleri, kaynağın yanındaki açılır geçmiş bölümünden incelenir. Her bulgu, dayandığı pasaj ve belge sürümüne bağlıdır.
- **D-06** — Kısa künye belge adını, kaynak türünü, belge tarihini ve sürümü gösterir. Künye açıldığında erişim ve doğrulama tarihleri, ilgili madde/sayfa veya pasaj ve özgün belge ile arşiv bağlantıları görünür.
- **D-07** — Belgenin ait olduğu dönem ve önceki sürümle ilişkisi, kaynaklar elverdiğinde kısa açıklamayla verilir. Kaynaklı yapay zekâ açıklaması koyu mavi, doğrudan aktarım siyah ve tırnak içinde gösterilir. Bu metinlerin kökeni de veri kaydında tutulur.
- **D-08** — Parti sekmesinin altındaki kaynaklar beş araştırma başlığına göre gruplanır. Belge geçmişi ilgili belgenin yanında, kaynak türü kısa künyede gösterilir. Bulgulardaki bağlantılar ilgili kaynak kaydını açar.

### Temel bilgi kartı ve kuruluş kronolojisi

- **D-09** — Sade bilgi kartı resmî ad, kısaltma, kuruluş tarihi, sicil kimliği ve doğrulanmış resmî siteyi içerir. Genel merkez ve genel başkan gibi diğer kaynaklı temel bilgiler Kuruluş bölümünde yer alır. Bilgiler ilgili kaynak ve tarihleriyle sunulur.
- **D-10** — Kuruluş bağlamı ve varsa ad değişiklikleri tarih sıralı kayıtlarla gösterilir. Her olay kendi tarihi ve kaynağıyla ayrı satırda yer alır.
- **D-11** — Kronoloji kuruluşu, belgelenmiş ad ve kısaltma değişikliklerini, tüzel statü kayıtlarını ve ilk kongre veya ilk yönetim gibi doğrulanabilen kuruluş adımlarını kapsar.
- **D-12** — Aynı adı taşımış ayrı bir partiye değinmek gerektiğinde kronolojinin yanındaki not, her iki tüzel kimliği kaynaklarıyla açıklar.

### Faz 1 yönteminin uygulanması

- Her parti kendi kaynakla doğrulanmış kuruluşundan itibaren incelenir. Kapsam kararı, tüzel kimlik, milletvekilinin parti üyeliği ve Meclis grubu ayrı kanıtlarla izlenir. Belge, olay, hesap dönemi, erişim ve doğrulama tarihleri kendi anlamlarıyla kaydedilir.
- Birincil kaynağa öncelik verilir. Gazetecilik, akademik çalışma ve bağımsız raporların türü künyede görünür. Olgu, kaynak beyanı ve yorum ayrımı ile kısa özet ve kısa alıntının birlikte sunulması Faz 1 kararlarına tabidir.
- Henüz incelenmemiş başlıklar “Henüz incelenmedi” olarak görünür. “Bulunamadı”, “Erişilemedi” ve “Doğrulanamadı” durumları belgelenmiş girişime dayanır. İlgili başlıkta gerekçe ve girişim tarihi gösterilir.

### Planlamaya bırakılan ayrıntılar

- Planlayıcı, parti dilimlerini mevcut arşiv ve rapor akışına bağlayacak planları ve doğrulama adımlarını belirler. Faz 1 yöntem kesiminin belge ve olay tarihlerine uygulanması araştırmada açıklanır.
- Belge sürümü ilişkilerinin veri yapısı, sekme sırasının temsili ve açılır künye bileşeninin tasarımı yukarıdaki davranışları sağlayacak şekilde planlanır.

</decisions>

<canonical_refs>
## Canonical References

Araştırma ve planlama bu dosyalara dayanır.

### Kapsam ve yöntem

- `.planning/ROADMAP.md` — Faz 2 hedefi, dört gereksinim ve kabul ölçütleri.
- `.planning/REQUIREMENTS.md` — DOS-01, DOS-02, KAY-01 ve KAY-04 ile devreden kaynak, metin kökeni ve eksik bilgi kuralları.
- `.planning/PROJECT.md` — Dokuz partilik onaylı liste, kapsam gerekçeleri ve ortak inceleme yöntemi.
- `.planning/phases/01-kapsam-y-ntem-ve-kaynakl-pilot-rapor/01-CONTEXT.md` — Kimlik, zaman aralığı, kaynak zinciri ve rapor sunumu kararları.
- `.planning/STATE.md` — Faz 1 kabulü, pilotun kaynak sınırları ve TİP tüzük kaydının konu sözlüğündeki kullanımı.

### Uygulama

- `README.md` — Yerel arşiv, kayıt ekleme, rapor üretimi ve denetim komutları.
- `AGENTS.md` — Depo iş akışı ve model/maliyet tercihleri.

Bu fazın gereksinimleri yol haritası ve gereksinim belgesinde tanımlıdır.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `src/arsiv.py` — Kaynak yakalama, belge/sürüm/pasaj ve bulgu kayıtları, yerel çalışma alanı, kapalı SQLite kopyası ve sürüm denetimi.
- `src/rapor.py` — Geçerli sürümün sekmeli HTML üreticisi. Parti sekmeleri, kaynak bağlantıları, künye ayrıntıları ve “Henüz incelenmedi” görünümü hazırdır.
- `data/current.json` — Geçerli SQLite, JSON ve HTML dosyalarının aynı kapalı sürümdeki konumunu gösterir. TİP’e bağlı sicil, TBMM komisyon raporu ve tüzük kayıtları araştırma için başlangıç noktasıdır. Tüzük, Faz 1’de ortak konu sözlüğünün dayanağı olarak kullanılmıştır. Kesim tarihindeki tüzük sürümü ayrıca doğrulanmalıdır.
- `tests/test_documents.py`, `tests/test_report.py` ve `tests/test_publication.py` — Kaynak sahipliği, rapor görünümü ve sürüm üretimi kontrolleri.

### Established Patterns

- Özgün belge baytları ve okunabilir kopyaları arşivde saklanır. Bulgu kanıtı, bir sürüme bağlı pasaj üzerinden izlenir.
- HTML ve JSON kapalı SQLite kopyasından türetilir. Üretim ve denetim tamamlandığında geçerli sürüm işaretçisi güncellenir. Önceki sürümler kendi rapor üreticileriyle denetlenir.

### Integration Points

- `src/rapor.py` şu anda sekme sırası için `scope_party.approved_order` alanını kullanıyor ve Yeni Parti dışındaki sekmeleri araştırılmamış gösteriyor. Planlama, yeni dosyaların parti kimliğiyle üretilmesini ve D-03’teki sunum sırasını kapsar.
- `src/arsiv.py` içindeki olay tarihi ve hesap dönemi doğrulamaları pilot partiye özel. Bu kayıtlar yeni bir parti için kullanıldığında planlama kuruluş ve kapsam kanıtlarıyla bağlantıyı ele alır.
- İlk uçtan uca dilim TİP kaydı → kaynak sürümü ve pasaj → parti sekmesi → doğrulanmış yerel rapordur. Aynı akış belirlenen sırayla sonraki partilere uygulanır.

</code_context>

<specifics>
## Specific Ideas

- “TİP'den başlayarak parti parti ekleyelim.”
- “2 + resmi site” ifadesi sade bilgi kartına doğrulanmış resmî sitenin eklenmesini belirtir.
- Sürüm açıklaması için “tabii yapay zeka aciklamasiysa uygun renk kullanarak” denildi. Faz 1 renk ve metin kökeni kuralları bu açıklamalara da uygulanır.

</specifics>

<deferred>
## Deferred Ideas

Ayrıntılı karşılaştırmalar ve mali araştırma Faz 3–5, güncelleme süreci ve paylaşılabilir raporun tamamlanması Faz 6 kapsamındadır.

</deferred>

---

*Phase: 02-b-t-n-partiler-i-in-dosyalar-ve-s-r-ml-kaynaklar*
*Context gathered: 2026-11-10 (America/New_York)*
