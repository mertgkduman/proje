"""Build the 2/3050 filing and 7253 comparison with distinct later records."""

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
source_dir = checks / "law-7253-sources"
source_root = working / "sources" / "demokrat"
case = "0412-law-7253"
party = "demokrat"
topic = "ifade-basin-ozgurlugu"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
from_predecessor_draft = sys.argv[1:] == ["--from-predecessor-draft"]
assert preflight or from_predecessor_draft or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(content):
    return hashlib.sha256(content).hexdigest()

if preflight or from_predecessor_draft:
    pair = (checks / "law-7333-draft.json", checks / "law-7333-review-draft.json")
else:
    pair = (working / "04-demokrat.json", working / "04-demokrat-review.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "164de9d091d9e1af9c8674efec7a49d716e382a7fc3a09151c2d9aca938f558d",
    "4e25d2bc3124f6d4dde25a49efe8a3712083e9a752b5901a798a3adfb9ab67b5",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [65, 49, 0]
receipt = read(source_dir / "reading.json")
source_rows = {row["original_path"]: row for row in receipt["sources"]}
party_rows = {row["position"]: row for row in read(checks / "party-news-036-reading.json")["examined"] if row["position"] in (240, 242)}

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
    ("filing", "tbmm-2-3050-sicil.html.bin", "2020-07-21", "TBMM 2/3050 teklif sicili"),
    ("floor", "tbmm-118-tam.pdf", "2020-07-29", "28 Temmuz’da açılan 118. birleşim"),
    ("law", "tbmm-7253-kabul.html.bin", "2020-07-29", "7253 sayılı kanun kabul metni"),
    ("registry", "tbmm-7253-sicil.html.bin", "2020-07-31", "TBMM 7253 kanun sicili"),
    ("court", "aym-61-1-kararlar.pdf", "2023-10-11", "AYM E.2020/76 K.2023/172 hükmü"),
    ("court-publish", "aym-2024-norm-secme.pdf", "2024-01-10", "AYM kararının Resmî Gazete yayım kaydı"),
    ("btk", "btk-20211007-sura.html.bin", "2021-10-07", "BTK’nın Şûra ve temsilcilik duyurusu"),
    ("party-before", party_rows[242]["original_path"], "2020-07-24", "Gültekin Uysal’ın 24 Temmuz açıklaması"),
    ("party-after", party_rows[240]["original_path"], "2020-07-29", "Gültekin Uysal’ın 29 Temmuz açıklaması"),
):
    is_party = suffix.startswith("party-")
    raw_path = (checks if is_party else source_dir) / name
    source = next(row for row in party_rows.values() if row["original_path"]==name) if is_party else source_rows[name]
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
        published_at=date if is_party or suffix=="btk" else None,
        date_precision="day" if is_party or suffix=="btk" else "unknown",
        public_url=source["url"], basis=source["reading"]))
    if kind == "html":
        charset = source.get("passive_view", {}).get("http_charset")
        view = build_view(raw, source["url"], source_root, fetch_assets=False, http_charset=charset)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=version))
    sources[suffix] = (raw_path, source["url"])

