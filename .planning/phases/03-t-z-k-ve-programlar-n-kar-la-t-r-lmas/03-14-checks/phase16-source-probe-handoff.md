# 03-14 → 03-16 kaynak ve locator devri

Başvuru: kabul edilmiş `b513965558094e338a941be90a1960a4`, seçili taxonomy 4,
schema 6 ve renderer 18. Bu dosya 03-16 planı, UAT veya tamamlanmış doğrulama
değildir. Aşağıdaki kaynakçı kararları ve kanıtları yeniden kullanılabilir;
önceki tam kaynak okumalarını baştan yaptırmak yerine ilgili özgün sayfa,
pasaj, alan ve soy ilişkisinin seçili raporda korunmasını hedefli denetleyin.

* EMEP `0208-emep-charter-pdf-v1`, SHA
  `82a0ec082d33e31eeb3ad2e3f0955b851f2d2fc4e9e417fac3bd148bd805f171`:
  `emep-locator-independent.md` içindeki 17 manuel pasajın tek tek görsel
  tablosunda 15 locator doğru, iki eski eğitim locator hatalıdır. Kanıt
  `gsd-emep-page01.png`–`gsd-emep-page04.png`; gerçek düzeltme PDF sıfır
  tabanlı index 1 / basılı 2'dir. Seçili `04-0314-emep-education-correct-access-f`
  ve `04-0314-emep-education-correct-language-f` yalnız doğru
  `0314-emep-education-proposal-correct-page-p` pasajına ve yeni bulgulara
  bağlanır. Eski yanlış sayfalı passage/finding kapalı snapshot'ta korunur,
  yeni seçili bulguya tekrar bağlanmaz. İlk dört sayfa kongreye sunulan
  öneridir; ayrıca kabul/yürürlük kanıtı değildir.
* TİP `0203-tip-charter2022-v1`, SHA
  `e86237895eda1cec2e66ac388ce7b9cd7096e86dfc9f1cccdd93ab1a298e4a60`:
  `gsd-0314-tip2022-index22-white.png`, PDF index 22/basılı 21 toplantı
  kapsamını (`0314-cm-x11-part1-p`, seçili
  `04-03-v3-0304-tip-pdf-genisletilmis-field`); `gsd-0314-tip2022-index8.png`,
  index 8/basılı 7 adaylık maddesini (`0314-charter2-full-3-passage`, seçili
  `04-03-v3-0304-tip-pdf-aday-yetki-field`) gösterir. HTML ve PDF nüshalarının
  farklı görev/listeleri birleştirilmez; dosya adı kabul tarihi değildir.
* Demokrat `0210-demokrat-program-archive-v1`, 83 PDF sayfası, SHA
  `6554ec05b00d37f62159e1d722f4464ff8b32569ddf7455108530cc772747da2`:
  birinci tabanlı PDF sayfa 8'in metin katmanı boş olsa da basılı 14'te gerçek
  önsöz devamı vardır. `03-13-RESEARCH-DRAFT.md` ve `03-13-materialize*.py`
  görsel incelemeyi kaydeder. `0313-demokrat-image-01-p` Senato,
  `0313-demokrat-image-02-p` seçim barajı; seçili alanları sırasıyla
  `04-03-v3-0313-demokrat-003-anayasal-denetim-f` ve
  `04-03-v3-0313-demokrat-006-secim-siyasi-partiler-f`. Boş çıkarım, boş sayfa
  veya belge yokluğu demek değildir. Tarihsel `0210-demokrat-old1985-v1`
  SHA `ce791d9c79c4fc93a6cc3eb8d40827ea1238b6a3ce6549b5027966624b15449a`
  nüshasında basılı 99–100 fiziksel olarak eksiktir; `medical-deep-review.md`
  ve `income-scope-matrix.md` bu sınırı, `0314-dyp-1985-income-page-check` ve
  `0314-dyp-1985-income-pages-missing` gerçek girişim/açığı kaydeder. Başka
  kopyadan bu nüshanın sayfası tamamlanmaz, parti tutumu yokluğu çıkarılmaz.
* `v3-v4-row-lineage.json` ve `v4-batch-replacement-lineage.json` 18 gerekçeli
  eski→yeni seçili row ilişkisini, `v4-batch-independent-audit.md` 13 alan/23
  özgün pasajı, `dependent-claims-independent-audit.md` etkilenen 16 cümle ve
  46 proof bağını kaydeder. `v3-v4-synthesis-lineage.json` değişmeyen taşıma
  ile özgül yeniden incelemeyi ayırır. Demokrat yeni kongre hesap komisyonu
  `0314-v4-demokrat-kongre-hesap-komisyon-f`, eski dar bağımsız-kurul
  `0312-demokrat-2-scope-06` ile birlikte kendi kapsamlarında görünmelidir.
  Demokrat mahalle/köy hükmü için özgün sayfa, madde/fıkra sınırı, kadın ve
  gençlik kolları başlığı ve devamı birlikte değerlendirilir: başlık komşuluğundan
  kesin münhasırlık veya genel parti organı kapsamı kendiliğinden çıkarılmaz.
* `income-scope-matrix.md` ve `medical-deep-review.md` Saadet'in doğum/çalışma/
  vergi koşullarını, Demokrat'ın her vatandaşa asgari nakit ifadesini ve ayrı
  dar çalışan sigortasını, DYP yaşlı/muhtaç gelir hedeflerini ve 2012 tarihli
  atfedilmiş aktarımın kuruluş öncesi öneri rolünü ayrıştırır. Gelir sağlama
  aracını, düzenli ödeme veya koşulsuz vatandaşlık geliri kaynak söylemedikçe
  üretmeyin. `charter-last-authored-review.json`, `policy-more-authored-review.json`
  ve mevcut sentez proof'ları çalışma sürelerinde `<40` eşiğini, gün/hafta
  birimlerini, genel ve sektör özelini ve öneri/gövde ayrımını korur; iş günü
  dönüşümü eklenmez. Demokrat'ın 2020 emisyon hedefi gidişat projeksiyonuna
  göre %20'dir; ithalat karbon vergisi emisyon sınırlamayan ülke koşulundadır:
  seçili `04-03-v3-0313-demokrat-177-doga-ekoloji-f` ve tam iki sayfa dayanak.

Son 03-14 P3/P2 ve paket kontrol sonuçları kendi exit kanıtlarında ayrıca
izlenir; bu devir onlardan bağımsız bir başarı iddiası üretmez.
