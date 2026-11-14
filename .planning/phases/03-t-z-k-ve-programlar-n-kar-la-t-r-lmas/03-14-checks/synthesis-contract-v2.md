# Karşılaştırma sentezi sözleşmesi 2

Sözleşme 2, schema 6 üzerindeki mevcut `comparison_semantic_review` kaydını
kullanır; tablo, kolon veya eski kaynak kaydı değiştirmez. Seçili sözlük en az
3 olduğunda sözleşme 1'den 2'ye atomik geçişe izin verilir. Yayın manifesti
`comparison_validation_version: 2` ve
`comparison_synthesis_contract_version: 2` taşır. Sözleşme 1 snapshot'ları
eski doğrulamayla okunur. Daha yeni bir sözlük seçildiğinde, önceki sözlükteki
açık sözleşme-2 yazar incelemesi taşıyan cümle kendi tipli taraf ve gerçek
kanıt kurallarıyla doğrulanmaya devam eder; böyle bir kaydı olmayan sözleşme-1
cümlelerinin iki ayrı gerçek olumlu kaynak sahibi kuralı korunur. İnceleme
kaydının varlığı iddianın kapsamını otomatik üretmez veya kanıt koşulunu
gevşetmez. Renderer 17 ve 18 ile eski manifestlerin girdileri
değiştirilmez.

Her yeni seçili sentez için `subject_kind: comparison_synthesis`, o sentezin
kimliği, `reviewer_kind: agent`, zaman dilimli inceleme zamanı ve
`result: reviewed` taşıyan ayrı bir karar gerekir. `reason` alanı yazarın
hazırladığı JSON nesnesidir:

```json
{
  "contract_version": 2,
  "claim_type": "one_positive",
  "explanation": "Pasaj ve incelenmiş kapsamın cümleye uygunluğu hakkında kaynakçı gerekçesi",
  "sides": [
    {"party_id": "parti-a", "row_id": "satir-a", "support": "passage", "refs": ["pasaj-a"]},
    {"party_id": "parti-b", "row_id": "satir-b", "support": "scope", "refs": ["inceleme-b"]}
  ]
}
```

`multi_positive` en az iki ayrı partinin kendi konu alanına bağlı gerçek
pasajlarını; `one_positive` bir olumlu partiyi ve kapsam/belge durumu belirtilen
en az bir tarafı; `status_only` yalnız gerçek incelenmiş kapsam veya belge açığı
dayanaklarını belirtir. `scope` ilgili satırın `comparison_review_scope`
kimliğine; `missing` ilgili `missing` ve onun gerçek `attempt` kimliklerine
bağlanır; kapsam sonucu `no_explicit_statement` ve zamanı geçerli olmalıdır.
`passage` kimlikleri aynı satırın alan kanıtı olmalı ve sentezin
`comparison_synthesis_evidence` bağlantılarıyla tam uyuşmalıdır. Yazar bir
partinin hem ek/tarihsel kaynağını hem eksik bağımsız programını ayrı satırlarla
belirtebilir. Eksik veya dar kapsam, karşıt siyasi tutum anlamına gelmez.

Bu veri sözleşmesi kaynak anlamı, koşul veya cümlede sözü edilen tarafları
metinden otomatik çıkarmaz. Yazarın açıklaması ve kaynak incelemesi gerçek iddia
kapsamını göstermelidir; mekanik bağ doğrulaması bu araştırmanın yerine geçmez.