passages = {}
for suffix, source, page, printed, exact, section in (
    ("pre-quote", "party-before", None, None, "kısıtlanacak endişesi yaratıyor.", "24 Temmuz, kabul öncesi ifade özgürlüğü kaygısı"),
    ("pre-representation", "party-before", None, None, "temsilcilik a&ccedil;mak ve vergi m&uuml;kellefiyeti getirmek gibi isabetli", "24 Temmuz, temsile ve vergi mükellefiyeti fikrine olumlu bakış"),
    ("post-quote", "party-after", None, None, "son derece riskli buluyoruz", "29 Temmuz, kabul sonrası parti değerlendirmesi"),
    ("filing", "filing", None, None, "21/07/2020", "2/3050 teklif sicili, Başkanlığa geliş"),
    ("docket", "floor", 22, None, "(2/3050)", "118. birleşim gündemi, 2/3050"),
    ("acceptance", "floor", 103, None, "Teklif kabul edilmiş ve kanunlaşmıştır.", "2/3050 tümü için Genel Kurul kabulü"),
    ("acceptance-date", "registry", None, None, "29/07/2020", "TBMM sicili, 7253 kabul günü"),
    ("publication", "registry", None, None, "31/07/2020", "31202 sayılı Resmî Gazete yayımı"),
    ("representation", "law", None, None, "Türkiye’den günlük erişimi bir milyondan fazla olan yurt dışı", "Temsilci yükümlülüğünün kapsadığı sağlayıcılar"),
    ("effective", "law", None, None, "(s) bendi, 6 ncı ve 7 nci maddeleri 1/10/2020 tarihinde,", "7253 madde 8’de 1 Ekim yürürlük grubu"),
    ("btk", "btk", None, None, "atamaları gerçekleşti ancak istediğimiz performansı almış değiliz.", "BTK yayımında aktarılan temsilci ataması beyanı"),
    ("court-key", "court", 42, "38", "VIII. HÜKÜM", "AYM E.2020/76 K.2023/172 hükmü"),
    ("court-annul", "court", 44, "40", "YAYIMLANMASINDAN BAŞLAYARAK DOKUZ AY SONRA YÜRÜRLÜĞE", "5651 madde 9’a ilişkin iptaller ve dokuz aylık erteleme"),
    ("court-extra", "court", 44, "40", "6. 6. maddesiyle 5651 sayılı Kanun’a eklenen ek 4. maddeye ilişkin", "Ek madde 4 istemi hakkında karar verilmesine yer olmadığı hükmü"),
    ("court-publish", "court-publish", 13, "1", "10/1/2024-32425", "AYM derlemesinde yayım günü ve sayı"),
):
    path = sources[source][0]
    body = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    if exact not in body:
        raise ValueError((suffix, exact))
    row = dict(id=pid(suffix), version_id=vid(source), exact=exact, prefix=None, suffix=None,
               article=None, section=section, pdf_page_index=page, printed_page=printed)
    insert("passage", row)
    passages[suffix] = row

scopes = {row["research_kind"]: row["id"] for row in records["practice_scope_v2"] if row["topic_id"]==topic}
for key, (_, url) in sources.items():
    lane = "statement" if key.startswith("party-") else "event"
    scope = scopes[lane]
    version = vid(key)
    sections = sorted(row["section"] for row in passages.values() if row["version_id"]==version)
    attempt = f"{version}-{lane}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now, inspected_sections=json.dumps(sections,ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url,
        result="examined", reason="2/3050, 7253 ve ilgili açıklamanın özgün pasajı okundu.", source_version_id=version)
    if not any(row["scope_id"]==scope and row["url"]==url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
            relevance_reason="2/3050 düzenlemesi, temsilcilik veya sonraki yargı incelemesi.",
            state="examined", attempt_ids=json.dumps([attempt]))

bounds = ("24 Temmuz açıklamasında temsilcilik ve ifade özgürlüğü değerlendirmeleri ayrı. 29 Temmuz metni kabul sonrası. "
          "Kişisel oy, temsilci atama belgeleri ve tekil erişim kararlarının sonuçları açık.")

def finding(suffix, content, refs, *, quote=False, pair=None):
    ident = f"{case}-{suffix}"
    insert("finding", dict(id=ident, party_id=party, heading="Belgelenmiş uygulamalar", pair_id=pair or ident,
        text=content, provenance="quote" if quote else "summary", epistemic_type="claim"))
    insert("review", dict(id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent",
        reviewed_at=now, result="reviewed", reason="İlgili 2/3050, 7253 veya parti pasajının özgün kaydı okundu."))
    for ref in refs:
        insert("finding_evidence", dict(finding_id=ident, passage_id=pid(ref), role="support"))
        insert("verification", dict(finding_id=ident, passage_id=pid(ref), checked_at=now,
            result="confirmed", reason=passages[ref]["section"]))
    return ident

statement = f"{case}-statement"
summary = finding("statement-summary", "Gültekin Uysal 24 Temmuz 2020’de sosyal medya teklifinin ifade özgürlüğünü sınırlayabileceğinden kaygı duyduğunu açıkladı. Temsilcilik ve vergi mükellefiyeti fikrini olumlu değerlendirdi.", ("pre-quote", "pre-representation"))
quote = finding("statement-quote", passages["pre-quote"]["exact"], ("pre-quote",), quote=True, pair=summary)
template = next(row for row in records["practice_statement"] if row["topic_id"]==topic)
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2020-07-24", date_precision="day",
    version_id=vid("party-before"), period_basis="24 Temmuz 2020 tarihli Demokrat Parti basın merkezi yayını.",
    comparison_row_id=template["comparison_row_id"], uncertainty_reason=bounds)

