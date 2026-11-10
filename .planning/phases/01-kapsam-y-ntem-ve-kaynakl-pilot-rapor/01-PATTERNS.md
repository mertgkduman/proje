# Faz 01: Kapsam, yöntem ve kaynaklı pilot rapor — örüntü haritası

**Tarih:** 2026-11-10  
**Sınıflandırılan:** 12 önerilen dosya grubu  
**Mevcut uygulama analoğu:** 0 / 12

Depoda izlenen planlama kayıtları var; uygulama kodu, veritabanı, arşiv, rapor ve test yok. Aşağıdaki yollar araştırmacının önerileridir; nihai adlar altı PLAN.md ve SKELETON.md içinde seçilmiştir. Kopyalanabilecek mevcut uygulama örüntüsü veya kod parçası bulunmamıştır.

## Dosya sınıflandırması

| Önerilen dosya grubu | Sorumluluk | Veri akışı | Mevcut uygulama analoğu |
|---|---|---|---|
| `src/db.py` | Veritabanı servisi | CRUD, dosya I/O | Yok |
| `src/schema.sql` | Veri modeli | CRUD | Yok |
| `src/export.py` | Dışa aktarım | Dönüşüm, dosya I/O | Yok |
| `src/archive.py` | Kaynak arşivi | Dosya I/O | Yok |
| `src/evidence.py` | Kanıt ilişkileri | Dönüşüm | Yok |
| `src/research.py` | Araştırma yöntemi | Olaylar, CRUD | Yok |
| `src/report.py` | Rapor üretimi | Dönüşüm, dosya I/O | Yok |
| `src/cli.py` | Yerel CLI | İstek/yanıt, toplu işlem | Yok |
| `assets/report.css` | Görsel sunum | Dönüşüm | Yok |
| `assets/report.js` | Etkileşim | Olaylar | Yok |
| `tests/test_*.py`, `tests/fixtures/` | Doğrulama | Dosya I/O, dönüşüm | Yok |
| `data/`, `archive/`, `report/` | Veri ve türetilmiş çıktılar | Dosya I/O | Yok |

## Önerilen örüntüler

Bu öneriler [01-RESEARCH.md](01-RESEARCH.md) kaynaklıdır; mevcut uygulamadan çıkarılmamıştır. Bağlayıcı kararların tamamı [01-CONTEXT.md](01-CONTEXT.md) D-01–D-24 içindedir.

**Veritabanı ve şema:** Python `sqlite3`, parametreli SQL ve her bağlantıda etkin yabancı anahtarlar kullanılır. Parti kimliği, bireysel üyelik/grup gözlemleri, belge/sürüm/arşiv/pasaj, bulgu/kanıt, girişim/eksik durumları, söylem–eylem eşleşmesi ve mali dönem ilişkileri ayrılır. Belge/olay/erişim/doğrulama tarihleri, quote/summary kökeni ve fact/source_assertion/comment türü ayrı kalır. Kanıtsız bulgu ve geçersiz ilişki reddedilir; olmayan mali tutar NULL'dır.

**Kanonik kayıt ve aktarım:** Doğrulanmış kapalı SQLite snapshot'ı tek kalıcı doğruluk kaynağı olmalıdır. Düzenlemek için yerel scratch'e yüklenir; tek yazıcıyla değişiklik yapılır, kapatılıp doğrulanır, sonra aynı snapshot'tan JSON/HTML türetilir. JSON bağımsız düzenlenmez. Yerine koyma ve kurtarma sırası son doğrulanmış kayıt/rapor bütününü korumalıdır; nihai release/işaretçi protokolü SKELETON.md içindedir.

**Arşiv ve kanıt:** PDF özgün baytları veya tarihli ham HTML, güvenli okunabilir türev, özgün/nihai URL, MIME, erişim zamanı ve SHA-256 korunur. Pasaj ve sayfa/madde konumu değişmez sürüme bağlanır. PDF sıra sayfası ile basılı sayfa farklıdır. Dosya/hash/kimlik/pasaj ilişkileri doğrulanır; ham kaynak HTML etkin çalıştırılmaz.

**Araştırma yöntemi:** Başlangıç sorguları, bağlantılar, girişimler, dışlamalar, açık uçlar, kapanma ve yeniden açılma kaydedilir. URL takma adı ve içerik hash'iyle tekilleştirme yönlendirme ve yeni sürümü kaybetmez. İncelenmemiş ilgili uç varken konu kapanamaz; engelli uç görünür kalır. Bütün uygun kanıtlı eşleşmeler alınır; sayısal kota veya sonuca göre seçim yapılmaz. Girişime bağlı üç eksik durum `not_researched` durumundan ayrılır.

