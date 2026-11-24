"""Build TİP’s 2023 earthquake reconstruction and higher education comparisons."""

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
source_dir = checks / "tip-publication-catalog" / "party-statements-09"
source_root = working / "sources" / "tip"
case = "0405-tip-earthquake-2023"
party = "tip"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


pair = (working / "04-tip.json", working / "04-tip-review.json")
expected_base = (
    "50f9d38beb9f8dadc14b4197eff3dc2b4b37cfdd432a3b12e19b1ed28432e9e5",
    "5f0ad90f062fc061bcfdb98235b0faceed62e2b32cd4ba0ab1096657e1f4aa3a",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [33, 31, 0]


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
sources = {}
for key, name, day, title, kind, publisher, author, published, basis in (
    ("housing-statement", "067.html.bin", "2023-03-09", "9 Mart TİP afet sonrası yeniden inşa açıklaması", "party_publication",
     "Türkiye İşçi Partisi", None, "2023-03-09", "TİP Bilim Kurulu ve Kent ve Yerel Yönetimler Çalışma Grubu imzalı tarihli açıklama."),
    ("housing-docket", "tbmm-126-docket.html.bin", "2023-02-24", "TBMM 1/292 sicili", "official",
     "TBMM", None, None, "126 sayılı kararnamenin Meclise sunulması ve 7452 bağlantısı."),
    ("housing-floor", "tbmm-7452-floor.html.bin", "2023-04-05", "5 Nisan TBMM 85. birleşim tam tutanağı", "official",
     "TBMM", None, None, "1/292 görüşmesi ve kabul duyurusu."),
    ("housing-registry", "tbmm-7452-registry.html.bin", "2023-04-05", "TBMM 7452 sicili", "official",
     "TBMM", None, None, "5 Nisan kabulü, 10 Nisan ve 32159 sayılı Resmî Gazete."),
    ("housing-law", "tbmm-7452-law.html.bin", "2023-04-05", "7452 sayılı kanun", "official",
     "TBMM", None, None, "Madde 2 fıkra 4, seçili alanlarda askı, ilan ve itiraz istisnası."),
    ("education-statement", "070.html.bin", "2023-02-14", "14 Şubat TİP Bilim Kurulu öğretim açıklaması", "party_publication",
     "Türkiye İşçi Partisi", None, "2023-02-14", "Özgün parti sayfasında Bilim Kurulunun yüz yüze eğitim çağrısı."),
    ("education-yok", "yok-march.pdf", "2023-03-31", "31 Mart YÖK yazısı ve yükseköğretim kararları", "official",
     "Yükseköğretim Kurulu", None, None, "TBMM 7/193 soru cevabı ekindeki 31 Mart tarihli 23957 sayılı YÖK yazısı."),
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

source_versions = {key: vid(key) for key in sources}
passages = {}
for key, source, page, printed, exact, label in (
    ("housing-call", "housing-statement", None, None,
     "Plan ve parselasyon işlemlerinde askı, ilan, itirazlara ilişkin hükümler uygulanmayacak,",
     "9 Mart TİP açıklamasında 126 sayılı kararnameye itirazın dayanağı"),
    ("housing-docket-no", "housing-docket", None, None, "1 / 292", "TBMM 1/292 dosya numarası"),
    ("housing-docket-day", "housing-docket", None, None, "24/02/2023", "1/292 Başkanlığa geliş günü"),
    ("housing-adopted", "housing-floor", None, None, "Cumhurbaşkanlığı Kararnamesi kabul edilmiş ve kanunlaşmıştır.",
     "85. birleşimde başkanın 1/292 kabul duyurusu"),
    ("housing-adoption", "housing-registry", None, None, "05/04/2023", "7452’nin kabul günü"),
    ("housing-publication", "housing-registry", None, None, "10/04/2023", "7452’nin Resmî Gazete’de yayım günü"),
    ("housing-exception", "housing-law", None, None, "askı, ilan, itirazlara ilişkin hükümleri uygulanmaz.",
     "7452 madde 2 fıkra 4, karar kapsamındaki plan ve parselasyon işlemleri"),
    ("education-call", "education-statement", None, None,
     "Okullar gecikmeli de olsa fiziken açılmalı, öğrencilerin normalleşme ve nitelikli eğitim hakları ellerinden alınmamalıdır.",
     "TİP Bilim Kurulunun fizikî açılış çağrısı"),
    ("education-first", "education-yok", 6, None,
     "Yükseköğretim Kurulu olarak 17 Şubat 2023 tarihinde;",
     "31 Mart yazısında 17 Şubat uzaktan öğretim kararı"),
    ("education-remote", "education-yok", 6, None,
     "öğretimin uzaktan öğretim yöntemi ile yürütülmesine karar", "17 Şubat kararında uzaktan öğretim"),
    ("education-decision", "education-yok", 6, None,
     "30.03.2023 tarihli Yükseköğretim Genel Kurul toplantısında yapılan değerlendirme",
     "YÖK Genel Kurulu yeniden değerlendirme günü"),
    ("education-effective", "education-yok", 6, None, "03.04.2023 tarihi itibarıyla",
     "3 Nisan başlangıcı ve 2022–2023 bahar dönemi"),
    ("education-choice", "education-yok", 6, None,
     "isteyen öğrencilere devam şartı\naranmaksızın sınıflarda yüz yüze eğitim verilebilmesine,", "Devam şartı olmadan yüz yüze seçenek"),
    ("education-university", "education-yok", 6, None,
     "verilebilmesine ilişkin kararları ilgili kurullarında alarak gerekli düzenlemeleri yapmalarına,",
     "Uygulamayı belirleyen üniversite kurulları"),
):
    path = sources[source][0]
    original = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in original, (key, exact)
    passage = dict(id=pid(key), version_id=source_versions[source], exact=exact, prefix=None, suffix=None, article=None,
        section=label, pdf_page_index=page, printed_page=printed)
    insert("passage", passage)
    passages[key] = passage

scopes = {}
topics = {"barinma-konut", "yuksekogretim"}
for row in read(working / "04-inventory.json")["cells"]:
    topic = row["topic_id"]
    if row["party_id"] != party or topic not in topics:
        continue
    scope = row["cell_id"]
    scopes[topic,row["research_kind"]] = scope
    if not any(existing["id"] == scope for existing in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope, **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="2023 afet sonrası yerleşim hükmü veya yükseköğretim biçimi ilgili kaynaklardan okundu.")
assert len(scopes) == 4
for key, (_, url) in sources.items():
    topic = "barinma-konut" if key.startswith("housing-") else "yuksekogretim"
    lane = "statement" if key.endswith("-statement") else "event"
    scope = scopes[topic,lane]
    version = source_versions[key]
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    if not any(row["scope_id"] == scope and row["version_id"] == version for row in records["practice_scope_source"]):
        add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now, inspected_sections=json.dumps(sections, ensure_ascii=False))
    attempt = f"{case}-{key}-reading"
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="Tarih, konu, işlem ve hüküm ilgili kaynak pasajlarından okundu.", source_version_id=version)
    if not any(row["scope_id"] == scope and row["url"] == url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
            relevance_reason="7452 yerleşim hükmü veya 2023 YÖK kararı için tarihli kaynak.", state="examined", attempt_ids=json.dumps([attempt]))

