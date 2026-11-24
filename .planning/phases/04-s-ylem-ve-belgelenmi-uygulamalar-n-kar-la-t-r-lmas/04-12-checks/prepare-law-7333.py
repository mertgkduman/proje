"""Build the 2/3740 filing, 7333 comparison, and separate constitutional judgment."""

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
source_dir = checks / "law-7333-sources"
source_root = working / "sources" / "demokrat"
case = "0412-law-7333"
party = "demokrat"
topic = "anayasal-denetim"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
from_predecessor_draft = sys.argv[1:] == ["--from-predecessor-draft"]
assert preflight or from_predecessor_draft or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(content):
    return hashlib.sha256(content).hexdigest()

if preflight or from_predecessor_draft:
    pair = (checks / "budget-7344-draft.json", checks / "budget-7344-review-draft.json")
else:
    pair = (working / "04-demokrat.json", working / "04-demokrat-review.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "3848a79473d94f409206f9ee6299533ae278eaeae31b11a067639b9ee68a88d8",
    "8787e957eed48406c0021a83e1504765de820c22d0a43cce367637028cbd639d",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [62, 48, 0]
receipt = read(source_dir / "reading.json")
source_rows = {row["original_path"]: row for row in receipt["sources"]}
party_row = next(row for row in read(checks / "party-news-033-reading.json")["examined"] if row["position"] == 222)

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
    ("filing", "tbmm-2-3740-sicil.html.bin", "2021-07-09", "TBMM 2/3740 teklif sicili"),
    ("commission", "tbmm-ss277.pdf", "2021-07-13", "2/3740 Plan ve Bütçe Komisyonu raporu"),
    ("floor", "tbmm-105-tam.pdf", "2021-07-18", "17 Temmuz 2021’de açılan 105. birleşim"),
    ("law", "tbmm-7333-kabul.html.bin", "2021-07-18", "7333 sayılı kanun kabul metni"),
    ("registry", "tbmm-7333-sicil.html.bin", "2021-07-28", "TBMM 7333 kanun sicili"),
    ("court", "aym-2022-norm-denetimi-secme.pdf", "2022-06-30", "AYM E.2018/137 K.2022/86 hükmü"),
    ("party", party_row["original_path"], party_row["displayed_day"], "Gültekin Uysal’ın 14 Temmuz açıklaması"),
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
    ("party-quote", "party", None, None, "kimi OHAL uygulamalarının 3 yıl daha uzatılmasını teklif etmektedir.", "Uysal’ın teklif aşamasındaki süre açıklaması"),
    ("file-date", "filing", None, None, "09/07/2021", "2/3740 Başkanlığa geliş tarihi"),
    ("file-signers", "commission", 12, "13", "Ankara Milletvekili Orhan YEGİN ile 45 milletvekili tarafından 9/7/2021 tarihinde Türkiye", "Komisyon raporunda imzacılar ve başvuru günü"),
    ("file-text", "commission", 112, "113", "ibareleri “altı yıl” şeklinde değiştirilmiştir.", "2/3740 madde 22 ve rapor madde 23, altı yıllık toplam süre"),
    ("floor-motion", "floor", 103, None, "“dört yıl” şeklinde değiştirilmesini arz ve teklif ederiz.", "277 sıra sayısı madde 23 üzerindeki Genel Kurul önergesi"),
    ("floor-article", "floor", 103, None, "23’üncü madde kabul edilmiştir.", "Değiştirilen 23. madde ayrı kabul edildi"),
    ("floor-adoption", "floor", 113, None, "Teklif kabul edilmiş ve kanunlaşmıştır.", "2/3740 teklifinin tümünün kabulü"),
    ("floor-count", "floor", 113, None, "Kullanılan oy sayısı\n:\n327\nKabul\n:\n266\nRet\n:\n61 (x)", "Kürsü sayımı 266 kabul, 61 ret"),
    ("law-23", "law", None, None, "(Ç), (D) ve (G) fıkralarında yer alan “üç yıl” ibareleri “dört yıl” şeklinde", "7333 madde 23, geçici 35’in altı fıkrasında dört yıllık süre"),
    ("law-20", "law", None, None, "Değişiklik Yapılmasına Dair Kanunun geçici 1 inci maddesinin birinci fıkrasında", "7333 madde 20, 7145 geçici 1’deki ayrı süre"),
    ("law-enter", "law", None, None, "ç) Diğer maddeleri\r\nyayımı tarihinde,", "7333 madde 25 ç bendi, yayım günü yürürlük"),
    ("registry-adopt", "registry", None, None, "18/07/2021", "Kanunun kabul tarihi"),
    ("registry-publish", "registry", None, None, "28/07/2021", "31551 sayılı Resmî Gazete yayımı"),
    ("court-date", "court", 651, "641", "30/6/2022 tarihinde karar verildi.", "AYM E.2018/137 K.2022/86 karar günü"),
    ("court-reject", "court", 651, "641", "a. (A), (B) ve (G) fıkralarında yer alan “…üç yıl…” ibarelerinin “…dört", "A, B ve G fıkralarındaki süre değişiklikleri için oyçokluğuyla ret"),
    ("court-annul", "court", 651, "641", "İPTALLERİNE OYBİRLİĞİYLE,", "C, Ç ve D fıkralarındaki süre değişiklikleri için oybirliğiyle iptal"),
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
    lane = "statement" if key=="party" else "event"
    scope = scopes[lane]
    version = vid(key)
    sections = sorted(row["section"] for row in passages.values() if row["version_id"]==version)
    attempt = f"{version}-{lane}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now, inspected_sections=json.dumps(sections,ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url,
        result="examined", reason="2/3740, 7333 veya ilgili yargı işlemi için özgün pasaj okundu.", source_version_id=version)
    if not any(row["scope_id"]==scope and row["url"]==url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
            relevance_reason="2/3740 teklifi, 7333 kanunu veya fıkraların norm denetimi.",
            state="examined", attempt_ids=json.dumps([attempt]))

