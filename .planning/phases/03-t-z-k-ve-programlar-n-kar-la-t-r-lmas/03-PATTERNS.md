# Faz 3: Tüzük ve programların karşılaştırılması — Örüntü Haritası

**Tarih:** 2026-11-12  
**Kapsam:** 12 dosya veya dosya grubu; 10 doğrudan/rol eşleşmesi, 2 yeni tasarım.  
**Kural:** Aşağıdaki örnek yolların tamamı Git tarafından izlenen kaynaklardır. Önerilen yeni dosya adları ve API'ler kesinleşmiş sözleşme değildir.

## Dosya sınıflandırması

| Yeni/değişen dosya | Rol | Veri akışı | En yakın izlenen örnek | Eşleşme |
|---|---|---|---|---|
| `src/arsiv.py` | model, CLI, servis | CRUD, dosya I/O, batch | `src/arsiv.py` | tam |
| `src/dosyalar.py` | model, doğrulayıcı | dönüşüm, batch | `src/dosyalar.py` | tam |
| `src/karsilastirma.py` **öneri** | model, doğrulayıcı | CRUD, dönüşüm | `src/dosyalar.py` | rol eşleşmesi |
| Faz 3 karşılaştırma yükleme/kabul CLI'sı **adı ve yeri belirlenmedi** | CLI | dosya I/O, batch | `src/arsiv.py` | kısmi; henüz mevcut değil |
| `src/rapor.py` | renderer/bileşen | dönüşüm | `src/rapor.py` | tam |
| `src/rapor_v15.py` **öneri** | tarihsel renderer | dönüşüm | `src/rapor_v14.py` | rol eşleşmesi |
| yeni sürümlü CSS **adı belirlenmedi** | stil | dönüşüm | `src/rapor_v14.css` | rol eşleşmesi |
| `data/dossiers/*.json` veya yeni kaynaklı içerik paketleri **biçim kararı açık** | veri | dosya I/O | `data/dossiers/02-iyi.json` | rol eşleşmesi |
| `tests/test_topics.py` | test | batch | aynı dosya | tam |
| `tests/test_documents.py`, `tests/test_dossiers.py` | test | batch | aynı dosyalar | tam |
| `tests/test_report.py`, `tests/browser_probe.py` | test | olay, dosya I/O | aynı dosyalar | tam |
| `tests/test_publication.py` ve yeni karşılaştırma testleri | test | dosya I/O, batch | `tests/test_publication.py` | rol eşleşmesi |

`tests/run.py` mevcut test keşif çalıştırıcısıdır; yeni test adı onun `test_*.py` örüntüsüne uymalıdır. Üretilen snapshot/JSON/HTML ve tarihsel sürümler elle düzenlenecek içerik dosyaları değildir.

## Örüntü atamaları

### Şema, çalışma alanı ve karşılaştırma modeli

**Kaynak:** `src/arsiv.py:46-54,69-88`. Mevcut iskelet karşılaştırma kaydı parti, alan, sürüm ve tarihçe bilgisi içermez:

```python
'finding_evidence': 'finding_id TEXT NOT NULL REFERENCES finding(id), passage_id TEXT NOT NULL REFERENCES passage(id), role TEXT NOT NULL, PRIMARY KEY(finding_id, passage_id, role)',
'comparison': 'id TEXT PRIMARY KEY, topic_id TEXT NOT NULL, state TEXT NOT NULL',
'comparison_evidence': 'comparison_id TEXT NOT NULL REFERENCES comparison(id), passage_id TEXT NOT NULL REFERENCES passage(id), PRIMARY KEY(comparison_id, passage_id)'
```

**Uygula:** Parti × konu sürümü × düzey/organ × belge sürümü/alternatif × alan tanesini ve çoklu kanıtı açık tanımla; ayrı ilke/hedef/araç, konu sentezi ve iki pasajlı değişiklik geçmişi tasarla. Bu henüz mevcut model veya yükleme API'sı değildir. Aynı kanonik satır kimlikleri dosya ve karşılaştırma görünümlerinde kullanılmalı; iki veri kopyası oluşturulmamalı. `topic`, `topic_basis`, `finding_topic`, `attempt`, `missing` ve `research_state` var olan ilişkilerden yararlanır.

**Çalışma alanı örneği:** `src/arsiv.py:300-318` önce kapalı tabanı denetleyip kopyalar, sonra yalnız workspace üzerinde tablo/kolon ekler:

```python
base = current()
work = Path(tempfile.mkdtemp(prefix='proje-work-', dir=root))
if base:
    audit_release(base)
    shutil.copyfile(DATA / 'releases' / base / 'records.sqlite3', work / 'records.sqlite3')
db = connect(work / 'records.sqlite3')
for name, definition in TABLES.items():
    if name in DOSSIER_TABLES or name in POLICY_TABLES or name in VIEW_TABLES: continue
    db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
```

