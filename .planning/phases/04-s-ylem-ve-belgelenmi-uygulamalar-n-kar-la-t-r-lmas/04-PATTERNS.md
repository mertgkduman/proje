# Faz 04: Söylem ve belgelenmiş uygulamalar — Örüntü Haritası

**Tarih:** 2026-11-17  
**Sınıflandırılan:** 9 dosya/grup; **örnek bulunan:** 9/9

## Dosya sınıflandırması

| Hedef | Rol | Veri akışı | Git izlemeli örnek | Eşleşme |
|---|---|---|---|---|
| `src/uygulamalar.py` (önerilen, yeni) | model/doğrulayıcı | CRUD, dönüştürme | `src/arsiv.py` | rol ve akış |
| `src/arsiv.py` | servis/CLI | dosya G/Ç, işlem, batch | `src/dosyalar.py` | rol ve akış |
| `src/dosyalar.py` | servis/doğrulayıcı | dönüştürme | kendisi | tam |
| `src/rapor.py` | HTML üretici | dönüştürme | kendisi | tam |
| `src/rapor_v24.py` (önerilen, yeni) | tarihsel HTML üretici | dönüştürme | `src/rapor.py` | rol ve akış |
| Faz 04 test modülleri (adları planlayıcıca belirlenecek, yeni) | test | CRUD, hata, DOM | `tests/test_matches.py` | rol ve akış |
| `tests/test_comparisons.py` | test | sözleşme, regresyon | kendisi | tam |
| `tests/test_comparison_content.py` | test | içerik, regresyon | kendisi | tam |
| `tests/test_comparison_navigation.py` | test | tarayıcı, olay | kendisi | tam |

Yeni isimler tasarım önerisidir; üretilen release JSON/HTML doğrudan düzenlenecek kaynak dosyaları değildir. Tarihsel stil varlığının adı ve konumu uygulama planında mevcut sürümleme düzenine göre belirlenmelidir.

## Örüntü atamaları

### `src/uygulamalar.py`: olay ve kanıt sözleşmesi

**Örnek:** `src/arsiv.py:56-61,79-85,99-105`. Mevcut ilişkiler somut sınırı gösterir:

```python
'finding_evidence': 'finding_id TEXT NOT NULL REFERENCES finding(id), passage_id TEXT NOT NULL REFERENCES passage(id), role TEXT NOT NULL, PRIMARY KEY(finding_id, passage_id, role)',
'actor': 'id TEXT PRIMARY KEY, kind TEXT NOT NULL, party_id TEXT NOT NULL REFERENCES party(id), person_id TEXT REFERENCES person(id), authorization_passage_id TEXT REFERENCES passage(id)',
'action': 'finding_id TEXT PRIMARY KEY REFERENCES finding(id), actor_id TEXT NOT NULL REFERENCES actor(id), event_date TEXT NOT NULL, date_precision TEXT NOT NULL, occurrence_passage_id TEXT NOT NULL REFERENCES passage(id), context TEXT NOT NULL',
'match': 'id TEXT PRIMARY KEY, topic_id TEXT NOT NULL, statement_finding_id TEXT NOT NULL REFERENCES finding(id), action_finding_id TEXT NOT NULL REFERENCES action(finding_id), relation TEXT NOT NULL, rationale TEXT NOT NULL, eligibility TEXT NOT NULL, exclusion_reason TEXT, reviewed_at TEXT NOT NULL'
```

Bu model ortak olay/aşama/katkıyı veya söylemsiz olayı doğrudan temsil etmez. Eklemeli, kararlı olay kimliği; ayrı aşama ve parti/kişi katkısı; söylem-olay-konu ilişkisi, ihtilaf ve kaynaklı söylem araması kayıtları tasarlayın. Eski pilot kimliklerine açık köprü kurun, ortak olayı parti başına çoğaltmayın. Ayrı beyan ve oluş kanıtı, yetki ve parti bağlarını `src/arsiv.py:2391-2414` örüntüsüyle doğrulayın; ortak kaynağın kapsamını açık ilişkiyle modelleyin.

**Dönem:** `src/arsiv.py:2415-2416` pilot için `validate_dates(..., '2026-07-24', ...)` kullanıyor; bu sabit dokuz partiye genellenemez. `src/dosyalar.py:64-72` örneğini yeni denetimde kullanın:

```python
identities = db.execute(
    "SELECT * FROM identity_observation WHERE entity_id=? AND entity_kind='party' AND valid_from IS NOT NULL",
    (party_id,),
).fetchall()
if len(identities) != 1:
    raise ValueError('Parti için tek doğrulanmış kuruluş tarihi gerekli')
identity = dict(identities[0])
check_identity(db, identity)
return identity['valid_from']
```

### `src/arsiv.py`: arama, snapshot ve sürümleme

**Kapanış örneği:** `src/arsiv.py:2495-2509` her ucun gerçek girişimle desteklendiğini denetler:

```python
leads = db.execute('SELECT * FROM lead WHERE topic_id=?', (v['topic_id'],)).fetchall()
if not leads: raise ValueError('Uçsuz tarama kapanamaz')
for lead in leads:
    if lead['status'] not in ('examined', 'blocked', 'excluded'): raise ValueError('İncelenmemiş uç var')
```

Mevcut `topic_search` anahtarı yalnız `topic_id` (`src/arsiv.py:83`); Faz 04 için parti + konu/sürüm + dönem + araştırma türü kapsamı ekleyin. Aday, takip ucu, girişim, kapanış ve yeniden açılışı bu kapsama bağlayın; eski kapanışın anlamını değiştirmeyin.

