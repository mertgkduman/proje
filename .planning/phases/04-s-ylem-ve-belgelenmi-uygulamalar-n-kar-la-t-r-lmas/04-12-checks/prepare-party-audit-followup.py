"""Append the 2018 and 2019 Demokrat Parti audit decisions to the verified pair."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
import uygulamalar as rules
from arsiv import pdf_page_text, readable_bytes

checks = Path(__file__).resolve().parent
source_dir = checks / "party-financial-audit-sources"
working = Path("data/practices")
source_root = working / "sources" / "demokrat"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
case = "0412-party-audit-followup"
party = "demokrat"
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

pair = (working / "04-demokrat.json", working / "04-demokrat-review.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "c17ae50aece24672536936b966a47ea5f8df003835d3e4e00b625cb58e8e146d",
    "990e69ca6db0a1fa2246b98ed3484588ae20ff24889a19970a029845417b9585",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert tuple(len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")) == (73,50,0)
receipt = read(source_dir / "followup-reading.json")
scopes = {row["research_kind"]:row["id"] for row in records["practice_scope_v2"] if row["topic_id"]=="mali-kesin-hesap"}

def insert(table, **row):
    entries.append(dict(kind=table, values=row))

def add(table, **row):
    records[table].append(row)

clauses = {
    2018: ("2019-47-2021-153", 652, "2592", "6.641.061,27 TL gelir", "OYBİRLİĞİYLE karar verildi.",
           "2018 hükmünde 6.641.061,27 TL gelir, 6.640.527,90 TL gider ve sonraki yıla 1.704,82 TL devreden nakit var. Hesap oybirliğiyle uygun bulundu."),
    2019: ("2020-22-2023-9", 776, "5760", "7.017.267,12 TL gelir", "7.018.363,30 TL gider",
           "2019 hükmünde 7.017.267,12 TL gelir, 7.018.363,30 TL gider, önceki yıldan 1.704,82 TL ve sonraki yıla 608,64 TL devreden nakit var. Hesap oybirliğiyle uygun bulundu."),
}

bounds = ("Mahkemenin kararı ilgili hesap yılı ve eldeki bilgi ve belgelerle sınırlı. "
          "Parti içi yetkili organ kararı ve irat hükmünün fiilî tahsilatı açık. "
          "18 Haziran 2022’de yakalanan tüzüğün bu yıllardaki yürürlük durumu açık.")
claims = {}
for row in receipt["sources"]:
    year = row["accounting_year"]
    if year not in (2018, 2019):
        continue
    docket, page, printed, figure, verdict, point = clauses[year]
    stem = f"{case}-{year}"
    vid = f"{stem}-v1"
    title = f"Demokrat Parti {year} kesin hesabına ilişkin AYM kararı"
    path = source_dir / row["original_path"]
    raw = path.read_bytes()
    assert sha(raw)==row["sha256"]
    original = Path("objects") / row["sha256"] / "original.pdf"
    readable = original.with_name("readable.html")
    (source_root / original).parent.mkdir(parents=True, exist_ok=True)
    for relative, value in ((original, raw),(readable, readable_bytes(raw,"pdf"))):
        destination = source_root / relative
        if destination.exists():
            assert destination.read_bytes()==value
        else:
            destination.write_bytes(value)
    insert("document", id=stem, party_id=party, title=title, source_kind="official")
    insert("document_version", id=vid, document_id=stem, original_url=row["url"], final_url=row["url"],
        document_date=row["decision_day"], date_precision="day", date_unknown_reason=None,
        version_label=f"AYM Kararlar Dergisi, {row['printed_pages']}", accessed_at=row["retrieved_at_utc"],
        verified_at=now, mime="application/pdf", sha256=row["sha256"], original_path=str(original), readable_path=str(readable))
    insert("source_attribution", version_id=vid, kind="official", publisher="Anayasa Mahkemesi", author=None,
        social_handle=None, published_at=None, date_precision="unknown", public_url=row["url"], basis=row["reading"])
    event = f"{stem}-event"
    add("practice_event", id=event, common_event_key=f"aym-spmd-{docket}-demokrat-{year}",
        event_at=row["decision_day"], date_precision="day", date_unknown_reason=None, title=title,
        scope_context=f"Demokrat Parti’nin {year} hesap yılı ve AYM mali denetimi.",
        occurrence_basis="AYM Kararlar Dergisinde yayımlanan kararın hüküm bölümü.")
    evidences = [
        ("case", row["pages_zero_based"][0], row["printed_pages"].split("–")[0],
         f"{year} yılı kesin hesabının incelenmesidir.", "Mali denetimin konusu ve hesap yılı", "action", f"{year} kesin hesabı, {row['case']}."),
        ("figures", page, printed, figure, "Hükümde hesap tutarları", "result", point),
        ("verdict", page, printed, verdict, "Hükmün karar şekli ve sınırlaması", "result", point),
    ]
    refs, sections = [], []
    for suffix,index,printed_page,exact,section,stage,detail in evidences:
        assert exact in pdf_page_text(path,index), (year,suffix,exact)
        passage=f"{stem}-{suffix}-p"
        insert("passage", id=passage, version_id=vid, exact=exact, prefix=None, suffix=None,
            article=None, section=section, pdf_page_index=index, printed_page=printed_page)
        add("practice_event_evidence", event_id=event, passage_id=passage, stage=stage,
            supported_point=detail, concrete_basis=section, limitation=bounds, epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=passage, stage=stage, basis_kind="document")
        claims[passage] = detail
        refs.append(passage)
        sections.append(section)
    scope = scopes["event"]
    attempt = f"{stem}-reading"
    add("practice_scope_source", scope_id=scope, version_id=vid, inspected_at=now,
        inspected_sections=json.dumps(sections,ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=row["url"], url=row["url"],
        result="examined", reason=f"{year} denetiminin ilk incelemesi, gerekçesi ve hükmü özgün sayfalardan okundu.", source_version_id=vid)
    add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=row["url"],
        relevance_reason=f"Demokrat Parti’nin {year} yılı mali denetim kararı.", state="examined", attempt_ids=json.dumps([attempt]))
    add("practice_candidate", id=f"{stem}-candidate", scope_id=scope, event_id=event,
        relation_id=None, state="unmatched", passage_ids=json.dumps(refs),
        reason=f"{year} hesabına özgü bağımsız dönemsel parti açıklaması bu aramada doğrulanmadı. {point}")


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
passages = {row["id"]:row for row in snapshot["passage"]}
reviews = review["practice_source_review"]
existing = {(row["subject_kind"],row["subject_id"]) for row in reviews}
assert existing <= targets.keys()
for kind,ident in sorted(targets.keys()-existing):
    refs,_ = targets[kind,ident]
    inspected = [passages[ref] for ref in sorted(refs)]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        source_version_ids=json.dumps(sorted({row["version_id"] for row in inspected})),
        passage_ids=json.dumps([row["id"] for row in inspected]),
        inspected_sections=json.dumps(sorted({row["section"] for row in inspected}),ensure_ascii=False),
        supported_claim=" ".join(dict.fromkeys(claims[ref] for ref in sorted(refs))), limitations=bounds,
        result="reviewed", reason=f"{ident} kaydındaki {kind} için AYM’nin ilgili hesap yılı ve hüküm sayfası okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{key:row[key] for key in ("subject_kind","subject_id")} for row in reviews]
for payload in (package,review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft",package),("review-draft",review)):
        with (checks / f"party-audit-followup-{suffix}.json").open("x") as stream:
            stream.write(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
print("DEMOCRAT_PARTY_AUDIT_FOLLOWUP_OK",len(records["practice_event"]),len(records["practice_relation"]))
