"""Build the two TİP 2023 Atalay comparisons from their source records."""

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
source_dir = checks / "tip-publication-catalog" / "party-statements-06"
source_root = working / "sources" / "tip"
case = "0405-tip-atalay-2023"
party = "tip"
topic = "yargi-bagimsizligi"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


pair = (working / "04-tip.json", working / "04-tip-review.json")
expected_base = (
    "3b8ebcc9b594565ecf758a4480cdfe208fa66be0b519197b7365f1b0c413ec17",
    "26b3459223c698b77fb7434a9533f7db97be4e5156cda2adadd5da92b6cee9ed",
)
if preflight and sha(pair[0].read_bytes()) != expected_base[0]:
    pair = (checks / "tip-law-7527-draft.json", checks / "tip-law-7527-review-draft.json")
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [26, 25, 0]


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


receipt = read(source_dir / "reading.json")
source_rows = {row["path"]: row for row in receipt["linked_material"]}
source_rows.update({row["path"]: row for row in read(source_dir / "capture.json")})
yargitay = read(source_dir / "yargitay-20231108-reading.json")
source_rows[yargitay["path"]] = yargitay
sources = {}
for key, name, day, title, kind, publisher, author, published, basis in (
    ("walk-statement", "047.html.bin", "2023-09-20", "20 Eylül TİP açıklaması",
     "party_publication", "Türkiye İşçi Partisi", None, "2023-09-20", "TİP’in tarihli özgün yayımındaki yürüyüş çağrısı."),
    ("court-statement", "042.html.bin", "2023-11-07", "7 Kasım TİP açıklaması",
     "party_publication", "Türkiye İşçi Partisi", None, "2023-11-07", "TİP’in tarihli özgün yayımındaki AYM kararının uygulanması çağrısı."),
    ("walk-start", "artigercek-start.html.bin", "2023-10-01", "Özgürlük Yürüyüşü’nün Hatay başlangıcı",
     "journalism", "Artı Gerçek", None, "2023-10-01", "Yerinde 1 Ekim haberi. 2 Ekim 2023 güncellemesi gösteriliyor."),
    ("walk-progress", "anka-27.html.bin", "2023-10-27", "Özgürlük Yürüyüşü’nün 27. günü",
     "journalism", "ANKA Haber Ajansı", None, "2023-10-27", "Haberde ANKA mahreci, özgün yayım tarihi ve 3 Haziran 2026 güncellemesi yer alıyor."),
    ("walk-end", "anka-28-syndication.html.bin", "2023-10-28", "Anıtpark’taki bitiş mitingi",
     "journalism", "Haberler.com", "ANKA", "2023-10-28", "Yayın sayfasında kaynak ANKA. 28 Ekim 2023 tarihli etkinlik anlatımı."),
    ("aym-first", "aym-cilt-2023-2.pdf", "2023-10-25", "AYM 2023/53898 kararı",
     "official", "Anayasa Mahkemesi", None, None, "AYM Kararlar Dergisindeki 2023/53898 hükmü. Cildin yayım günü incelenen sayfalarda yok."),
    ("yargitay", "20231108-yargitay.pdf", "2023-11-08", "Yargıtay 3. Ceza Dairesi 8 Kasım kararı",
     "official", "Yargıtay 3. Ceza Dairesi", None, None, "Habertürk’ün yayımladığı mahkeme kararı PDF nüshası. Esas, gün ve hüküm AYM 2024/65 ile karşılaştırıldı."),
    ("aym-norm", "aym-2024-65.pdf", "2024-02-22", "AYM 2024/65 kararındaki işlemler",
     "official", "Anayasa Mahkemesi", None, None, "AYM’nin ayrı norm kararındaki §15–20 kronolojisi."),
):
    row = source_rows[name]
    path = source_dir / name
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
        document_date=day, date_precision="day", date_unknown_reason=None, version_label=title,
        accessed_at=row["retrieved_at_utc"], verified_at=now, mime="application/pdf" if media == "pdf" else "text/html",
        sha256=row["sha256"], original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=vid(key), kind=kind, publisher=publisher, author=author,
        social_handle=None, published_at=published, date_precision="day" if published else "unknown", public_url=url, basis=basis))
    if media == "html":
        view = build_view(raw, url, source_root, fetch_assets=False)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=vid(key)))
    sources[key] = (path, url)

