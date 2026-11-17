# Faz 04 açık probe varsayımları

SPEC yok; fallback açık, Edge Coverage ve Prohibitions bölümleri sağlanmadı. Ham deterministik çıktı 04-EDGE-PROBE.json'dadır. Satırlar **sınıflandırılmamış ve çözülmemiş** kalır; aşağıdaki kabul ölçütlerinin planlanması bunları otomatik çözmez.

| Gereksinim | category | status | verification | probe | Yönlendirme |
|---|---|---|---|---|---|
| UYG-01 | unclassified | unresolved | null | unclassified — review manually | flagged assumption; yöntem/gerçek kaynak ve okuyucu kabulünde açık tutulur |
| UYG-02 | unclassified | unresolved | null | unclassified — review manually | flagged assumption; aktör/dönem/kanıt yorumu kabulünde açık tutulur |
| KAR-03 | unclassified | unresolved | null | unclassified — review manually | flagged assumption; ortak ölçüt/kapsam kabulünde açık tutulur |

No-silent-drop: applicable=3, resolved=0, unresolved=3; 3 surfaced = 0 lifted resolved truth + 3 flagged assumptions. Unclassified satıra backstop/explicit çözüm atanmamıştır. Sonraki doğrulayıcı bu satırları göz ardı ederek “tamamı çözüldü” diyemez.

## Yasak probu: adversarial recall → precision

Her gereksinim için “Bu özellik yazarın istemeyeceği neye dönüşebilir?” sorusu uygulandı. Aşağıdaki aday listeleri recall kaydıdır; hepsi yeni gereksinim değildir.

| ID | Recall adayları | Precision |
|---|---|---|
| UYG-01 | Sonuca göre olay seçme; kanıt eksikliğini olumsuz sonuç sayma; söylemi olay kanıtı sayma; ortak olayı çoğaltma; bağı yanlış konuya kurma; eski sürümü gizleme; yanlış FK; boş liste hatası; HTML script; path traversal | İlk iki değer kısıtı tek olay seçimi prohibition'ında korunur; söylem/olay ve ortak kimlik zaten açık D-03/D-05 uygulamasıdır; FK/boş liste mühendislik kontrolleridir; script/path canon'a yönlendirilir |
| UYG-02 | Niyet uydurma; kaynakta olmayan sorumluluk; yanıt vermedi iddiası; üyeliği tüm kararlarına destek sayma; sonraki vaatle geçmiş ihlal; yetkiyi yanlış okuma; tarih parse; eksik alan; SQL injection; gizli credential çıktısı | Kaynaksız niyet/sorumluluk/yanıtsızlık tek şeffaflık prohibition'ında korunur; diğer içerik D-09/D-11 açık kurallarıdır; parse/alan mühendisliktir; injection/credential canon'a yönlendirilir |
| KAR-03 | Partileri puanlama; oy yönlendirmesi; tarama farkını üstünlük sayma; cherry-picking; ortak konuyu düşürme; bir partiye daha sıkı standart; dönemi gizleme; yavaş DOM; kaynak hash; XSS | Puanlama/yönlendirme/tarama farkından siyasi sonuç tek proje değeri prohibition'ında korunur; cherry-picking UYG-01 ile birleştirilir; ortak konu/dönem kaynak kararları zaten planlıdır; DOM/hash mühendisliktir; XSS canon'a yönlendirilir |

Canon breadcrumb: XSS, path traversal, SQL injection ve sır sızıntısı OWASP/ASVS kanonudur; her planın somut threat_model kontrolleri ve $gsd-secure-phase tarafından ele alınır; yeni prohibition olarak üretilmedi.

## Korunan değer kısıtları

Üç kayıt projectProhibitions serializer'ıyla /hpc/home/mg551/.codex/gsd-core/bin/lib/probe-core.cjs üzerinden gerçekten projekte edildi. Projeksiyon 04-15-PLAN.md must_haves.prohibitions sibling alanına descriptor olmadan yazıldı. Bunlar **flagged-unverified**, status=unresolved; check_kind/check_target/check_rule/check_violation_fixture/check_clean_fixture üretilmedi. Kullanıcı veya downstream gerçek inceleme olmadan resolved/dismissed yapılmaz.

1. UYG-01: Siyasi sonuç lehine veya aleyhine olduğu için uygun olayları seçerek dışarıda bırakma; bütün uygun kaynaklı eşleşmeleri koru.
2. UYG-02: Kaynakta bulunmayan niyet, kişisel ya da kurumsal sorumluluk veya yanıt vermeme iddiasını kanıtlanmış sonuç gibi sunma.
3. KAR-03: Tarama ve kanıt kapsamı farklarından parti lehine/aleyhine puanlama, sıralama veya oy yönlendirmesi üretme.

No-silent-drop: 3 precision-kept = 3 authored prohibitions + 0 dropped; 0 resolved, 3 unresolved. Ham/projection nihai 04-probe-record.json ve UAT'de korunur. Bu belge bir source kullanımı insan ön kabul kapısı değildir.

