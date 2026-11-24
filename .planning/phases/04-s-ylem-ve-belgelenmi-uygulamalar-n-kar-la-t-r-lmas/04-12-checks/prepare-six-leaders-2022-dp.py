"""Build the Demokrat Parti comparison for the 2 October 2022 leader meeting."""

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
party = "demokrat"
topic = "siyasal-ittifaklar"
source_root = working / "sources" / party
case = "0412-six-leaders-2022-dp"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


pair = (working / "04-demokrat.json", working / "04-demokrat-review.json")
expected = (
    "fb64269082d819d7fac41b5a112071c4c7bd2f93fd24106d8603018dfe43f9d1",
    "9b0a5216ce038c3568c031bc3195d08dbdaaf471d71ee83c4bd2e889ad8c5f32",
)
if preflight and sha(pair[0].read_bytes()) != expected[0]:
    pair = (checks / "question-13274-bulletins-draft.json", checks / "question-13274-bulletins-review-draft.json")
assert tuple(sha(path.read_bytes()) for path in pair) == expected
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [79, 50, 0]


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
receipt = read(checks / "six-leaders-2022-dp-reading.json")
for row in receipt["sources"]:
    name, url, day = row["key"], row["url"], row["date"]
    raw = (checks.parent / row["phase_relative_path"]).read_bytes()
    assert len(raw) == row["bytes"] and sha(raw) == row["sha256"]
    if name == "conclusion":
        continue
    folder = Path("objects") / row["sha256"]
    original, readable = folder / "original.html.bin", folder / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, "html"))
    document = f"{case}-{name}"
    journal = name == "meeting"
    title = ("2 Ekim CHP Genel Merkezi toplantısının tarihli haberi" if journal
             else "21 Ağustos altı parti liderinin ortak açıklaması")
    insert("document", dict(id=document, party_id=party, title=title, source_kind="journalism" if journal else "party"))
    insert("document_version", dict(id=vid(name), document_id=document, original_url=url, final_url=url,
        document_date=day, date_precision="day", date_unknown_reason=None, version_label=title,
        accessed_at=row["retrieved_at_utc"], verified_at=now, mime="text/html",
        sha256=row["sha256"], original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=vid(name), kind="journalism" if journal else "party_publication",
        publisher=row["publisher"], author=row["author"], social_handle=None, published_at=day,
        date_precision="day", public_url=url, basis=row["basis"]))
    view = build_view(raw, url, source_root, fetch_assets=False)
    validate_view(source_root, view)
    insert("archive_view", dict(view, version_id=vid(name)))
    sources[name] = (raw, url)

passages = {}
for key, source, exact, section in (
    ("plan", "statement", "2 Ekim 2022 Pazar g&uuml;n&uuml; saat 14.00&rsquo;da CHP Genel Merkezinde", "21 Ağustos ortak açıklamasında toplantı planı"),
    ("first-round", "statement", "6. toplantımızla tamamlıyoruz.", "21 Ağustos metninde ilk turun son toplantısı"),
    ("uysal", "meeting", "13.57’de Demokrat Parti Genel Başkanı Gültekin Uysal geldi.", "2 Ekim haberinde DP genel başkanının gelişi"),
    ("meeting-time", "meeting", "Saat 14.11’de başlayan görüşmenin", "2 Ekim haberinde görüşmenin başlangıç saati"),
    ("meeting-round", "meeting", "ikinci tur görüşmeleri CHP’nin ev sahipliğinde başladı.", "2 Ekim haberinde ev sahibi ve toplantı sırası"),
    ("working-group", "meeting", "ortak bir çalışma grubu kurulmasına", "2 Ekim haberinde aktarılan ortak çalışma grubu kararı"),
):
    assert exact in html_source_text(sources[source][0]), key
    row = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None,
        article=None, section=section, pdf_page_index=None, printed_page=None)
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
            boundary_reason="21 Ağustos 2022 ortak duyurusu ve 2 Ekim buluşması dar kapsamda okundu.")
assert set(scopes) == {"statement", "event"}
for key, (_, url) in sources.items():
    scope = scopes["statement" if key == "statement" else "event"]
    version = vid(key)
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    attempt = f"{version}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(sections, ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="Ortak duyuru, tarihli haber ve toplantı sonrası bildiri ilgili pasajlarından okundu.", source_version_id=version)
    add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
        relevance_reason="21 Ağustos duyurusu ve 2 Ekim altı lider toplantısı.", state="examined", attempt_ids=json.dumps([attempt]))

bounds = ("Duyuruda 14.00 planlandı. Independent Türkçe’nin haberinde toplantı 14.11’de başladı. "
          "Çalışma grubu kurma kararı ayrı bir bildiri maddesi. Politika uygulaması ve adayın daha sonra belirlenmesi ayrı araştırma konusu.")


def finding(suffix, content, refs, *, quote=False, pair=None):
    ident = f"{case}-{suffix}"
    insert("finding", dict(id=ident, party_id=party, heading="Belgelenmiş uygulamalar", pair_id=pair or ident,
        text=content, provenance="quote" if quote else "summary", epistemic_type="claim"))
    insert("review", dict(id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        result="reviewed", reason="Ortak açıklama ve tarihli toplantı haberi ilgili pasajlarından okundu."))
    for ref in refs:
        insert("finding_evidence", dict(finding_id=ident, passage_id=pid(ref), role="quotation" if quote else "support"))
        insert("verification", dict(finding_id=ident, passage_id=pid(ref), checked_at=now, result="confirmed", reason=passages[ref]["section"]))
    return ident


