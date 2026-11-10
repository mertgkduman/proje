# Kaynaklı pilot arşiv

Python 3 ve standart kitaplık ile yerel kullanım içindir. Ağdan kaynak alma işlemi yalnız açıkça çalıştırıldığında yapılır; testler kaydedilmiş kaynağı kullanır. Raporu kamuya yayınlamaz.

1. `python3 src/arsiv.py capture --url https://www.yargitaycb.gov.tr/sipar/365 --kind html` kaynak baytlarını `data/objects` altında özetiyle saklar ve kayıt alanlarını JSON olarak döndürür. `--out DIR` ayrı bir nesne kökü seçer.
2. `python3 src/arsiv.py workspace --scratch /tmp` tek yazıcı kilidini alır, geçerli doğrulanmış snapshot'tan yerel çalışma dizini oluşturur ve dizini yazdırır. Çalışan SQLite için yerel dosya sistemi gerekir.
3. Her satırı `python3 src/arsiv.py record --workspace DIZIN --kind party --input -` ile stdin üzerinden JSON vererek yazın. Türler: `party`, `document`, `document_version`, `passage`, `finding`, `finding_evidence`, `comparison`, `comparison_evidence`. İlişkili üst kayıtları önce girin; kaynak ve bulgu ilişkileri zorunludur.
4. `python3 src/arsiv.py publish --workspace DIZIN` kapalı snapshot, türetilmiş JSON ve HTML'yi doğrulayıp atomik işaretçiyi değiştirir. `python3 src/arsiv.py audit --release current` doğrulanmış sürümde `AUDIT_OK` verir.
5. `python3 src/arsiv.py serve --host 127.0.0.1 --port 8000` sonrasında `data/current.json` içindeki release kimliğiyle `http://127.0.0.1:8000/releases/KIMLIK/index.html` açılabilir.

JSON ve HTML yalnız snapshot'tan türetilir; elle düzenlenmez. `python3 tests/run.py` tüm testleri, `python3 tests/run.py --pattern test_publication.py` seçili testleri çalıştırır; sıfır test başarı değildir. Tarayıcı testi Chrome/Chromium'u veya `BROWSER_BIN` ile verilen çalıştırılabilir dosyayı kullanır.

Yayın başarısızsa `audit --release current` ile son sürümü doğrulayın, ardından yeni workspace oluşturup kayıtları yeniden uygulayın. `.staging` altında kalan dizinler yayınlanmamış adaylardır; etkin yazıcı bulunmadığını doğruladıktan sonra içeriğini inceleyip ayrı ayrı silebilirsiniz. `.write.lock` dosyasını yalnızca içindeki makine ve PID için sahibinin öldüğü bağımsız olarak kanıtlandığında silin; yaşına bakarak silmeyin. İşaretçi değişmişse önce yeni sürümü denetleyin. Ham HTML `.bin` olarak saklanır ve yerel sunucu tarafından indirme olarak sunulur; okunabilir kopya kaçışlanmıştır.