`src/dosyalar.py:30-56` içindeki yedek/transaction/bütünlük kontrollü `migrate_workspace` desenini yeni geçişe uyarla; tarihsel kapalı veritabanlarını yerinde değiştirme. Migration, yazma doğrulaması, export ve audit aynı yeni sözleşmeyi kontrol etmeli.

### Kanıt, konu dayanağı ve eksiklik

**Kaynak:** `src/arsiv.py:607-613`, parametreli sahiplik sorgusu ve atıf kontrolü:

```python
row = db.execute('SELECT d.party_id,d.source_kind,v.id AS version_id FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (passage['id'],)).fetchone()
if not row or row['party_id'] != finding['party_id']: raise ValueError('Kanıt başka partiye ait')
if finding['provenance'] == 'quote' and finding['text'] not in passage['exact']: raise ValueError('Alıntı pasajda bulunamadı')
compiled = check_evidence_attribution(db,finding,row)
```

`src/arsiv.py:843-874` özgün belge içindeki pasajı, birebir alıntıyı ve doğrulanmış konu dayanağını export sırasında da denetler. Mevcut dayanak kapısı `document_authority` ve başlık sözcüklerine bağlıdır; yeni konu sözleşmesinde atıf politikası ve açık belge türünü esas alan uyumlu kontrol ekle, tarihsel kayıtların sözleşmesini değiştirme. `src/kaynaklar.py:89-98` atıf politikasının yeridir. Sırası belirsiz sürümleri beraber göster; erişim tarihiyle sıralama icat etme.

`src/arsiv.py:73-78` girişime bağlı `missing` ve ayrı `research_state` kayıtlarını tanımlar. Belgeye erişilememe, bulunamama, doğrulanamama, henüz incelenmeme ve incelenmiş bölümde açık ifade bulunmamasını ayrı sonuçlar olarak modelle; sonuncusu için incelenen sürüm ve kapsam gereklidir. Ek bildirgeyi program diye etiketleme.

### Dosya ilişkileri, tarihçe ve içerik paketleri

**Kaynak:** `src/dosyalar.py:124-128` kaynaklı özet ve alıntı çiftini aynı parti, başlık ve ortak pasaj üzerinden bağlar:

```python
summary_passages = {e['passage_id'] for e in evidence if e['finding_id'] == fid}
if f['provenance'] != 'summary' or not any(x['pair_id'] == f['pair_id'] and x['party_id'] == party and x['provenance'] == 'quote' and x['heading'] == f['heading'] and x['epistemic_type'] == f['epistemic_type'] and checked_finding(x['id'], party) and summary_passages.intersection(e['passage_id'] for e in evidence if e['finding_id'] == x['id']) for x in findings.values()):
    raise ValueError('Kaynaklı özet ve alıntı çifti gerekli')
```

`src/dosyalar.py:185-198` sürüm ilişkisinde aynı belge, `supersedes`/`related`/`uncertain`, sahiplik ve döngüsüzlük denetler. Faz 3 önce–sonra açıklamasına iki sürümün ilgili pasajlarını ayrıca bağla; mevcut tek ilişki açıklamasını maddi değişikliğin yeterli kanıtı sayma. `data/dossiers/02-iyi.json:433-448` mevcut kaynaklı tarihçe içeriğine örnektir; yeni paket biçimi kararlaştırılmalıdır.

### Export, audit ve atomik refresh

**Kaynak:** `src/arsiv.py:791-805` salt okunur export ve mevcut şema seçimi:

```python
db = connect_readonly(path)
if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
    raise ValueError('Veritabanı bütünlük hatası')
existing = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
names = [n for n in TABLES if n in existing] if 'scope_party' in existing else LEGACY_TABLES
```

`src/arsiv.py:800-805,909-950,1019-1086` schema/manifest, renderer seçimi, kapalı kopya denetimi ve yayın akışını birlikte ele alır. Yeni şema sürümünü ve manifest/audit kabulünü beraber genişlet; yeni tabloların yalnız varlığı eski snapshot export'unu değiştirmemeli. Tamamlanmış dokuz parti tabanında mevcut `publish --refresh` yolunu koru; `src/dosyalar.py:75-100` teslim sırası denetimini atlama. Parser `src/arsiv.py:1105-1107` şu an yalnız Faz 1/2 audit seçeneği sunar: Faz 3 kabul CLI adı yeni tasarımdır, varmış gibi çağrılmamalı. Başarısız yeni yayın mevcut pointer'ı korumalı.

### Renderer ve karşılıklı bağlantılar

**Kaynak:** `src/rapor.py:11-12,146-160,182-184`:

```python
RENDERER_VERSION = 15
STYLE = Path(__file__).with_name('rapor_v14.css').read_text(encoding='utf-8')
findings = {f['id']: f for f in data['finding']}
evidence = defaultdict(list)
for row in data['finding_evidence']:
    evidence[row['finding_id']].append(row)
def citation(pid, label='Kaynak'):
    title = documents[versions[passages[pid]['version_id']]['document_id']]['title']
    return f'<a class="citation" href="#source-{esc(pid)}" aria-label="{esc(label)}: {esc(title)}">[{esc(label)}]</a>'
```

