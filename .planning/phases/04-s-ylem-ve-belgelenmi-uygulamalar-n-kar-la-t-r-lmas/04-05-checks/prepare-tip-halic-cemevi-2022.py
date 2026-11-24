"""Build TİP’s Haliç meeting and 7421 cemevi legislation records."""

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
source_dir = checks / "tip-publication-catalog" / "party-statements-12"
source_root = working / "sources" / "tip"
case = "0405-tip-halic-cemevi-2022"
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
    "366fafcea5829e6aaa7f98c78313626fbfbb561b0fbefa3f4a260adaf4d27e8f",
    "e00cb2ee931c6138457a70b8f2171757c310bded68e89cb8f29d42a03296f34d",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [35, 33, 0]

education = next(row for row in records["practice_event"] if row["common_event_key"] == "yok-2023-03-30-bahar-yuzyuze-secenegi")
assert education["scope_context"] == "14 Şubat TİP Bilim Kurulu fizikî açılış çağrısı ve 30 Mart YÖK kararıyla uzaktan eğitimin yanında yüz yüze seçenek."
education["scope_context"] = "30 Mart 2023 YÖK kararıyla bahar döneminde uzaktan öğretimin yanında yüz yüze eğitim seçeneği."



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
prior_dir = source_dir.with_name("party-statements-13")
source_rows.update({row["path"]: row for row in read(prior_dir / "capture.json")})
source_specs = {
    "declaration": ("095.html.bin", "2022-09-25", "TİP’in yayımladığı ortak ittifak deklarasyonu",
                    "party_publication", "Türkiye İşçi Partisi", None,
                    "25 Eylül TİP yayımı 24 Eylül buluşmasını geriye dönük bildiriyor ve ortak metni basıyor."),
    "prior": ("097.html.bin", "2022-08-25", "TİP’in yayımladığı 25 Ağustos ortak ittifak açıklaması",
              "party_publication", "Türkiye İşçi Partisi", None,
              "Altı bileşenin ortak metni, Eylül sonunda halk buluşması ve ittifak ilanı kararını bildiriyor."),
    "bianet": ("bianet-267592.html.bin", "2022-09-24", "Bianet’in Haliç buluşması haberi",
               "journalism", "Bianet", "Ruken Tuncel",
               "Olay günü yerinde haber. İlk yayım 15.24, erişilen metnin güncellemesi 23.08."),
    "cemevi-statement": ("092.html.bin", "2022-10-10", "10 Ekim TİP cemevi ve eşit yurttaşlık açıklaması",
                         "party_publication", "Türkiye İşçi Partisi", None,
                         "TİP’in tarihli kaynak yayımı. Duyurulan başkanlık, hizmet giderleri ve tanınma talebi."),
    "gazette": ("rg-7421-cemevi.htm", "2022-11-26", "7421 sayılı kanunun Resmî Gazete metni",
                "official", "Resmî Gazete", None,
                "32025 sayılı Resmî Gazete. 16 Kasım kabulü ve 26 Kasım yayımı."),
}
sources = {}
for key, (name, day, title, kind, publisher, author, basis) in source_specs.items():
    row = source_rows[name]
    if row.get("archive_copy"):
        path = Path(row["archive_copy"])
    else:
        path = (prior_dir if key == "prior" else source_dir) / name
    raw = path.read_bytes()
    assert sha(raw) == row["sha256"]
    folder = Path("objects") / row["sha256"]
    original, readable = folder / "original.html.bin", folder / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, "html"))
    url = row["final_url"]
    document = f"{case}-{key}"
    source_kind = {"party_publication": "party", "journalism": "news", "official": "official"}[kind]
    insert("document", dict(id=document, party_id=party, title=title, source_kind=source_kind))
    insert("document_version", dict(id=vid(key), document_id=document, original_url=row["url"], final_url=url,
        document_date=day, date_precision="day", date_unknown_reason=None, version_label=title,
        accessed_at=row["retrieved_at_utc"], verified_at=now, mime="text/html",
        sha256=row["sha256"], original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=vid(key), kind=kind, publisher=publisher, author=author,
        social_handle=None, published_at=day, date_precision="day", public_url=url, basis=basis))
    view = build_view(raw, url, source_root, fetch_assets=False)
    validate_view(source_root, view)
    insert("archive_view", dict(view, version_id=vid(key)))
    sources[key] = path, url

