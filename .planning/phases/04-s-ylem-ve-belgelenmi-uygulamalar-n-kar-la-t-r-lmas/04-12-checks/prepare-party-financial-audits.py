"""Append four historical Demokrat Parti audit decisions to the audited working pair."""

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
case = "0412-party-financial-audits"
party = "demokrat"
preflight = sys.argv[1:] == ["--preflight"]
from_draft = sys.argv[1:] == ["--from-predecessor-draft"]
assert preflight or from_draft or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

pair = (checks / "law-7253-draft.json", checks / "law-7253-review-draft.json") if preflight or from_draft else (
    working / "04-demokrat.json", working / "04-demokrat-review.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "e5e6a2a1ab47e4500bc85a6063e4b0b7b5cb3494d7051904e150fafa206331da",
    "5c2746deb539c3452ea47d53b741153ce5b9db90cf1dc5869ae7dc35eac68d06",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert tuple(len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")) == (69,50,0)
receipt = read(source_dir / "reading.json")
scopes = {row["research_kind"]:row["id"] for row in records["practice_scope_v2"] if row["topic_id"]=="mali-kesin-hesap"}

def insert(table, **row):
    entries.append(dict(kind=table, values=row))

def add(table, **row):
    records[table].append(row)

clauses = {
    2011: ("2012-37-2014-68", 588, "4074", "24.101.628,06 TL", "300,00 TL karşılığı Parti malvarlığının",
           "2011 hesabı için 24.101.628,06 TL gelir ve 24.950.172,00 TL gider kaydedildi. Mahkeme, kalan kısmı uygun buldu ve 300 TL’nin Hazineye irat kaydına oybirliğiyle karar verdi."),
    2012: ("2013-42-2014-77", 661, "4147", "2.522.875,06 TL gelir", "karşıoyları ve OYÇOKLUĞUYLA",
           "2012 hesabı için 2.522.875,06 TL gelir ve 5.853.864,60 TL gider kaydedildi. Mahkeme oyçokluğuyla hesabı uygun buldu. Üç karşıoy, 2.904,36 TL gecikme giderini konu aldı."),
    2013: ("2014-44-2016-33", 486, "1722", "3.179.378,16 TL gelir", "OYBİRLİĞİYLE karar verildi.",
           "2013 hesabı için 3.179.378,16 TL gelir ve 5.700.224,17 TL gider kaydedildi. Mahkeme eldeki belgelerle uygunluğa oybirliğiyle hükmetti."),
    2017: ("2018-37-2021-89", 360, "2300", "6.229.333,19 TL gelir", "4/3/2021 tarihinde OYBİRLİĞİYLE karar verildi.",
           "2017 hesabında 6.229.333,19 TL gelir, 2.438.709,12 TL gider ve devreden nakit ile borçlar ayrı. Mahkeme eldeki belgelerle uygunluğa oybirliğiyle hükmetti."),
}

bounds = ("Mahkemenin kararı ilgili hesap yılı ve eldeki bilgi ve belgelerle sınırlı. "
          "Parti içi yetkili organ kararı ve irat hükmünün fiilî tahsilatı açık. "
          "18 Haziran 2022’de yakalanan tüzüğün bu yıllardaki yürürlük durumu açık.")
claims = {}
for row in receipt["sources"]:
    year = row["accounting_year"]
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
    if year==2012:
        evidences.append(("dissent", 662, "4148", "2904,36 TL gecikme", "Gecikme bedeliyle ilgili karşıoyun kapsamı", "result", "Üç üyenin karşıoyu, gecikme gideriyle ilgili. Çoğunluk hesabı uygun buldu."))
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

search = receipt["unmatched_statement_search"]
for i, query in enumerate(search["queries"], start=1):
    add("practice_attempt_v2", id=f"{case}-statement-search-{i}", scope_id=scopes["statement"],
        attempted_at=search["searched_at"], query=query, url=None, result="results", reason=search["reading"], source_version_id=None)

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
        with (checks / f"party-financial-audits-{suffix}.json").open("x") as stream:
            stream.write(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
print("DEMOCRAT_PARTY_FINANCIAL_AUDITS_OK",len(records["practice_event"]),len(records["practice_relation"]))
