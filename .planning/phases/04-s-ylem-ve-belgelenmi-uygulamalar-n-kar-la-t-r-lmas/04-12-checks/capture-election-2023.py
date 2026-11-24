"""Preserve the March agreement and the YSK candidacy and runoff records."""

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
        optical = document == "0412-election-2023-definitive" and index in (1, 2)
        if optical:
            assert not text.strip()
        else:
            assert exact in text, (document, section, exact)
        passage_id = document + "-" + key
        add("passage", id=passage_id, version_id=version, exact=exact, prefix=None, suffix=None,
            article=None, section=section, pdf_page_index=index, printed_page=printed)
        if optical:
            add("manual_passage", passage_id=passage_id, checked_at=now,
                method="YSK nüshasının özgün tarama sayfası Poppler görüntüsünde okundu.",
                reason="Sayfanın metin katmanı boş ve pasaj sayfa görüntüsünde doğrulandı.")


stem = "0412-election-2023"
party_news = next(row for row in json.loads((checks / "party-news-011-reading.json").read_bytes())["examined"]
                  if row["position"] == 111)
archive(stem + "-agreement", "6 Mart 2023 Millet İttifakı ortak aday ve geçiş yol haritası",
        checks / party_news["original_path"], party_news["url"], party_news["displayed_day"],
        "Demokrat Parti", "Millet İttifakı genel başkanları", party_news["accessed_at"], party_news["sha256"], (
            ("candidate", None, None, "6 Mart yol haritasının son paragrafındaki ortak aday",
             "ortak Cumhurbaşkanı adayımız Sayın Kemal"),
            ("transition", None, None, "Yol haritasında anayasa değişikliği için TBMM yapısı",
             "TBMM yapısının m&uuml;mk&uuml;n kıldığı"),
        ))
conditions = next(row for row in json.loads((checks / "party-news-012-reading.json").read_bytes())["examined"]
                  if row["position"] == 118)
archive(stem + "-conditions", "5 Ocak 2023 ortak açıklamasında geçiş koşulları",
        checks / conditions["original_path"], conditions["url"], conditions["displayed_day"],
        "Demokrat Parti", "Altı siyasi partinin genel başkanları", conditions["accessed_at"],
        conditions["sha256"], (
            ("criteria", None, None, "Ortak aday seçimi ve TBMM çoğunluğu için iki gerekli koşul",
             "iki gerekli şarta bağlı olduğunun"),
        ))
sources = (
    ("application", "ysk254.pdf", "24 Mart 2023 YSK adaylık başvuruları kararı 2023/254", "2023-03-24",
     "https://www.ysk.gov.tr/doc/karar/dosya/82595/2023-254.pdf",
     "de493ef1f0223a125db3b10f8f757e1cf50434028f745a547dfc177b366d4e66", (
        ("id", 3, None, "Karar kimliği", "Karar No: 2023/254"),
        ("sponsors", 3, None, "Kemal Kılıçdaroğlu için başvuran iki TBMM grubu",
         "Cumhuriyet Halk Partisi Grubu ve İyi Parti Grubu"),
        ("decision", 3, None, "Kılıçdaroğlu ve Erdoğan başvurularının kabulü",
         "KILIÇDAROĞLU ve Recep Tayyip ERDOĞAN'ın başvurularının kabulüne,"),
        ("day", 3, None, "Kararın oybirliğiyle verildiği gün",
         "24.03.2023 tarihinde oy birliği ile karar verildi"),
    )),
    ("definitive", "ysk321-alternate.pdf", "30 Mart 2023 YSK kararı ve 31 Mart kesin aday listesi",
     "2023-03-31", "https://www.ysk.gov.tr/doc/karar/dosya/82605/2023-321.pdf",
     "58f6d18963fd6c3802bfd4c2aad3912fd6e61633ba840b2df99929b9b8db8e5e", (
        ("publication", 0, None, "31 Mart Resmî Gazete tarihi ve 32149 sayısı", "31 Mart 2023 CUMA"),
        ("decision", 1, None, "30 Mart 2023 karar günü", "30.03.2023 tarihinde oy birliği ile karar verildi"),
        ("list", 2, None, "Kesin aday listesinde soyadı sütunu", "KILIÇDAROĞLU"),
    )),
    ("runoff", "ysk-bulletin-28.pdf", "28 Mayıs 2023 ikinci oylama YSK ülke geneli sonuçları", None,
     "https://www.ysk.gov.tr/doc/dosyalar/docs/28%20May%C4%B1s%202023%20Cumhurba%C5%9Fkan%C4%B1%20Se%C3%A7imi%202.%20Oylama%20B%C3%BClteni.pdf",
     "e49fc4bfd0b6fcd70a49cddc018c38c57cef6781a27966880f6b42a7bddf09f4", (
        ("scope", 23, "20", "İkinci oylama toplam sonuç tablosunun sandık kapsamı",
         "Yurt İçi, Yurt Dışı ve Gümrük Kapıları Sandıkları Dahil Seçim Sonucu"),
        ("total", 23, "20", "İkinci oylama ülke geneli geçerli oy toplamı", "53.339.313"),
        ("votes", 23, "20", "İki aday için ülke geneli oylar ve oranlar", "27.834.589\n52,18\n25.504.724\n47,82"),
    )),
)
for label, filename, title, day, url, digest, anchors in sources:
    path = stage / filename
    archive(stem + "-" + label, title, path, url, day, "Yüksek Seçim Kurulu", None,
            datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(), digest, anchors)

(checks / "election-2023-source-records.json").write_text(
    json.dumps(dict(party_id="demokrat", entries=entries), ensure_ascii=False, indent=2) + "\n")
(stage / "election-2023-source-paths").write_text("\n".join(map(str, sorted(paths))) + "\n")
print(len(entries), len(paths))
