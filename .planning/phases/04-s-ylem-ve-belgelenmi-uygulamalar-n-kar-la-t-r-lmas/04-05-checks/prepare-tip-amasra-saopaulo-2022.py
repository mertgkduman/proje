"""Build TİP’s Amasra and São Paulo initiative, action and decision comparisons."""

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
source_dir = checks / "tip-publication-catalog" / "party-statements-12"
source_root = working / "sources" / "tip"
case = "0405-tip-amasra-saopaulo-2022"
party = "tip"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight-draft"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


pair = (checks / "tip-halic-cemevi-2022-draft.json", checks / "tip-halic-cemevi-2022-review-draft.json") if preflight else (
    working / "04-tip.json", working / "04-tip-review.json")
expected_base = (
    "2aa9e8ff83b996341bc8e7ae4ed4bfd61f53969d84470e342536f2cf1d8766dc",
    "ae9732dae11c885a82160a0d0aebdafd7ceaf1fecd3beddb4aca8a34aaf700ea",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [37, 35, 0]


def insert(kind, row):
    entries.append({"kind": kind, "values": row})


def add(table, **row):
    records[table].append(row)


def vid(suffix):
    return f"{case}-{suffix}-v1"


def pid(suffix):
    return f"{case}-{suffix}-p"


def store(relative, content):
    destination = source_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        assert destination.read_bytes() == content, destination
    else:
        destination.write_bytes(content)


later_dir = source_dir.with_name("party-statements-13")
supplement = later_dir / "linked-institutions"
source_rows = {}
for directory, name, linked in (
    (source_dir, "capture.json", False), (source_dir, "reading.json", True),
    (later_dir, "capture.json", False), (supplement, "reading.json", True),
):
    receipt = read(directory / name)
    for row in receipt["linked_material"] if linked else receipt:
        source_rows[row["path"]] = (directory / row["path"], row)

sources = {}
for key, name, day, title, kind, publisher, author, basis in (
    ("mine-statement", "091.html.bin", "2022-10-14", "14 Ekim TİP Amasra ve soruşturma açıklaması",
     "party_publication", "Türkiye İşçi Partisi", None, "Olay günü yayımlanan TİP açıklaması. Sayılar yayım anına atfedildi."),
    ("mine-registry", "amasra-commission-registry.html.bin", "2022-10-19", "TBMM Amasra Araştırma Komisyonu sicili",
     "official", "TBMM", None, "Komisyonun kuruluş tarihini, 9. birleşimi, 1344 kararını ve sekiz önergeyi gösteren sicil."),
    ("mine-gazette", "amasra-1344-gazette-index.html.bin", "2022-10-22", "31991 sayılı Resmî Gazete fihristi",
     "official", "Resmî Gazete", None, "22 Ekim tarihli gazete fihristinde 1344 Amasra araştırma komisyonu kararı."),
    ("ship-statement", "101.html.bin", "2022-07-28", "TİP’in São Paulo gemisinin getirilmesine ilişkin açıklaması",
     "party_publication", "Türkiye İşçi Partisi", None, "TİP Kent ve Ekoloji Bürosu ile Emek Bürosunun 28 Temmuz yayımı."),
    ("ship-aa", "naesao-2670217.html.bin", "2022-08-26", "Bakanın São Paulo iptal açıklaması",
     "journalism", "Anadolu Ajansı", "Burcu Çalık Göçümlü", "26 Ağustos haberinde Bakan Murat Kurum’un açıklaması. Güncelleme 27 Ağustos."),
    ("ship-reply", "naesao-856c24c0.pdf", "2022-09-29", "São Paulo hakkında 7/69915 sayılı önergenin Bakanlık cevabı",
     "official", "Çevre, Şehircilik ve İklim Değişikliği Bakanlığı", None, "Murat Kurum imzalı üst yazı ve soru-cevap eki."),
):
    path, row = source_rows[name]
    raw = path.read_bytes()
    assert sha(raw) == row["sha256"]
    media = "pdf" if path.suffix == ".pdf" else "html"
    folder = Path("objects") / row["sha256"]
    original = folder / ("original.pdf" if media == "pdf" else "original.html.bin")
    readable = folder / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, media))
    url = row["final_url"]
    document = f"{case}-{key}"
    source_kind = "party" if kind == "party_publication" else kind
    insert("document", dict(id=document, party_id=party, title=title, source_kind=source_kind))
    insert("document_version", dict(id=vid(key), document_id=document, original_url=row["url"], final_url=url,
        document_date=day, date_precision="day", date_unknown_reason=None,
        version_label=title, accessed_at=row["retrieved_at_utc"], verified_at=now,
        mime="application/pdf" if media == "pdf" else "text/html", sha256=row["sha256"],
        original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=vid(key), kind=kind, publisher=publisher, author=author,
        social_handle=None, published_at=None if key == "mine-registry" else day,
        date_precision="unknown" if key == "mine-registry" else "day", public_url=url, basis=basis))
    if media == "html":
        content_type = row.get("content_type", "")
        charset = content_type.split("charset=", 1)[1] if "charset=" in content_type else None
        view = build_view(raw, url, source_root, fetch_assets=False, http_charset=charset)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=vid(key)))
    sources[key] = path, url

