---
phase: "01"
slug: "kapsam-y-ntem-ve-kaynakl-pilot-rapor"
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-11-10"
---

# Faz 1 — Doğrulama stratejisi

Bu belge yürütme için taslaktır; testlerin çalıştığını veya pilot içeriğinin doğrulandığını iddia etmez. Planlayıcı görev/test eşlemesini son planlarla eşitleyecektir.

## Test Infrastructure

| Özellik | Değer |
|---|---|
| Framework | Python standart kitaplığı `unittest` |
| Yapılandırma | Wave 0'da `tests/` ve yerel fixture'lar kurulacak |
| Hızlı komut | `python3 -m unittest discover -s tests -v` |
| Tam paket | `python3 -m unittest discover -s tests -v` + planlarda tanımlanacak gerçek veri/rapor denetimi |
| Süre hedefi | Hızlı <30 sn; tam otomatik <60 sn; henüz ölçülmedi |

## Sampling Rate

- Her görev commit'inden sonra hedefli test; henüz olmayan testin önceki Wave 0 görevi açık olmalı.
- Her plan dalgasından sonra tam paket ve gerçek veri/çıktı bütünlüğü denetimi.
- `$gsd-verify-work` öncesi tam paket yeşil, kaynak doğruluğu ve tarayıcı incelemesi tamamlanmış olmalı.
- Sıfır test, çalıştırılmamış test veya eksik tarayıcı kontrolü başarı değildir.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---|---|---|---|---|---|---|---|---|---|
| Planlama sonrası atanacak | — | 0 | VER-01, KAY-02, KAY-03 | — | Scratch DB ve kaynak bütünlüğü | Integration | `python3 -m unittest discover -s tests -v` | Hayır, Wave 0 | pending |
| Planlama sonrası atanacak | — | — | KAPS-01–04 | — | Kapsam/kimlik korunur | Contract | Planlarda hedefli test atanacak | Hayır | pending |
| Planlama sonrası atanacak | — | — | MET-01–04 | — | Kaynak metni kaçışlanır, köken korunur | Integration/browser | Planlarda hedefli test atanacak | Hayır | pending |
| Planlama sonrası atanacak | — | — | EKS-01–02 | — | Girişimsiz eksik/sıfır üretilemez | Contract | Planlarda hedefli test atanacak | Hayır | pending |

## Wave 0 Requirements

- [ ] `tests/` ve küçük yerel belge fixture'ları; sıfır testin sahte başarı sayılmaması.
- [ ] Yerel scratch DB yazma–kapatma–yeniden okuma düzeneği.
- [ ] Kaynak/pasaj, hash ve yerel HTML/arşiv bağlantısı denetimi.
- [ ] Paket kurmadan kullanılabilir tarayıcı yolunun keşfi ve ürün probu.

## Manual-Only Verifications

| Davranış | Gereksinim | Neden insan incelemesi | Adımlar |
|---|---|---|---|
| Alıntı/özet/pasaj doğruluğu | KAY-02, MET-01–04 | Metnin kaynak sınırını aşması salt şemayla anlaşılamaz | Her önemli bulguyu özgün pasajla karşılaştır; alıntıyı ve özetin anlamını kontrol et |
| Kapsam, kimlik, tarafsız yöntem | KAPS-01–04 | Hukuki kimlik ve aktör bağlamı yargı gerektirir | Arşiv TBMM/Yargıtay kayıtlarını aç; ad/grup/üyelik ve dışlama gerekçelerini karşılaştır |
| Okunabilirlik ve kaynak etkileşimi | MET-01–03, KAY-03, EKS-02 | DOM kontrolleri gerçek okuma incelemesini tamamlamaz | Kaynak bağlantısı, geri/fokus, klavye, dar ekran ve çevrimdışı arşivi dene; özet ve alıntıyı birlikte gör |

## Validation Sign-Off

- [ ] Her görevde `<automated>` + `<fails_when>` veya açık Wave 0 bağımlılığı.
- [ ] Üç ardışık doğrulamasız görev yok.
- [ ] Wave 0 bütün henüz olmayan test yollarını karşılıyor.
- [ ] Watch kipinde veya sınırsız komut yok.
- [ ] Son görev eşlemesi ve tehdit referansları planlarla eşit.
- [ ] Gecikme hedefleri yürütmede ölçüldü.
- [ ] Gerçek testler/kaynak incelemesi sonrası `nyquist_compliant` ve `wave_0_complete` güncellendi.

**Approval:** pending — plan ve yürütme kontrolü tamamlanmadı.
