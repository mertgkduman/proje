"""Build TİP’s 2023 election and NATO records from verified source passages."""

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
source_dir = checks / "tip-publication-catalog" / "party-statements-08"
source_root = working / "sources" / "tip"
case = "0405-tip-election-finland-2023"
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
    "dafab220fa2f5bfb2e0826b1d959d19abc0cf1fc43a16ddfb9e4ceb90582199d",
    "08168a0a869c69bbc832b05421c7f406897d0b69319f730f06b4f79d98b9502b",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [30, 29, 0]


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
    ("election-statement", "059.html.bin", "2023-05-15", "15 Mayıs TİP seçim açıklaması", "party_publication",
     "Türkiye İşçi Partisi", None, "2023-05-15", "Özgün parti metninin yayın günü ve açıkça geçici milletvekili seçimi sonucu."),
    ("election-gazette", "gazette-2023-1255.pdf", "2023-05-30", "YSK 2023/1255 ve kesin seçim cetvelleri", "official",
     "Yüksek Seçim Kurulu / Resmî Gazete", None, None, "30 Mayıs 2023, mükerrer 32206 sayısı ve YSK karar ekleri."),
    ("nato-statement", "063.html.bin", "2023-04-04", "4 Nisan TİP NATO açıklaması", "party_publication",
     "Türkiye İşçi Partisi", None, "2023-04-04", "Özgün metindeki Finlandiya genişlemesi ve Türkiye’nin üyeliğine dair parti tutumu."),
    ("nato-membership", "nato-finland-20230404.html.bin", "2023-04-04", "Finlandiya’nın NATO üyeliği", "official",
     "NATO", None, None, "NATO açıklamasında üyeliğin tarihi ve katılma belgesinin teslimi."),
    ("nato-floor", "tbmm-finland-floor.pdf", "2023-03-30", "30 Mart TBMM 82. birleşim tutanağı", "official",
     "TBMM", None, None, "Teklif ve sıra sayısı, kürsü bildirimi ve ayrı kesin açık oy cetveli."),
    ("nato-registration", "tbmm-finland-register.html.bin", "2023-03-30", "TBMM 7448 sicili", "official",
     "TBMM", None, None, "7448, kabul ve yayım günleri ve Resmî Gazete sayısı."),
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
for key, source, page, printed, exact, label, manual in (
    ("election-call", "election-statement", None, None,
     "1 milyona yakın oyla (81 ilin 51’inden alınan yüzde 1,75 oy) şimdilik çıkardığımız 4 vekillik",
     "15 Mayıs parti açıklamasında geçici oy oranı ve sandalye sayısı", False),
    ("election-decision", "election-gazette", 0, None, "Karar No: 2023/1255",
     "30 Mayıs mükerrer 32206 sayılı Resmî Gazete. 14 Mayıs milletvekili seçimi kesin kararı", True),
    ("election-total", "election-gazette", 3, "MM/24", "TÜRKİYE İŞÇİ PARTİSİ | 903.742 | 52.315 | 956.057 | %1,76",
     "Türkiye geneli toplamı, yurt içi, yurt dışı ve gümrük oyları ve yüzde satırı", True),
    ("election-seats", "election-gazette", 4, "MM/25", "TÜRKİYE İŞÇİ PARTİSİ | 4",
     "Partilere göre kazanılan milletvekili sayısı", True),
    ("nato-call", "nato-statement", None, None, "NATO’nun en son Finlandiya’yı kapsayan genişleme süreci olağanüstü kaygı vericidir.",
     "4 Nisan TİP açıklamasında Finlandiya genişlemesine ilişkin cümle", False),
    ("nato-member", "nato-membership", None, None, "Finland became NATO’s newest member today (4 April 2023)",
     "NATO açıklamasında Finlandiya’nın üye olduğu gün ve katılma belgesinin teslimi", False),
    ("nato-bill", "nato-floor", 114, "823", "Kanun Teklifi (2/5005) ve\nDışişleri Komisyonu Raporu (S. Sayısı 438)",
     "82. birleşimde 2/5005 ve S.S. 438", False),
    ("nato-announcement", "nato-floor", 126, "835", "“Kullanılan oy sayısı : 276\nKabul\n: 276 (*)",
     "2/5005 için kürsü bildirimi", False),
    ("nato-final", "nato-floor", 130, "839", "Sıra Sayısı : 438 | Kabul Edenler : 275 | Mükerrer Oylar : 2 | Toplam : 277",
     "23.51 kesin cetveli. Başlık ve sayılar S.S. 438 sütunundan", True),
    ("nato-atay", "nato-floor", 137, "846", "Hatay | Mengüllüoğlu | Barış Atay | TİP | S.S. 438 Katılmadı",
     "Barış Atay Mengüllüoğlu, S.S. 438 sütunu", True),
    ("nato-bas", "nato-floor", 138, "847", "İstanbul | Baş | Erkan | TİP | S.S. 438 Katılmadı",
     "Erkan Baş, S.S. 438 sütunu", True),
    ("nato-kadigil", "nato-floor", 139, "848", "İstanbul | Kadıgil Sütlü | Saliha Sera | TİP | S.S. 438 Katılmadı",
     "Saliha Sera Kadıgil Sütlü, S.S. 438 sütunu", True),
    ("nato-sik", "nato-floor", 140, "849", "İstanbul | Şık | Ahmet | TİP | S.S. 438 Katılmadı",
     "Ahmet Şık, S.S. 438 sütunu", True),
    ("nato-adoption", "nato-registration", None, None, "30/03/2023",
     "TBMM 7448 sicilinde kabul günü", False),
    ("nato-publication", "nato-registration", None, None, "01/04/2023",
     "TBMM 7448 sicilinde 32150 sayılı Resmî Gazete yayım günü", False),
):
    path = sources[source][0]
    if manual:
        insert("manual_passage", dict(passage_id=pid(key), checked_at=now, method="Görsel PDF sayfası okuması",
            reason=label + ". Dikey cetvel döndürülüp ilgili başlık ve satırlar özgün PDF’den okundu."
            if source == "nato-floor" else label + ". Tarama görselindeki karar başlığı veya cetvel satırı okundu."))
    elif page is None:
        assert exact in html_source_text(path.read_bytes()), key
    else:
        assert exact in pdf_page_text(path, page), key
    passage = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None,
        article=None, section=label, pdf_page_index=page, printed_page=printed)
    insert("passage", passage)
    passages[key] = passage

