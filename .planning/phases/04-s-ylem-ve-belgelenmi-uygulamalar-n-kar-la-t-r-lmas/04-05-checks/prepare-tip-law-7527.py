"""Build the TİP statement and 7527 parliamentary record."""

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
source_dir = checks / "law-7527-sources"
source_root = working / "sources" / "tip"
case = "0405-tip-law-7527"
party = "tip"
topic = "doga-ekoloji"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(content):
    return hashlib.sha256(content).hexdigest()

pair = (working / "04-tip.json", working / "04-tip-review.json")
if preflight and sha(pair[0].read_bytes()) != "f216db2920b59806af3585e96ca38fd724a2d9395068adff43054be4c36cd371":
    pair = (checks / "tip-peace-summit-2026-draft.json", checks / "tip-peace-summit-2026-review-draft.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "f216db2920b59806af3585e96ca38fd724a2d9395068adff43054be4c36cd371",
    "17975c478ff2402d8149ef66c32a4ae9bf3f9bd828778c6548da319d7c4b90c5",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [25, 24, 0]
receipt = read(source_dir / "reading.json")
source_rows = {row["path"]: row for row in receipt["sources"] if "path" in row}
party_dir = checks / "tip-publication-catalog" / "party-statements-03"
party_row = next(row for row in read(party_dir / "capture.json") if row["i"] == 24)

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
    ("party", "024.html.bin", "2024-07-13", "TİP Hayvan Hakları Komisyonunun 13 Temmuz açıklaması"),
    ("proposal", "proposal-2275.html.bin", "2024-07-12", "TBMM 2/2275 teklif bilgileri"),
    ("floor", "floor-112.pdf", "2024-07-30", "29 Temmuz’da açılan 112. birleşim, 30 Temmuz oylaması"),
    ("correction", "floor-113-correction.pdf", "2024-08-15", "113. birleşimde Cengiz Aydoğdu’nun düzeltme talebi"),
    ("registry", "law-register.html.bin", "2024-08-02", "TBMM 7527 kanun sicili"),
):
    is_party = suffix == "party"
    source = party_row if is_party else source_rows[filename]
    raw_path = (party_dir if is_party else source_dir) / filename
    raw = raw_path.read_bytes()
    assert sha(raw) == source["sha256"], raw_path
    kind = "pdf" if filename.endswith(".pdf") else "html"
    object_dir = Path("objects") / source["sha256"]
    original = object_dir / ("original.pdf" if kind == "pdf" else "original.html.bin")
    readable = object_dir / "readable.html"
    copy_verified(source_root / original, raw)
    copy_verified(source_root / readable, readable_bytes(raw, kind))
    doc_id = f"{case}-{suffix}"
    version = vid(suffix)
    insert("document", dict(id=doc_id, party_id=party, title=label, source_kind="party" if is_party else "official"))
    insert("document_version", dict(id=version, document_id=doc_id, original_url=source["url"], final_url=source.get("final_url", source["url"]),
        document_date=date, date_precision="day", date_unknown_reason=None, version_label=label,
        accessed_at=source["retrieved_at_utc"], verified_at=now,
        mime="application/pdf" if kind=="pdf" else "text/html", sha256=source["sha256"],
        original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=version, kind="party_publication" if is_party else "official",
        publisher="Türkiye İşçi Partisi" if is_party else "TBMM", author="TİP Hayvan Hakları Komisyonu" if is_party else None, social_handle=None,
        published_at=date if is_party else None, date_precision="day" if is_party else "unknown",
        public_url=source.get("final_url", source["url"]), basis="Kaynakta ilgili belge kimliği, tarih ve teklif veya işlem pasajı okundu."))
    if kind == "html":
        charset = None
        view = build_view(raw, source.get("final_url", source["url"]), source_root, fetch_assets=False, http_charset=charset)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=version))
    sources[suffix] = (raw_path, source["url"])

