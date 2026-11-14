# Çalışma alanı hazırlığında erken kesilme

İlk 03-14 çalışma alanı hazırlama denemesi yeni session olmadan `nohup` ile
başlatıldı. Wrapper ve `arsiv.py workspace` işçisi araç oturumu bitince
sonlandı; günlük boş kaldı, çıkış dosyası oluşmadı ve kabul edilmiş sürüme
yayın yapılmadı. Denemeden önce `data/.write.lock` yoktu. Sonrasında görülen
kilit bu hostta PID 696292'ye işaret ediyordu; bu PID ve wrapper PID'sinin
yaşamadığı kontrol edildi. Yalnız o gözlenen host/PID eşleşmesi doğrulanarak
denemenin sahipsiz kilidi kaldırıldı. `data/current.json` kabul edilmiş
`ae42ae1897864fda810b033ce3ac1e8f` sürümünü göstermeye devam etti.

**Kanıt sınırı:** Kilidin tam baytları ve token'ı silinmeden önce ayrı dosyaya
kaydedilmedi. Bu nedenle token'ın harici bir sahiplik kaydıyla eşleştiği
geriye dönük iddia edilemez. İlk deneme başarılı sayılmadı. Sonraki deneme
`start_new_session=True`, `DEVNULL` stdin, kalıcı günlük/çıkış ve
PID/host/token içeren `run.json` ile ayrı yürütülür; aynı adlı herhangi başka
bir kilidin kaldırılması için bu olay emsal değildir.