source_versions = {key: vid(key) for key in sources}
passages = {}
for key, source, page, exact, label in (
    ("mine-call", "mine-statement", None, "sorumlular hakkında derhal soruşturma başlatılmalıdır.",
     "TİP’in 14 Ekim Amasra soruşturma çağrısı"),
    ("mine-approved", "mine-registry", None, "19/10/2022",
     "TBMM komisyon sicilinde kuruluş tarihi ve 9. birleşim"),
    ("mine-commission", "mine-registry", None, "1344",
     "TBMM komisyon sicilinde 1344 kuruluş kararı"),
    ("mine-published", "mine-gazette", None, "22 Ekim 2022 Tarihli ve 31991 Sayılı",
     "22 Ekim 31991 sayılı Resmî Gazete fihristi"),
    ("mine-title", "mine-gazette", None, "1344&nbsp;&nbsp;&nbsp;&nbsp; Bartın’ın Amasra",
     "Fihristte 1344 Amasra Meclis Araştırması Komisyonu kararı"),
    ("ship-call", "ship-statement", None, "NAe São Paulo Gemisi’nin ülkemize gelişi bir an önce durdurulmalıdır.",
     "28 Temmuz parti çağrısı"),
    ("ship-announce", "ship-aa", None, "26 Ağustos 2022", "Bakanın iptali bildirdiği 26 Ağustos tarihli haber"),
    ("ship-announced-cancel", "ship-aa", None, "şartlı notifikasyon onayının iptal edilmesine karar verilmiştir.",
     "Anadolu Ajansının bakan açıklamasından aktardığı iptal"),
    ("ship-init", "ship-reply", 2, "başvurusuna 30.05.2022 tarihinde", "Bakanlık cevabında 30 Mayıs şartlı başvuru onayı"),
    ("ship-cancel", "ship-reply", 2, "onayının iptal edilmesine karar\nverilmiştir.",
     "Bakanlık cevabında şartlı notifikasyon onayının iptali"),
    ("ship-boundary", "ship-reply", 2, "geminin Türk karasularına girmesine izin verilmeyecektir.",
     "Bakanlığın girişe izin verilmeyeceğine ilişkin ifadesi"),
):
    path = sources[source][0]
    original = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in original, (key, exact)
    passage = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None, article=None,
        section=label, pdf_page_index=page, printed_page=None)
    insert("passage", passage)
    passages[key] = passage

scopes = {}
topics = {"madencilik", "is-sagligi"}
for row in read(working / "04-inventory.json")["cells"]:
    topic = row["topic_id"]
    if row["party_id"] != party or topic not in topics:
        continue
    scope = row["cell_id"]
    scopes[topic, row["research_kind"]] = scope
    if not any(existing["id"] == scope for existing in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope, **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="Madencilik araştırma komisyonu veya gemi sökümüne ilişkin iş sağlığı dayanakları.")