passages = {}
for suffix, source, page, printed, exact, section in (
    ("party-quote", "party", None, None, "Bu Bir Katliam Yasasıdır!", "13 Temmuz tarihli parti açıklamasının başlığı"),
    ("party-commission", "party", None, None, "TİP Hayvan Hakları Komisyonu", "Açıklamanın parti komisyonu imzası"),
    ("proposal-number", "proposal", None, None, "2 / 2275", "TBMM esas numarası"),
    ("proposal-day", "proposal", None, None, "12/07/2024", "TBMM Başkanlığına geliş tarihi"),
    ("floor-count", "floor", 213, "388", "Kullanılan oy sayısı : 500", "Kürsüde açıklanan ilk toplam ve dağılım"),
    ("floor-adopt", "floor", 213, "388", "Teklif kabul edilmiş ve kanunlaşmıştır.", "Başkanlığın kabul duyurusu"),
    ("roll-time", "floor", 214, "389", "Oylama Saati : 03:46", "Kesin cetvelde oylama saati"),
    ("roll-count", "floor", 214, "389", "Kabul Edenler : 273", "Kesin cetvelde 273 kabul ve iki mükerrer"),
    ("roll-duplicates", "floor", 214, "389", "Mükerrer Oylar : 2", "Kesin cetvelde iki mükerrer oy"),
    ("roll-bas", "floor", 219, "394", "İstanbul Baş Erkan TİP Ret", "Erkan Baş’ın kesin cetveldeki kişisel ret oyu"),
    ("roll-kadigil", "floor", 220, "395", "İstanbul Kadıgil Saliha Sera TİP Ret", "Saliha Sera Kadıgil’in kesin cetveldeki kişisel ret oyu"),
    ("roll-sik", "floor", 221, "396", "İstanbul Şık Ahmet TİP Ret", "Ahmet Şık’ın kesin cetveldeki kişisel ret oyu"),
    ("correction", "correction", 70, "491", "Oyumun rengi “kabul” şeklindedir", "Aydoğdu’nun kullanamadığı oya ilişkin beyanı"),
    ("adopt-day", "registry", None, None, "30/07/2024", "TBMM sicilinde kabul günü"),
    ("gazette-day", "registry", None, None, "02/08/2024", "TBMM sicilinde Resmî Gazete yayımı"),
    ("gazette-number", "registry", None, None, "32620", "Resmî Gazete sayısı"),
):
    raw = sources[source][0]
    text = html_source_text(raw.read_bytes()) if page is None else pdf_page_text(raw, page)
    assert exact in text, (suffix, exact)
    row = dict(id=pid(suffix), version_id=vid(source), exact=exact, prefix=None, suffix=None,
               article=None, section=section, pdf_page_index=page, printed_page=printed)
    insert("passage", row)
    passages[suffix] = row

inventory = read(working / "04-inventory.json")
scopes = {}
for row in inventory["cells"]:
    if row["party_id"]!=party or row["topic_id"]!=topic:
        continue
    cell = row["cell_id"]
    scopes[row["research_kind"]]=cell
    if not any(r["id"] == cell for r in records["practice_scope_v2"]):
        add("practice_scope_v2", id=cell, **{key:row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="13 Temmuz 2024 parti yayımı ve 2/2275 kabulü için ilgili kaynaklar okundu.")
assert len(scopes)==2
for key,(_,url) in sources.items():
    lane = "statement" if key=="party" else "event"
    scope = scopes[lane]
    version = vid(key)
    sections = sorted(row["section"] for row in passages.values() if row["version_id"]==version)
    attempt = f"{version}-{lane}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now, inspected_sections=json.dumps(sections,ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url,
        result="examined", reason="Parti açıklaması, TBMM teklifi, nihai oy cetveli veya düzeltme kaydı okundu.", source_version_id=version)
    add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
        relevance_reason="13 Temmuz parti yayımı ve 2/2275 işlem zinciri.", state="examined", attempt_ids=json.dumps([attempt]))

bounds = ("Kürsü 275 kabul açıkladı. Kesin cetvelde 273 kabul ve 2 mükerrer var. "
          "Aydoğdu’nun 15 Ağustos niyet beyanı ayrı. Kanunun belediyelerde fiilî uygulanması ve sonuçları açık.")

def finding(suffix, content, refs, *, quote=False, pair=None):
    ident = f"{case}-{suffix}"
    insert("finding",dict(id=ident,party_id=party,heading="Belgelenmiş uygulamalar",pair_id=pair or ident,
        text=content,provenance="quote" if quote else "summary",epistemic_type="claim"))
    insert("review",dict(id=f"review-{ident}",kind="finding",subject_id=ident,reviewer_kind="agent",
        reviewed_at=now,result="reviewed",reason="Parti açıklaması ve ilgili tutanak pasajları ayrı okundu."))
    for ref in refs:
        insert("finding_evidence",dict(finding_id=ident,passage_id=pid(ref),role="quotation" if quote else "support"))
        insert("verification",dict(finding_id=ident,passage_id=pid(ref),checked_at=now,result="confirmed",reason=passages[ref]["section"]))
    return ident

statement = f"{case}-statement"
summary = finding("statement-summary", "TİP Hayvan Hakları Komisyonu 13 Temmuz 2024’te Hayvanları Koruma Kanunu değişiklik teklifine karşı çıktı.",
                  ("party-quote", "party-commission"))
quote = finding("statement-quote", passages["party-quote"]["exact"], ("party-quote",), quote=True, pair=summary)
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2024-07-13", date_precision="day",
    version_id=vid("party"), period_basis="TİP’in 13 Temmuz 2024 tarihli özgün yayımı.",
    comparison_row_id="04-03-v3-0304-tip-program-hayvan-haklari-row", uncertainty_reason=bounds)

