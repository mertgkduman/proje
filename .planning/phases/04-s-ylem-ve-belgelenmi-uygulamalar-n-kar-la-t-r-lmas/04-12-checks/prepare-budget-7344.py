"""Build the 1/283 filing and 7344 comparison from reviewed source bytes."""

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
source_dir = checks / "budget-7344-sources"
source_root = working / "sources" / "demokrat"
case = "0412-budget-7344"
party = "demokrat"
topic = "maliye-vergi"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(content):
    return hashlib.sha256(content).hexdigest()

if preflight:
    pair = (checks / "budget-7414-draft.json", checks / "budget-7414-review-draft.json")
else:
    pair = (working / "04-demokrat.json", working / "04-demokrat-review.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "880c9b403dea3ead7d8fdecf7a9f1eec29404ad01356cb117f9e3c8601dccef9",
    "0664f803762554f9975b5786fe29fd8f85b85776495782881cf4cd1fca156718",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [60, 47, 0]
receipt = read(source_dir / "reading.json")
source_rows = {row["original_path"]: row for row in receipt["sources"]}
party_row = next(row for row in read(checks / "party-news-025-reading.json")["examined"] if row["position"] == 183)

def insert(kind, row):
    entries.append({"kind": kind, "values": row})

def add(table, **row):
    records[table].append(row)

def vid(suffix):
    return f"{case}-{suffix}-v1"

def pid(suffix):
    return f"{case}-{suffix}-p"

def copy_verified(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content, path
    else:
        path.write_bytes(content)

sources = {}
for suffix, name, date, label in (
    ("filing", "tbmm-1-283-sicil.html.bin", "2021-10-15", "TBMM 1/283 teklif sicili"),
    ("submission", "tbmm-1-283-imzali.pdf", "2021-10-15", "1/283 imzalı sunuş"),
    ("speech", "tbmm-35-tutanak.pdf", "2021-12-13", "13 Aralık 2021 tarihli 35. birleşim"),
    ("floor", "tbmm-39-tutanak.pdf", "2021-12-17", "17 Aralık 2021 tarihli 39. birleşim"),
    ("roll", "tbmm-39-basilmis.pdf", "2021-12-17", "39. birleşim basılı kesin oy cetveli"),
    ("law", "tbmm-7344-kabul.html.bin", "2021-12-17", "7344 sayılı kanun kabul metni"),
    ("registry", "tbmm-7344-sicil.html.bin", "2021-12-31", "TBMM 7344 kanun sicili"),
    ("party", party_row["original_path"], party_row["displayed_day"], "Demokrat Parti 13 Aralık konuşması yayımı"),
):
    is_party = suffix == "party"
    raw_path = (checks if is_party else source_dir) / name
    source = party_row if is_party else source_rows[name]
    raw = raw_path.read_bytes()
    assert sha(raw) == source["sha256"], raw_path
    kind = "pdf" if name.endswith(".pdf") else "html"
    object_dir = Path("objects") / source["sha256"]
    original = object_dir / ("original.pdf" if kind == "pdf" else "original.html.bin")
    readable = object_dir / "readable.html"
    copy_verified(source_root / original, raw)
    copy_verified(source_root / readable, readable_bytes(raw, kind))
    doc_id = f"{case}-{suffix}"
    version = vid(suffix)
    insert("document", dict(id=doc_id, party_id=party, title=label, source_kind="party" if is_party else "official"))
    insert("document_version", dict(id=version, document_id=doc_id, original_url=source["url"], final_url=source["url"],
        document_date=date, date_precision="day", date_unknown_reason=None, version_label=label,
        accessed_at=source.get("retrieved_at_utc") or source["accessed_at"], verified_at=now,
        mime="application/pdf" if kind=="pdf" else "text/html", sha256=source["sha256"],
        original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=version, kind="party_publication" if is_party else "official",
        publisher=source["publisher"], author="Gültekin Uysal" if is_party else None, social_handle=None,
        published_at=date, date_precision="day", public_url=source["url"], basis=source["reading"]))
    if kind == "html":
        charset = source.get("passive_view", {}).get("http_charset")
        view = build_view(raw, source["url"], source_root, fetch_assets=False, http_charset=charset)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=version))
    sources[suffix] = (raw_path, source["url"])

