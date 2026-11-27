# Phase 5: Finansman ve harcamaların belgelenmesi - Context

**Gathered:** 2026-11-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Onaylı dokuz parti için kaynakla izlenebilir gelir ve gider bilgileri ve bu bilgilerin kapsamadığı hesap dönemleri gösterilir.

</domain>

<decisions>
## Implementation Decisions

### Hesap dönemleri

- D-01 Kullanıcının 27 Kasım onayıyla 2023, 2024 ve 2025 hesap dönemleri taranır. Kaynaklarda bulunan en yeni yayımlanmış kesin hesap daha eskiyse o dönem de açık dönem etiketiyle gösterilir.
- D-02 Hesap dönemi, karar tarihi, yayım tarihi, para birimi ve örgütsel kapsam ayrı bilgilerdir. Farklı dönem ve kapsamlar arasında toplama veya sıralama yapılmaz.
- D-03 Sicil kimliği kesin hesapta geçen partiyle eşleştirilir. Aynı adla anılan başka tüzel kişiler ve ittifak bileşenleri ayrı tutulur.

### Kaynak ve eksikler

- D-04 AYM’nin yayımlanmış kararı veya Resmî Gazete kaydı resmî kesin hesap için kanıttır. Gündem ve ilk inceleme kayıtları ancak ilgili süreci belgeleyebilir. Parti yayını kendi yayıncı atfıyla kullanılabilir.
- D-05 Gelir, gider ve devreden kalemler kaynağın adlandırmasıyla kaydedilir. Tutarı açıklamayan ve ulaşılamayan belgeler için proje statüleri ve arama kaydı kullanılır.
- D-06 Kaynak metinleri değiştirilmeden saklanır. Onaylı çalışma alanı yazıcısı ve mevcut Türkçe HTML bölümünden üretilir.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets

- `src/arsiv.py` mali kayıt, mali dönem, tutar/pasaj denetimi, kaynak atfı ve gerekçeli eksik kaydı sağlıyor.
- `src/rapor_v30.py` mali kayıtların dönemini, kapsamını, yayımını ve kanıt bağını okuyucuya gösteriyor.
- `tests/test_finance.py` tutar biçimi, açık sıfır, eksik tutar ve kaynak ilişkisini sınar.

### Established Patterns

- Yeni belgeler değişmez özgün kopya ve okunabilir türev olarak saklanır.
- Kayıtlar çalışma alanında doğrulandığında değişmez HTML, SQLite ve JSON sürümü üretilebilir.

### Integration Points

- Faz 4’ün tamamlanan dokuz partilik teslimi kanonik tabandır.
- Finansman başlığı için kesin hesap bulgusu veya gerekçeli eksik bilgisi her partide görünür.

</code_context>

<specifics>
## Specific Ideas

- Tablodaki tutarın birimi ve kapsamı orijinal kararda hangi anlamla verildiyse o anlam korunur.

</specifics>

<deferred>
## Deferred Ideas

- Tam arama dönemi dışındaki eski yılların sistematik taraması ve farklı dönemler için fiyat düzeltmesi.

</deferred>
