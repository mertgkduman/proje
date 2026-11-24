"""Build the the TİP joint statement and 7242 parliamentary record."""

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
source_dir = checks / "tip-7242-sources"
source_root = working / "sources" / "tip"
case = "0405-tip-7242"
party = "tip"
topic = "cezaevleri"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(content):
    return hashlib.sha256(content).hexdigest()

pair = (working / "04-tip.json", working / "04-tip-review.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "57271c62f71966dbe8e1139060d3c2c10949234713ae279b9ae67b34eeac194e",
    "add02d05e5cebcea4657eaf4ab578b2ff809544474d6cfa1bf83c1efcf6773dc",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [21, 20, 0]
receipt = read(source_dir / "reading.json")
source_rows = {row["original_path"]: row for row in receipt["sources"]}

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
for suffix, filename, date, label in (
    ("party", "tip-20200406-ortak-aciklama.html.bin", "2020-04-06", "TİP’in yayımladığı 6 Nisan ortak açıklaması"),
    ("floor", "tbmm-27-3-84-tutanak.pdf", "2020-04-14", "13 Nisan’da açılan 84. birleşim"),
    ("roll", "tbmm-27-3-84-basilmis.pdf", "2020-04-14", "84. birleşim kesin açık oy cetveli"),
    ("law", "tbmm-7242-kabul.html.bin", "2020-04-14", "7242 sayılı kanun kabul metni"),
    ("registry", "tbmm-7242-kanun-sicili.html.bin", "2020-04-15", "TBMM 7242 kanun sicili"),
):
    is_party = suffix=="party"
    source = next(row for path,row in source_rows.items() if Path(path).name==filename)
    name = source["original_path"]
    raw_path = source_dir / name
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
        publisher=source["publisher"], author="Ortak açıklamanın imzacıları" if is_party else None, social_handle=None,
        published_at=date if is_party else None, date_precision="day" if is_party else "unknown",
        public_url=source["url"], basis=source["reading"]))
    if kind == "html":
        charset = source.get("passive_view", {}).get("http_charset")
        view = build_view(raw, source["url"], source_root, fetch_assets=False, http_charset=charset)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=version))
    sources[suffix] = (raw_path, source["url"])

passages = {}
for suffix, source, page, printed, exact, section in (
    ("party-quote", "party", None, None, "siyasi tutuklu ve hükümlülerin kapsam dışı bırakılması asla kabul edilemez.", "6 Nisan ortak açıklamasındaki kapsam itirazı"),
    ("party-name", "party", None, None, "TÜRKİYE İŞÇİ PARTİSİ", "Açıklamanın 11 imzacısı içinde TİP"),
    ("floor-votes", "floor", 68, None, "Oy sayısı :330\nKabul\n:279\nRet\n:51", "Kürsünün okuduğu toplam ve oy sayıları"),
    ("floor-accepted", "floor", 69, None, "Teklif kabul edilmiş ve kanunlaşmıştır.", "207 sıra sayılı teklifin kabulü"),
    ("roll-count", "roll", 158, "383", "IX.- OYLAMALAR\n383", "Basılı s. 383, 00.09 kesin sonuç ve sayısal oy cetveli"),
    ("roll-atay", "roll", 162, "387", "B: 84\n13 . 4 . 2020\n387", "Basılı s. 387, TİP Hatay Barış Atay Mengüllüoğlu satırı"),
    ("roll-bas", "roll", 163, "388", "388\nB: 84\n13 . 4 . 2020", "Basılı s. 388, TİP İstanbul Erkan Baş satırı"),
    ("registry-adopt", "registry", None, None, "14/04/2020", "TBMM sicilinde 7242 kabul tarihi"),
    ("registry-publish", "registry", None, None, "15/04/2020", "TBMM sicilinde 7242 yayımı"),
    ("registry-issue", "registry", None, None, "31100", "Resmî Gazete sayısı"),
    ("law-exclusions", "law", None, None, "Terörle Mücadele Kanunu kapsamına giren suçlar hariç olmak üzere, 105/A", "52. madde geçici denetimli serbestlik istisnası"),
    ("law-effective", "law", None, None, "Bu Kanun yayımı\r\ntarihinde yürürlüğe girer.", "68. maddeye göre yayım günü yürürlük"),
):
    raw = sources[source][0]
    body = html_source_text(raw.read_bytes()) if page is None else pdf_page_text(raw,page)
    assert exact in body, (suffix,exact)
    row = dict(id=pid(suffix), version_id=vid(source), exact=exact, prefix=None, suffix=None,
        article=None, section=section, pdf_page_index=page, printed_page=printed)
    insert("passage",row)
    passages[suffix]=row

