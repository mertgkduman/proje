# Faz 2: Bütün partiler için dosyalar ve sürümlü kaynaklar — Örüntü Haritası

**Tarih:** 2026-11-11  
**Sınıflandırılan iş alanı:** 8; **eşleşme:** 8/8 (bazıları kısmi)

## Dosya sınıflandırması

| Yeni/değişen dosya veya iş alanı | Rol | Veri akışı | İzlenen en yakın örnek | Eşleşme |
|---|---|---|---|---|
| `src/arsiv.py` kayıt ve doğrulama | servis | CRUD, dosya G/Ç | `src/arsiv.py` | Tam |
| `src/arsiv.py` içindeki SQLite şeması | model/migration | CRUD, dönüşüm | `src/arsiv.py` | Tam; yeni ilişkiler kısmi |
| `src/rapor.py` parti kartı, kronoloji, kaynak geçmişi | bileşen | dönüşüm | `src/rapor.py` | Rol eşleşmesi |
| Parti kaynak/veri girişi; yolu henüz belirlenmedi | veri girişi | dosya G/Ç, CRUD | `src/arsiv.py` | Kısmi |
| Sürüm yayını ve audit | servis | dosya G/Ç, dönüşüm | `src/arsiv.py` | Tam |
| `tests/test_documents.py` | test | CRUD | `tests/test_documents.py` | Tam |
| `tests/test_report.py` | test | dönüşüm | `tests/test_report.py` | Tam |
| `tests/test_publication.py` | test | dosya G/Ç | `tests/test_publication.py` | Tam |

Veri ve parti bazlı ara teslim dosyaları için karar verilmiş bir yol yoktur. Kaynak olgularını bu harita belirlemez. İş sırası TİP → DEM → İYİ → Yeni Yol → DBP → EMEP → Saadet → Demokrat; mevcut Yeni Parti pilotu korunur. Bu sıra kapsam kararındaki `approved_order` ile karıştırılmamalıdır.

## Örüntü atamaları

### `src/arsiv.py`: şema, kayıt ve kaynak verisi

**Örnek:** `src/arsiv.py:33-39,43-54,277-345`. Şema ayrı bir migration dosyasında değil `TABLES` içinde; belge ve pasaj zinciri gerçek yabancı anahtarlarla tanımlıdır:

```python
'document': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), title TEXT NOT NULL, source_kind TEXT NOT NULL',
'document_version': 'id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES document(id), original_url TEXT NOT NULL, final_url TEXT NOT NULL, document_date TEXT, version_label TEXT, accessed_at TEXT NOT NULL, verified_at TEXT NOT NULL, mime TEXT NOT NULL, sha256 TEXT NOT NULL, original_path TEXT NOT NULL, readable_path TEXT NOT NULL',
'passage': 'id TEXT PRIMARY KEY, version_id TEXT NOT NULL REFERENCES document_version(id), exact TEXT NOT NULL, prefix TEXT, suffix TEXT, article TEXT, section TEXT, pdf_page_index INTEGER, printed_page TEXT',
'finding_evidence': 'finding_id TEXT NOT NULL REFERENCES finding(id), passage_id TEXT NOT NULL REFERENCES passage(id), role TEXT NOT NULL, PRIMARY KEY(finding_id, passage_id, role)',
```

`connect` yabancı anahtarları açar (`src/arsiv.py:217-222`); `record` alanları `PRAGMA table_info` ile sınırlar, belge URL ve bilinmeyen tarih gerekçelerini doğrular (`src/arsiv.py:277-300`). `capture_source`, özgün baytı SHA-256 ile nesne deposuna, kaçışlanmış okunabilir kopyayı yanına koyar (`src/arsiv.py:187-214`). CLI giriş düzeni README'nin 1–5. adımlarındadır: `capture`, `workspace`, üst kayıtlardan başlayarak `record`, gerekirse `freeze`, `publish` ve `audit`. Elle release JSON/HTML düzenlenmez.

**Dikkat:** `record` olay ve hesap dönemini halen `yeni-parti` ve `2026-07-24` ile sınırlar (`src/arsiv.py:310-327`); diğer partiye genelleme kaynaklı kuruluş ve yöntem kesimiyle bağlanmalıdır. `event_date` mevcut haliyle açıklamalı kronoloji modeli değildir. `edge` bir sürümden `lead` kaydına bağlanır; doğrudan iki belge sürümü ilişkisi olarak varsayılmamalıdır (`src/arsiv.py:57-60,296-297`). Sürüm ilişkisi, kart alanları ve kaynaklı kronoloji için yeni veri gösteriminin adı ve migration yöntemi planlamaya açıktır.

### `src/rapor.py`: kaynak künyesi ve parti başlıkları

**Örnek:** `src/rapor.py:62-127,230-281`. Bulgudan kaynağa geçiş pasaj kimliğine bağlıdır:

```python
def citation(pid, label='Kaynak'):
    title = documents[versions[passages[pid]['version_id']]['document_id']]['title']
    return f'<a class="citation" href="#source-{esc(pid)}" aria-label="{esc(label)}: {esc(title)}">[{esc(label)}]</a>'
```

Kaynak `details` bileşeni başlık ve türü gösterir; sürüm, belge/erişim/doğrulama tarihleri ve pasaj konumu ayrıntılardadır (`src/rapor.py:95-123`). `web_url` ve `esc` kullanımı, `objects/` yol kontrolü ve kaynak açma davranışı korunmalıdır (`src/rapor.py:95-99,362-399`). Mevcut kaynak gruplaması sadece partiye göredir; beş başlığa göre gruplama ve diğer sürümlerin açılır geçmişi henüz yoktur.

