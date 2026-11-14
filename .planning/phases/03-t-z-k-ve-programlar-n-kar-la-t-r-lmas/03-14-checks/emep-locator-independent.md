# EMEP 82a0 taraması: index0–3 hedefli pasaj konumu denetimi

14 Kasım 2026. Read-only araştırma. İncelenen mevcut kayıt tabanı data/releases/ae42ae1897864fda810b033ce3ac1e8f/records.json. Eski kayıt, özgün dosya, veri tabanı veya yayın değiştirilmedi.

## Kaynak ve yöntem

Sürüm: 0208-emep-charter-pdf-v1. Kaynak https://www.yargitaycb.gov.tr/documents/emep.pdf. SHA256 82a0ec082d33e31eeb3ad2e3f0955b851f2d2fc4e9e417fac3bd148bd805f171. Özgün dosya data/objects/82a0ec082d33e31eeb3ad2e3f0955b851f2d2fc4e9e417fac3bd148bd805f171/original.pdf.

Metadata: tarihsiz 38 sayfalık tarama; değişiklik önerisi, program, tüzük ve kurucular. İlk dört sayfa program/tüzük değişikliği önerisini içerir. Sayfa0 başlığı 6. Kongre Divan Başkanlığına hitap eder; girişte Genel Yönetim Kurulu adına Selma Gürkan değişiklikleri önerir. Maddelerde değiştirilmiştir/eklenmiştir ifadelerinin bulunması, bu önerinin ayrıca kabul edilip yürürlüğe girdiğinin kanıtı sayılmadı.

İlk dört özgün sayfa görselinin tamamını doğrudan okuyup her mevcut passage.exact parçasını yerinde eşledim. Betik yalnız kimlik/metadata ve finding_evidence→field→row ilişkisi envanteri çıkardı; sayfa veya inceleme kararı üretmedi. Görsellerin kaynak eşlemesi mevcut /tmp/gsd-emep-render.py okunarak kontrol edildi: betik aynı SHA256 özgün PDF’yi Poppler-glib ile açar; index i → /tmp/gsd-emep-page{i+1:02}.png.

| Sıfır tabanlı index | PDF’de sıralı sayfa | Basılı sayfa | Doğrudan incelenen gerçek görsel | Görünen sınırlar |
|---|---|---|---|---|
| 0 | 1 | 1 | /tmp/gsd-emep-page01.png | Öneri başlığı/girişi; Program Değişikliği1–7, son madde devam eder. |
| 1 | 2 | 2 | /tmp/gsd-emep-page02.png | 7’nin devamı; program değişikliği8–13. Eğitim değişikliği13 sayfanın altındadır. |
| 2 | 3 | 3 | /tmp/gsd-emep-page03.png | Program değişikliği14–16; Tüzük Değişikliği1–4. |
| 3 | 4 | 4 | /tmp/gsd-emep-page04.png | Tüzük Değişikliği5–6; MYK18/A metni bu sayfadadır. |

## Mevcut 17 kimliğin tek tek sonucu

Sütunlar index/basılı sayfayı birlikte verir. “Doğru” yalnız pasajın gerçek sayfa yerini onaylar; ilgili siyasi karşılaştırmanın anlamı veya yürürlük kararı değildir. Tablo hükümleri kendim görsel eşlemeyle yazdım.

