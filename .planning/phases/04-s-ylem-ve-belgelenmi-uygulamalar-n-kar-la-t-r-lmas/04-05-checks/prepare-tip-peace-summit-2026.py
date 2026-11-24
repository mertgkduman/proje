"""Record the announced and held 2026 Istanbul peace summit."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
import uygulamalar as rules
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(__file__).resolve().parent
working = Path("data/practices")
source_dir = checks / "ankara-nato-2026-sources"
source_root = working / "sources" / "tip"
case = "0405-tip-peace-summit-2026"
party = "tip"
topic = "nato-iliskileri"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(content):
    return hashlib.sha256(content).hexdigest()

pair = (working / "04-tip.json", working / "04-tip-review.json")
if preflight and sha(pair[0].read_bytes()) != "16509cb6e3ab23425df31f1073f4bc71a90fc8e53a3e52f0822a2e72780e005f":
    pair = (checks / "tip-x-20261014-draft.json", checks / "tip-x-20261014-review-draft.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "16509cb6e3ab23425df31f1073f4bc71a90fc8e53a3e52f0822a2e72780e005f",
    "02a982182ac260806d380c89670e239a73e26102b58d89e20d515da0098d0b52",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [24, 23, 0]
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
first = {r["path"]: r for r in read(source_dir / "reading.json")["sources"]}
later = {r["path"]: r for r in read(source_dir / "reading-followup.json")["sources"] if "path" in r}
for name, source, label, kind, publisher, day in (
    ("announcement", first["tip-0515-call.html.bin"], "TİP’in 15 Mayıs barış zirvesi çağrısı", "party", "Türkiye İşçi Partisi", "2026-05-15"),
    ("organizer", first["tip-0705-report.html.bin"], "TİP’in 5 Temmuz toplantı aktarımı", "party", "Türkiye İşçi Partisi", "2026-07-05"),
    ("attendee", first["cso-attendee-report.html.bin"], "Comité Surveillance OTAN katılımcı anlatımı", "independent_report", "Comité Surveillance OTAN", None),
    ("declaration", later["final-tr-confirmed.html.bin"], "No to NATO Girişimi, 25 Temmuz nihai deklarasyonu", "unknown", "No to NATO Girişimi", "2026-07-25"),
    ("nato", first["nato-0708-recap.html.bin"], "NATO’nun Ankara zirvesi kapanış açıklaması", "official", "NATO", "2026-07-08"),
):
    raw = (source_dir / source["path"]).read_bytes()
    assert sha(raw) == source["sha256"]
    obj = Path("objects") / source["sha256"]
    original, readable = obj / "original.html.bin", obj / "readable.html"
    copy_verified(source_root / original, raw)
    copy_verified(source_root / readable, readable_bytes(raw, "html"))
    url = source["url"]
    final_url = source.get("final_url", url)
    precision = "day" if day else "unknown"
    insert("document", dict(id=f"{case}-{name}", party_id=party, title=label, source_kind=kind))
    insert("document_version", dict(id=vid(name), document_id=f"{case}-{name}", original_url=url, final_url=final_url,
        document_date=day, date_precision=precision, date_unknown_reason=None if day else "Katılımcı yazısının sayfasında yayım günü bulunamadı.",
        version_label=label, accessed_at=source["retrieved_at_utc"], verified_at=now, mime="text/html",
        sha256=source["sha256"], original_path=str(original), readable_path=str(readable)))
    attribution = {"party": "party_publication", "independent_report": "other", "unknown": "other", "official": "official"}
    insert("source_attribution", dict(version_id=vid(name), kind=attribution[kind], publisher=publisher, author=None,
        social_handle=None, published_at=day, date_precision=precision, public_url=final_url, basis=source["reading"]))
    view = build_view(raw, final_url, source_root, fetch_assets=False)
    validate_view(source_root, view)
    insert("archive_view", dict(view, version_id=vid(name)))
    sources[name] = (raw, final_url)

passages = {}
for key, source, exact, section, suffix in (
    ("announcement", "announcement", "4 Temmuz’da Uluslararası Anti-Emperyalist Barış Zirvesi’ne ev sahipliği yapacağız",
     "TİP’in 15 Mayıs duyurusundaki ev sahipliği hedefi", "</h1>"),
    ("organizer", "organizer", "Uluslararası Anti-Emperyalist Barış Zirvesi’ne ev sahipliği yaptık",
     "TİP’in 5 Temmuz toplantı başlığı", "</h1>"),
    ("planned-declaration", "organizer", "son halini alarak kamuoyuna duyurulacak.",
     "5 Temmuz yazısındaki 7 Temmuz için deklarasyon planı", None),
    ("attendee", "attendee", "organized by TIP - The Turkish Workers Party on 4 July 2026",
     "Katılımcının İstanbul buluşması tarihi ve TİP’in organizasyonuna ilişkin anlatımı", None),
    ("final-declaration", "declaration", "NATO dağıtılsın, tüm askeri üsleri kapatılsın!",
     "25 Temmuz nihai deklarasyonundaki talepler", None),
    ("ankara", "nato", "8 July 2026",
     "NATO’nun Ankara zirvesi kapanış tarihi", None),
):
    assert exact + (suffix or "") in html_source_text(sources[source][0]), (key, exact)
    row = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=suffix,
               article=None, section=section, pdf_page_index=None, printed_page=None)
    insert("passage", row)
    passages[key] = row

inventory = read(working / "04-inventory.json")
scopes = {}
for row in inventory["cells"]:
    if row["party_id"] != party or row["topic_id"] != topic:
        continue
    lane, cell = row["research_kind"], row["cell_id"]
    scopes[lane] = cell
    if not any(r["id"] == cell for r in records["practice_scope_v2"]):
        add("practice_scope_v2", id=cell, **{k: row[k] for k in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="TİP’in zirve çağrısı, toplantı ve 25 Temmuz nihai deklarasyonu incelendi.")
assert len(scopes) == 2
for key, (_, url) in sources.items():
    scope = scopes["statement" if key == "announcement" else "event"]
    version = vid(key)
    sections = [r["section"] for r in passages.values() if r["version_id"] == version]
    attempt = f"{version}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(sections, ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="4 Temmuz İstanbul Barış Zirvesi ve karşılaştırma için tarihli kaynak pasajı okundu.", source_version_id=version)
    add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
        relevance_reason="İstanbul barış zirvesi ve Ankara NATO zirvesi tarih zinciri.", state="examined",
        attempt_ids=json.dumps([attempt]))

bounds = ("4 Temmuz İstanbul barış zirvesi ile 7–8 Temmuz Ankara NATO zirvesi ayrı. "
          "TİP ve katılımcının anlatımı İstanbul’daki organizasyonu belgeliyor. Nihai deklarasyon 25 Temmuz tarihli. "
          "Daha erken deklarasyon yayımı, 3 Temmuz idari işlemlerinin özgün kayıtları ve politika hedeflerinin uygulanması açık.")

def finding(suffix,text,refs,*,quote=False,pair=None):
    ident=f"{case}-{suffix}"
    insert("finding",dict(id=ident,party_id=party,heading="Belgelenmiş uygulamalar",pair_id=pair or ident,
        text=text,provenance="quote" if quote else "summary",epistemic_type="claim"))
    insert("review",dict(id=f"review-{ident}",kind="finding",subject_id=ident,reviewer_kind="agent",
        reviewed_at=now,result="reviewed",reason="TİP yayımları, katılımcı anlatımı ve girişimin nihai bildirgesi ilgili pasajlarından okundu."))
    for ref in refs:
        insert("finding_evidence",dict(finding_id=ident,passage_id=pid(ref),role="quotation" if quote else "support"))
        insert("verification",dict(finding_id=ident,passage_id=pid(ref),checked_at=now,result="confirmed",
            reason=passages[ref]["section"]))
    return ident

summary = finding("announcement-summary", "TİP, 15 Mayıs 2026’da 4 Temmuz İstanbul barış zirvesine ev sahipliği yapacağını açıkladı.",
                  ("announcement",))
quote = finding("announcement-quote", passages["announcement"]["exact"], ("announcement",), quote=True, pair=summary)
statement = f"{case}-statement"
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2026-05-15", date_precision="day",
    version_id=vid("announcement"), period_basis="TİP’in 15 Mayıs tarihli resmî yayımı.",
    comparison_row_id="04-03-v3-0304-tip-program-nato-row", uncertainty_reason=bounds)

event = f"{case}-event"
add("practice_event", id=event, common_event_key="istanbul-2026-07-04-anti-emperyalist-baris-zirvesi",
    event_at="2026-07-04", date_precision="day", date_unknown_reason=None,
    title="4 Temmuz 2026 İstanbul Uluslararası Anti-Emperyalist Barış Zirvesi",
    scope_context="TİP’in açıklaması ve Comité Surveillance OTAN katılımcı anlatımıyla belgelenen İstanbul toplantısı.",
    occurrence_basis="TİP’in 5 Temmuz tarihli düzenleyici duyurusu ve toplantıya giden katılımcının doğrudan anlatımı.")
points = {
    "attendee": ("result", "Katılımcı, 4 Temmuz İstanbul toplantısına gittiğini ve TİP’in düzenlediğini yazdı."),
}
for key, (stage, claim) in points.items():
    add("practice_event_evidence", event_id=event, passage_id=pid(key), stage=stage, supported_point=claim,
        concrete_basis=passages[key]["section"], limitation=bounds, epistemic_type="claim")
    add("practice_evidence_assessment", event_id=event, passage_id=pid(key), stage=stage, basis_kind="observation")
result = finding("summit-result", "4 Temmuz İstanbul buluşmasının düzenlendiğini TİP ve bir katılımcı kendi yayımlarında aktardı.",
                 ("organizer", "attendee"))
explanation = finding("comparison", "TİP’in 15 Mayıs’ta duyurduğu İstanbul toplantısı 4 Temmuz’da yapıldı. TİP’in 5 Temmuz yazısında 7 Temmuz için deklarasyon planı vardı. Girişimin nihai bildirgesi 25 Temmuz tarihli. Ankara NATO zirvesi ayrı. Deklarasyonun politika hedeflerinin uygulanması açık.",
                      ("announcement", "organizer", "attendee", "planned-declaration", "final-declaration", "ankara"))
relation = f"{case}-relation"
add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes["event"], statement_id=statement, event_id=event,
    target_finding_id=summary, result_finding_id=result, explanation_finding_id=explanation,
    comparability_reason="15 Mayıs çağrısı ve 4 Temmuz buluşması aynı İstanbul etkinliği ve ev sahipliğine ilişkin.",
    temporal_context="15 Mayıs çağrı, 4 Temmuz toplantı, 5 Temmuz parti aktarımı, 25 Temmuz tarihli nihai deklarasyon.",
    authority_context="TİP organizasyonunu, katılımcı kendi deneyimini, No to NATO Girişimi ortak taleplerini yayımladı.",
    uncertainty_reason=bounds)
add("practice_candidate", id=f"{case}-candidate", scope_id=scopes["event"], event_id=event, relation_id=relation,
    state="eligible", reason="Duyurulan toplantının oluşu parti yayımı ve katılımcının doğrudan anlatımıyla belgeli.",
    passage_ids=json.dumps([pid(ref) for ref in points]))

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
claims.update({pid(ref): point for ref, (_, point) in points.items()})
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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için parti, katılımcı veya girişim yayımındaki ilgili pasajlar okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-peace-summit-2026-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_PEACE_SUMMIT_2026_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