passages = {}
for key, source, exact, label, article in (
    ("halic-held", "bianet", "Haliç Kongre Merkezi'nde yol haritasını açıklamak üzere toplandı.",
     "24 Eylül Haliç buluşmasının gerçekleşmesi", None),
    ("halic-delivered", "bianet", "açıklanması ile devam etti.",
     "Bianet haberinde buluşmada deklarasyonun açıklanması", None),
    ("halic-parts", "bianet", "Emek Partisi (EMEP), Türkiye İşçi Partisi (TİP), Toplumsal Özgürlük Partisi (TÖP)",
     "Bianet haberinin kurucu bileşenleri", None),
    ("halic-authority", "bianet", "Türkiye İşçi Partisi Genel Başkanı Erkan Baş",
     "24 Eylül yayımında Erkan Baş’ın parti sıfatı", None),
    ("halic-spoke", "bianet", "Genel Başkanı Erkan Baş ise şunları söyledi:",
     "Bianet haberinde Erkan Baş’ın konuşması", None),
    ("halic-call", "prior", "Eylül ayı sonunda kitlesel bir halk buluşması",
     "25 Ağustos ortak açıklamasında Eylül sonu halk buluşması", None),
    ("halic-plan", "prior", "Emek ve Özgürlük İttifakı’nın kuruluşunun ilan edilmesine karar verilmiştir.",
     "25 Ağustos ortak açıklamasında ittifak ilanı kararı", None),
    ("halic-sign", "declaration", "EHP-EMEP-HDP-SMF-TİP-TÖP",
     "25 Eylül TİP yayımında ittifak metninin altı bileşeni", None),
    ("cemevi-call", "cemevi-statement", "İnanç ve ibadethanelerinin tanınmasını istiyor.",
     "10 Ekim metninde inanç ve ibadethanelerin tanınması", None),
    ("cemevi-adopted", "gazette", "16/11/2022", "7421 sayılı kanunun kabul tarihi", None),
    ("cemevi-published", "gazette", "26 Kasım 2022 CUMARTESİ", "7421 sayılı kanunun yayım tarihi", None),
    ("cemevi-local", "gazette", "bakım ve onarımını yapmak.", "Madde 14 yerel yapım, bakım ve onarım", "14"),
    ("cemevi-lighting", "gazette",
     "aydınlatma giderleri Kültür ve Turizm Bakanlığının bütçesine konulacak\r\n    ödenekten karşılanır.",
     "Madde 22, cemevleri aydınlatma giderinin kaynağı", "22"),
):
    assert exact in html_source_text(sources[source][0].read_bytes()), (key, exact)
    row = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None, article=article,
        section=label, pdf_page_index=None, printed_page=None)
    insert("passage", row)
    passages[key] = row

scopes = {}
topics = {"alevi-inanc-orgutlenmesi", "siyasal-ittifaklar"}
for row in read(working / "04-inventory.json")["cells"]:
    topic = row["topic_id"]
    if row["party_id"] != party or topic not in topics:
        continue
    scope = row["cell_id"]
    scopes[topic, row["research_kind"]] = scope
    if not any(existing["id"] == scope for existing in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope, **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="Haliç buluşması veya cemevleri düzenlemesi özgün belgelerde okundu.")
assert len(scopes) == 4
for key, (_, url) in sources.items():
    topic = "alevi-inanc-orgutlenmesi" if key in ("gazette", "cemevi-statement") else "siyasal-ittifaklar"
    lane = "statement" if key in ("declaration", "prior", "cemevi-statement") else "event"
    scope = scopes[topic, lane]
    version = vid(key)
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(sections, ensure_ascii=False))
    attempt = f"{case}-{key}-reading"
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="Yayım tarihi, olay veya hüküm ve yetki bağlamı özgün kaynakta okundu.", source_version_id=version)
    if not any(x["scope_id"] == scope and x["url"] == url for x in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
            relevance_reason="Haliç buluşması veya 7421 cemevi hükümleri için tarihli kaynak.",
            state="examined", attempt_ids=json.dumps([attempt]))

limitations = ("İttifak deklarasyonu 25 Eylül TİP yayımında geriye dönük aktarıldı. "
               "7421 düzenlemesinde tek tek gider ödemeleri ve yerel hizmet uygulaması açık.")

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

def evidence(event, points, limit):
    for ref, stage, basis, claim in points:
        add("practice_event_evidence", event_id=event, passage_id=pid(ref), stage=stage, supported_point=claim,
            concrete_basis=passages[ref]["section"], limitation=limit, epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=pid(ref), stage=stage, basis_kind=basis)
        event_claims[pid(ref)] = claim
    return tuple(point[0] for point in points)


halic = f"{case}-halic-event"
halic_limit = ("TİP altı kurucu bileşenden biri. Erkan Baş’ın Haliç konuşması parti temsilci katkısı. "
               "TİP’in 25 Eylül program yayımı olay sonrası. Aynı toplantıya davetli katılım ve ortak kararlar ayrı.")