assert len(scopes) == 4
for key, (_, url) in sources.items():
    topic = "madencilik" if key.startswith("mine-") else "is-sagligi"
    lane = "statement" if key.endswith("-statement") else "event"
    scope = scopes[topic, lane]
    version = source_versions[key]
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    if not any(row["scope_id"] == scope and row["version_id"] == version for row in records["practice_scope_source"]):
        add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
            inspected_sections=json.dumps(sections, ensure_ascii=False))
    attempt = f"{case}-{key}-reading"
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="Tarih, parti veya kurum sıfatı ve işlem aşaması ilgili pasajlarda okundu.", source_version_id=version)
    if not any(row["scope_id"] == scope and row["url"] == url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
            relevance_reason="2022 Amasra Meclis araştırması veya São Paulo gemisi işlemi için tarihli kaynak.",
            state="examined", attempt_ids=json.dumps([attempt]))

limitations = ("Amasra Meclis araştırması ve kişisel ceza sorumluluğu farklı süreçlerdir. São Paulo şartlı onayının iptali, "
               "geminin konumu ve atık miktarlarına ilişkin iddialardan ayrı.")

def finding(suffix, content, refs, *, quote=False, pair=None):
    ident = f"{case}-{suffix}"
    insert("finding", dict(id=ident, party_id=party, heading="Belgelenmiş uygulamalar", pair_id=pair or ident,
        text=content, provenance="quote" if quote else "summary", epistemic_type="claim"))
    insert("review", dict(id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        result="reviewed", reason="İddianın dayandığı tarihli özgün pasajlar okundu."))
    for ref in refs:
        insert("finding_evidence", dict(finding_id=ident, passage_id=pid(ref), role="quotation" if quote else "support"))
        insert("verification", dict(finding_id=ident, passage_id=pid(ref), checked_at=now, result="confirmed", reason=passages[ref]["section"]))
    return ident


event_claims = {}

def add_case(key, topic, comparison_row, source_day, occurrence_day, title, common_key, context, occurrence_basis,
             summary, outcome, comparison, authority, timeline, points, extra_refs=()):
    call = f"{key}-call"
    summary_id = finding(f"{key}-summary", summary, (call,))
    quote = finding(f"{key}-quote", passages[call]["exact"], (call,), quote=True, pair=summary_id)
    statement = f"{case}-{key}-statement"
    add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
        summary_finding_id=summary_id, quote_finding_id=quote, statement_at=source_day, date_precision="day",
        version_id=vid(f"{key}-statement"), period_basis="TİP’in tarihli özgün parti yayımı.",
        comparison_row_id=comparison_row, uncertainty_reason=limitations)
    event = f"{case}-{key}-event"
    add("practice_event", id=event, common_event_key=common_key, event_at=occurrence_day, date_precision="day",
        date_unknown_reason=None, title=title, scope_context=context, occurrence_basis=occurrence_basis)
    for ref, stage, point, basis in points:
        add("practice_event_evidence", event_id=event, passage_id=pid(ref), stage=stage, supported_point=point,
            concrete_basis=passages[ref]["section"], limitation=limitations, epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=pid(ref), stage=stage, basis_kind=basis)
        event_claims[pid(ref)] = point
    refs = tuple(point[0] for point in points)
    result = finding(f"{key}-result", outcome, refs)
    explanation = finding(f"{key}-comparison", comparison, (call, *refs, *extra_refs))
    relation = f"{case}-{key}-relation"
    add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes[topic,"event"], statement_id=statement,
        event_id=event, target_finding_id=summary_id, result_finding_id=result, explanation_finding_id=explanation,
        comparability_reason=context, temporal_context=timeline, authority_context=authority, uncertainty_reason=limitations)
    add("practice_candidate", id=f"{case}-{key}-candidate", scope_id=scopes[topic,"event"], event_id=event, relation_id=relation,
        state="eligible", reason=context, passage_ids=json.dumps([pid(ref) for ref in refs]))


