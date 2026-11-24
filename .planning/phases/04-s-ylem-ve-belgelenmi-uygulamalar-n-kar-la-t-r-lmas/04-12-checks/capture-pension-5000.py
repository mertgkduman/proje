"""Archive the one-time 5,000 TL pension payment and its reported implementation."""

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
        final_url=url, document_date=date, date_precision="day" if date else "unknown",
        date_unknown_reason=None if date else "İlk yayım günü kaynakta belirtilmiyor.",
        version_label="Yayıncının özgün nüshası.", accessed_at=accessed, verified_at=now,
        mime="application/pdf" if pdf else "text/html", sha256=digest,
        original_path=original_name, readable_path=readable)
    add("source_attribution", version_id=version, publisher=publisher, author=author,
        kind="party_publication" if party_publication else "official", published_at=date,
        date_precision="day" if date else "unknown", social_handle=None, public_url=url,
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
        assert exact in text, (document, section, exact)
        passage_id = document + "-" + key
        add("passage", id=passage_id, version_id=version, exact=exact, prefix=None, suffix=None,
            article=None, section=section, pdf_page_index=index, printed_page=printed)


stem = "0412-pension-5000"
article = next(row for row in json.loads((checks / "party-news-010-reading.json").read_bytes())["examined"]
               if row["position"] == 96)
archive(stem + "-statement", "14 Kasım 2023 Altıntaş’ın bir defalık emekli ödemesi açıklaması",
        checks / article["original_path"], article["url"], article["displayed_day"], "Demokrat Parti", "Anadolu Ajansı",
        article["accessed_at"], article["sha256"], (
            ("critique", None, None, "AA metninde Altıntaş’ın 5.000 TL kapsamı değerlendirmesi", "Bunlar ciddi manada haksızlıktır"),
            ("farmers", None, None, "Çiftçi ve esnaf emeklilerine ilişkin aktarım", "esnaf ve sanatkar olarak"),
        ))
sources = (
    ("7464-register", "7464 sayılı kanunun TBMM sicili", None, "TBMM", None,
     "https://tbmm.gov.tr/Yasama/Kanun/8a8acb35-4a1d-4446-8146-018b193352df",
     "e7f41dc7dbebf8a986c6ff66a55a36f58507e23ff324ab0c8734e8f75bc4e1b9", (
        ("adopted", None, None, "Kabul tarihi", "25/10/2023"),
        ("published", None, None, "Resmî Gazete yayım günü", "02/11/2023"),
    )),
    ("7464-law", "7464 sayılı Kanun’un geçici 98’i ekleyen 20. maddesi", "2023-11-02", "TBMM", None,
     "https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y6/KanunMetni/0ad8a727-9c26-42ec-9eaa-e3d6dc92595d.htm",
     "63d72285427b6b274f326c3210f94c9dcf7268d42e933178b4ecde4841120101", (
        ("amount", None, None, "Geçici 98’in bir defalık tutarı", "dosya bazında 5.000 TL"),
        ("exclusion", None, None, "Dördüncü fıkradaki çalışma koşulu", "madde uyarınca ödeme yapılmaz"),
        ("eligibility", None, None, "Çalışma nedeniyle dışarıda bırakılan gruplar", "Ekim ayı içinde bu Kanun"),
    )),
    ("7491-register", "7491 sayılı kanunun TBMM sicili", None, "TBMM", None,
     "https://tbmm.gov.tr/Yasama/Kanun/76587700-6870-41fa-85ae-018c0159e5b9",
     "d718cf5853e48a26ea896e7cc5623a13dcab78875d60d6cdf4aa6ba4286ddbdd", (
        ("adopted", None, None, "48. Birleşimde kabul tarihi", "27/12/2023"),
        ("published", None, None, "Resmî Gazete yayım tarihi", "28/12/2023"),
    )),
    ("7491-law", "7491 sayılı Kanun’un çalışma istisnasını kaldıran 54. maddesi", "2023-12-28", "TBMM", None,
     "https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y6/KanunMetni/2c5232b7-098b-4fb5-98b8-9931160b7b3e.htm",
     "db97d993139eba1ed9d3ff2b34bfb39c7a7e3e917d8b63320c60afdc3630bbe1", (
        ("repeal", None, None, "Geçici 98’in dördüncü fıkrasını kaldıran 54. madde", "dördüncü fıkrası yürürlükten"),
        ("effective", None, None, "85(f) diğer maddelerin yürürlük tarihi", "Diğer maddeleri yayımı tarihinde"),
    )),
    ("csgb-nov27", "27 Kasım 2023 ÇSGB kapsam açıklaması", "2023-11-27",
     "Çalışma ve Sosyal Güvenlik Bakanlığı", "Vedat Işıkhan",
     "https://www.csgb.gov.tr/tr/haberler/27-11-2023/",
     "a2f80bfcfa3431b2fc9d27f9c2c4617c1aeb15739beff7e7d536ba21fd543719", (
        ("intent", None, None, "Bakanın kapsamı genişletme açıklaması", "Çalışan emeklilerimiz bu ödemenin kapsamı dışında tutulmuştu"),
        ("forecast", None, None, "Bakanın o gün bildirdiği beklenen kişi sayısı", "4 milyon 600 bin emeklimize ödeme yapacağız."),
    )),
    ("csgb-dec22", "22 Aralık 2023 ÇSGB ödeme hazırlığı açıklaması", "2023-12-22",
     "Çalışma ve Sosyal Güvenlik Bakanlığı", "Vedat Işıkhan",
     "https://www.csgb.gov.tr/tr/haberler/22-12-2023/",
     "b6b8c939172c9f21556be381ecd107194184a1755eb0fa148ac99b331bb58db3", (
        ("readiness", None, None, "Yayım sonrası ödeme hazırlığı", "ödemeleri iki gün içinde yapacak şekilde"),
    )),
    ("sgk2023", "Sosyal Güvenlik Kurumu 2023 faaliyet raporu", None, "Sosyal Güvenlik Kurumu", None,
     "https://www.sgk.gov.tr/Download/DownloadFile?d=65521b2e-039e-4819-abd1-77503ab4383e&f=f4d5530f-d587-4d5d-ace9-a45698148e6e.pdf",
     "9e45e0645f109058f891a48148b69cf0e7e96a59a6186f835e53080780f4514d", (
        ("initial-total", 70, "56", "İlk ödeme için rapordaki yaklaşık toplam", "yaklaşık 10,6 milyon kişiye 44,6 milyar TL"),
        ("additional-a", 70, "56", "Sonraki ödemede 4/1(a) ve 4/1(b) sayıları", "3.209.542 kişi, 4/1-(b) kapsamında 1.076.734 kişi"),
        ("additional-c", 70, "56", "Sonraki ödemede 4/1(c) sayısı", "4/1-(c) kapsamında 402.669 kişi"),
        ("additional-total", 70, "56", "Sonraki ödemede toplam kişi ve tutar", "yaklaşık 4,7 milyon kişiye 23,4 milyar TL"),
    )),
    ("sgk2024", "Sosyal Güvenlik Kurumu 2024 faaliyet raporu", None, "Sosyal Güvenlik Kurumu", None,
     "https://izmir.sgk.gov.tr/download/downloadfile?d=65521b2e-039e-4819-abd1-77503ab4383e&f=b1ae7c82-94ff-42fa-a4f5-452daf302c4a.pdf",
     "da614903d63cda3e24bcb5f05ddd9634b1e43f65fc544816a30b304464ffc23d", (
        ("month", 66, "66", "Hak sahiplerine ödemenin yapıldığı ay", "Aralık ayında emekli ve hak sahiplerine bir defaya mahsus olmak üzere ödenen"),
        ("transfer", 66, "66", "SGK’ya tutar aktarımının yapıldığı ay", "2024 yılı Ocak ayında Kuruma aktarılması"),
    )),
)
for label, title, day, publisher, author, url, digest, slices in sources:
    ext = ".pdf" if label.startswith("sgk") else ".html"
    path = stage / (label + ext)
    archive(stem + "-" + label, title, path, url, day, publisher, author,
            datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), digest, slices)

(checks / "pension-5000-source-records.json").write_text(
    json.dumps(dict(party_id="demokrat", entries=entries), ensure_ascii=False, indent=2) + "\n")
(stage / "pension-5000-source-paths").write_text("\n".join(map(str, sorted(paths))) + "\n")
print(len(entries), len(paths))
