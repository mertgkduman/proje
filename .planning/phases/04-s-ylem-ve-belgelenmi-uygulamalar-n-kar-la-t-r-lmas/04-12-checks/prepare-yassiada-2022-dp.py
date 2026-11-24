"""Build the Demokrat Parti comparison for the Yassıada hotel allocation process."""

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
party = "demokrat"
topic = "kulturel-miras"
source_root = working / "sources" / party
case = "0412-yassiada-2022-dp"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


pair = (working / "04-demokrat.json", working / "04-demokrat-review.json")
expected = (
    "13daa495af604e8c69c9eb4833b5a26bc0a1608071c354e5fba47572d423e815",
    "05a018a14c684cd1072323a96972d17fa07d279ed4239c370c694ac4d9928fd4",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [80, 51, 0]


def insert(kind, row):
    entries.append({"kind": kind, "values": row})


def add(table, **row):
    records[table].append(row)


def vid(suffix):
    return f"{case}-{suffix}-v1"


def pid(suffix):
    return f"{case}-{suffix}-p"


def store(relative, raw):
    destination = source_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == raw, destination
    else:
        destination.write_bytes(raw)


sources = {}
source_dir = checks / "party-news-access-040"
receipt = read(source_dir / "reading.json")
rows = {row["path"]: row for row in receipt["linked_material"]}
for name, row, title, kind, publisher, date_note, basis in (
    ("statement", receipt["related_party_original"], "5 Eylül 2022 Demokrat Parti Yassıada açıklaması", "party_publication",
     "Demokrat Parti", None, "DP Basın Merkezi 5 Eylül kaydı ve Uysal’ın yazılı açıklaması."),
    ("terms", rows["253-ktb-2022-2.pdf"], "2022/2 Kamu Taşınmazı Tahsis Şartnamesi", "official",
     "Kültür ve Turizm Bakanlığı", "Dosyada 2022/2 seri numarası ve ilgililere erişim tarihi var. Belgenin düzenlenme günü açık.",
     "Bakanlık duyurusu, taşınmaz satırı ve müzakere ile tahsisin ayrı şartları."),
    ("negotiation", rows["253-ada-negotiation.html.bin"], "Yassıada turizm tesisleri tahsis müzakeresi", "journalism",
     "Ada Gazetesi", None, "18 Ekim günlü ve Aralık güncellemeli haber, Bakanlık müzakeresi ve katılımcıları bildiriyor."),
):
    path = source_dir / row["path"]
    raw = path.read_bytes()
    assert sha(raw) == row["sha256"]
    media = "pdf" if path.suffix == ".pdf" else "html"
    url, day = row.get("final_url", row["url"]), row["date"]
    folder = Path("objects") / row["sha256"]
    original = folder / ("original.pdf" if media == "pdf" else "original.html.bin")
    readable = folder / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, media))
    document = f"{case}-{name}"
    source_kind = "party" if kind == "party_publication" else kind
    insert("document", dict(id=document, party_id=party, title=title, source_kind=source_kind))
    precision = "day" if day else "unknown"
    insert("document_version", dict(id=vid(name), document_id=document, original_url=row["url"], final_url=url,
        document_date=day, date_precision=precision, date_unknown_reason=date_note, version_label=title,
        accessed_at=row["retrieved_at_utc"], verified_at=now, mime="application/pdf" if media=="pdf" else "text/html",
        sha256=row["sha256"], original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=vid(name), kind=kind, publisher=publisher, author=None,
        social_handle=None, published_at=day, date_precision=precision, public_url=url, basis=basis))
    if media == "html":
        view = build_view(raw, url, source_root, fetch_assets=False)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=vid(name)))
    sources[name] = (path, url)

passages = {}
for key, source, page, printed, exact, section in (
    ("statement-call", "statement", None, None, "sermayedarların girişine m&uuml;saade etmeyin.",
     "Uysal’ın Yassıada tesislerinin tahsisine itirazı"),
    ("statement-press", "statement", None, None, "otel zarar ettiği gerek&ccedil;esiyle yerli ve yabancı yatırımcıların teklifine a&ccedil;ıldı.",
     "Uysal’ın basına atfettiği tahsis haberi"),
    ("terms-property", "terms", 4, "5", "Hazine\nOtel\n(5 Yıldızlı)\n5\n324 Yatak",
     "Hazine taşınmazı ve 324 yataklı otel satırı"),
    ("terms-procedure", "terms", 8, "9", "Müzakere sonucunda Bakanlık Arazi Tahsis Komisyonunca tahsis kararı alınması",
     "Müzakere sonrasında alınabilen ayrı tahsis kararı"),
    ("negotiation-chair", "negotiation", None, None, "Nadir Alpaslan başkanlığında düzenlendi.",
     "18 Ekim tarihli Ada Gazetesi haberinde müzakere başkanlığı"),
    ("negotiation-parties", "negotiation", None, None, "Mesant Gıda Restaurant İşletmeciliği Ticaret Anonim Şirketi katılım sağladı.",
     "18 Ekim tarihli haberde iki girişimcinin katılımı"),
    ("negotiation-next", "negotiation", None, None, "tesislerin işletme hakları 2 haftalık bir süreç içerisinde onaylanıp devredileceği bildirildi.",
     "Haberde ileriye dönük onay ve devir beklentisi"),
):
    path = sources[source][0]
    text = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path,page)
    assert exact in text, (source,key)
    row = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None,
        article=None, section=section, pdf_page_index=page, printed_page=printed)
    insert("passage", row)
    passages[key] = row

