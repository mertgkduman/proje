# Aydın kaynak incelemesi gerçek hata ve düzeltme

Paket `2b56b5767b3caa81c79911eeacfb0de4ae162ace75815a00b2d8dfec8fc43b6f`, ilk review `1eeaa995369b60ebe349e3a77a341bccb09ccac4dd4d4a6352001db54af27d07` için gerçek `practice-source-check` session 49943 çıkış 1: `Aynı genel açıklama birden çok hedefe kopyalanamaz`. Aydın hedeflerine aynı genel okuma açıklamasının tekrarlanması hataydı; gerçek red ve eski review korunuyor.

Yeni review v2 SHA256 `f7a5d3da6ceb0340b4afd287c117933b94bb515cb8e0c791d1ea0f19bb0e756a`: aynı gerçek pasajlara dayanan olay kanıtı, olay, ilişki, hedef ve açıklama için ilgili iddialar ayrı yazıldı. 165 açıklamada tekrarlı dörtlü olmadığının mekanik kontrolü tam CLI değildir. Aynı paket ile yeni review için source-check session 97095 çalışıyor; sonuç henüz alınmadı.