scopes = {}
topics = {"secime-katilma", "nato-iliskileri"}
for row in read(working / "04-inventory.json")["cells"]:
    topic = row["topic_id"]
    if row["party_id"] != party or topic not in topics:
        continue
    scope = row["cell_id"]
    scopes[topic, row["research_kind"]] = scope
    if not any(existing["id"] == scope for existing in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope, **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="2023 milletvekili kesin sonucu ve Finlandiya’nın NATO üyeliği seçili özgün kaynaklardan okundu.")
assert len(scopes) == 4
for key, (_, url) in sources.items():
    topic = "secime-katilma" if key.startswith("election-") else "nato-iliskileri"
    scope = scopes[topic, "statement" if key.endswith("-statement") else "event"]
    version = vid(key)
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(sections, ensure_ascii=False))
    attempt = f"{case}-{key}-reading"
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="Tarih, işlem ve sonuç özgün kaynak pasajlarından okundu.", source_version_id=version)
    if not any(row["scope_id"] == scope and row["url"] == url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url, relevance_reason="Dönemsel özgün kaynak.",
            state="examined", attempt_ids=json.dumps([attempt]))

limitations = ("Milletvekili seçimi, cumhurbaşkanı seçiminin iki oylamasından ayrı. 4 Nisan üyeliği, "
               "30 Mart TBMM oylamasından ayrı. Cetveldeki kişisel kayıtların gerekçesi ve ortak parti talimatı açık.")

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
    "election", "secime-katilma", "04-03-v3-0304-tip-secime-katilma-row", "2023-05-15", "2023-05-30",
    "14 Mayıs 2023 milletvekili seçiminin kesinleştirilmesi", "ysk-2023-1255-2023-05-30-final-milletvekili",
    "15 Mayıs geçici TİP açıklaması, 14 Mayıs milletvekili seçimi ve YSK 2023/1255 kesin cetvelleri.",
    "30 Mayıs 2023 tarihli ve 32206 mükerrer sayılı Resmî Gazete, YSK kararı ve MM/24–25 cetvelleri.",
    "TİP, 15 Mayıs’ta milletvekili seçiminde geçici olarak yüzde 1,75 ve dört sandalye açıkladı.",
    "30 Mayıs’ta yayımlanan YSK kesin sonuçlarına göre TİP 956.057 oyla yüzde 1,76 aldı ve dört sandalye kazandı.",
    "TİP’in 15 Mayıs açıklamasında oran yüzde 1,75 ve sandalye sayısı dört olarak geçiciydi. YSK kesin cetvelinde 903.742 yurt içi ve 52.315 yurt dışı ve gümrük oyu toplam 956.057 ediyor. Kesin oran yüzde 1,76. Sandalye sayısı dört. Parti itirazlarının dosyaları ve cumhurbaşkanı seçimi ayrı.",
    "TİP geçici sayıları yayımladı. Kesin sonucu YSK ilan etti.",
    "14 Mayıs oy verme, 15 Mayıs geçici parti açıklaması ve 30 Mayıs YSK kesin sonucu.",
    (("election-decision", "action", "YSK 2023/1255 sayılı kararla 14 Mayıs milletvekili seçimini kesinleştirdi.", "document"),
     ("election-total", "result", "TİP için 956.057 toplam oy ve yüzde 1,76 oran.", "document"),
     ("election-seats", "result", "TİP için dört milletvekilliği.", "document")),
)
add_case(
    "nato", "nato-iliskileri", "04-03-v3-0304-tip-program-nato-row", "2023-04-04", "2023-04-04",
    "Finlandiya’nın NATO’ya katılması", "nato-2023-04-04-finland-membership",
    "4 Nisan TİP açıklaması ve NATO’nun aynı gün Finlandiya’nın üyeliğine dair kaydı.",
    "NATO, Finlandiya’nın katılma belgesinin teslimiyle 4 Nisan’da üye olduğunu kaydetti.",
    "TİP, Finlandiya’yı kapsayan NATO genişlemesini olağanüstü kaygı verici olarak niteledi.",
    "Finlandiya 4 Nisan’da katılma belgesini teslim ederek NATO üyesi oldu.",
    "TİP aynı gün Finlandiya’yı kapsayan genişlemeye karşı çıktı. NATO üyeliği 4 Nisan’da gerçekleşti. Yayım ile belge tesliminin gün içindeki sırası açık. Türkiye’deki 30 Mart 2/5005 oylaması ve 1 Nisan 7448 yayımı üyelik işleminden ayrı.",
    "Parti görüşünü açıkladı. Türkiye’de TBMM onayı uygun buldu. NATO açıklaması Finlandiya’nın katılma belgesini teslim ettiğini kaydediyor.",
    "30 Mart Türkiye’de kabul, 1 Nisan 7448 yayımı ve 4 Nisan Finlandiya’nın üyeliği ile TİP açıklaması.",
    (("nato-member", "result", "Finlandiya’nın NATO üyeliği 4 Nisan’da gerçekleşti.", "document"),),
    ("nato-adoption", "nato-publication"),
)

