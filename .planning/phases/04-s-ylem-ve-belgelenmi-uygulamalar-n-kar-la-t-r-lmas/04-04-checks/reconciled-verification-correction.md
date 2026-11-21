# Birleşik Yeni Parti taslağında program doğrulama bağları

`62376013` girdi denetimi `Partiyle eşleşen doğrulanmış bulgu gerekli` hatasıyla durdu. İki seçili Faz 3 Sosyal Hizmetler bulgusunun kaynak ve önceki inceleme satırları mevcuttu. Faz 4’ün aradığı dört açık `verification` bağı eksikti. Birleşik girişte kullanılan 79 bulgunun tüm kanıt ve inceleme bağlantılarında eksik yalnız bu dört bağdı.

`epm-program-v1` özgün SHA-256 kimliği, Sosyal Hizmetler bölümündeki üç pasajın özgün metindeki eşitliği ve alıntının ilk pasaja uyumu yeniden kontrol edildi. Üç doğrulama özete, bir doğrulama alıntıya eklendi. Bulgu, pasaj, Faz 3 seçimi ve arşivdeki eski kayıtlar aynı kaldı. `elder-care-verification-draft.json` bu dört satırı ayrı taşır.

`62376648`, `package-reconciled-verification-draft.json` ve mevcut `reconciled-review-draft.json` üzerinde girdi, kaynak ve önizleme denetimlerini çalıştırıyor. Başarı yeni işin kayıtlarıyla belgelenecektir.