add("practice_event", id=halic, common_event_key="halic-emek-ozgurluk-2022-09-24", event_at="2022-09-24",
    date_precision="day", date_unknown_reason=None, title="Emek ve Özgürlük İttifakı’nın Haliç halk buluşması",
    scope_context="24 Eylül 2022’de İstanbul Haliç Kongre Merkezi’nde düzenlenen Emek ve Özgürlük İttifakı halk buluşması ve deklarasyonun açıklanması.",
    occurrence_basis="24 Eylül 2022 tarihli Bianet haberi ve HDP yayını, Haliç Kongre Merkezi’ndeki halk buluşmasını ve deklarasyonun açıklanmasını bildiriyor.")
halic_refs = evidence(halic, (
    ("halic-held", "action", "independent_report", "Haliç Kongre Merkezi’nde 24 Eylül buluşması yapıldı."),
    ("halic-delivered", "result", "independent_report", "Haliç programında ortak deklarasyon açıklandı."),
    ("halic-parts", "action", "independent_report", "TİP ortak buluşmanın kurucu bileşenlerinden biri olarak anıldı."),
    ("halic-spoke", "action", "independent_report", "Erkan Baş Haliç toplantısında konuştu."),
), halic_limit)
party_claim = finding("halic-party", "TİP, buluşmada çerçevesi açıklanan ittifakın altı kurucu bileşeni arasında yer aldı.",
                      ("halic-parts", "halic-sign"))
speaker_claim = finding("halic-speaker", "TİP Genel Başkanı Erkan Baş, 24 Eylül’de Haliç buluşmasına katılıp parti adına konuştu.",
                        ("halic-authority", "halic-spoke"))
institution = f"{case}-party-actor"
representative = f"{case}-speaker-actor"
insert("actor", dict(id=institution, kind="institution", party_id=party, person_id=None, authorization_passage_id=None))
insert("actor", dict(id=representative, kind="authorized_representative", party_id=party, person_id="0405-tip-erkan-bas",
    authorization_passage_id=pid("halic-authority")))
for suffix, actor, finding_id, authority, limit in (
    ("party", institution, party_claim, None, "Altı kurucu bileşenden biri olarak ortak çerçeveye katılım."),
    ("speaker", representative, speaker_claim, pid("halic-authority"), "Olay günündeki parti adına temsilci konuşması."),
):
    contribution = f"{case}-halic-{suffix}-contribution"
    add("practice_contribution", id=contribution, event_id=halic, party_id=party, actor_id=actor,
        contribution_kind="support" if suffix == "party" else "task", finding_id=finding_id,
        authority_passage_id=authority, membership_passage_id=None, responsibility_limit=limit)
    if authority:
        add("practice_actor_period", contribution_id=contribution, valid_from="2022-09-24", valid_to="2022-09-24",
            identity_passage_id=authority)
topic = "siyasal-ittifaklar"
halic_statement = f"{case}-halic-statement"
halic_target = finding("halic-target", "TİP’in yayımladığı 25 Ağustos ortak açıklamasında altı bileşen, Eylül sonunda halka açık bir buluşma ve ittifakın kuruluşunun ilanını kararlaştırdı.", ("halic-call", "halic-plan"))
halic_quote = finding("halic-quote", passages["halic-call"]["exact"], ("halic-call",), quote=True, pair=halic_target)
add("practice_statement", id=halic_statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=halic_target, quote_finding_id=halic_quote, statement_at="2022-08-25", date_precision="day",
    version_id=vid("prior"), period_basis="TİP’in 25 Ağustos 2022’de yayımladığı altı bileşenli ortak açıklama.",
    comparison_row_id="04-03-v3-0304-tip-program-sinif-ittifak-row", uncertainty_reason=None)
halic_result = finding("halic-result", "Altı bileşenin Haliç buluşması 24 Eylül’de gerçekleşti. İttifakın deklarasyonu açıklandı. Erkan Baş toplantıda TİP adına konuştu.", halic_refs)
halic_comparison = finding("halic-comparison", "25 Ağustos ortak ilan kararı 24 Eylül Haliç buluşmasında gerçekleşti. TİP altı bileşenden biriydi ve Erkan Baş parti adına konuştu. TİP’in program metnini yeniden yayımladığı 25 Eylül, buluşmadan sonraki gündü.", ("halic-call", "halic-plan", *halic_refs, "halic-sign"))
halic_relation = f"{case}-halic-relation"
add("practice_relation", id=halic_relation, party_id=party, topic_id=topic, scope_id=scopes[topic, "event"],
    statement_id=halic_statement, event_id=halic, target_finding_id=halic_target, result_finding_id=halic_result,
    explanation_finding_id=halic_comparison, comparability_reason="25 Ağustos ortak açıklaması ve 24 Eylül buluşması aynı kuruluş ilanına ilişkin.",
    temporal_context="25 Ağustos hazırlık açıklaması, 24 Eylül Haliç buluşması ve 25 Eylül TİP yayımı.",
    authority_context="Altı bileşenin ortak kararı ve TİP’in bireysel temsilci konuşması ayrı kayıtlarda.",
    uncertainty_reason=halic_limit)
