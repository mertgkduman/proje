# Kaynak türevi düzeltmesi

Üç yeni haberin yanlış oluşturulan, yayımlanmamış `readable.html` türevi özgün baytları değiştirmeden düzeltildi. Kanonik `f67ca0a35e634035bf3aa83a46571f50` veritabanında üç SHA için sıfır belge sürümü vardır; bu nesnelerin Git geçmişi sadece bu planın `94b026f` ve `c81bc19` yakalama kayıtlarını gösterir. Eski türevler aynı nesne dizininde `readable-invalid-diagnostic.html` olarak korunmuştur; yeni türev `arsiv.readable_bytes(raw, 'html')` ile üretilmiş ve `readable-verified.html` ile de saklanmıştır.

| Özgün nesne SHA-256 | Eski türev SHA-256 | Düzeltilmiş türev SHA-256 |
| --- | --- | --- |
| `39f724a48147da9c146b05f45eefdee8ec1a8c2f6bcf1cc38d1a5154972ba3da` | `1d97ad8ccaae3e7b09ad94a3d11b932e03f8fa1b888578881077e94edf97531a` | `57bce4707402c146416d9c6c55499b3141eea674accdb795d4300166428861ef` |
| `f4cda8687670963c3dff4d850192c9fd50e109589d59dd7e219751fb3cde22b5` | `3edad37999314b29f7eae99cbb90965013fbd7168f2d7ae9b7041779657bde3e` | `ee4f91a5940ea06a668164ae5b978e78f9d0925e305288a2b69c2f9f5b5ca06e` |
| `d7e6c67db7bc3f5e5c4f04a718e1c3b8d3897ddd2664a2256ed7cdc0725e2615` | `350a2efbb3d193248f8274ea897b7b6860aa872301497fb4f18e3875979102e4` | `cffc918224a2cc84478a10532a7885db42bba18581ff679fa13251f6237ab035` |

Muğla v2 staging kontrolü, yanlış türev nedeniyle `Okunabilir arşiv özgün belgeden farklı`; v3 staging kontrolü ayrı doğru türev dosyasıyla `PRACTICE_INPUT_OK` verdi fakat v3 preview standart olmayan türev adı nedeniyle `Kaynak nesne yolu veya özeti geçersiz` dedi. v4 standart `objects/<sha>/readable.html` yolunu kullanır. v4 preview ve kaynak incelemesinin gerçek sonuçları henüz bekleniyor; bu belge başarı iddiası değildir.