ballot_event = f"{case}-nato-vote-event"
add("practice_event", id=ballot_event, common_event_key="tbmm-27-6-82-2-5005-law-7448", event_at="2023-03-30",
    date_precision="day", date_unknown_reason=None, title="Finlandiya’nın NATO protokolü için 7448 sayılı kanunun kabulü",
    scope_context="TBMM 27. Dönem 6. Yasama Yılı 82. Birleşim, 2/5005 ve S.S. 438.",
    occurrence_basis="30 Mart 2023 82. birleşimin altıncı oturum tutanağı, kesin cetvel ve 7448 sicili.")
ballot_refs = {
    "nato-bill": "2/5005 ve S.S. 438 aynı dosya.",
    "nato-announcement": "Kürsü, kullanılan 276 oyun 276’sını kabul olarak duyurdu.",
    "nato-final": "S.S. 438 kesin cetvelinde 275 kabul, 0 ret, 0 çekimser, 2 mükerrer ve 277 toplam.",
    "nato-atay": "Barış Atay Mengüllüoğlu için Katılmadı kaydı.",
    "nato-bas": "Erkan Baş için Katılmadı kaydı.",
    "nato-kadigil": "Saliha Sera Kadıgil Sütlü için Katılmadı kaydı.",
    "nato-sik": "Ahmet Şık için Katılmadı kaydı.",
    "nato-adoption": "7448’in kabul günü 30 Mart.",
    "nato-publication": "7448, 1 Nisan 32150 sayılı Resmî Gazete’de yayımlandı.",
}
for ref, point in ballot_refs.items():
    stage = "initiative" if ref == "nato-bill" else "result"
    add("practice_event_evidence", event_id=ballot_event, passage_id=pid(ref), stage=stage, supported_point=point,
        concrete_basis=passages[ref]["section"], limitation=limitations, epistemic_type="claim")
    add("practice_evidence_assessment", event_id=ballot_event, passage_id=pid(ref), stage=stage, basis_kind="document")
    event_claims[pid(ref)] = point
add("practice_candidate", id=f"{case}-nato-vote-candidate", scope_id=scopes["nato-iliskileri", "event"],
    event_id=ballot_event, relation_id=None, state="unmatched",
    reason="TİP’in 4 Nisan parti açıklaması 30 Mart oylamasından sonra. Oylama öncesi Finlandiya protokolüne özgü parti açıklaması ve kişinin katılmama gerekçesi açık.",
    passage_ids=json.dumps([pid(ref) for ref in ballot_refs]))

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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün parti, YSK, TBMM veya NATO kaydı okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-election-finland-2023-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_ELECTION_FINLAND_2023_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