limitations = ("Yasal düzenleme, fiilî imar ve yapım işlemlerinden ayrı. YÖK kararı üniversite kurullarına seçenek tanıyor. "
               "Tek tek kampüslerdeki uygulama, KYK yerleştirmeleri ve parti açıklamalarının etkisi açık.")

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
    "housing", "barinma-konut", "04-03-v3-0304-tip-program-barinma-row", "2023-03-09", "2023-04-05",
    "126 sayılı afet sonrası yapılaşma düzenlemesinin 7452 ile kabulü", "tbmm-27-6-85-1-292-law-7452",
    "9 Mart TİP açıklamasındaki afet sonrası plan ve parselasyon eleştirisi ile 126 sayılı kararnameye ait 1/292 dosyasının 7452 sayılı kanun olarak kabulü.",
    "TBMM’nin 85. birleşim tutanağı ile 1/292 ve 7452 sicilleri, kanunun 2. maddesi.",
    "TİP’in iki çalışma birimi 9 Mart’ta 126 sayılı kararnameye ve seçili yapılaşma alanlarında askı, ilan ve itiraz usullerinin uygulanmamasına karşı çıktı.",
    "TBMM, 5 Nisan’da kararnameyi 7452 olarak kabul etti. 10 Nisan’da yayımlanan 2. maddenin 4. fıkrasında ilgili alanlar için istisna yer aldı.",
    "TİP’in 9 Mart’ta eleştirdiği plan ve parselasyon kuralı 5 Nisan’da kabul edilen 7452 metninde yer aldı. Düzenleme belirli alanlardaki işlemleri kapsıyor. Bu belgeler belirli bir parselde yapılan işlemi veya konut teslimini göstermiyor.",
    "TİP Bilim Kurulu ve çalışma grubu görüş açıkladı. TBMM kanunu kabul etti. Alanda uygulama yetkisi ve fiilî işlem ayrı.",
    "24 Şubat kararname ve Başkanlığa geliş. 9 Mart TİP açıklaması. 5 Nisan TBMM kabulü ve 10 Nisan yayımı.",
    (("housing-docket-no", "initiative", "1/292 kararname dosyası.", "document"),
     ("housing-docket-day", "initiative", "1/292 dosyasının Başkanlığa geliş tarihi 24 Şubat.", "document"),
     ("housing-adopted", "result", "TBMM 85. birleşimde kararnameyi kabul etti.", "document"),
     ("housing-adoption", "result", "7452 kabulü 5 Nisan.", "document"),
     ("housing-publication", "result", "7452 yayımı 10 Nisan.", "document"),
     ("housing-exception", "result", "7452 madde 2 fıkra 4’te askı, ilan ve itiraz usullerine ilişkin istisna.", "document")),
)
add_case(
    "education", "yuksekogretim", "04-03-v3-0304-tip-program-yuksek-baglam-row", "2023-02-14", "2023-03-30",
    "YÖK’ün 2023 bahar dönemi için yüz yüze öğretim seçeneği kararı", "yok-2023-03-30-bahar-yuzyuze-secenegi",
    "14 Şubat TİP Bilim Kurulu fizikî açılış çağrısı ve 30 Mart YÖK kararıyla uzaktan eğitimin yanında yüz yüze seçenek.",
    "31 Mart tarihli YÖK yazısının TBMM 7/193 cevabındaki tarihli eki.",
    "TİP Bilim Kurulu 14 Şubat’ta uzaktan eğitimden vazgeçilmesini ve okulların fizikî açılmasını istedi.",
    "YÖK 30 Mart kararıyla 3 Nisan’dan itibaren isteyenlere devam zorunluluğu olmadan yüz yüze ders seçeneği açtı. Uzaktan öğretim sürdü.",
    "14 Şubat TİP Bilim Kurulu çağrısını 17 Şubat uzaktan öğretim kararı izledi. 30 Mart kararı 3 Nisan’dan itibaren isteyen öğrencilere yüz yüze ders seçeneği tanıdı. Uzaktan öğretim yürürlükte kaldı ve ders biçimini üniversite kurulları belirledi. Kampüs bazında katılım ve yurt tahsisi açık.",
    "Bilim Kurulu görüşünü yayımladı. YÖK bahar döneminde uygulanabilecek biçimleri kararlaştırdı. Ders bazında düzenlemeler üniversite kurullarına bırakıldı.",
    "14 Şubat parti çağrısı, 17 Şubat uzaktan öğretim kararı, 30 Mart YÖK yeniden değerlendirmesi, 31 Mart yazısı ve 3 Nisan uygulama başlangıcı.",
    (("education-first", "initiative", "31 Mart yazısı 17 Şubat YÖK kararına atıf yapıyor.", "document"),
     ("education-remote", "initiative", "YÖK önce uzaktan öğretime karar verdi.", "document"),
     ("education-decision", "action", "Yükseköğretim Genel Kurulu 30 Mart’ta yeniden değerlendirdi.", "document"),
     ("education-effective", "result", "Bahar dönemi için düzenleme 3 Nisan’dan başlıyor.", "document"),
     ("education-choice", "result", "Devam şartı aranmadan yüz yüze öğretim seçeneği.", "document"),
     ("education-university", "result", "Ders biçimini kurumlar ilgili kurullarında kararlaştırıyor.", "document")),
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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün parti metni, Meclis belgesi veya YÖK kararı okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-earthquake-2023-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_EARTHQUAKE_2023_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
