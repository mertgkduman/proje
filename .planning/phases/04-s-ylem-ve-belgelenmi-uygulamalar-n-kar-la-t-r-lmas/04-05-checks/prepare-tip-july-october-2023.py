"""Build two 2023 TİP comparisons from the verified source readings."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
import uygulamalar as rules
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(__file__).resolve().parent
working = Path("data/practices")
source_dir = checks / "tip-publication-catalog" / "party-statements-07"
source_root = working / "sources" / "tip"
case = "0405-tip-july-october-2023"
party = "tip"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


pair = (working / "04-tip.json", working / "04-tip-review.json")
expected_base = (
    "16f63dee44edc978c22ff6b4a7b697409d1278fb15d62ebdc378e7f575143b81",
    "9f58ce7c51422863d8652ebb81fd0c4ac33285eb12138dc65fdbfc4160c4e607",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [28, 27, 0]


def insert(kind, row):
    entries.append({"kind": kind, "values": row})


def add(table, **row):
    records[table].append(row)


def vid(suffix):
    return f"{case}-{suffix}-v1"


def pid(suffix):
    return f"{case}-{suffix}-p"


def store(relative, content):
    destination = source_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == content, destination
    else:
        destination.write_bytes(content)


receipt = read(source_dir / "reading.json")
source_rows = {row["path"]: row for row in receipt["linked_material"]}
source_rows.update({row["path"]: row for row in read(source_dir / "capture.json")})
sources = {}
for key, name, day, title, kind, publisher, author, published, basis in (
    ("court-statement", "050.html.bin", "2023-08-25", "25 Ağustos TİP Atalay açıklaması", "party_publication",
     "Türkiye İşçi Partisi", None, "2023-08-25", "Tarih üst verisi ve özgün parti yayımındaki AYM çağrısı."),
    ("debt-statement", "053.html.bin", "2023-07-07", "7 Temmuz TİP vergi ve borçlanma açıklaması", "party_publication",
     "Türkiye İşçi Partisi", None, "2023-07-07", "Özgün yayımda borç kullanım tutarı, vergi ve harç ayrı konular."),
    ("proposal", "tbmm-1264-proposal.html.bin", "2023-07-05", "TBMM 2/1264 teklif sicili", "official",
     "TBMM", None, None, "Teklifin geliş günü, esas numarası ve borçlanma özeti."),
    ("floor", "tbmm-7456-floor.html.bin", "2023-07-14", "14 Temmuz TBMM 15. birleşim tutanağı", "official",
     "TBMM", None, None, "Başkanlığın 2/1264 kabul duyurusu."),
    ("registry", "tbmm-7456-registry.html.bin", "2023-07-14", "TBMM 7456 sicili", "official",
     "TBMM", None, None, "Kanun kimliği, 14 Temmuz kabul ve 15 Temmuz 32249 yayımı."),
    ("law", "tbmm-7456-law.html.bin", "2023-07-14", "7456 sayılı kanun metni", "official",
     "TBMM", None, None, "11. madde, 4749’un geçici 38. maddesi ve 2023 borç kullanım kuralı."),
):
    row = source_rows[name]
    path = source_dir / name
    raw = path.read_bytes()
    assert sha(raw) == row["sha256"]
    media = "pdf" if path.suffix == ".pdf" else "html"
    folder = Path("objects") / row["sha256"]
    original = folder / ("original.pdf" if media == "pdf" else "original.html.bin")
    readable = folder / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, media))
    url = row["final_url"]
    document = f"{case}-{key}"
    source_kind = "party" if kind == "party_publication" else kind
    insert("document", dict(id=document, party_id=party, title=title, source_kind=source_kind))
    insert("document_version", dict(id=vid(key), document_id=document, original_url=row["url"], final_url=url,
        document_date=day, date_precision="day", date_unknown_reason=None, version_label=title,
        accessed_at=row["retrieved_at_utc"], verified_at=now, mime="application/pdf" if media == "pdf" else "text/html",
        sha256=row["sha256"], original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=vid(key), kind=kind, publisher=publisher, author=author,
        social_handle=None, published_at=published, date_precision="day" if published else "unknown", public_url=url, basis=basis))
    if media == "html":
        view = build_view(raw, url, source_root, fetch_assets=False)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=vid(key)))
    sources[key] = (path, url)

aym = "0405-tip-atalay-2023-aym-first-v1"
old_version = next(entry["values"] for entry in entries if entry["kind"] == "document_version" and entry["values"]["id"] == aym)
old_path = source_root / old_version["original_path"]
assert sha(old_path.read_bytes()) == old_version["sha256"]
sources["aym-first"] = (old_path, old_version["final_url"])
source_versions = {key: vid(key) for key in sources}
source_versions["aym-first"] = aym

passages = {}
for key, source, page, printed, exact, label in (
    ("court-call", "court-statement", None, None, "yapılan başvurunun derhal gündeme alınarak Anayasal ihlalin sonlandırılması ve tahliyesinin sağlanmasıdır.", "TİP’in 25 Ağustos çağrısı"),
    ("court-date", "aym-first", 801, None, "Karar Tarihi: 25/10/2023", "AYM 2023/53898 karar günü"),
    ("court-number", "aym-first", 801, None, "(Başvuru Numarası: 2023/53898)", "AYM bireysel başvuru kimliği"),
    ("court-ministry", "aym-first", 803, "1555", "Bakanlık, görüşünü bildirmiştir.", "AYM kararında Adalet Bakanlığı görüşü"),
    ("court-rights", "aym-first", 849, "1601", "siyasi faaliyette bulunma hakkının İHLAL EDİLDİĞİNE", "Hüküm B, seçilme ve siyasi faaliyette bulunma hakkı"),
    ("court-liberty", "aym-first", 849, "1601", "ve güvenliği hakkının İHLAL EDİLDİĞİNE", "Hüküm B, kişi hürriyeti ve güvenliği"),
    ("court-order", "aym-first", 850, "1602", "hükmünün infazının durdurulması, ceza infaz kurumundan tahliyesinin", "AYM hükmü D’de tahliye ve diğer işlemler"),
    ("court-referral", "aym-first", 850, "1602", "Mahkemesine (E.2021/178) GÖNDERİLMESİNE,", "İlk dereceye gönderme hükmü"),
    ("debt-call", "debt-statement", None, None, "maddenin iptali olmak üzere", "TİP’in 7 Temmuz çağrısı"),
    ("debt-criticism", "debt-statement", None, None, "borç kullanım tutarının üç kat arttırılması", "7 Temmuz parti metninde karşı çıkılan hüküm"),
    ("debt-file", "proposal", None, None, "2 / 1264", "TBMM teklif esas numarası"),
    ("debt-file-day", "proposal", None, None, "05/07/2023", "TBMM teklif geliş günü"),
    ("debt-vote", "floor", None, None, "Teklif kabul edilmiş ve kanunlaşmıştır.", "15. birleşimde Başkanlığın kabul duyurusu"),
    ("debt-adoption", "registry", None, None, "14/07/2023", "Kanun sicilinde kabul günü"),
    ("debt-publication", "registry", None, None, "15/07/2023", "Kanun sicilinde yayım günü"),
    ("debt-issue", "registry", None, None, "32249", "Kanun sicilinde Resmî Gazete sayısı"),
    ("debt-text", "law", None, None, "borç kullanım tutarının üç katı olarak uygulanır.", "7456 madde 11 ve 4749 geçici 38 metni"),
):
    path = sources[source][0]
    original = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in original, (key, exact)
    passage = dict(id=pid(key), version_id=source_versions[source], exact=exact, prefix=None, suffix=None, article=None,
        section=label, pdf_page_index=page, printed_page=printed)
    insert("passage", passage)
    passages[key] = passage

scopes = {}
topics = {"yargi-bagimsizligi", "makroekonomik-politika"}
for row in read(working / "04-inventory.json")["cells"]:
    topic = row["topic_id"]
    if row["party_id"] != party or topic not in topics:
        continue
    scope = row["cell_id"]
    scopes[topic,row["research_kind"]] = scope
    if not any(existing["id"] == scope for existing in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope, **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="2023 Atalay çağrısı veya 2023 net borç kullanımı kuralı ilgili kaynaklardan okundu.")
assert len(scopes) == 4
for key, (_, url) in sources.items():
    topic = "yargi-bagimsizligi" if key in {"court-statement", "aym-first"} else "makroekonomik-politika"
    lane = "statement" if key.endswith("-statement") else "event"
    scope = scopes[topic,lane]
    version = source_versions[key]
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    if not any(row["scope_id"] == scope and row["version_id"] == version for row in records["practice_scope_source"]):
        add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now, inspected_sections=json.dumps(sections, ensure_ascii=False))
    attempt = f"{case}-{key}-reading"
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="Tarih, konu, işlem ve hüküm ilgili kaynak pasajlarından okundu.", source_version_id=version)
    if not any(row["scope_id"] == scope and row["url"] == url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
            relevance_reason="AYM 2023/53898 veya 7456 borç kullanım hükmünü izleyen kaynak.", state="examined", attempt_ids=json.dumps([attempt]))

limitations = ("AYM hükmü fiilî tahliyeden, kanuni borç sınırı fiilî borç kullanımından ayrı. "
               "Yargı ve yasama işlemlerinde parti açıklamasının nedensel etkisi açık.")


def finding(suffix, content, refs, *, quote=False, pair=None):
    ident = f"{case}-{suffix}"
    insert("finding", dict(id=ident, party_id=party, heading="Belgelenmiş uygulamalar", pair_id=pair or ident,
        text=content, provenance="quote" if quote else "summary", epistemic_type="claim"))
    insert("review", dict(id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        result="reviewed", reason="İddianın dayandığı tarihli özgün pasajlar okundu."))
    for ref in refs:
        insert("finding_evidence", dict(finding_id=ident, passage_id=pid(ref), role="quotation" if quote else "support"))
        insert("verification", dict(finding_id=ident, passage_id=pid(ref), checked_at=now, result="confirmed", reason=passages[ref]["section"]))
    return ident


event_claims = {}

def add_case(key, topic, comparison_row, source_day, occurrence_day, title, common_key, context, occurrence_basis,
             summary, outcome, comparison, authority, timeline, points, extra_refs=()):
    call = f"{key}-call"
    summary_id = finding(f"{key}-summary", summary, (call,))
    quote = finding(f"{key}-quote", passages[call]["exact"], (call,), quote=True, pair=summary_id)
    statement = f"{case}-{key}-statement"
    add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
        summary_finding_id=summary_id, quote_finding_id=quote, statement_at=source_day, date_precision="day",
        version_id=vid(f"{key}-statement"), period_basis="TİP’in tarihli özgün parti yayımı.",
        comparison_row_id=comparison_row, uncertainty_reason=limitations)
    event = f"{case}-{key}-event"
    add("practice_event", id=event, common_event_key=common_key, event_at=occurrence_day, date_precision="day",
        date_unknown_reason=None, title=title, scope_context=context, occurrence_basis=occurrence_basis)
    for ref, stage, point, basis in points:
        add("practice_event_evidence", event_id=event, passage_id=pid(ref), stage=stage, supported_point=point,
            concrete_basis=passages[ref]["section"], limitation=limitations, epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=pid(ref), stage=stage, basis_kind=basis)
        event_claims[pid(ref)] = point
    refs = tuple(point[0] for point in points)
    result = finding(f"{key}-result", outcome, refs)
    explanation = finding(f"{key}-comparison", comparison, (call, *refs, *extra_refs))
    relation = f"{case}-{key}-relation"
    add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes[topic,"event"], statement_id=statement,
        event_id=event, target_finding_id=summary_id, result_finding_id=result, explanation_finding_id=explanation,
        comparability_reason=context, temporal_context=timeline, authority_context=authority, uncertainty_reason=limitations)
    add("practice_candidate", id=f"{case}-{key}-candidate", scope_id=scopes[topic,"event"], event_id=event, relation_id=relation,
        state="eligible", reason=context, passage_ids=json.dumps([pid(ref) for ref in refs]))


add_case(
    "court", "yargi-bagimsizligi", "04-03-v3-0304-tip-program-adalet-row", "2023-08-25", "2023-10-25",
    "AYM’nin 25 Ekim 2023 Can Atalay kararı", "aym-bb-2023-53898-can-atalay",
    "25 Ağustos parti açıklamasındaki Atalay bireysel başvurusu ve AYM’nin 2023/53898 kararı.",
    "AYM Kararlar Dergisinde başvuru kimliği, karar günü ve hüküm bölümü.",
    "TİP 25 Ağustos’ta AYM’den Atalay’ın başvurusunu gündeme almasını, ihlalin giderilmesini ve tahliyeyi istedi.",
    "AYM 25 Ekim’de iki hak ihlali saptadı. Tahliyenin sağlanması ve diğer işlemler için karar örneğinin İstanbul 13. Ağır Ceza Mahkemesine gönderilmesine hükmetti.",
    "AYM kaydı Adalet Bakanlığının görüş bildirdiğini gösteriyor. TİP’in 25 Ağustos çağrısından sonra AYM, 25 Ekim’de iki hak ihlali saptadı ve tahliyenin sağlanması için karar örneğinin ilk derece mahkemesine gönderilmesine hükmetti. Fiilî tahliye ayrı. 8 Kasım Yargıtay ve 21 Aralık AYM kararları ayrı olaylar.",
    "TİP çağrı yayımladı, AYM hüküm verdi. Kararda yapılması gereken işlemler ilk derece mahkemesine iletilmek üzere belirlendi.",
    "25 Ağustos 2023 TİP çağrısı. 25 Ekim 2023 AYM kararı.",
    (("court-date", "action", "2023/53898 karar günü 25 Ekim 2023.", "document"),
     ("court-number", "action", "AYM kararına konu başvuru 2023/53898.", "document"),
     ("court-rights", "result", "AYM seçilme ve siyasi faaliyette bulunma hakkının ihlal edildiğine karar verdi.", "document"),
     ("court-liberty", "result", "AYM kişi hürriyeti ve güvenliği hakkının ihlal edildiğine karar verdi.", "document"),
     ("court-order", "result", "AYM infazın durdurulması ve tahliyenin sağlanmasına ilişkin işlemleri hükümde gösterdi.", "document"),
     ("court-referral", "result", "Karar örneğinin ilk derece mahkemesine gönderilmesine hükmedildi.", "document")),
    ("court-ministry",),
)
add_case(
    "debt", "makroekonomik-politika", "04-03-v3-0304-tip-program-makro-row", "2023-07-07", "2023-07-14",
    "7456 sayılı kanunun kabulü ve 2023 net borç kullanımı hükmü", "tbmm-28-1-15-2-1264-law-7456",
    "TİP’in 7 Temmuz açıklamasındaki 2023 net borç kullanım kuralı, 2/1264 teklifi ve 7456’nın 11. maddesi.",
    "TBMM teklif sicili, 15. birleşim tutanağı, kanun sicili ve TBMM kanun metni.",
    "TİP, 7 Temmuz’da torba teklifte net borç kullanım tutarının üç katına çıkarılmasına karşı çıktı.",
    "TBMM 2/1264’ü 14 Temmuz’da kabul etti. 7456’nın 11. maddesindeki üç kat hükmü 15 Temmuz’da yayımlandı.",
    "7 Temmuz parti açıklamasında eleştirilen üç kat kuralı, 14 Temmuz’da kabul edilen metinde yer aldı. Madde 11, 2023 net borç kullanım tutarının 1 Ocak’tan geçerli olmak üzere artırılmış sınırın üç katı olarak uygulanmasını düzenledi. Fiilî borç tutarı ve kişisel oy kaydı açık. KDV ve telefon harcı ayrı dosyalar.",
    "TİP görüş yayımladı. Genel Kurul kanunu kabul etti. Kuralın fiilî kullanımına ilişkin tutar bu belgelerde yer almıyor.",
    "5 Temmuz teklif gelişi, 7 Temmuz TİP açıklaması, 14 Temmuz kabul, 15 Temmuz 32249 sayılı yayım.",
    (("debt-file", "initiative", "Teklif esas numarası 2/1264.", "document"),
     ("debt-file-day", "initiative", "Teklifin Başkanlığa geliş günü 5 Temmuz 2023.", "document"),
     ("debt-vote", "result", "Başkanlık teklifin kabul edilip kanunlaştığını duyurdu.", "document"),
     ("debt-adoption", "result", "TBMM sicili 14 Temmuz 2023 kabulünü gösteriyor.", "document"),
     ("debt-publication", "result", "Sicilde 15 Temmuz 2023 yayımı var.", "document"),
     ("debt-issue", "result", "Resmî Gazete sayısı 32249.", "document"),
     ("debt-text", "result", "7456/11 üç kat net borç kullanım kuralını düzenliyor.", "document")),
    ("debt-criticism",),
)

snapshot = read(Path("data/releases") / package["base_release"] / "records.json")
for entry in entries:
    rows = snapshot.setdefault(entry["kind"], [])
    if entry["values"] not in rows:
        rows.append(entry["values"])
snapshot["practice_contract"] = records["practice_contract"]
for table, rows in records.items():
    target = snapshot.setdefault(table, [])
    target.extend(row for row in rows if row not in target)
rules.validate_practices(snapshot)
targets = rules.practice_review_package_targets(snapshot, records,
    {row["values"]["id"] for row in entries if row["kind"]=="passage"}, party_id=party)
by_id = {row["id"]: row for row in snapshot["passage"]}
claims = {pid(ref): row["section"] for ref, row in passages.items()}
claims.update(event_claims)
reviews = review["practice_source_review"]
existing = {(row["subject_kind"], row["subject_id"]) for row in reviews}
assert existing <= targets.keys()
for kind, ident in sorted(targets.keys() - existing):
    refs, _ = targets[kind, ident]
    inspected = [by_id[ref] for ref in sorted(refs)]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        source_version_ids=json.dumps(sorted({row["version_id"] for row in inspected})),
        passage_ids=json.dumps([row["id"] for row in inspected]),
        inspected_sections=json.dumps(sorted({row["section"] for row in inspected}), ensure_ascii=False),
        supported_claim=" ".join(claims[ref] for ref in sorted(refs)), limitations=limitations,
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün parti metni, mahkeme kararı veya Meclis kaydı okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-july-october-2023-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_JULY_OCTOBER_2023_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
