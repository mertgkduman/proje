# Eski doğrulama kayıtları gerçek hata ve düzeltme

Satır kimlikleri düzeltilmiş paket SHA `a3e4bd51409df102f4066d00938c06ddfa258fb88ba2e940a973991c26628fb0` ile gerçek staging practice-check session 56754 çıkış 1 `Önceki kayıt değiştirilemez`. Salt okunur temel DB birincil anahtar karşılaştırması üç çakışma buldu: `0105-action-provinces|0105-provinces-p` ve `0105-tbmm-statement` için iki mevcut pasaj doğrulaması. Bunlar aynı anahtara farklı tarih/gerekçe ile yeniden eklenmişti; mevcut doğrulamalar ve tekrar okuma kayıtları korunarak yalnız üç gereksiz yeni `verification` girdisi ayrı kopyadan çıkarıldı.

Yeni paket SHA256 `c69ca34f9dee8c641b7bc760da9a4e8dec948dd9a7f4c0757a6b4e162b308ef1`, review SHA256 `3a986b6a636fef482a0c1ab7a4cc166eb46a02c571d703a1606cde997c64b186`; 234 staging kaynak yolu eşit. Aynı gerçek CLI session 43994 sürüyor; sonucu henüz alınmadı. Eski red ve girdiler saklandı, bu işlem kapsam veya plan kapanışı değildir.