bounds = ("Süreler ilgili madde ve fıkra bakımından geçerli. Uysal’ın açıklaması teklif aşamasındaki değerlendirmesi. "
          "Kişisel oy, fiilî idari işlem ve sonraki uygulama açık.")

def finding(suffix, content, refs, *, quote=False, pair=None):
    ident = f"{case}-{suffix}"
    insert("finding", dict(id=ident, party_id=party, heading="Belgelenmiş uygulamalar", pair_id=pair or ident,
        text=content, provenance="quote" if quote else "summary", epistemic_type="claim"))
    insert("review", dict(id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent",
        reviewed_at=now, result="reviewed", reason="İlgili 2/3740, 7333 veya parti pasajının özgün kaydı okundu."))
    for ref in refs:
        insert("finding_evidence", dict(finding_id=ident, passage_id=pid(ref), role="support"))
        insert("verification", dict(finding_id=ident, passage_id=pid(ref), checked_at=now,
            result="confirmed", reason=passages[ref]["section"]))
    return ident

statement = f"{case}-statement"
summary = finding("statement-summary", "Gültekin Uysal 14 Temmuz 2021’de, Meclise sunulan teklifin kimi OHAL uygulamalarını üç yıl daha uzatacağını belirterek teklifi eleştirdi.", ("party-quote",))
quote = finding("statement-quote", passages["party-quote"]["exact"], ("party-quote",), quote=True, pair=summary)
template = next(row for row in records["practice_statement"] if row["id"]=="0412-atalay-statement")
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2021-07-14", date_precision="day",
    version_id=vid("party"), period_basis="Demokrat Parti basın merkezi açıklama günü.",
    comparison_row_id=template["comparison_row_id"], uncertainty_reason=bounds)