event = f"{case}-event"
add("practice_event", id=event, common_event_key="tbmm-28-2-112-2-2275-law-7527", event_at="2024-07-30", date_precision="day",
    date_unknown_reason=None, title="7527 sayılı Hayvanları Koruma Kanunu değişikliğinin kabulü",
    scope_context="28. Dönem 2. Yasama Yılı 112. birleşim, 2/2275 ve 160 sıra sayılı teklif.",
    occurrence_basis="TBMM Genel Kurul tutanağı, kesin açık oy cetveli ve kanun sicili.")
points = {
    "proposal-number": ("initiative", "12 Temmuz’da Başkanlığa gelen teklif 2/2275."),
    "proposal-day": ("initiative", "Teklifin Başkanlığa geliş günü 12 Temmuz 2024."),
    "floor-count": ("action", "Başkanlık 500 oy, 275 kabul, 224 ret ve 1 çekimser açıkladı."),
    "floor-adopt": ("result", "Başkanlık teklifin kanunlaştığını açıkladı."),
    "roll-time": ("action", "29 Temmuz’da açılan birleşimde kesin cetvelin oylama saati 03.46."),
    "roll-count": ("result", "Kesin cetvelde 273 kabul, 224 ret, 1 çekimser ve toplam 500."),
    "roll-duplicates": ("result", "Kesin cetvel 2 mükerrer oy kaydetti."),
    "roll-bas": ("result", "Kesin cetvelde Erkan Baş’ın oyu ret."),
    "roll-kadigil": ("result", "Kesin cetvelde Saliha Sera Kadıgil’in oyu ret."),
    "roll-sik": ("result", "Kesin cetvelde Ahmet Şık’ın oyu ret."),
    "correction": ("action", "Aydoğdu 15 Ağustos kaydında oy kullanamadığını bildirdi ve kabul niyetinin kaydını istedi."),
    "adopt-day": ("result", "TBMM sicili kabul gününü 30 Temmuz 2024 olarak veriyor."),
    "gazette-day": ("result", "2 Ağustos 2024 Resmî Gazete yayımı TBMM sicilinde."),
    "gazette-number": ("result", "Resmî Gazete sayısı 32620."),
}
for key, (stage, claim) in points.items():
    add("practice_event_evidence", event_id=event, passage_id=pid(key), stage=stage, supported_point=claim,
        concrete_basis=passages[key]["section"], limitation=bounds, epistemic_type="claim")
    add("practice_evidence_assessment", event_id=event, passage_id=pid(key), stage=stage, basis_kind="document")
result = finding("result", "TBMM 2/2275’i 30 Temmuz’da kabul etti. Erkan Baş, Saliha Sera Kadıgil ve Ahmet Şık kesin cetvelde ret oyu verdi. 7527, 2 Ağustos 2024’te yayımlandı.",
                 ("floor-adopt", "adopt-day", "roll-bas", "roll-kadigil", "roll-sik", "gazette-day", "gazette-number"))
explanation = finding("comparison", "TİP Hayvan Hakları Komisyonunun itirazı ile üç milletvekilinin kişisel ret oyu ayrı kayıtlarda. Kürsü 275 kabul, 224 ret ve 1 çekimser açıkladı. Kesin cetvel 273 kabul, 224 ret, 1 çekimser ve 2 mükerrer gösteriyor. Aydoğdu’nun 15 Ağustos beyanı ayrı. Yerel uygulama sonuçları açık.",
                      ("party-quote", "party-commission", "floor-count", "roll-count", "roll-duplicates",
                       "roll-bas", "roll-kadigil", "roll-sik", "correction"))
relation = f"{case}-relation"
add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes["event"], statement_id=statement,
    event_id=event, target_finding_id=summary, result_finding_id=result, explanation_finding_id=explanation,
    comparability_reason="13 Temmuz açıklaması ve 7527 kabulü aynı Hayvanları Koruma Kanunu değişikliği dosyasına ilişkin.",
    temporal_context="12 Temmuz teklif, 13 Temmuz açıklama, 30 Temmuz kabul, 2 Ağustos yayım, 15 Ağustos düzeltme talebi.",
    authority_context="TİP komisyonu açıklama yayımladı. Genel Kurul karar aldı. Üç ret oyu kişisel.", uncertainty_reason=bounds)
add("practice_candidate", id=f"{case}-candidate", scope_id=scopes["event"], event_id=event, relation_id=relation, state="eligible",
    reason="2/2275, TİP’in tarihli itirazı ve kişisel oyların resmi cetveliyle karşılaştırılabiliyor.",
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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için ilgili parti metni ve 7527 kaynak pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-law-7527-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_LAW_7527_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
