# Kaynak araştırmacısı dispatch notu

Tıbbi kaynakların açık hücreleri ve önceki 10 politika sentezinde eksik
taraflar için iki ayrı `gsd-phase-researcher` görevi salt okunur, yalnız
`/tmp` çıktılı olarak açıldı. Her iki dispatch öncesinde model çözücüsü ayrı
çağrıldı ve `gpt-6.1-sol` döndü. Araçta rolün model ve reasoning ayarları
sabit olarak `gpt-6.1-sol` ve `xhigh` tanımlıdır; Astra kullanılmadı.

İki dispatch öncesinde `query resolve-model gsd-phase-researcher --pick effort`
ayrıca çalıştırılmadı. Bu, istenen eşlenik sorgu kanıtındaki süreç sapmasıdır;
sonradan alınacak sonuç önceden alınmış gibi gösterilmez. Çalışan araştırma
kesilmedi. Sonraki typed dispatch öncesinde model ve effort ayrı taze
sorgulanacaktır.