inventory = read(working / "04-inventory.json")
scopes = {}
for row in inventory["cells"]:
    if row["party_id"]!=party or row["topic_id"]!=topic:
        continue
    cell = row["cell_id"]
    scopes[row["research_kind"]]=cell
    add("practice_scope_v2", id=cell, **{key:row[key] for key in (
        "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
        boundary_reason="6 Nisan 2020 ortak açıklaması ve 2/2762 kabulü için ilgili kaynaklar okundu.")
assert len(scopes)==2
for key,(_,url) in sources.items():
    lane = "statement" if key=="party" else "event"
    scope = scopes[lane]
    version = vid(key)
    sections = sorted(row["section"] for row in passages.values() if row["version_id"]==version)
    attempt = f"{version}-{lane}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now, inspected_sections=json.dumps(sections,ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url,
        result="examined", reason="Ortak açıklama, Meclis kabulü veya yayımın ilgili kaydı okundu.", source_version_id=version)
    add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
        relevance_reason="6 Nisan ortak açıklaması ve 2/2762 işlem zinciri.", state="examined", attempt_ids=json.dumps([attempt]))

bounds = ("TİP ortak açıklamanın ayrı imzacısı. TBMM cetvelinde iki kişisel kayıt Katılmadı. "
          "Katılmama kaydının nedeni, ayrı parti kararı ve bireysel infaz uygulaması açık.")

def finding(suffix, content, refs, *, quote=False, pair=None):
    ident = f"{case}-{suffix}"
    insert("finding",dict(id=ident,party_id=party,heading="Belgelenmiş uygulamalar",pair_id=pair or ident,
        text=content,provenance="quote" if quote else "summary",epistemic_type="claim"))
    insert("review",dict(id=f"review-{ident}",kind="finding",subject_id=ident,reviewer_kind="agent",
        reviewed_at=now,result="reviewed",reason="Ortak açıklama ve ilgili tutanak pasajları ayrı okundu."))
    for ref in refs:
        insert("finding_evidence",dict(finding_id=ident,passage_id=pid(ref),role="support"))
        insert("verification",dict(finding_id=ident,passage_id=pid(ref),checked_at=now,result="confirmed",reason=passages[ref]["section"]))
    return ident

statement = f"{case}-statement"
summary = finding("statement-summary", "TİP’in de imzaladığı 6 Nisan 2020 ortak açıklaması, siyasi tutuklu ve hükümlülerin infaz düzenlemesi kapsamına alınmasını istedi.", ("party-quote","party-name"))
quote = finding("statement-quote", passages["party-quote"]["exact"], ("party-quote",), quote=True,pair=summary)
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2020-04-06", date_precision="day",
    version_id=vid("party"), period_basis="Türkiye İşçi Partisi’nin 6 Nisan 2020 tarihli ortak açıklama yayımı.",
    comparison_row_id="04-03-v3-0304-tip-program-scope-cezaevi-row", uncertainty_reason=bounds)

result = finding("result", "TBMM teklifi 14 Nisan 2020’de 279 kabul ve 51 retle kabul etti. Kesin cetvelde Barış Atay Mengüllüoğlu ve Erkan Baş için Katılmadı yazıyor. 7242, 15 Nisan’da yayımlandı ve yürürlüğe girdi.",
    ("floor-votes","floor-accepted","roll-atay","roll-bas","registry-publish","law-effective"))