passages = {}
for suffix, source, page, printed, exact, section in (
    ("filing-day", "filing", None, None, "15/10/2021", "1/283 sicili Başkanlığa geliş"),
    ("filing-nr", "filing", None, None, "1 / 283", "TBMM teklif esas numarası"),
    ("submission", "submission", 0, None, "Tarih: 15 Ekim 2021 Esas No: 1/283", "İmzalı sunuş yazısı ve Başkanlık kaşesi"),
    ("speech-docket", "speech", 0, None, "2022 Yılı Merkezi Yönetim Bütçe Kanunu Teklifi (1/283)", "35. birleşim gündeminde 1/283"),
    ("chair-speech", "speech", 94, None, "Şimdi aleyhinde söz isteyen Afyonkarahisar Milletvekili Sayın Gültekin Uysal.", "35. birleşimde Uysal’a aleyhte söz"),
    ("forecast", "speech", 94, None, "öngörülerinin çökmesi sonrası âdeta bir usulü tamamlama işlemine dönüşmesidir.", "Uysal’ın 2022 bütçe tahminleri eleştirisi"),
    ("party-speech", "party", None, None, "DP Basın Merkezi -13 Aralık 2021", "Parti yayımında konuşmanın tarihi"),
    ("floor-docket", "floor", 0, None, "2022 Yılı Merkezi Yönetim Bütçe Kanunu Teklifi (1/283)", "39. birleşim gündeminde 1/283"),
    ("chair-votes", "floor", 54, None, "Kullanılan oy sayısı\n:\n524\nKabul\n:\n327\nRet\n:\n197 (x)", "Kürsünün okuduğu ilk sonuç"),
    ("chair-decision", "floor", 54, None, "2022 Yılı Merkezi Yönetim Bütçe Kanunu Teklifi kabul edilmiş ve kanunlaşmıştır", "1/283 Genel Kurul kabulü"),
    ("roll-uysal", "roll", 121, "372", "372\nB: 39\n17 . 12 . 2021", "Kesin cetvel, saat 22.50, oy dağılımı ve Afyonkarahisar Uysal satırı"),
    ("roll-enginyurt", "roll", 131, "382", "382\nB: 39\n17 . 12 . 2021", "Kesin cetvelde Ordu Enginyurt satırı"),
    ("law-amount", "law", None, None, "1.728.401.621.000", "7344 madde 1, genel bütçe başlangıç ödeneği"),
    ("effective", "law", None, None, "Bu Kanun 1/1/2022 tarihinde yürürlüğe girer.", "7344 madde 15, yürürlük"),
    ("publication", "registry", None, None, "31706 (1. M&#xFC;k.)", "TBMM kanun sicilinde 31 Aralık 2021 yayımı"),
):
    raw = sources[source][0]
    body = html_source_text(raw.read_bytes()) if page is None else pdf_page_text(raw, page)
    assert (not body if suffix == "submission" else exact in body), (suffix, exact)
    row = dict(id=pid(suffix), version_id=vid(source), exact=exact, prefix=None, suffix=None,
               article=None, section=section, pdf_page_index=page, printed_page=printed)
    insert("passage", row)
    passages[suffix] = row
    if suffix == "submission":
        insert("manual_passage", dict(passage_id=pid(suffix),
            checked_at=now, method="Özgün sunuş PDF’sinin ilk sayfası Poppler ile görüntülendi ve Başkanlık kaşesi görsel okundu.",
            reason="İlk sayfanın metin katmanı boş. TBMM teklif sicili aynı tarih ve numarayı veriyor."))

scopes = {row["research_kind"]: row["id"] for row in records["practice_scope_v2"] if row["topic_id"] == topic}
for key, (_, url) in sources.items():
    for lane in (("statement",) if key in {"speech", "party"} else ("event",)):
        scope = scopes[lane]
        version = vid(key)
        reviewed_sections = sorted(row["section"] for row in passages.values() if row["version_id"] == version)
        attempt = f"{version}-{lane}-reading"
        add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
            inspected_sections=json.dumps(reviewed_sections, ensure_ascii=False))
        add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url,
            result="examined", reason="1/283 ve 7344 için özgün kaydın ilgili pasajları okundu.", source_version_id=version)
        if not any(row["scope_id"]==scope and row["url"]==url for row in records["practice_lead"]):
            add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
                relevance_reason="1/283 ana bütçe için söylem, başvuru, kabul veya yayım kaydı.",
                state="examined", attempt_ids=json.dumps([attempt]))