add("practice_candidate", id=f"{case}-halic-candidate", scope_id=scopes[topic, "event"], event_id=halic,
    relation_id=halic_relation, state="eligible", reason="25 Ağustos ortak ilan kararı ve 24 Eylül Haliç buluşması.",
    passage_ids=json.dumps([pid(ref) for ref in halic_refs]))

topic = "alevi-inanc-orgutlenmesi"
cemevi = f"{case}-cemevi-event"
statement = f"{case}-cemevi-statement"
summary = finding("cemevi-target", "TİP’in 10 Ekim açıklaması Alevilerin eşit yurttaşlık ve ibadethanelerin tanınması talebini aktardı.",
                  ("cemevi-call",))
quote = finding("cemevi-quote", passages["cemevi-call"]["exact"], ("cemevi-call",), quote=True, pair=summary)
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2022-10-10", date_precision="day",
    version_id=vid("cemevi-statement"), period_basis="TİP’in 10 Ekim 2022 tarihli açıklaması.",
    comparison_row_id="04-03-v3-0304-tip-program-alevi-row", uncertainty_reason=None)
cemevi_limit = ("Mevzuatın getirdiği bütçe ve hizmet hükümleri incelendi. Fiilî ödeme, yapım, bakım ve kişilere etkisi ayrıca açık.")
add("practice_event", id=cemevi, common_event_key="tbmm-2022-11-16-law-7421-cemevi", event_at="2022-11-16",
    date_precision="day", date_unknown_reason=None, title="7421 sayılı kanunun cemevi hizmeti ve aydınlatma hükümleri",
    scope_context="7421’in cemevlerine ilişkin yapım, bakım, onarım ve aydınlatma gideri hükümlerinin kabulü.",
    occurrence_basis="7421 sayılı kanunun 26 Kasım 2022 tarihli ve 32025 sayılı Resmî Gazete yayımı.")
cemevi_refs = evidence(cemevi, (
    ("cemevi-adopted", "action", "document", "7421, 16 Kasım 2022’de kabul edildi."),
    ("cemevi-published", "result", "document", "7421, 26 Kasım 2022’de yayımlandı."),
    ("cemevi-local", "result", "document", "Madde 14 cemevlerine ilişkin yerel bakım ve onarım hükmü içeriyor."),
    ("cemevi-lighting", "result", "document", "Madde 22, cemevleri aydınlatma giderini Bakanlık bütçesindeki ödeneğe bağlıyor."),
), cemevi_limit)
result = finding("cemevi-result", "7421 sayılı kanun cemevlerinin yapım, bakım ve onarımı için yerel yönetim hükümleri getirdi. Aydınlatma giderlerini Kültür ve Turizm Bakanlığı bütçesindeki ödeneğe bağladı.", cemevi_refs)
comparison = finding("cemevi-comparison", "TİP 10 Ekim’de eşit yurttaşlık ve ibadethanelerin tanınması talebini dile getirdi. 7421’in incelenen maddeleri cemevleri için bütçe ve yerel hizmet hükümleri getirdi. Cemevlerine ibadethane statüsü verilmesine ilişkin hüküm bu maddelerde yer almıyor. Ödeme ve hizmet uygulaması açık.", ("cemevi-call", *cemevi_refs))
relation = f"{case}-cemevi-relation"
add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes[topic, "event"],
    statement_id=statement, event_id=cemevi, target_finding_id=summary, result_finding_id=result,
    explanation_finding_id=comparison, comparability_reason="10 Ekim açıklaması ve 7421’in seçili maddeleri cemevlerinin tanınma ve hizmet koşullarını ele alıyor.",
    temporal_context="10 Ekim açıklaması, 16 Kasım TBMM kabulü, 26 Kasım Resmî Gazete yayımı.",
    authority_context="TİP görüş açıkladı. TBMM kanunu kabul etti. Yerel yönetim görevleri ve Bakanlık ödeneği ilgili maddelerde belirlendi.",
    uncertainty_reason=cemevi_limit)
add("practice_candidate", id=f"{case}-cemevi-candidate", scope_id=scopes[topic, "event"], event_id=cemevi,
    relation_id=relation, state="eligible", reason="Cemevlerine ilişkin 10 Ekim açıklaması ile sonraki 7421 hizmet hükümleri.",
    passage_ids=json.dumps([pid(ref) for ref in cemevi_refs]))

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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün parti metni, olay günü haberi veya Resmî Gazete okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-halic-cemevi-2022-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_HALIC_CEMEVI_2022_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