scopes = {}
for row in read(working / "04-inventory.json")["cells"]:
    if (row["party_id"], row["topic_id"]) != (party, topic):
        continue
    scope = row["cell_id"]
    scopes[row["research_kind"]] = scope
    if not any(existing["id"] == scope for existing in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope, **{k: row[k] for k in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="Yassıada otelinin 2022 tahsis süreci dar kapsamda okundu.")
assert set(scopes) == {"statement", "event"}
for key, (_, url) in sources.items():
    scope = scopes["statement" if key == "statement" else "event"]
    version = vid(key)
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    attempt = f"{version}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(sections, ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="Parti açıklaması, şartname ve müzakere haberi ilgili pasajlarından okundu.", source_version_id=version)
    if not any(row["scope_id"] == scope and row["url"] == url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
            relevance_reason="2022 Yassıada tahsis sürecinin tarihli kaynağı.", state="examined", attempt_ids=json.dumps([attempt]))

bounds = ("Uysal’ın itirazı, Bakanlığın şartnamesi ve 18 Ekim müzakeresi ayrı. Sonraki onay ve devir haberde beklenen işlemler. "
          "İmzalı tahsis kararı, devir tarihi ve partinin sürece etkisi açık.")

def finding(suffix, content, refs, *, quote=False, pair=None):
    ident = f"{case}-{suffix}"
    insert("finding", dict(id=ident, party_id=party, heading="Belgelenmiş uygulamalar", pair_id=pair or ident,
        text=content, provenance="quote" if quote else "summary", epistemic_type="claim"))
    insert("review", dict(id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        result="reviewed", reason="Parti metni, Bakanlık şartnamesi ve tarihli müzakere haberi okundu."))
    for ref in refs:
        insert("finding_evidence", dict(finding_id=ident, passage_id=pid(ref), role="quotation" if quote else "support"))
        insert("verification", dict(finding_id=ident, passage_id=pid(ref), checked_at=now, result="confirmed", reason=passages[ref]["section"]))
    return ident


summary = finding("summary", "Uysal, 5 Eylül 2022’de Yassıada’daki otelin yatırımcılara açılmasına karşı çıktı ve buna izin verilmemesini istedi.",
    ("statement-call", "statement-press"))
quote = finding("quote", passages["statement-call"]["exact"], ("statement-call",), quote=True, pair=summary)
statement = f"{case}-statement"
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2022-09-05", date_precision="day",
    version_id=vid("statement"), period_basis="Demokrat Parti Basın Merkezinin 5 Eylül 2022 yayımı.",
    comparison_row_id="04-03-v3-0313-demokrat-kulturel-miras", uncertainty_reason=bounds)

event = f"{case}-event"
add("practice_event", id=event, common_event_key="ktb-2022-10-18-yassiada-hotel-allocation-negotiation",
    event_at="2022-10-18", date_precision="day", date_unknown_reason=None,
    title="Yassıada otelinin tahsisi için Bakanlık müzakeresi",
    scope_context="Kültür ve Turizm Bakanlığının 2022/2 düzeninde Yassıada’daki otel için düzenlenen müzakere.",
    occurrence_basis="18 Ekim Ada Gazetesi haberinde Bakanlık toplantısı, başkan ve iki katılımcı. Bakanlığın 2022/2 şartnamesinde tesis ve işlem.")
points = {
    "terms-property": ("initiative", "2022/2 şartnamesi Hazineye ait 324 yataklı oteli listeliyor.", "document"),
    "terms-procedure": ("initiative", "Şartname müzakereden sonra ayrı komisyon kararı öngörüyor.", "document"),
    "negotiation-chair": ("action", "Ada Gazetesi müzakerenin Bakan Yardımcısı Nadir Alpaslan başkanlığında yapıldığını bildirdi.", "independent_report"),
    "negotiation-parties": ("action", "Haber Albayrak Turizm ve Mesant’ın müzakereye katıldığını bildirdi.", "independent_report"),
}
for key, (stage, claim, basis_kind) in points.items():
    add("practice_event_evidence", event_id=event, passage_id=pid(key), stage=stage, supported_point=claim,
        concrete_basis=passages[key]["section"], limitation=bounds, epistemic_type="claim")
    add("practice_evidence_assessment", event_id=event, passage_id=pid(key), stage=stage, basis_kind=basis_kind)
explanation = finding("comparison", "Uysal’ın 5 Eylül itirazından sonra, Ada Gazetesi 18 Ekim’de Bakanlığın iki şirketle müzakere yaptığını bildirdi. Şartnamede müzakere sonrasındaki tahsis kararı ayrı. Haberdeki onay ve devir beklentisi, işlemin tamamlandığına dair belge sağlamıyor.",
    ("statement-call", *points, "negotiation-next"))
relation = f"{case}-relation"
comparability = "5 Eylül açıklaması ve 2022/2 şartnamesi ile 18 Ekim müzakeresi Yassıada’daki aynı otelin tahsisini ele alıyor."
add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes["event"], statement_id=statement,
    event_id=event, target_finding_id=summary, result_finding_id=None, explanation_finding_id=explanation,
    comparability_reason=comparability, temporal_context="5 Eylül itirazı. 18 Ekim Bakanlık müzakeresi. Sonraki devir açık.",
    authority_context="Uysal Demokrat Parti genel başkanı olarak karşı çıktı. Tahsis sürecini Kültür ve Turizm Bakanlığı yürüttü.",
    uncertainty_reason=bounds)
add("practice_candidate", id=f"{case}-candidate", scope_id=scopes["event"], event_id=event, relation_id=relation,
    state="eligible", reason=comparability, passage_ids=json.dumps([pid(key) for key in points]))

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
claims.update({pid(ref): point for ref, (_, point, _) in points.items()})
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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için Yassıada tahsis süreci kaynakları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"yassiada-2022-dp-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("DP_YASSIADA_2022_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
