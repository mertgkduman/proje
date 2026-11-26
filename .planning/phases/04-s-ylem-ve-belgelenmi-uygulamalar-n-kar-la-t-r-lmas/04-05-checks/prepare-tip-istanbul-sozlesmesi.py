"""Prepare three TİP comparisons on the Istanbul Convention and its judicial review."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

from arsiv import pdf_page_text, readable_bytes
import uygulamalar as rules


checks = Path(__file__).resolve().parent
assert len(sys.argv) in (1, 2)
output_dir = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else checks
practices = Path("data/practices")
source_root = practices / "sources" / "tip"
prefix = "0405-tip-istanbul-sozlesmesi"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")


def read(path):
    return json.loads(path.read_bytes())


base_paths = [
    checks / f"tip-2020-autumn-civic{suffix}-draft.json" for suffix in ("", "-review")
]
assert [sha256(path.read_bytes()).hexdigest() for path in base_paths] == [
    "dfce59c6a97b80c40ce5585bf818cafb1a4000801485e1fe5a26501ed5dcde5d",
    "ed76cf45dd5085d6f5beb059f9c26a98e55df62a44070a9b799852bee6a87829",
]
package, review = map(read, base_paths)
entries, records = package["entries"], package["practice_records"]


def insert(table, **values):
    entries.append({"kind": table, "values": values})


def add(table, **values):
    records[table].append(values)


def identifier(key):
    return f"{prefix}-{key}"


def store(path, content, *, archival_original=None):
    target = source_root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes() == content, target
    elif archival_original:
        os.link(archival_original, target)
    else:
        target.write_bytes(content)


folder = checks / "istanbul-sozlesmesi-case-sources"
captures = {row["path"]: (folder, row) for row in read(folder / "reading.json")["captures"] if row["status"] == 200}
cark = checks / "tip-cark-basak-catalog" / "issue-16"
party_pdf = read(cark / "reading-01.json")["source"]
captures[party_pdf["path"]] = cark, party_pdf

sources = {}
for key, filename, document_day, publication_day, kind, publisher, author, title, basis in (
    ("stance", "cark-basak-16.pdf", None, None, "party_publication", "Türkiye İşçi Partisi",
     "Kadın Koordinasyonu", "ÇarkBaşak, Ağustos 2020, sayı 16",
     "Kadın Koordinasyonu imzalı yazı. Ağustos künyesi var, gün açık."),
    ("3718", "rg-3718.pdf", "2021-03-19", "2021-03-20", "official", "Resmî Gazete",
     "Cumhurbaşkanlığı", "19 Mart 2021 tarihli 3718 sayılı Cumhurbaşkanı Kararı",
     "31429 sayılı Resmî Gazete’nin tam sayfasında karar metni görsel olarak okundu."),
    ("3928", "rg-3928.pdf", "2021-04-29", "2021-04-30", "official", "Resmî Gazete",
     "Cumhurbaşkanlığı", "29 Nisan 2021 tarihli 3928 sayılı Cumhurbaşkanı Kararı",
     "31470 sayılı Resmî Gazete’nin tam sayfasında Türkiye bakımından sona erme tarihi 1 Temmuz 2021 olarak okundu."),
    ("court", "tip-danistay-dosya.pdf", "2022-12-19", None, "official", "Türkiye İşçi Partisi",
     "Danıştay İdari Dava Daireleri Kurulu", "İDDK E.2022/3473, K.2022/3752 karar nüshası",
     "TİP’in sitesinde yayımlanan 14 sayfalık karar nüshası. Belgeyi düzenleyen Danıştay İdari Dava Daireleri Kurulu, "
     "çevrimiçi nüshayı yayımlayan TİP. Çevrimiçi ilk yayın günü belirlenmedi."),
):
    directory, capture = captures[filename]
    path = directory / filename
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == capture["sha256"] and raw.startswith(b"%PDF-")
    storage = Path("objects", capture["sha256"])
    original, readable = storage / "original.pdf", storage / "readable.html"
    store(original, raw, archival_original=path)
    store(readable, readable_bytes(raw, "pdf", legacy=False))
    document, version = identifier(key), identifier(f"{key}-v1")
    url = capture["final_url"]
    insert("document", id=document, party_id="tip", title=title,
           source_kind="official" if kind == "official" else "party")
    insert("document_version", id=version, document_id=document, original_url=capture["url"], final_url=url,
           document_date=document_day, date_precision="day" if document_day else "unknown",
           date_unknown_reason=None if document_day else "Dergi künyesinde Ağustos 2020 var. Yayın günü açık.",
           version_label=title, accessed_at=capture["retrieved_at_utc"], verified_at=now,
           mime="application/pdf", sha256=capture["sha256"], original_path=str(original), readable_path=str(readable))
    insert("source_attribution", version_id=version, kind=kind, publisher=publisher, author=author,
           social_handle=None, published_at=publication_day, date_precision="day" if publication_day else "unknown",
           public_url=url, basis=basis)
    sources[key] = path, version, url, document_day

passages = {}
for key, source, page, printed, exact, section in (
    ("stance-text", "stance", 8, "9", "İstanbul Sözleşmesi’nden vazgeç-\nmiyoruz.",
     "Ağustos 2020 Kadın Koordinasyonu yazısının sonunda sözleşmeye bağlılık."),
    ("withdrawal-id", "3718", 0, None, "Karar Sayısı: 3718\n19 Mart 2021",
     "3718 karar başlığı ve karar günü. Aynı sayfada feshin konusu görsel olarak okundu."),
    ("withdrawal-publication", "3718", 0, None, "20 Mart 2021 CUMARTESİ\nSayı : 31429",
     "3718 sayılı kararın 20 Mart tarihli Resmî Gazete yayımı."),
    ("effect-id", "3928", 0, None, "Karar Sayısı: 3928\n29 Nisan 2021",
     "3928 karar başlığı ve karar günü. Aynı sayfanın görsel metni sona erme tarihini 1 Temmuz olarak tespit ediyor."),
    ("effect-publication", "3928", 0, None, "30 Nisan 2021 CUMA\nSayı : 31470",
     "3928 sayılı kararın 30 Nisan tarihli Resmî Gazete yayımı."),
    ("object-of-suit", "court", 0, "1",
     "Konseyi Sözleşmesinin Türkiye Cumhuriyeti bakımından feshedilmesine ilişkin 19/03/2021 tarih\nve 3718 sayılı Cumhurbaşkanı Kararının iptali",
     "İDDK’nın dava konusuna ilişkin özeti. 19 Mart 3718 kararının içerdiği fesih ve davanın iptal istemi."),
    ("appellant", "court", 0, "1", ":Türkiye İşçi Partisi",
     "İDDK kararında temyiz eden davacı Türkiye İşçi Partisi."),
    ("first-instance", "court", 0, "1",
     "Daire kararının özeti: Danıştay Onuncu Dairesinin 14/06/2022 tarih ve E:2021/1514,\nK:2022/3217 sayılı kararıyla;",
     "İDDK kararında 14 Haziran 2022 tarihli ilk derece kararının dosya kimliği ve özeti."),
    ("standing", "court", 12, "13",
     "davacının dava açma ehliyetinin bulunduğuna oyçokluğu ile karar verilerek işin esasına geçildi.",
     "İDDK çoğunluğu davacının dava açma ehliyetini kabul etti ve esasa geçti."),
    ("affirmed", "court", 12, "13",
     "1. Davacının temyiz isteminin reddine,\n2.Davanın yukarıda özetlenen gerekçeyle reddine ilişkin Danıştay Onuncu Dairesinin\ntemyize konu 14/06/2022 tarih ve E:2021/1514, K:2022/3217 sayılı kararının ONANMASINA,",
     "İDDK karar sonucu. Temyiz istemi reddedildi ve Onuncu Dairenin ret kararı onandı."),
    ("final", "court", 12, "13", "Kesin olarak, 19/12/2022 tarihinde usulde ve esasta oyçokluğu ile karar verildi.",
     "İDDK karar sonucu. 19 Aralık 2022 tarihinde kesin karar verildi."),
    ("case-number", "court", 12, "13", "Esas No : 2022/3473\nKarar No : 2022/3752",
     "İDDK E.2022/3473, K.2022/3752 dosya kimliği."),
):
    path, version, _, _ = sources[source]
    assert exact in pdf_page_text(path, page), (key, exact)
    row = dict(id=identifier(key), version_id=version, exact=exact, prefix=None, suffix=None,
               article=None, section=section, pdf_page_index=page, printed_page=printed)
    insert("passage", **row)
    passages[key] = row

scope_rows = {
    (row["topic_id"], row["research_kind"]): row
    for row in read(practices / "04-inventory.json")["cells"] if row["party_id"] == "tip"
}


def add_scope(topic, lane, source):
    scope = scope_rows[topic, lane]
    scope_id = scope["cell_id"]
    if not any(row["id"] == scope_id for row in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope_id, **{key: scope[key] for key in
            ("party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="Dönemsel kaynaklar incelendi. Kapsam araştırması sürüyor.")
    _, version, url, _ = sources[source]
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    add("practice_scope_source", scope_id=scope_id, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(sections, ensure_ascii=False))
    attempt = identifier(f"{source}-reading")
    add("practice_attempt_v2", id=attempt, scope_id=scope_id, attempted_at=now, query=url, url=url, result="examined",
        reason="Tarih, yetki, kaynak metni ve işlem sınırları incelendi.", source_version_id=version)
    if not any(row["scope_id"] == scope_id and row["url"] == url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope_id, url=url,
            relevance_reason="Tarihsel parti açıklaması veya kararın özgün kurumsal belgesi.",
            state="examined", attempt_ids=json.dumps([attempt]))
    return scope_id


def finding(key, content, refs, *, quote_pair=None):
    ident = identifier(key)
    provenance = "quote" if quote_pair else "summary"
    insert("finding", id=ident, party_id="tip", heading="Belgelenmiş uygulamalar", pair_id=quote_pair or ident,
           text=content, provenance=provenance, epistemic_type="claim")
    insert("review", id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent",
           reviewed_at=now, result="reviewed", reason="Tarihli özgün kaynak pasajları incelendi.")
    for ref in refs:
        row = passages[ref]
        insert("finding_evidence", finding_id=ident, passage_id=row["id"], role="quotation" if quote_pair else "support")
        insert("verification", finding_id=ident, passage_id=row["id"], checked_at=now,
               result="confirmed", reason=row["section"])
    return ident


topic = "toplumsal-cinsiyet"
add_scope(topic, "statement", "stance")
for source in ("3718", "3928", "court"):
    event_scope = add_scope(topic, "event", source)
target = "stance-text"
summary = finding("stance-summary", "TİP Kadın Koordinasyonu Ağustos 2020’de İstanbul Sözleşmesi’nin korunmasını savundu.", (target,))
quote = finding("stance-quote", passages[target]["exact"], (target,), quote_pair=summary)
statement = identifier("stance-statement")
add("practice_statement", id=statement, party_id="tip", topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at=None, date_precision="unknown",
    version_id=sources["stance"][1], period_basis="Ağustos 2020 tarihli ÇarkBaşak künyesi ve Kadın Koordinasyonu imzası.",
    uncertainty_reason="Derginin gün düzeyinde ilk yayım tarihi açık.",
    comparison_row_id="04-03-v3-0304-tip-program-kadin-row")
actor = identifier("institution")
insert("actor", id=actor, kind="institution", party_id="tip", person_id=None, authorization_passage_id=None)
cases = (
    dict(key="withdrawal", day="2021-03-19", common="cumhurbaskanligi-2021-03-19-3718",
         title="İstanbul Sözleşmesi için 3718 sayılı fesih kararı",
         context="Cumhurbaşkanı 19 Mart 2021’de İstanbul Sözleşmesi’nin Türkiye bakımından feshedilmesine karar verdi.",
         occurrence="Resmî Gazete’nin 31429 sayısındaki 3718 kararı ve Danıştay’ın dava konusu tespiti.",
         outcome="3718 sayılı fesih kararı 20 Mart’ta yayımlandı. 3928 sayılı karar, sözleşmenin Türkiye bakımından sona erme tarihini 1 Temmuz 2021 olarak tespit etti.",
         comparison="TİP Kadın Koordinasyonu sözleşmenin korunmasını savundu. Araştırılan dönemde Cumhurbaşkanının fesih kararı ve 1 Temmuz için sona erme kararı kayda geçti.",
         authority="Kararları Cumhurbaşkanı verdi. TİP’in daha sonraki davacı rolü yargı kayıtlarında ayrıca gösteriliyor.",
         timeline="19 Mart fesih kararı, 20 Mart yayım, 29 Nisan 3928 sayılı karar, 30 Nisan yayım, 1 Temmuz 2021 sona erme.",
         limit="6284 sayılı Kanun’un fiilî uygulanması ve sözleşmeden ayrılışın sonuçları ayrı kanıt gerektiriyor.",
         points=(("withdrawal-id", "action"), ("withdrawal-publication", "result"), ("object-of-suit", "action"),
                 ("effect-id", "result"), ("effect-publication", "result")),
         role=None),
    dict(key="court-first", day="2022-06-14", common="danistay-10d-2022-06-14-e2021-1514-k2022-3217",
         title="İstanbul Sözleşmesi davasında Danıştay Onuncu Daire kararı",
         context="Türkiye İşçi Partisi’nin 3718 sayılı karara karşı açtığı davada Danıştay Onuncu Dairesinin kararı.",
         occurrence="İDDK’nın 19 Aralık tarihli karar nüshası, Onuncu Dairenin kararını ve dosyasını aktarıyor.",
         outcome="Danıştay Onuncu Dairesi 14 Haziran 2022 tarihli E.2021/1514, K.2022/3217 kararıyla davayı reddetti.",
         comparison="Partinin sözleşmenin korunması yönündeki tutumunu iptal talebi izledi. Onuncu Daire parti talebini reddetti.",
         authority="TİP davacı, Cumhurbaşkanlığı davalı. İlk derece kararını Danıştay Onuncu Dairesi verdi.",
         timeline="19 Mart 2021 fesih kararı. 14 Haziran 2022 Onuncu Daire kararı. 19 Aralık 2022 İDDK kararı ayrı aşama.",
         limit="İlk derece kararının bağımsız yayımlanmış nüshası açık. Dosya kimliği, tarihi ve sonucu İDDK nüshasından denetlendi.",
         points=(("first-instance", "action"), ("affirmed", "result"), ("object-of-suit", "initiative")),
         role=("TİP, 3718 sayılı Cumhurbaşkanı Kararının iptalini isteyen davacıydı.", ("appellant", "object-of-suit", "first-instance"))),
    dict(key="court-final", day="2022-12-19", common="danistay-iddk-2022-12-19-e2022-3473-k2022-3752",
         title="İstanbul Sözleşmesi davasında Danıştay İDDK onaması",
         context="TİP’in açtığı davanın temyizinde Danıştay İdari Dava Daireleri Kurulunun E.2022/3473, K.2022/3752 kararı.",
         occurrence="TİP’in yayımladığı Danıştay İdari Dava Daireleri Kurulu karar nüshasının 13. sayfası.",
         outcome="Kurul, TİP’in dava açma ehliyetini oyçokluğuyla kabul ederek esasa geçti. Temyiz istemini reddetti ve Onuncu Daire kararını 19 Aralık 2022’de kesin olarak onadı.",
         comparison="TİP kararı temyiz etti. Kurul parti başvurusunu esastan inceleyerek ilk derece ret kararını onadı.",
         authority="TİP temyiz eden davacı. Onama Danıştay İdari Dava Daireleri Kurulunun kararı.",
         timeline="14 Haziran ilk derece ret kararı. 19 Aralık İDDK onaması. Sonraki bireysel başvuru ayrı bir süreç.",
         limit="Sonraki AYM başvurusunun resmî kayıt numarası ve inceleme sonucu açık.",
         points=(("case-number", "action"), ("final", "action"), ("standing", "result"), ("affirmed", "result")),
         role=("TİP, Onuncu Daire ret kararının temyizen bozulmasını isteyen davacıydı.", ("appellant", "case-number", "affirmed"))),
)
for case in cases:
    key = case["key"]
    event = identifier(f"{key}-event")
    add("practice_event", id=event, common_event_key=case["common"], event_at=case["day"], date_precision="day",
        date_unknown_reason=None, title=case["title"], scope_context=case["context"], occurrence_basis=case["occurrence"])
    refs = tuple(ref for ref, _ in case["points"])
    for ref, stage in case["points"]:
        row = passages[ref]
        add("practice_event_evidence", event_id=event, passage_id=row["id"], stage=stage, supported_point=row["section"],
            concrete_basis=row["section"], limitation=case["limit"], epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=row["id"], stage=stage, basis_kind="document")
    result = finding(f"{key}-result", case["outcome"], refs)
    explanation = finding(f"{key}-comparison", case["comparison"], (target, *refs))
    relation = identifier(f"{key}-relation")
    add("practice_relation", id=relation, party_id="tip", topic_id=topic, scope_id=event_scope, statement_id=statement,
        event_id=event, target_finding_id=summary, result_finding_id=result, explanation_finding_id=explanation,
        comparability_reason=case["context"], temporal_context=case["timeline"], authority_context=case["authority"],
        uncertainty_reason=case["limit"])
    add("practice_candidate", id=identifier(f"{key}-candidate"), scope_id=event_scope, event_id=event, relation_id=relation,
        state="eligible", reason=case["context"], passage_ids=json.dumps([passages[ref]["id"] for ref in refs]))
    if case["role"]:
        text, role_refs = case["role"]
        role = finding(f"{key}-objection", text, role_refs)
        add("practice_contribution", id=identifier(f"{key}-contribution"), event_id=event, party_id="tip",
            actor_id=actor, contribution_kind="objection", finding_id=role, authority_passage_id=None,
            membership_passage_id=None, responsibility_limit=case["authority"])

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
targets = rules.practice_review_package_targets(
    snapshot, records, {row["values"]["id"] for row in entries if row["kind"] == "passage"}, party_id="tip"
)
reviews = review["practice_source_review"]
existing = {(row["subject_kind"], row["subject_id"]) for row in reviews}
assert existing <= targets.keys()
by_id = {row["id"]: row for row in passages.values()}
for kind, ident in sorted(targets.keys() - existing):
    refs, _ = targets[kind, ident]
    inspected = [by_id[ref] for ref in sorted(refs)]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        source_version_ids=json.dumps(sorted({row["version_id"] for row in inspected})), passage_ids=json.dumps(sorted(refs)),
        inspected_sections=json.dumps([row["section"] for row in inspected], ensure_ascii=False),
        supported_claim=" ".join(row["section"] for row in inspected),
        limitations="Parti tutumu, karar ve yayım tarihi ile yargılama aşaması ayrı incelendi.",
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün belge pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id="tip", target_keys=set(targets))
refs = [{key: row[key] for key in ("subject_kind", "subject_id")} for row in reviews]
assert [len(records[table]) for table in ("practice_event", "practice_relation", "practice_closure")] == [78, 60, 0]
for suffix, value in (("", package), ("-review", review)):
    value["source_review_refs"] = refs
    path = output_dir / f"tip-istanbul-sozlesmesi{suffix}-draft.json"
    with path.open("x") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(sha256(path.read_bytes()).hexdigest(), path)