**Migration örneği:** `src/dosyalar.py:30-56`: workspace SQLite yedeği, `BEGIN IMMEDIATE`, eklemeli tablolar, integrity/foreign-key denetimi, commit; hata halinde rollback. `src/arsiv.py:2670` export ve `src/arsiv.py:3165` publish giriş noktalarıdır. Şema 7/renderer 25 araştırma önerisidir; tek yerde kararlaştırılmalıdır.

**Tarihsel üretici örneği:** `src/arsiv.py:2911-2913,2934-2941` manifest sürüm dallarını, sürüme göre renderer seçimini ve snapshot'tan HTML byte eşitliğini denetler. Renderer 24'ü stil ile dondurun; dispatch, izinli sürümler, şema dalları, manifest ve Faz 3 denetimini birlikte genişletin. Eski şema 6 export davranışı korunmalıdır.

**Aktif görünüm:** `src/arsiv.py:2826-2848` son `revision.selection` ile satırları seçer, bağımsız kullanılan bulguları ve eşlerini tutar:

```python
revision = max(data['comparison_completion_revision'], key=lambda item: item['epoch'])
selection = json.loads(revision['selection'])
referenced = set(active_findings)
for table in ('action', 'match', 'dossier_field', 'dossier_event', 'version_context', 'version_relation'):
    for row in data.get(table, []):
        referenced.update(value for key, value in row.items() if key.endswith('finding_id') and value)
```

Yeni söylem, olay ve aşama tablolarının bulgu referanslarını da projeksiyonda koruyun; tarihsel pasajlar görünüm filtresinde kaybolmamalı. Faz 3 `complete` sözleşmesini yeni araştırma nedeniyle geriletmeyin.

### `src/rapor.py` ve tarihsel renderer

**Atıf örneği:** `src/rapor.py:207-210`:

```python
def citation(pid, label='Kaynak'):
    version = versions[passages[pid]['version_id']]
    title = version_source_label(version, attributions.get(version['id']), documents[version['document_id']]['title'])
    return f'<a class="citation" href="#{fragment("source-" + pid)}" aria-label="{esc(label)}: {esc(title)}">[{esc(label)}]</a>'
```

`src/rapor.py:408-438` mevcut eşleşmeleri `details` içinde, `match-` kimliği ve kaynak, oluş, yetki atıflarıyla kurar. Yeni görünümde söylemi bir kez, olayları tarih sırasıyla açık kısa kayıtlar halinde gösterin; ilişki enum'unu görünür başlık yapmayın. Parti ve karşılaştırma panelleri için tek sunumdan çakışmayan DOM kimlikleri üretin; Faz 3 satırına, kaynak pasajına ve aynı olayın diğer ilişkilerine çift yönlü geçişleri koruyun. Kaçış ve `fragment` yardımcılarını yeniden kullanın.

### Testler ve regresyon sınırları

`tests/test_matches.py:22-40` açıkça gerçek olay iddiası olmayan amaçlı kaynak, pasaj ve bulgu fixture'ları kurar. Yeni sözleşme, ortak olay ve eksik/aşama testlerinde bu ayrımı koruyun; sentetik örnekleri gerçek siyasi araştırma verisi diye yayımlamayın. `tests/test_comparison_navigation.py:83-98` gerçek Chromium ile hash, odak ve görünürlüğü doğrular:

```python
target = url + '#comparison-' + quote(config['row'], safe='')
result = subprocess.run(['node', str(PROBE), executable, target, str(width), json.dumps(config, ensure_ascii=False)], capture_output=True, text=True, timeout=160)
self.assertEqual(result.returncode, 0, result.stderr[-2000:])
```

Mevcut `tests/test_comparisons.py`, `tests/test_comparison_content.py`, `tests/test_comparison_navigation.py` Faz 3 içeriği ve gezinti regresyon sınırıdır. `src/dosyalar.py:75-92` Faz 2 tamamlanmış teslim sırasının refresh sırasında değişmemesini şart koşar. Yeni testler migration rollback, eski renderer byte eşitliği, sözleşmenin manifestten çıkarılması, dokuz kuruluş tarihi, ortak olayın tek kimliği ve parti-konu kapanışı için anlamlı olumsuz durumları kapsamalıdır.

## Paylaşılan örüntüler

- Kaynak zinciri `document_version → passage → finding_evidence → finding`; özet ve alıntı eşleri korunur (`src/arsiv.py:56-61`, `src/arsiv.py:2838-2848`).
- Parametreli SQL, gerçek girişim/gerekçe ve açık hata ile doğrulama kullanılır (`src/arsiv.py:2495-2509`).
- Kaynaklı olgu ile kaynağın iddiası ayrılır; `src/kaynaklar.py:93-106` kaynak politikası haber bulgusunu otomatik `fact` yapmaya gerekçe değildir.
- `src/rapor.py:207-210` atıf ve kaçış yardımcıları; `src/arsiv_gorunum.py` pasif yerel arşiv örneğidir.

## Yakın örneği olmayanlar

Ortak olay/aşama/katkı ve parti-konu-dönem kapsamı mevcut tek bir tabloda yoktur; yukarıdaki örnekler yalnız yapı ve doğrulama örüntüsüdür. Veri modeli için `04-RESEARCH.md` önerileri ve D-01–D-16 uygulanmalıdır.

## Metadata

**Arama kapsamı:** `src/`, `tests/`, Faz 04 bağlam ve araştırma belgeleri. Yukarıda örnek gösterilen tüm mevcut kaynak yolları `git ls-files` ile doğrulandı. Yeni yollar açıkça işaretlendi.