| Mevcut passage ID | Mevcut index/basılı | Gerçek index/basılı | Görsel | Yerinde karşılık ve karar |
|---|---|---|---|---|
| 0208-emep-archive-proposal | 0/1 | 0/1 | /tmp/gsd-emep-page01.png | Üstteki program ve tüzük değişikliği önerisi başlığı. Konum doğru. |
| 0208-emep-program-archive | 0/1 | 0/1 | /tmp/gsd-emep-page01.png | Girişin ardından Program Değişikliği ara başlığı. Konum doğru. |
| 0309-emep-pdf-000-0-passage | 2/3 | 2/3 | /tmp/gsd-emep-page03.png | Tüzük Değişikliği1, madde5; aylık ödenti10–500TL. Konum doğru. |
| 0309-emep-pdf-002-0-passage | 2/3 | 2/3 | /tmp/gsd-emep-page03.png | Tüzük Değişikliği4, madde18; Genel Başkan ve seçilen43üyeli GYK. Konum doğru. |
| 0309-emep-pdf-004-0-passage | 3/4 | 3/4 | /tmp/gsd-emep-page04.png | Tüzük Değişikliği5, madde18/A; GYK’nin kendi içinden seçtiği17üyeli MYK. Konum doğru. |
| 0309-emep-program-pdf-000-0-passage | 1/2 | 1/2 | /tmp/gsd-emep-page02.png | Program Değişikliği8, günlük7/haftalık35saat yeni ibaresi. Konum doğru. |
| 0309-emep-program-pdf-003-0-passage | 1/2 | 1/2 | /tmp/gsd-emep-page02.png | Program Değişikliği9, işsiz/yaşlı/malul aylığına ilişkin eklenen bölüm. Konum doğru. |
| 0309-emep-program-pdf-003-1-passage | 1/2 | 1/2 | /tmp/gsd-emep-page02.png | Öncekiyle aynı9.madde ve aynı metin parçası. Konum doğru. |
| 0309-emep-program-pdf-004-0-passage | 2/3 | 2/3 | /tmp/gsd-emep-page03.png | Program Değişikliği14, yeterli/parasız su hakkı cümleleri. Konum doğru. |
| 0309-emep-program-pdf-005-0-passage | 0/1 | 0/1 | /tmp/gsd-emep-page01.png | Program Değişikliği4, AB ve benzeri birliklerde yer almama ibaresi. Konum doğru. |
| 0309-emep-program-pdf-006-0-passage | 2/3 | **1/2** | /tmp/gsd-emep-page02.png | Program Değişikliği13, ilk/orta/yüksek öğrenimde demokratik/bilimsel/anadilde/parasız eğitim. Eski konum yanlış; gerçek sayfa bir önceki. |
| 0309-emep-program-pdf-006-1-passage | 2/3 | **1/2** | /tmp/gsd-emep-page02.png | Öncekiyle aynı13.madde ve aynı metin. Aynı konum hatası. |
| 0309-emep-program-pdf-007-0-passage | 2/3 | 2/3 | /tmp/gsd-emep-page03.png | Program Değişikliği15;18yaşını dolduranlara seçilme hakkı. Konum doğru. |
| 0309-emep-program-pdf-007-1-passage | 2/3 | 2/3 | /tmp/gsd-emep-page03.png | Öncekiyle aynı15.madde ve aynı metin. Konum doğru. |
| 0309-emep-program-pdf-009-0-passage | 2/3 | 2/3 | /tmp/gsd-emep-page03.png | Program Değişikliği16’nın son cümlesi; çalışamayan engellilere aylık. Konum doğru. |
| 0309-emep-program-pdf-009-1-passage | 2/3 | 2/3 | /tmp/gsd-emep-page03.png | Aynı16.madde son cümlesi. Konum doğru. |
| 0309-emep-program-pdf-009-2-passage | 2/3 | 2/3 | /tmp/gsd-emep-page03.png | Aynı16.madde son cümlesi. Konum doğru. |

Sonuç:17pasajın15’inde sayfa doğru; yalnız006-0/006-1 yanlış konumlu. Bu sürümde index0–3’e kayıtlı, verilen kimlik kümesinin dışında başka manuel passage bulunmadığı envanterle kontrol edildi. Bu,38sayfanın geri kalanındaki konumların onaylandığı anlamına gelmez.

## Düzeltilmesi gereken iki kayıt için gerçek tam bağlam

Gerçek bölüm: Program Değişikliği,13.madde. Gerçek index1/PDF2/basılı2; /tmp/gsd-emep-page02.png’nin altı. Başlık ile ilk/son sözcükler dâhil tam madde görselden okundu:

~~~text
DATA_e70c12b5_START
13 - Programımızın 6. Bölümündeki, Eğitim, spor ve çevre kısmının 2.
fıkrasındaki “İlk, orta ve yüksek öğrenim...” cümlesi “İlk, orta ve yüksek
öğrenimde demokratik, bilimsel, anadilde, parasız eğitim gerçekleşecektir.”
Olarak değiştirilmiştir.
DATA_e70c12b5_END
~~~

Yeni dar pasaj için kaynakta gerçekten bulunan exact:

~~~text
DATA_8a007f4b_START
İlk, orta ve yüksek öğrenimde demokratik, bilimsel, anadilde, parasız eğitim gerçekleşecektir.
DATA_8a007f4b_END
~~~

Metinde düzeltilecek içerik yoktur. Yeni pasaj aynı source_version=0208-emep-charter-pdf-v1 ile pdf_page_index=1, printed_page=2 ve öneri13 bölümünü göstermelidir. Geniş13.madde ayrıca ayrı tam-bağlam pasajı olarak tutulabilir; dar cümleye önerinin kabul edildiğine dair anlam eklenmemeli.