relation = f"{case}-adoption-relation"
actions = {"file-date", "file-signers", "file-text", "floor-motion", "floor-article", "floor-count"}
for key, common, day, title, refs, reason in (
    ("filing", "tbmm-27-4-2-3740-filing", "2021-07-09", "2/3740 teklifinin Başkanlığa sunulması",
     ("file-date", "file-signers", "file-text"), "Başvuru, 14 Temmuz parti açıklamasından önce."),
    ("adoption", "tbmm-27-4-105-2-3740-law-7333", "2021-07-18", "2/3740 teklifinin 7333 sayılı kanun olarak kabulü",
     ("floor-motion", "floor-article", "floor-count", "floor-adoption", "law-20", "law-23", "law-enter", "registry-adopt", "registry-publish"),
     "Parti açıklamasındaki altı yıla çıkarma önerisi ve Genel Kurulun dört yıl kabulü, aynı madde zincirinde."),
    ("court", "aym-2018-137-2022-86-decision", "2022-06-30", "AYM’nin 7333’teki süre değişiklikleri hakkında hükmü",
     ("court-date", "court-reject", "court-annul"), "Mahkeme hükmü ayrı işlem. Parti açıklaması teklif aşamasındaki tutum."),
):
    ident = f"{case}-{key}-event"
    add("practice_event", id=ident, common_event_key=common, event_at=day, date_precision="day",
        date_unknown_reason=None, title=title, scope_context="2/3740 ve 7333’teki süre değişiklikleri",
        occurrence_basis=passages[refs[0]]["section"])
    for ref in refs:
        row = passages[ref]
        stage = "action" if ref in actions else "result"
        add("practice_event_evidence", event_id=ident, passage_id=pid(ref), stage=stage,
            supported_point=row["section"], concrete_basis=row["section"], limitation=bounds, epistemic_type="claim")
        add("practice_evidence_assessment", event_id=ident, passage_id=pid(ref), stage=stage, basis_kind="document")
    matched = key=="adoption"
    add("practice_candidate", id=f"{case}-{key}-candidate", scope_id=scopes["event"], event_id=ident,
        relation_id=relation if matched else None, state="eligible" if matched else "unmatched",
        reason=reason, passage_ids=json.dumps([pid(ref) for ref in refs]))

result = finding("adoption-result",
    "7333 sayılı kanunun 23. maddesi, 375 sayılı KHK’nın geçici 35. maddesindeki ilgili süreyi üç yıldan dört yıla çıkardı. Kanun 18 Temmuz’da kabul edildi ve bu hüküm 28 Temmuz’da yürürlüğe girdi.",
    ("floor-adoption", "law-23", "law-enter", "registry-adopt", "registry-publish"))
comparison = finding("adoption-comparison",
    "Uysal’ın eleştirdiği teklif üç yıllık süreyi altı yıla çıkarmayı öngörüyordu. Genel Kurul 23. madde için dört yılı kabul etti. 20. maddede yer alan 7145 sayılı kanunun geçici 1. maddesine ilişkin ayrı süre altı yıla çıktı.",
    ("party-quote", "file-text", "floor-motion", "floor-article", "law-23", "law-20"))
add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes["event"],
    statement_id=statement, event_id=f"{case}-adoption-event", target_finding_id=summary,
    result_finding_id=result, explanation_finding_id=comparison,
    comparability_reason="Muhalefet açıklaması ve yasama metinleri aynı sürenin teklif ve kabul aşamalarına ilişkin.",
    temporal_context="9 Temmuz başvuru, 14 Temmuz açıklama, 18 Temmuz kabul, 28 Temmuz yayım ve ilgili hükmün yürürlüğü.",
    authority_context="Teklif Orhan Yegin ve 45 milletvekilinden, değişiklik ve kabul TBMM Genel Kurulundan.", uncertainty_reason=bounds)

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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için ilgili 2/3740, 7333 veya AYM pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"law-7333-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("DEMOCRAT_LAW_7333_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