passages = {}
for key, source, page, printed, exact, label in (
    ("walk-call", "walk-statement", None, None, "Ankara’ya büyük bir özgürlük yürüyüşü düzenleyeceğiz.", "20 Eylül tarihli parti çağrısı"),
    ("court-call", "court-statement", None, None, "Anayasa Mahkemesi kararını derhal uygulayarak tahliye kararı vermeleridir.", "7 Kasım tarihli parti talebi"),
    ("start", "walk-start", None, None, "Hatay Meclis Binası önünde başlanan yürüyüşe", "1 Ekim yerinde haber pasajı"),
    ("progress", "walk-progress", None, None, "27. gününde devam ediyor", "27 Ekim tarihinde yürüyüşün sürmesi"),
    ("finish", "walk-end", None, None, "yürüyüşün son durağında Ankara Anıtpark", "28 Ekim bitiş mitinginin ANKA aktarımı"),
    ("aym-rule", "aym-first", 850, "1602", "sağlanması ve yeniden yapılacak yargılamada durma kararı verilmesi", "AYM 2023/53898 hüküm D"),
    ("aym-to-court", "aym-first", 850, "1602", "Mahkemesine (E.2021/178) GÖNDERİLMESİNE,", "AYM karar örneğinin ilk derece mahkemesine gönderilmesi"),
    ("yargitay-docket", "yargitay", 0, None, "Esas No : 2023/12611", "Yargıtay karar nüshasının esas numarası"),
    ("yargitay-ruling", "yargitay", 21, None, "Anayasa Mahkemesi'nin anılan kararına UYULMAMASINA,", "8 Kasım kararının birinci hüküm bendi"),
    ("yargitay-parliament", "yargitay", 22, None, "örneğinin TBMM Başkanlığı'na GÖNDERİLMESİNE,", "Yargıtay kararında TBMM’ye gönderme hükmü"),
    ("yargitay-day", "yargitay", 22, None, "08.11.2023 tarihinde oy birliği ile karar verildi.", "Yargıtay kararının tarihi ve oy birliği"),
    ("aym-nov", "aym-norm", 3, "4", "ilk derece mahkemesinin başkanı 30/10/2023", "AYM norm kararında 30 Ekim müzekkeresi ve sonraki işlemler"),
    ("aym-nov-referral", "aym-norm", 3, "4", "dosyanın kendisine iade edildiği 1/11/2023", "AYM norm kararında 1 Kasım ek kararı"),
    ("aym-dec", "aym-norm", 4, "5", "2023/99744, 21/12/2023)", "AYM norm kararında 21 Aralık bireysel başvurusu"),
    ("aym-jan", "aym-norm", 4, "5", "Daire 3/1/2024 tarihinde", "AYM norm kararında 3 Ocak 2024 Yargıtay işlemi"),
    ("aym-parliament", "aym-norm", 4, "5", "tarihli 54. Birleşiminde Dairenin 3/1/2024 tarihli", "AYM norm kararında 30 Ocak 2024 TBMM işlemi"),
):
    path = sources[source][0]
    original = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in original, (key, exact)
    passage = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None, article=None,
        section=label, pdf_page_index=page, printed_page=printed)
    insert("passage", passage)
    passages[key] = passage

scopes = {}
for row in read(working / "04-inventory.json")["cells"]:
    if (row["party_id"], row["topic_id"]) != (party, topic):
        continue
    scope = row["cell_id"]
    scopes[row["research_kind"]] = scope
    if not any(existing["id"] == scope for existing in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope, **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="Atalay dosyasına ilişkin 2023 tarihli parti çağrıları, yürüyüş ve yargı kararları dar kapsamda okundu.")
assert set(scopes) == {"statement", "event"}
for key, (_, url) in sources.items():
    lane = "statement" if key in {"walk-statement", "court-statement"} else "event"
    scope = scopes[lane]
    version = vid(key)
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    attempt = f"{version}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now, inspected_sections=json.dumps(sections, ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="TİP çağrısı, yerinde haber ve yargı kararının ilgili pasajı okundu.", source_version_id=version)
    add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
        relevance_reason="Atalay dosyasındaki yürüyüş veya 8 Kasım yargı kararıyla ilişkili kaynak.",
        state="examined", attempt_ids=json.dumps([attempt]))

limitations = ("1–28 Ekim yürüyüşü, 25 Ekim AYM hükmü, 8 Kasım Yargıtay kararı ve 21 Aralık AYM kararı ayrı işlemler. "
               "Eylemin yargı kararlarına nedensel etkisi, 8 Kasım nüshasının elektronik imza durumu ve fiilî tahliye bu kayıtlarda doğrulanmadı.")


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

def add_case(key, source_day, occurrence_day, title, common_key, context, occurrence_basis,
             summary, outcome, comparison, authority, timeline, points, extra_refs=()):
    call = f"{key}-call"
    summary_id = finding(f"{key}-summary", summary, (call,))
    quote = finding(f"{key}-quote", passages[call]["exact"], (call,), quote=True, pair=summary_id)
    statement = f"{case}-{key}-statement"
    add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
        summary_finding_id=summary_id, quote_finding_id=quote, statement_at=source_day, date_precision="day",
        version_id=vid(f"{key}-statement"), period_basis="TİP’in tarihli özgün parti yayımı.",
        comparison_row_id="04-03-v3-0304-tip-program-adalet-row", uncertainty_reason=limitations)
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
    add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes["event"], statement_id=statement,
        event_id=event, target_finding_id=summary_id, result_finding_id=result, explanation_finding_id=explanation,
        comparability_reason=context, temporal_context=timeline, authority_context=authority, uncertainty_reason=limitations)
    add("practice_candidate", id=f"{case}-{key}-candidate", scope_id=scopes["event"], event_id=event, relation_id=relation,
        state="eligible", reason=context, passage_ids=json.dumps([pid(ref) for ref in refs]))