add_case(
    "mine", "madencilik", "04-03-v3-0304-tip-program-context-madencilik-row", "2022-10-14", "2022-10-19",
    "Amasra maden faciası için 1344 sayılı TBMM araştırma kararı", "tbmm-2022-10-19-amasra-karar-1344",
    "14 Ekim TİP soruşturma çağrısı ve 19 Ekim Genel Kurulun aynı Amasra olayıyla ilgili araştırma kararı.",
    "TBMM komisyon sicili ve 22 Ekim Resmî Gazete fihristindeki 1344 sayılı karar.",
    "TİP’in 14 Ekim açıklaması Amasra maden faciasında sorumlular hakkında soruşturma başlatılması çağrısı yaptı.",
    "TBMM, 19 Ekim’de sekiz önerge üzerine Meclis araştırması açılmasına ve komisyon kurulmasına karar verdi. 1344 sayılı karar 22 Ekim’de yayımlandı.",
    "14 Ekim TİP çağrısı ve TBMM’nin 19 Ekim kararı aynı Amasra olayına ilişkin. Komisyonun görevi olayın nedenlerini ve önleyici tedbirleri araştırmaktı. TİP’in istediği bireysel sorumluluk soruşturması ve yargı sonucu ayrı kaynaklarda izleniyor.",
    "TİP kamuya çağrı yaptı. Meclis araştırmasının açılması Genel Kurula, kişisel adli süreçler yetkili yargı makamlarına ait.",
    "14 Ekim TİP açıklaması, 19 Ekim Genel Kurul kararı ve 22 Ekim Resmî Gazete yayımı. S. Sayısı 440 raporunun kapağı Mart 2023.",
    (("mine-approved", "action", "19 Ekim 2022 Genel Kurul işlem tarihi.", "document"),
     ("mine-commission", "result", "Amasra araştırma komisyonu kuruldu.", "document"),
     ("mine-published", "result", "22 Ekim Resmî Gazete fihristi ve sayı numarası.", "document"),
     ("mine-title", "result", "1344 Amasra komisyonu kararı gazete fihristinde yer alıyor.", "document")),
)
add_case(
    "ship", "is-sagligi", "04-03-v3-0304-tip-program-issagligi-baglam-row", "2022-07-28", "2022-08-26",
    "NAe São Paulo gemisinin şartlı notifikasyon onayının iptalinin açıklanması", "nae-saopaulo-2022-08-26-notifikasyon-iptali",
    "TİP’in 28 Temmuz geminin gelişini durdurma çağrısı ve 26 Ağustos iptal açıklaması.",
    "26 Ağustos Anadolu Ajansı haberi ve Bakanlığın 7/69915 sayılı önergeye imzalı cevabı.",
    "TİP’in Kent ve Ekoloji ile Emek büroları 28 Temmuz’da São Paulo gemisinin Türkiye’ye getirilmesinin durdurulmasını istedi.",
    "Bakan Murat Kurum 26 Ağustos’ta şartlı onayın iptal edildiğini ve geminin Türk karasularına girişine izin verilmeyeceğini açıkladı.",
    "28 Temmuz TİP çağrısını 26 Ağustos iptal açıklaması izledi. Bakanlık imzalı cevabında önceki şartlı onayı, istenen belgeleri ve iptali anlattı. Asbest miktarı ve geminin daha sonraki Brezilya süreci ayrı belgeler gerektiriyor.",
    "TİP büroları çağrı yaptı. Şartlı onay ve iptal Çevre, Şehircilik ve İklim Değişikliği Bakanlığı yetkisinde.",
    "30 Mayıs şartlı onay, 28 Temmuz TİP çağrısı, 9 Ağustos belge isteği, 26 Ağustos iptal açıklaması, 29 Eylül imzalı cevap.",
    (("ship-init", "initiative", "30 Mayıs tarihli şartlı ön işlem.", "document"),
     ("ship-announce", "action", "26 Ağustos tarihli bakan açıklaması.", "independent_report"),
     ("ship-announced-cancel", "action", "Bakanın bildirdiği şartlı onay iptali.", "independent_report"),
     ("ship-cancel", "result", "Bakanlık cevabında onayın iptal edildiği belirtiliyor.", "document"),
     ("ship-boundary", "result", "Bakanlık cevabında girişe izin verilmeyeceği belirtiliyor.", "document")),
)

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
claims.update(event_claims)
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
        supported_claim=" ".join(claims[ref] for ref in sorted(refs)), limitations=limitations,
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün parti metni, kurum belgesi veya tarihli basın haberi okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-amasra-saopaulo-2022-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_AMASRA_SAOPAULO_2022_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
