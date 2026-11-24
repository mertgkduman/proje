"""Preserve Democratic Party releases, the reported AYM judgment and TBMM minutes."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks, stage = map(Path, sys.argv[1:])
root = Path("data/practices/sources/demokrat")
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()


def add(table, **values):
    entries.append(dict(kind=table, values=values))


def save(relative, data):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data
    else:
        path.write_bytes(data)
    paths.add(path)


def archive(document, label, path, url, date, publisher, author, accessed, expected_sha, slices):
    original = path.read_bytes()
    digest = sha256(original).hexdigest()
    assert digest == expected_sha
    party_publication = publisher == "Demokrat Parti"
    version = document + "-v1"
    pdf = path.suffix == ".pdf"
    kind = "pdf" if pdf else "html"
    original_name = f"objects/{digest}/" + ("original.pdf" if pdf else "original.html.bin")
    readable = f"objects/{digest}/readable.html"
    save(original_name, original)
    save(readable, readable_bytes(original, kind, legacy=False))
    add("document", id=document, party_id="demokrat", title=label,
        source_kind="party" if party_publication else "official")
    add("document_version", id=version, document_id=document, original_url=url,
        final_url=url, document_date=date, date_precision="day", date_unknown_reason=None,
        version_label="Yayıncının özgün nüshası.", accessed_at=accessed, verified_at=now,
        mime="application/pdf" if pdf else "text/html", sha256=digest,
        original_path=original_name, readable_path=readable)
    add("source_attribution", version_id=version, publisher=publisher, author=author,
        kind="party_publication" if party_publication else "official", published_at=date,
        date_precision="day", social_handle=None, public_url=url,
        basis="Yayımlayan kurum ve tarih özgün nüshada gösteriliyor.")
    if not pdf:
        view = build_view(original, url, root, fetch_assets=False)
        view["version_id"] = version
        validate_view(root, view)
        manifest = root / view["manifest_path"]
        paths.add(manifest)
        paths.update(manifest.parent / name for name in json.loads(manifest.read_bytes())["files"])
        add("archive_view", **view)
    for key, index, printed, section, exact in slices:
        text = pdf_page_text(path, index) if pdf else html_source_text(original)
        optical = publisher == "Resmî Gazete" and index != 0
        if optical:
            assert not text.strip()
        else:
            assert exact in text, (document, section, exact)
        passage_id = document + "-" + key
        add("passage", id=passage_id, version_id=version, exact=exact, prefix=None, suffix=None,
            article=None, section=section, pdf_page_index=index, printed_page=printed)
        if optical:
            add("manual_passage", passage_id=passage_id, checked_at=now,
                method="Resmî Gazete özgün PDF sayfası Poppler ile görüntülenerek okundu.",
                reason="İlgili tarama sayfasının metin katmanı boş. İfade sayfa görüntüsünde görüldü.")


news = {row["position"]: row for row in
        json.loads((checks / "party-news-010-reading.json").read_bytes())["examined"]}
party_sources = (
    (104, "0412-divan-notice", "22 Temmuz 2023 GİK toplantısı ve görev dağılımı duyurusu",
     "DP Basın Merkezi", (
        ("meeting", None, None, "22 Temmuz tarihli DP Basın Merkezi bildirimi",
         "22 Temmuz 2023) Demokrat Parti Genel İdare Kurulu"),
        ("secretariat", None, None, "Ertan Küçükay adı ve Genel Sekreterlik görevi",
         "Genel Sekreter Ertan"),
        ("spokesperson", None, None, "Altıntaş’ın sözcü olarak görevlendirildiği satır",
         "İzmir Milletvekili Haydar Altıntaş olarak"),
     )),
    (97, "0412-atalay-statement", "9 Kasım 2023 Altıntaş’ın Can Atalay ve AYM açıklaması",
     "Haydar Altıntaş", (
        ("case", None, None, "Atalay kararının uygulanmasına yönelik eleştiri",
         "Can Atalay kararını yok sayması"),
        ("position", None, None, "Yargıtay daire mensupları hakkında işlem çağrısı",
         "derhal yasal işlem başlatılmalıdır."),
     )),
)
for pos, document, label, author, slices in party_sources:
    row = news[pos]
    archive(document, label, checks / row["original_path"], row["url"], row["displayed_day"],
            "Demokrat Parti", author, row["accessed_at"], row["sha256"], slices)

court = stage / "aym-99744-rg.pdf"
archive("0412-atalay-aym", "Can Atalay (3), AYM 2023/99744, 27 Aralık Resmî Gazete",
        court, "https://www.resmigazete.gov.tr/eskiler/2023/12/20231227-15.pdf",
        "2023-12-27", "Resmî Gazete", "Anayasa Mahkemesi Genel Kurulu",
        datetime.fromtimestamp(court.stat().st_mtime, timezone.utc).isoformat(),
        "261830c334860c66e81a5074cb02896aec2721a40a3e3e41bcd5bc81522c9875", (
            ("publication", 0, None, "27 Aralık yayım tarihi ve karar kapağı", "27 Aralık 2023 ÇARŞAMBA"),
            ("initial", 2, None, "§10, 25 Ekim 2023 tarihli ilk hak ihlali kararı",
             "Anayasa Mahkemesi Genel Kurulu 25/10/2023 tarihinde"),
            ("chamber", 3, None, "§17, Yargıtay 3. Ceza Dairesinin 8 Kasım kararı",
             "Yargıtay 3. Ceza Dairesi 8/11/2023 tarihinde"),
            ("complaint", 3, None, "§17, kararın suç duyurusu hükmüne ilişkin AYM aktarımı",
             "Yargıtay Cumhuriyet Başsavcılığına suç duyurusunda bulunulmasına"),
            ("decision", 22, None, "Hüküm B.1, bireysel başvuru hakkı",
             "hakkının İHLAL EDİLDİĞİNE OYBİRLİĞİYLE"),
            ("majority", 22, None, "Hüküm B.2, seçilme ve kişi hürriyeti hakkında oyçokluğu",
             "İNCE’nin karşıoyları ve OYÇOKLUĞUYLA"),
            ("order", 22, None, "Hüküm C, yeniden yargılama ve tahliyeyi sağlama işlemleri",
             "ceza infaz kurumundan tahliyesinin sağlanması"),
        ))

minutes = stage / "tbmm54.pdf"
archive("0412-atalay-tbmm", "30 Ocak 2024 TBMM 54. Birleşim 3/835 tutanağı",
        minutes, "https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/2/54/Basilmis/51d80cf1-ea9e-46c6-a3c8-d8cd19f40cee.pdf",
        "2024-01-30", "TBMM", "Tutanak Hizmetleri Başkanlığı",
        datetime.fromtimestamp(minutes.stat().st_mtime, timezone.utc).isoformat(),
        "82f14606b4f299479c7afe800483a9406a9b6154829163988716aa32433632e2", (
            ("reading", 81, "1048", "Yargıtay yazısının 3/835 ile Genel Kurulda okunması",
             "Yargıtay 3. Ceza Dairesinin bir yazısı vardır, okutuyorum"),
            ("case", 81, "1048", "3 Ocak tarihli karar yazısının dosya numarası",
             "Sayılı Karar yazımız ekinde gönderilmiştir."),
            ("notice", 82, "1049", "Oturum başkanının okuma sonrasındaki açıklaması",
             "Şerafettin Can Atalay’ın milletvekilliği düşmüştür."),
        ))

norm = stage / "aym-65-rg.pdf"
archive("0412-atalay-norm", "Can Atalay işlemi, AYM E.2024/43 K.2024/65, 1 Ağustos Resmî Gazete",
        norm, "https://www.resmigazete.gov.tr/eskiler/2024/08/20240801-16.pdf?download=1",
        "2024-08-01", "Resmî Gazete", "Anayasa Mahkemesi",
        datetime.fromtimestamp(norm.stat().st_mtime, timezone.utc).isoformat(),
        "4f44a3c051a60ab537f88dfafe109e6e354da8ca48bd4c1331e704263c92b30e", (
            ("publication", 0, None, "1 Ağustos 2024 yayım tarihi ve E.2024/43, K.2024/65 karar kapağı",
             "1 Ağustos 2024 PERŞEMBE"),
            ("reason", 5, None, "§25, okuma sonrası fiilî durumun değerlendirmesi",
             "ve böylece fiilî (de facto) bir durum oluşturulmuştur."),
            ("reason-legal", 5, None, "§24, Yargıtay kararına hukuki değer atfedilmesine ilişkin gerekçe",
             "karara hukuki değer atfedilmesi mümkün olmadığı gibi"),
            ("result", 7, None, "Hüküm, karar verilmesine yer olmadığı ve 22 Şubat karar tarihi",
             "KARAR VERİLMESİNE YER OLMADIĞINA"),
        ))

(checks / "divan-atalay-source-records.json").write_text(
    json.dumps(dict(party_id="demokrat", entries=entries), ensure_ascii=False, indent=2) + "\n")
(stage / "divan-atalay-source-paths").write_text("\n".join(map(str, sorted(paths))) + "\n")
print(len(entries), len(paths))