| Eski row | Eski field | Konu | Eski summary/quote finding | Eski passage | Önerilen ardıl ilişki |
|---|---|---|---|---|---|
| 0309-emep-program-pdf-006-0-row | 0309-emep-program-pdf-006-0-field | anadilde-egitim | 0309-emep-program-pdf-006-0-summary / 0309-emep-program-pdf-006-0-quote | 0309-emep-program-pdf-006-0-passage | Yeni seçili ardıl row/field→yeni summary/quote→aynı gerçek exact’li doğru index1/basılı2 passage. Eski row/field/passage korunur; açık predecessor/lineage gerekir. |
| 0309-emep-program-pdf-006-1-row | 0309-emep-program-pdf-006-1-field | egitime-erisim | 0309-emep-program-pdf-006-1-summary / 0309-emep-program-pdf-006-1-quote | 0309-emep-program-pdf-006-1-passage | Aynı doğru kaynak yerine bağlanan ayrı erişim ardıl row/field ve bulgu ilişkisi; diğer konunun ardılı gibi birleştirilmez. |

Her iki eski satırın source_role değeri supplement’tir. Doğru konumlu tek gerçek pasaj iki yeni finding_evidence ilişkisiyle kullanılabilir; konu alanları ve satır soyları ayrı kalır. Yeni kimlikleri/soy kayıtlarını ana yürütücü belirler. Bu araştırma bu kayıtları yaratmadı.

## Diğer mevcut alan ilişkileri

Bu bağlar snapshot’ta gerçekten vardır; aşağıdaki alanlar için konum değişikliği önermiyorum. Her passage ilgili summary ve quote bulgularının finding_evidence’ına bağlıdır. 0208 ile başlayan iki başlık pasajının summary/quote bulgusu vardır; comparison_field bağlantısı yoktur.

| Passage | Mevcut field | Mevcut row | Konu |
|---|---|---|---|
| 0309-emep-pdf-000-0-passage | 0309-emep-pdf-000-0-field | 0309-emep-pdf-000-0-row | uyelik-aidati |
| 0309-emep-pdf-002-0-passage | 0309-emep-pdf-002-0-field | 0309-emep-pdf-002-0-row | merkez-kurul-olusumu |
| 0309-emep-pdf-004-0-passage | 0309-emep-pdf-004-0-field | 0309-emep-pdf-004-0-row | merkez-yurutme |
| 0309-emep-program-pdf-000-0-passage | 0309-emep-program-pdf-000-0-field | 0309-emep-program-pdf-000-0-row | calisma-sureleri |
| 0309-emep-program-pdf-003-0-passage | 0309-emep-program-pdf-003-0-field | 0309-emep-program-pdf-003-0-row | sosyal-guvenlik |
| 0309-emep-program-pdf-003-1-passage | 0309-emep-program-pdf-003-1-field | 0309-emep-program-pdf-003-1-row | temel-yurttaslik-geliri |
| 0309-emep-program-pdf-004-0-passage | 0309-emep-program-pdf-004-0-field | 0309-emep-program-pdf-004-0-row | orman-su-yonetimi |
| 0309-emep-program-pdf-005-0-passage | 0309-emep-program-pdf-005-0-field | 0309-emep-program-pdf-005-0-row | avrupa-birligi |
| 0309-emep-program-pdf-007-0-passage | 0309-emep-program-pdf-007-0-field | 0309-emep-program-pdf-007-0-row | genel-secim-oy |
| 0309-emep-program-pdf-007-1-passage | 0309-emep-program-pdf-007-1-field | 0309-emep-program-pdf-007-1-row | genclik |
| 0309-emep-program-pdf-009-0-passage | 0309-emep-program-pdf-009-0-field | 0309-emep-program-pdf-009-0-row | engellilik |
| 0309-emep-program-pdf-009-1-passage | 0309-emep-program-pdf-009-1-field | 0309-emep-program-pdf-009-1-row | sosyal-guvenlik |
| 0309-emep-program-pdf-009-2-passage | 0309-emep-program-pdf-009-2-field | 0309-emep-program-pdf-009-2-row | temel-yurttaslik-geliri |

Bu tablo konu anlamlarının yeniden kabulü değildir: örneğin9.maddedeki belirli yararlanıcı aylığının evrensel gelir olup olmadığı veya15.maddedeki seçilme hakkının oy verme hakkı olup olmadığı ayrı anlamsal kapsam sorularıdır. Burada verilen görev doğrultusunda yalnız mevcut kaydın metin/sayfa karşılığı ve alan soyu hedefli denetlenmiştir.