```python
known_order = {pid: i for i, pid in enumerate(PRESENTATION_ORDER)}
scoped = sorted(data.get('scope_party', []),
                key=lambda row: (known_order.get(row['party_id'], len(known_order)), row['approved_order']))
```

Bu güncel kod zaten sunum sırasını `approved_order` değerinden ayırır (`src/rapor.py:125-127`); CONTEXT'teki eski durum tarifine göre geri alınmamalıdır. Her partinin beş başlığı ve veri yoksa `Henüz incelenmedi` durumu `src/rapor.py:230-281` içindeki mevcut akışa uyarlanabilir; eksik durumları girişim kaydına dayanır. Kaynak geçmişinde kullanılan açıklamalar için köken ve alıntı/özet renk kuralları korunmalıdır.

### Sürüm yayını ve denetimi

**Örnek:** `src/arsiv.py:796-815,886-926`; `tests/test_publication.py:30-42,67-75`. Kapalı SQLite kopyasından JSON ve HTML üretimi, faz doğrulaması, manifest, audit ve son olarak atomik işaretçi sırası:

```python
shutil.copyfile(work / 'records.sqlite3', staging / 'records.sqlite3')
payload = export_db(staging / 'records.sqlite3', release, strict_identity=True)
(staging / 'records.json').write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
(staging / 'index.html').write_text(render_report(payload), encoding='utf-8')
```

Sonrasında manifest oluşturulur, staging `releases` altına taşınır, `audit_release(release)` çalışır ve `os.replace(tmp, DATA / 'current.json')` uygulanır. Audit manifest hash'lerini, yeniden dışa aktarılan JSON'u ve manifestteki sürüme uygun renderer çıktısını karşılaştırır. Yeni renderer sürümü eklenirken eski renderer'ların denetlenebilirliği korunmalıdır; henüz Faz 2 kabul audit'i mevcut varsayılmamalıdır. Her parti teslimi bu mekanizmadan geçmiş yerel rapor bağlantısı, eklenen içerik ve önemli kaynak eksikleri içermelidir.

### Testler

**Örnekler:** `tests/test_documents.py:14-29,41-53`, `tests/test_report.py:36-48,69-87`, `tests/test_publication.py:30-42,67-93`.

```python
with self.assertRaises(ValueError):
    arsiv.export_db(work / 'records.sqlite3', 'test')
```

Belge testi geçici `DATA` kopyası ve workspace kullanarak başka partiye ait kanıtı reddeder. Rapor testi gerçek snapshot'tan üretilen sekme sırasını ve tarayıcı gezintisini sınar; sıra zaten Yeni Parti, TİP, DEM, İYİ, Yeni Yol, DBP, EMEP, Saadet, Demokrat ve karşılaştırmadır. Yayın testi hata enjeksiyonunda işaretçi ve audit bütünlüğünü sınar. Aynı örneklerle yeni sürüm/geçmiş bağlantısı, parti sahipliği, kart/kronoloji ve pilot regresyonu doğrulanabilir; parti bazlı tamamlanma makbuzları için mevcut test sözleşmesi yoktur.

## Ortak örüntüler

- **Kanıt zinciri:** `finding_evidence` → `passage` → `document_version` → `document` → `party` (`src/arsiv.py:34-39`); sahiplik denetimini atlamayın.
- **Güvenlik ve hata:** `safe_url`, `safe_path` (`src/arsiv.py:95-107`); geçersiz veri için `ValueError`; SQL parametreleri bağlanır (`src/arsiv.py:289-293,329`).
- **Tarih ayrımı:** belge, olay, hesap, erişim ve doğrulama tarihleri ayrı alanlardır; bilinmeyen tarih gerekçelidir. Kesim yeni parti kuruluşundan ayrı kaynaklı doğrulanmalıdır.
- **Eksik veri:** `missing` bir `attempt` kaydına bağlıdır (`src/arsiv.py:60-65`); henüz araştırılmayan başlık bir olumsuz bulgu değildir.

## Yakın örneği olmayan alanlar

| Alan | Neden |
|---|---|
| Kaynaklı parti kimlik kartı ve açıklamalı kuruluş kronolojisi | Pilotun genel bulguları ve `event_date` alanları var; istenen yapı tam olarak yok. |
| Aynı belgenin sürümler arası ilişkisi ve yanındaki geçmiş görünümü | Sürüm kayıtları var; doğrudan ilişki/geçmiş sunumu belirlenmemiş. |
| Parti bazlı ara teslim makbuzu | Çalışma alanı/yayın örneği mevcut; makbuz biçimi ve yolu belirlenmemiş. |
| Faz 2 kabul denetimi | Faz 1 denetimi örnektir; Faz 2 ölçütleri ve geriye uyumluluk planlanmalıdır. |

## Metadata

**Kapsam:** `src/`, `tests/`, README ve faz bağlamı. Beş güçlü izlenen kaynak örneği: `src/arsiv.py`, `src/rapor.py`, `tests/test_documents.py`, `tests/test_report.py`, `tests/test_publication.py`; tümü `git ls-files` ile doğrulandı. Araştırma kullanıcı kararıyla atlandı.
