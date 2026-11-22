# Açık oylama cetvelinin karakter kodlaması

TBMM’nin 5 Kasım oylama cetveli UTF-8 olarak çözümlenemiyor. Özgün bayt özetinin `dee8048e3732d2414f3db05c106dfa60b39b8d7a92cff70bb31198527e0939da` olduğu doğrulandı. Özgün HTML yanıtı bir karakter kodlaması bildirmiyor. Windows-1254 ile kurum başlığı, sayım başlıkları ve oy satırları okunuyor. Bu yerel okuma tercihi, aynı özgün özet ve URL’yi taşıyan doğrulanmış pasif görünüm manifestinde bulunuyor.

62388874, denetçinin beklediği okunabilir yan dosya biçimiyle uyuşmadı. 46c2b43 bu yan dosyayı mevcut üretim yardımcısıyla oluşturdu. 62388886 girdi denetimini geçti. Kaynak denetiminin kullandığı önizleme, özgün HTML’yi tek başına UTF-8 olarak çözmeye çalıştığı için durdu.

Önizleme, normal çözüm başarısız olduğunda aynı belge sürümü, özgün özet ve URL’ye bağlı pasif görünümün doğrulanmış manifestini kullanır. Kaynak kökü ve pasif görünüm güvenceleri bu yolu da kapsıyor. Özgün cetveldeki baytlar korunuyor. Eşleşen manifest, yokluk ve başka bir URL için odaklı denetim ile etkin öğe ve kök dışı yol denetimi başarılı. 62389517 tam gerçek paket denetimini yeniden çalıştırıyor.