relation = f"{case}-adoption-relation"
for key, common, day, title, refs, reason in (
    ("filing", "tbmm-27-3-2-3050-filing", "2020-07-21", "2/3050 teklifinin Başkanlığa sunulması",
     ("filing",), "Başvuru, 24 Temmuz parti açıklamasından önce."),
    ("adoption", "tbmm-27-3-118-2-3050-law-7253", "2020-07-29", "2/3050 teklifinin 7253 sayılı kanun olarak kabulü",
     ("docket", "acceptance", "acceptance-date", "publication", "representation", "effective"),
     "24 Temmuz açıklaması gündemdeki düzenlemeyi, 29 Temmuz açıklaması aynı düzenlemenin kabulünü ele alıyor."),
    ("btk", "btk-2021-10-07-social-representatives-report", "2021-10-07", "BTK yayımında temsilci ataması açıklaması",
     ("btk",), "Kurum, Bakan Yardımcısının atamaların yapıldığı beyanını aktarıyor. Platformların atama belgeleri açık."),
    ("court", "aym-2020-76-2023-172-decision", "2023-10-11", "AYM’nin 5651 hükümleri hakkında iptal kararı",
     ("court-key", "court-annul", "court-extra", "court-publish"), "Norm denetimi, 2020 Genel Kurul kabulünden sonraki ayrı karar."),
):
    ident = f"{case}-{key}-event"
    add("practice_event", id=ident, common_event_key=common, event_at=day, date_precision="day",
        date_unknown_reason=None, title=title, scope_context="2/3050, 7253, temsilcilik ve norm denetimi",
        occurrence_basis=passages[refs[0]]["section"])
    for ref in refs:
        row = passages[ref]
        stage = "action" if ref in {"filing", "docket", "btk"} else "result"
        add("practice_event_evidence", event_id=ident, passage_id=pid(ref), stage=stage,
            supported_point=row["section"], concrete_basis=row["section"], limitation=bounds, epistemic_type="claim")
        add("practice_evidence_assessment", event_id=ident, passage_id=pid(ref), stage=stage, basis_kind="document")
    matched = key=="adoption"
    add("practice_candidate", id=f"{case}-{key}-candidate", scope_id=scopes["event"], event_id=ident,
        relation_id=relation if matched else None, state="eligible" if matched else "unmatched",
        reason=reason, passage_ids=json.dumps([pid(ref) for ref in refs]))

result = finding("adoption-result",
    "TBMM 2/3050 teklifini 29 Temmuz’da 7253 sayılı kanun olarak kabul etti. Kanun 31 Temmuz’da yayımlandı. Temsilci yükümlülüğünü düzenleyen madde 1 Ekim’de yürürlüğe girdi.",
    ("acceptance", "acceptance-date", "publication", "representation", "effective"))
comparison = finding("adoption-comparison",
    "Uysal, 24 Temmuz’da temsilcilik fikrini olumlu buldu ve ifade özgürlüğü kaygısını bildirdi. Teklif kabul edildikten sonra 29 Temmuz açıklamasında düzenlemeyi riskli gördüğünü belirtti. 7253, günlük Türkiye erişimi bir milyonu aşan yurt dışı kaynaklı sağlayıcılara temsilci yükümlülüğü getirdi.",
    ("pre-quote", "pre-representation", "post-quote", "acceptance", "representation"))
add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes["event"],
    statement_id=statement, event_id=f"{case}-adoption-event", target_finding_id=summary,
    result_finding_id=result, explanation_finding_id=comparison,
    comparability_reason="24 Temmuz açıklaması ve Genel Kurul kabulü aynı sosyal medya düzenlemesine ilişkin.",
    temporal_context="21 Temmuz başvuru, 24 Temmuz açıklama, 29 Temmuz kabul ve sonraki açıklama, 31 Temmuz yayım, 1 Ekim 6. maddenin yürürlüğü.",
    authority_context="Uysal açıklama yaptı. Teklifi Genel Kurul kabul etti. Tutanağın işlem satırında kişisel oy açık.", uncertainty_reason=bounds)
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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için ilgili 2/3050, 7253 veya ilgili sonraki pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"law-7253-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("DEMOCRAT_LAW_7253_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
