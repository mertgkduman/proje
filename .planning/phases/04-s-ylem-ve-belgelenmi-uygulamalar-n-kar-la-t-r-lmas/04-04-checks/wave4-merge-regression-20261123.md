# Birleşim geri oynatma denetimi

62487356 işinde dokuz birleştirme motoru testi ve kapsam ile inceleme kapılarını deneyen kalıcılık testi geçti. Gerçek arşiv önizlemesi oluşturup yeniden denetleyen test iki saatlik Slurm sınırına ulaştı. Bu koşumda son iki test için toplu sonuç alınamadı. [İlk koşum](wave4-merge-page-regression-62487356.log)

Kayıp ilişkilendirme, kanıt ve kökeni reddeden tekrar oynatma testi ayrı koşumda geçti. Sonuca SQLite TEXT sütununa tamsayı olarak girilen sayfa numarası ve geçersiz farklı metin değerleri de dahil. Gerçek arşiv önizleme testi 62491689 işinde tek başına 1 saat 29 dakikada geçti. Test arşiv önizlemesini, SQLite ile JSON eşitliğini, birleştirilen olay ve kaynak incelemesi kökenlerini, manifest özetini ve `audit_release` denetimini tamamladı. [Gerçek arşiv koşumu](wave4-merge-preview-roundtrip-62491689.log) [Odaklı test](wave4-merge-replay-focused.log)

Dokuz parti paketini kullanan 62487355 provasının JSON, SQLite, iki HTML görünümü ve sabit yayın işaretçisi kendi makbuzunda doğrulandı. [Dokuz paket provası](wave4-merge-rehearsal-preview-pages-62487355.json)