summary = finding("announcement-summary", "Demokrat Parti’de yayımlanan 21 Ağustos ortak açıklamasında altı lider, 2 Ekim 2022’de CHP Genel Merkezinde toplanacaklarını duyurdu.", ("plan", "first-round"))
quote = finding("announcement-quote", passages["plan"]["exact"], ("plan",), quote=True, pair=summary)
statement = f"{case}-statement"
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2022-08-21", date_precision="day",
    version_id=vid("statement"), period_basis="Demokrat Parti’nin 21 Ağustos 2022 tarihli ortak metin yayımı.",
    comparison_row_id="04-03-v3-0313-demokrat-siyasal-ittifaklar", uncertainty_reason=bounds)

event = f"{case}-event"
add("practice_event", id=event, common_event_key="six-leaders-2022-10-02-chp-second-round-meeting", event_at="2022-10-02",
    date_precision="day", date_unknown_reason=None, title="Altı liderin CHP Genel Merkezindeki ikinci tur ilk toplantısı",
    scope_context="Altı siyasi parti liderinin 2 Ekim 2022 tarihinde CHP Genel Merkezindeki ikinci tur ilk toplantısı.",
    occurrence_basis="2 Ekim 2022’de CHP’nin ev sahipliğinde yapılan ikinci turun ilk toplantısını 2 Ekim ortak açıklaması ve Independent Türkçe’nin tarihli haberi belgeliyor. Katılımcılar arasında Temel Karamollaoğlu, Gültekin Uysal ve Meral Akşener vardı.")
points = {
    "uysal": ("action", "Independent Türkçe, DP Genel Başkanı Gültekin Uysal’ın 13.57’de CHP Genel Merkezine geldiğini bildirdi."),
    "meeting-round": ("action", "Haberde altı liderin ikinci tur görüşmelerinin CHP ev sahipliğinde başladığı belirtiliyor."),
    "meeting-time": ("result", "Habere göre altı liderin görüşmesi 14.11’de başladı."),
}
for key, (stage, claim) in points.items():
    add("practice_event_evidence", event_id=event, passage_id=pid(key), stage=stage, supported_point=claim,
        concrete_basis=passages[key]["section"], limitation=bounds, epistemic_type="claim")
    add("practice_evidence_assessment", event_id=event, passage_id=pid(key), stage=stage, basis_kind="observation")
result = finding("meeting-result", "Altı lider 2 Ekim’de CHP Genel Merkezinde buluştu. Gültekin Uysal Demokrat Parti genel başkanı sıfatıyla katıldı.", ("uysal", "meeting-time", "meeting-round"))
explanation = finding("comparison", "21 Ağustos’ta saat 14.00 için duyurulan buluşma 2 Ekim’de CHP Genel Merkezinde gerçekleşti. Independent Türkçe toplantının 14.11’de başladığını bildirdi. 2 Ekim ortak metninde çalışma grubu kurma kararı yer aldı. Politikaların uygulanmasına ilişkin sonuç açık.",
                      ("plan", "uysal", "meeting-time", "meeting-round", "working-group"))
relation = f"{case}-relation"
add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes["event"], statement_id=statement,
    event_id=event, target_finding_id=summary, result_finding_id=result, explanation_finding_id=explanation,
    comparability_reason="21 Ağustos duyurusu ve tarihli 2 Ekim kayıtları aynı toplantıya ilişkin.",
    temporal_context="21 Ağustos Saadet ev sahipliğinde önceki toplantı ve duyuru. 2 Ekim CHP ev sahipliğinde toplantı ve ortak metin.",
    authority_context="Altı lider ortak açıklama yaptı. CHP toplantıya ev sahipliği yaptı. Uysal Demokrat Parti genel başkanı sıfatıyla katıldı.", uncertainty_reason=bounds)
add("practice_candidate", id=f"{case}-candidate", scope_id=scopes["event"], event_id=event, relation_id=relation,
    state="eligible", reason="Toplantı planı, fiilî buluşma ve Demokrat Parti genel başkanının katılımı ayrı bağlı pasajlarda.",
    passage_ids=json.dumps([pid(key) for key in points]))
person, actor, contribution = (f"{case}-{suffix}" for suffix in ("uysal-person", "uysal-actor", "uysal-contribution"))
insert("person", dict(id=person, name="Gültekin Uysal"))
insert("actor", dict(id=actor, kind="authorized_representative", party_id=party, person_id=person, authorization_passage_id=pid("uysal")))
role = finding("uysal-role", "Gültekin Uysal, haberde 2 Ekim toplantısına gelen Demokrat Parti genel başkanı olarak yer alıyor.", ("uysal",))
add("practice_contribution", id=contribution, event_id=event, party_id=party, actor_id=actor, contribution_kind="task",
    finding_id=role, authority_passage_id=pid("uysal"), membership_passage_id=None,
    responsibility_limit="Kaynak temsil ve katılım sıfatını gösteriyor. Kapalı görüşmedeki tekil sözler ile politika sonucu açık.")
add("practice_actor_period", contribution_id=contribution, valid_from="2022-10-02", valid_to="2022-10-02", identity_passage_id=pid("uysal"))

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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için 21 Ağustos duyurusu ve 2 Ekim toplantısı kaynakları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"six-leaders-2022-dp-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("DEMOCRAT_SIX_LEADERS_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