**Statik rapor ve CLI:** JSON ve Türkçe HTML aynı kanonik snapshot'tan üretilir; yerel arşiv bağlantıları görelidir. Metin kaçışlanır, URL protokolü ve dosya kökü doğrulanır. Üretim hatası önceki çıktıyı korur. CLI scratch/snapshot akışını ve anlaşılır hata sonuçlarını sunar; hesap/oturum sistemi bu fazın ihtiyacı değildir.

**Sunum:** Parti sekmeleri, Karşılaştırmalı Özet ve beş araştırma başlığı bulunur; gerçek pilot Yeni Parti'dir. Diğer içerik ve karşılaştırmalar henüz incelenmedi olarak gösterilir. Kapsam/yöntem erişilebilir olmalıdır. Metin içi kaynak bağlantısı künye, pasaj, özgün URL ve yerel arşivi içeren kaydı açar; sekme altında da kaynakça vardır. Derin bağlantı, saklı panelin açılması, fokus/geri dönüş ve klavye hareketi planlanır. Kısa özet koyu mavi, kısa değişmemiş alıntı siyah ve tırnak içinde birlikte görünür; görünür üretim türü etiketi eklenmez, veri kökeni korunur.

**Testler:** Standart `unittest` ve küçük yerel fixture'lar; gerçek write/close/reopen, yabancı anahtar ve geçersiz kanıt, kimlik ayrımı, hash/pasaj, zincir döngüsü/sürüm/kapanma, girişime bağlı eksik durum, NULL/0, kaçış ve göreli bağlantılar denetlenir. Sıfır keşfedilen test başarı değildir. Tarayıcı davranışı ve insan kaynak/tarafsızlık incelemesi ayrı doğrulamalardır.

**Veri ve çıktı dizinleri:** Kanonik kapalı snapshot, değişmez arşiv belgeleri, JSON ve rapor ayrılır. NFS üzerinde aktif SQLite/WAL/eşzamanlı yazıcı kullanılmaz; aktif DB yerel scratch'tedir. Kamuya yayın yetkisi yoktur.

## Ortak kararlar ve bütünleşme

- D-01–D-05: Dokuz parti/dışlama kuralı, Yeni Parti hukuki kimliği ve kuruluşu, aynı adlı oluşum ayrımı, tarihli TBMM kaydı, üyelik/grup ayrımı ve uyuşmazlık kaydı korunur. Veri kesimi planlama tercihidir.
- D-06–D-12: Ortak konu sözlüğü, kaynak zinciri, kapanma/yeniden açılma, kurumsal/bireysel aktör ve olgu/beyan/yorum ayrımı uygulanır. Parti açıklaması tek başına eylemin gerçekleştiğine kanıt değildir.
- D-13–D-19: Parti sekmeleri/beş başlık, erişilebilir kapsam/yöntem, metin içi ve sekme altı kaynaklar, özgün/arşiv bağlantısı ve birlikte görünen özet/alıntı bulunur. Gerçek partiler arası karşılaştırmalar sonraki fazlardadır.
- D-20–D-24: Veri/dışa aktarım kökeni, etiketsiz siyah tırnaklı alıntı/koyu mavi özet ve başlık içinde gerekçeli/tarihli eksik durumlar korunur. Henüz incelenmedi ayrıdır.
- İlk çalışan dilim: Gerçek kaynak arşiv → kalıcı DB yaz/kapat/yeniden oku → JSON → HTML → kaynak kaydı/özgün ve arşiv bağlantısı. Araştırma gözlemi özgün arşiv kopyasının yerini tutmaz.
- Hata/güvenlik: Son doğrulanmış çıktı korunur; metin kaçışlanır, tehlikeli protokol/yol reddedilir, ham HTML çalıştırılmaz. Kopyalanabilecek mevcut hata/log sarmalayıcısı yoktur.

## Tarama kaydı

Ajanın tarama kapsamı `git ls-files` çıktısındaki izlenen dosyalar ve proje skill dizinleridir. Haritalama anında 10 izlenen dosya ve sıfır uygulama analoğu bulundu; proje skill index'i yoktu. Önerilen dosya grupları mimari sorumluluklardır, zorunlu ayrı modüller değildir. Son planlar bu sorumlulukları `src/arsiv.py` ve `src/rapor.py` içinde somutlaştırmıştır; yürütme PLAN.md yollarını esas alır.