bounds = ("13 Aralık konuşması kurum bütçesi ve kesin hesap başlıklarından sonra yapıldı. "
          "Teklifin geneli üzerine söz verilmediği Uysal’ın beyanı. "
          "Başlangıç ödeneği, yıl sonu gideri ve Haziran 2022 ek bütçe oylaması ayrı.")

def finding(suffix, content, refs, heading="Belgelenmiş uygulamalar", provenance="summary"):
    ident = f"{case}-{suffix}"
    insert("finding", dict(id=ident, party_id=party, heading=heading, pair_id=f"{case}-speech" if heading=="Maliye ve vergi" else ident,
        text=content, provenance=provenance, epistemic_type="claim"))
    insert("review", dict(id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent",
        reviewed_at=now, result="reviewed", reason="İlgili konuşma veya bütçe işlem kaynağı özgün kayıttan okundu."))
    for ref in refs:
        insert("finding_evidence", dict(finding_id=ident, passage_id=pid(ref), role="support"))
        insert("verification", dict(finding_id=ident, passage_id=pid(ref), checked_at=now, result="confirmed",
            reason=passages[ref]["section"]))
    return ident

statement = f"{case}-statement"
summary = finding("statement-summary", "Gültekin Uysal 13 Aralık 2021’de Mecliste 2022 bütçesinin faiz, döviz ve enflasyon tahminlerini eleştirdi.",
    ("forecast", "speech-docket", "chair-speech", "party-speech"), "Maliye ve vergi")
quote = finding("statement-quote", passages["forecast"]["exact"], ("forecast",), "Maliye ve vergi", "quote")
template = next(row for row in records["practice_statement"] if row["id"] == "0412-tax-deferral-2026-statement")
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2021-12-13", date_precision="day",
    version_id=vid("speech"), period_basis="13 Aralık 2021 tarihli 35. birleşimin TBMM tutanağı ve parti yayımı.",
    comparison_row_id=template["comparison_row_id"], uncertainty_reason=bounds)

details = {
    "filing-day": ("action", "TBMM sicilinde 1/283 Başkanlığa geliş 15 Ekim 2021."),
    "filing-nr": ("action", "Teklifin esas numarası 1/283."),
    "submission": ("action", "İmzalı Cumhurbaşkanlığı sunuşu 15 Ekim. TBMM kaşesinde 1/283 ve Plan ve Bütçe Komisyonu."),
    "floor-docket": ("action", "39. birleşim gündeminde 1/283 ana bütçesi ve sıra sayısı 281."),
    "chair-votes": ("action", "Başkan 524 kullanılan, 327 kabul ve 197 ret okudu. Kesin tablo ayrıca eklendi."),
    "chair-decision": ("result", "39. birleşimde 1/283 bütçe teklifi kabul edildi."),
    "roll-uysal": ("result", "Kesin cetvel saat 22.50, 320 kabul, 195 ret, 9 mükerrer ve 524 toplam gösteriyor. Gültekin Uysal (DP) Ret."),
    "roll-enginyurt": ("result", "Kesin cetvel S.S. 281 sütununda Cemal Enginyurt (DP) Ret."),
    "law-amount": ("result", "7344 madde 1 genel bütçe kapsamındaki idareler için 1.728.401.621.000 TL başlangıç ödeneği kaydediyor."),
    "effective": ("result", "7344 madde 15 uyarınca kanun 1 Ocak 2022’de yürürlüğe girdi."),
    "publication": ("result", "TBMM sicilinde 31 Aralık 2021, 31706 birinci mükerrer Resmî Gazete yayımı."),
}
relation = f"{case}-adoption-relation"
for key, common, day, title, refs in (
    ("filing", "tbmm-27-5-1-283-budget-filing", "2021-10-15", "1/283 ana bütçe teklifinin Başkanlığa sunulması",
     ("filing-day","filing-nr","submission")),
    ("adoption", "tbmm-27-5-39-1-283-law-7344", "2021-12-17", "1/283 ana bütçe teklifinin 7344 sayılı kanun olarak kabulü",
     ("floor-docket","chair-votes","chair-decision","roll-uysal","roll-enginyurt","law-amount","effective","publication")),
):
    ident = f"{case}-{key}-event"
    add("practice_event", id=ident, common_event_key=common, event_at=day, date_precision="day",
        date_unknown_reason=None, title=title, scope_context="2022 yılı merkezi yönetim ana bütçesi", occurrence_basis=details[refs[0]][1])
    for ref in refs:
        stage, point = details[ref]
        add("practice_event_evidence", event_id=ident, passage_id=pid(ref), stage=stage,
            supported_point=point, concrete_basis=passages[ref]["section"], limitation=bounds, epistemic_type="claim")
        add("practice_evidence_assessment", event_id=ident, passage_id=pid(ref), stage=stage, basis_kind="document")
    matched = key == "adoption"
    add("practice_candidate", id=f"{case}-{key}-candidate", scope_id=scopes["event"], event_id=ident,
        relation_id=relation if matched else None, state="eligible" if matched else "unmatched",
        reason="Konuşma ve kabul aynı 1/283 dosyasıyla ilgili." if matched else "Sunuş, 13 Aralık konuşmasından önce gerçekleşti.",
        passage_ids=json.dumps([pid(ref) for ref in refs]))