add_case(
    "walk", "2023-09-20", "2023-10-01", "2023 Hatay–Ankara Özgürlük Yürüyüşü",
    "hatay-ankara-2023-10-01-28-ozgurluk-yuruyusu",
    "20 Eylül TİP çağrısı ile 1–28 Ekim arasında Hatay’dan Ankara’ya uzanan aynı yürüyüş.",
    "1 Ekim Artı Gerçek yerinde haberi, 27 Ekim ANKA haberi ve 28 Ekim mitingine ilişkin ANKA yayımı.",
    "TİP 20 Eylül 2023’te Can Atalay ve Hatay halkı için Ankara’ya özgürlük yürüyüşü düzenleyeceğini açıkladı.",
    "Artı Gerçek 1 Ekim’de Hatay başlangıcını, ANKA 27 Ekim’de yürüyüşün sürdüğünü ve 28 Ekim’de Anıtpark’taki bitiş mitingini kaydetti.",
    "TİP’in duyurduğu yürüyüş 1 Ekim’de Hatay’da başladı ve 28 Ekim’de Ankara Anıtpark’taki mitingle tamamlandı. AYM’nin 25 Ekim kararı ayrı bir yargı işlemi. Yürüyüşün karara etkisi açık.",
    "Yürüyüş parti eylemi. Yürüyüşü ve mitingi haber kuruluşları yer ve tarihle aktardı. AYM kararını kendisi verdi.",
    "20 Eylül çağrı, 1 Ekim Hatay başlangıcı, 25 Ekim AYM hükmü, 27 Ekim yürüyüşün sürmesi ve 28 Ekim Ankara bitişi.",
    (("start", "action", "Artı Gerçek, yürüyüşün 1 Ekim’de Hatay Meclis Binası önünde başladığını aktardı.", "observation"),
     ("progress", "action", "ANKA 27 Ekim’de yürüyüşün 27. gününde sürdüğünü bildirdi.", "observation"),
     ("finish", "result", "ANKA kaynaklı 28 Ekim yayımı, TİP’in yürüyüşün son durağı Ankara Anıtpark’ta miting düzenlediğini aktardı.", "observation")),
    ("aym-rule",),
)
add_case(
    "court", "2023-11-07", "2023-11-08", "Yargıtay 3. Ceza Dairesinin 8 Kasım 2023 kararı",
    "yargitay-3cd-2023-11-08-e2023-12611-atalay",
    "TİP’in 7 Kasım çağrısı ile Yargıtay’ın 8 Kasım işlemi AYM’nin 2023/53898 sayılı aynı kararına ilişkin.",
    "Yargıtay 3. Ceza Dairesinin Habertürk’te yayımlanan nüshası ve AYM 2024/65 kararının kronolojisi.",
    "TİP 7 Kasım 2023’te 25 Ekim AYM kararının uygulanması ve Can Atalay’ın tahliyesi çağrısını yineledi.",
    "Yargıtay 3. Ceza Dairesi 8 Kasım’da AYM’nin 2023/53898 sayılı kararına uyulmamasına ve karar örneğinin TBMM’ye gönderilmesine karar verdi.",
    "AYM 25 Ekim’de tahliyenin sağlanması dahil işlemler için karar örneğinin ilk derece mahkemesine gönderilmesine hükmetti. 7 Kasım’da TİP uygulanmasını istedi. Yargıtay 8 Kasım’da uyulmamasına karar verdi. 21 Aralık kararı ayrı bireysel başvuruya ait. 3 Ocak 2024 kararı ve 30 Ocak TBMM işlemi bu 8 Kasım hükmünden ayrı.",
    "TİP çağrı yayımladı. AYM ve Yargıtay kendi yargı işlemlerini yaptı. TBMM’ye gönderme hükmü 8 Kasım kararının parçası.",
    "25 Ekim AYM kararı, 30 Ekim müzekkeresi, 1 Kasım yerel ek karar, 7 Kasım parti çağrısı, 8 Kasım Yargıtay kararı ve 21 Aralık ikinci AYM kararı.",
    (("yargitay-docket", "action", "Yayımlanmış dosyada esas numarası 2023/12611. Değişik iş numarası alanı 2023/ olarak görünüyor.", "document"),
     ("yargitay-ruling", "result", "İlk hüküm bendinde AYM kararına uyulmaması yazıyor.", "document"),
     ("yargitay-parliament", "result", "Ayrı hüküm bendi karar örneğinin TBMM Başkanlığına gönderilmesini öngörüyor.", "document"),
     ("yargitay-day", "result", "Karar tarihi 8 Kasım 2023 ve karar oy birliğiyle alındı.", "document")),
    ("aym-rule", "aym-to-court", "aym-nov", "aym-nov-referral", "aym-dec", "aym-jan", "aym-parliament"),
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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün parti metni, yerinde haber veya mahkeme pasajı okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-atalay-2023-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_ATALAY_2023_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
