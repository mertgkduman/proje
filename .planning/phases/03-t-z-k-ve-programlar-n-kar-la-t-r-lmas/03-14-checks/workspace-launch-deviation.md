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

## 14 Kasım: başarısız yayın ve aynı çalışma alanına dönüş

Atomik eşleme `COMPARISON_RECONCILE_OK` ve çıkış 0 ile bitti. Bu koşunun
üç girdi dosyası koşu süresince değiştirilmedi; koşu öncesi SHA ayrıca
alınmadı. Koşudan hemen sonra değişmeyen `f76ab7d` girdileri için SHA ve salt
okunur kopyalar `/tmp/gsd-0314-reconcile-inputs/` altında kaydedildi. İlk
sentez yüklemesinde salt okunur girdi süreçten önce oluşturuldu; SHA ise süreç
başlatıldıktan sonra run kaydına yazıldı. Sonraki koşularda kopya/SHA ve ilk
run kaydı süreç başlamadan oluşturulur.

İlk yerel yayın denemesi yeni bir bulguda Faz1 kaynak inceleme ilişkisinin
eksikliği nedeniyle çıkış 1 ile reddedildi; kabul edilmiş current işaretçisi
değişmedi. Yayın fonksiyonunun `finally` bölümü bu çalışma alanına ait
kilidi kaldırdı. Desteklenen bir workspace-resume komutu bulunmadığından,
aynı workspace metadata belirteci, sabit current/base ve O_EXCL ile bu
çalışma alanının kilidi yeniden alındı. Başka kilit üzerine yazılmadı.
O_EXCL öncesi workspace DB SHA'sı ayrıca ölçülmedi: sonradan başarısız
yayının staging DB SHA'sı, yayın öncesi kaydedilmiş workspace SHA'sıyla
`ed109bca93d73600ccb154e26ebb34af4c1e1b182b1d9e2a1f568e4b605e426b`
olarak birebir eşleşti. İlişki yüklemesinden sonra staging ile workspace'in
review dışındaki bütün tabloları iki yönlü EXCEPT ile eşitti; eski review
kaybı sıfır ve eklenen review sayısı 108 idi. İnceleme soyları
`finding-review-lineage.json`, yüklenebilir ilişkiler
`data/comparisons/03-finding-review-links.json` içindedir. Tam Faz1 workspace
kontrolü `PHASE_ONE_WORKSPACE_OK 8022` verdi. Başarısız yayın başarı olarak
kaydedilmedi; yalnız yayın adımı yeni tam kontrollerle tekrar başlatıldı.

Kısmi `4da93e2c64914eecb875c66cca14ea57` yayını sonraki denemede çıkış 0 ile
kabul edildi. Bu tabandan yeni workspace hazırlayan ayrı süreç, v3 tipli
sentezlerin v4 altındaki doğrulama düzeltmesinden önceki kodla başlatıldı.
Bu süreç yalnız mevcut v3 tabanı açıp kendi eski sözleşmesiyle denetler; v4
reconcile, sentez yüklemesi ve son denetimler GREEN kodla ayrı yürütülür.