result = finding("adoption-result",
    "17 Aralık 2021’de 1/283 bütçe teklifi 7344 sayılı kanun olarak kabul edildi. Kesin cetvelde Gültekin Uysal ve Cemal Enginyurt ret olarak kayıtlı. Kanun 31 Aralık’ta yayımlandı ve 1 Ocak 2022’de yürürlüğe girdi.",
    ("chair-decision", "roll-uysal", "roll-enginyurt", "publication", "effective"))
comparison = finding("adoption-comparison",
    "Uysal’ın 13 Aralık bütçe tahminleri eleştirisinin ardından aynı 1/283 dosyası 17 Aralık’ta kabul edildi. Kürsü sayımı 327 kabul ve 197 ret. Kesin cetvel 320 kabul, 195 ret ve dokuz mükerrer gösteriyor.",
    ("forecast", "chair-votes", "chair-decision", "roll-uysal"))
add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes["event"],
    statement_id=statement, event_id=f"{case}-adoption-event", target_finding_id=summary,
    result_finding_id=result, explanation_finding_id=comparison,
    comparability_reason="TBMM tutanağı 13 Aralık konuşmasını ve 17 Aralık kabulünü 1/283 ve 281 sıra sayısıyla ilişkilendiriyor.",
    temporal_context="15 Ekim 2021 sunuş, 13 Aralık konuşma, 17 Aralık kabul, 31 Aralık yayım, 1 Ocak 2022 yürürlük.",
    authority_context="Cumhurbaşkanı teklifi sundu, TBMM Genel Kurulu kabul etti. Kesin oy cetvelinde iki DP milletvekili ayrı satırlarda.",
    uncertainty_reason=bounds)

snapshot = read(Path("data/releases") / package["base_release"] / "records.json")
for entry in entries:
    rows = snapshot.setdefault(entry["kind"], [])
    if entry["values"] not in rows:
        rows.append(entry["values"])
for table, rows in records.items():
    target = snapshot.setdefault(table, [])
    target.extend(row for row in rows if row not in target)
rules.validate_practices(snapshot)
targets = rules.practice_review_package_targets(snapshot, records,
    {row["values"]["id"] for row in entries if row["kind"]=="passage"}, party_id=party)
by_id = {row["id"]: row for row in snapshot["passage"]}
claims = {pid(ref): row["section"] for ref, row in passages.items()}
claims.update({pid(ref): point for ref, (_, point) in details.items()})
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
        supported_claim=" ".join(claims[ref] for ref in sorted(refs)), limitations=bounds,
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için ilgili 1/283 veya 7344 pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"budget-7344-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("DEMOCRAT_BUDGET_7344_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