Önce bugünkü renderer 15'i `src/rapor_v15.py` gibi bağımsız tarihsel kopyaya dondur ve `src/arsiv.py:22-36,943-950` dispatch tablosuna bağla; **sonra** güncel renderer sürümünü ilerlet. `src/rapor_v14.css` tarihsel renderer'larca paylaşıldığından değiştirme; yeni sürümlü CSS oluştur. Tarihsel yeniden üretimi byte/hash ile denetle.

Tek kanonik karşılaştırma kayıtlarından hem parti ayrıntısını hem konu altında dokuz partiyi üret. `src/rapor.py:20,250-256` mevcut sırayı ve karşılaştırma sekmesini tanımlar. Her iki görünüm aynı kayıt kimliğinden kararlı, benzersiz hedefler ve karşılıklı bağlantılar üretmeli; kaynak bağlantısı ayrıca korunmalı. `esc`/`web_url` (`src/rapor.py:33-40`) veri kaçışlama örneğidir.

**Hedef açma:** `src/rapor.py:507-529`:

```javascript
function reveal(element) {
  const panel = element.closest('[role=tabpanel]');
  if (panel) selectTab(document.getElementById(panel.getAttribute('aria-labelledby')));
  for (let node = element; node; node = node.parentElement) {
    if (node.tagName === 'DETAILS') node.open = true;
  }
}
function hashTarget(hash) {
  try { return document.getElementById(decodeURIComponent(hash.slice(1))); }
  catch { return null; }
}
```

`src/rapor.py:530-547` hash ve kaynak odağı geri dönüşünü yönetir. Yeni karşılıklı hedeflerde sekme/details açılması, odak, doğrudan hash ve geri/ileri davranışını ayrıca tamamla; mevcut citation davranışını koru.

### Testler ve tarayıcı doğrulaması

**Kaynak:** `tests/test_topics.py:16-25` gerçek tabanın geçici kopyası ve export üzerinden olumsuz sözleşme testi:

```python
arsiv.DATA = Path(tmp) / 'data'
shutil.copytree(old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
work = arsiv.open_workspace(tmp)
arsiv.record_topic(work, dict(id='fake', label='Sahte', taxonomy_version=2, valid_from='2026-11-10', status='verified', change_reason='Test'))
with self.assertRaises(ValueError):
    arsiv.export_db(work / 'records.sqlite3', 'test')
```

`tests/test_documents.py:159-201` sahiplik ve belge ilişkileri; `tests/test_dossiers.py:44-100` dosya kabulü; `tests/test_publication.py:26-45` bozulma ve yayın hata noktaları için örnektir. İki yönlü bağ, farklı sürüm sırası, dayanak türü, alan/eksiklik ayrımı ve eski renderer uyumluluğuna anlamlı yeni kabul testleri ekle. Mevcut testlerin bunları zaten kapsadığı varsayılmamalı.

`tests/browser_probe.py:14-17,46-89` gerçek Chromium'u bulur, yerel HTTP ve file URL üzerinden 360 px görünüm, sekme, hash, geri dönüş, odak ve yatay taşmayı sınar. Yeni bağlantıları bu örüntüyle ve geniş ekranda doğrula. `tests/run.py:6-17` keşif ve sıfır test hata davranışıdır:

```python
suite = unittest.defaultTestLoader.discover(str(root / 'tests'), pattern=args.pattern)
count = suite.countTestCases()
if not count:
    print('Test bulunamadı', file=sys.stderr)
    raise SystemExit(2)
```

## Paylaşılan kurallar ve eşleşmeyen tasarımlar

- Kaynak → pasaj → belge sürümü → belge → parti zinciri ve kaynaklı özet/alıntı çifti bütün yeni içerikte korunur; konu sentezi tek partiye zorlanmaz.
- Aynı SHA'lı URL kopyası maddi değişiklik değildir; bilinmeyen tarih, yürürlük veya sıra üretilmez. Alıntı siyah/tırnaklı, özet koyu mavi sunulur.
- Yeni karşılaştırma sözleşmesi, konu inceleme kapsamı, konu sentezi ve Faz 3 CLI için tam analog **yoktur**; yukarıdaki mevcut kayıt/doğrulama örneklerinden tasarla. Dosya isimleri ve kesin API araştırma önerisidir.
- İstekleri parametrele, HTML/URL kaçışını ve pasif yerel arşivi koru. Kaynaklı içerik ve tarama kapsamı gerçek araştırmayla doldurulur; mevcut aday konu listesi tamamlanmış araştırma değildir.

## Metadata

**Arama kapsamı:** `src/`, `tests/`, `data/dossiers/`; faz bağlamı ve araştırması.  
**İzlenen analoglar:** `git ls-files` ile doğrulandı; tarihsel renderer örneği `src/rapor_v14.py` mevcut dispatch tarafından içe aktarılır.  
**Doğrulama:** Bu eşleme için test veya dış araştırma çalıştırılmadı.