explanation = finding("comparison", "6 Nisan ortak açıklaması siyasi tutuklu ve hükümlülerin kapsamda olmasını istedi. 7242’nin 52. maddesindeki geçici denetimli serbestlik hükmü, Terörle Mücadele Kanunu kapsamına giren suçları ayrı bir istisna olarak belirledi. 84. birleşim 13 Nisan’da açıldı. Kesin oy cetvelinde saat 00.09. Kişisel oylama satırları ile ortak açıklama ayrı kaynaklarda.",
    ("party-quote","law-exclusions","roll-count","registry-adopt","roll-atay","roll-bas"))
relation = f"{case}-relation"
event = f"{case}-event"
add("practice_event", id=event, common_event_key=receipt["common_event_key"], event_at="2020-04-14", date_precision="day",
    date_unknown_reason=None, title="7242 sayılı infaz kanunu teklifinin kabulü",
    scope_context="TBMM 27. dönem 3. yasama yılı 84. birleşim, 2/2762, 207 sıra",
    occurrence_basis="13 Nisan’da açılan 84. birleşimin gece yarısından sonra açıklanan kabulü, kesin cetvel ve sicil.")
points = {
    "floor-votes":("action","Kürsü 330 toplam, 279 kabul ve 51 ret bildirdi."),
    "floor-accepted":("result","2/2762 teklifinin kabul edildiği duyuruldu."),
    "roll-count":("result","Basılı kesin cetvel 00.09, 279 kabul, 51 ret ve 330 toplam gösteriyor."),
    "roll-atay":("result","Basılı 387. sayfa, TİP Hatay Barış Atay Mengüllüoğlu için Katılmadı."),
    "roll-bas":("result","Basılı 388. sayfa, TİP İstanbul Erkan Baş için Katılmadı."),
    "registry-adopt":("result","Sicil 14 Nisan kabul gününü kaydediyor."),
    "registry-publish":("result","Sicil 15 Nisan 2020 yayım gününü kaydediyor."),
    "registry-issue":("result","Resmî Gazete sayısı 31100."),
    "law-exclusions":("result","52. madde geçici denetimli serbestlikte Terörle Mücadele Kanunu kapsamı istisnasını içeriyor."),
    "law-effective":("result","68. madde uyarınca yürürlük günü yayımla aynı."),
}
for key,(stage,point) in points.items():
    add("practice_event_evidence",event_id=event, passage_id=pid(key), stage=stage,
        supported_point=point, concrete_basis=passages[key]["section"], limitation=bounds, epistemic_type="claim")
    add("practice_evidence_assessment",event_id=event, passage_id=pid(key), stage=stage, basis_kind="document")
add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes["event"],
    statement_id=statement, event_id=event, target_finding_id=summary, result_finding_id=result, explanation_finding_id=explanation,
    temporal_context="6 Nisan ortak çağrı, 13 Nisan birleşim açılışı, 14 Nisan 00.09 kabul, 15 Nisan yayım ve yürürlük.",
    comparability_reason="Ortak açıklamada ele alınan infaz teklifi ve sonraki Genel Kurul kabulü aynı 2/2762 dosyasına ait.",
    authority_context="TİP açıklamanın imzacısı. TBMM Genel Kurulu teklifi kabul etti. İki TİP milletvekilinin kayıtları kişisel.", uncertainty_reason=bounds)
add("practice_candidate",id=f"{case}-candidate",scope_id=scopes["event"],event_id=event,relation_id=relation,state="eligible",
    reason="TİP’in ortak açıklamasına konu infaz teklifi ve TBMM kabulü aynı dosyada.",passage_ids=json.dumps([pid(r) for r in points]))
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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için ilgili 6 Nisan ortak metni ve 7242 pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-7242-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_LAW_7242_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
