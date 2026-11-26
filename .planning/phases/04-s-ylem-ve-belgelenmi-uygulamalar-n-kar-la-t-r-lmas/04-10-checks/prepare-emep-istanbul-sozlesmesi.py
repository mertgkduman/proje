"""Compare EMEP’s documented position with the Istanbul Convention decisions."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
import uygulamalar as rules


checks = Path(__file__).resolve().parent
source_folder = Path(sys.argv[1]).resolve()
output_dir = Path(sys.argv[2]).resolve()
practices = Path("data/practices")
source_root = practices / "sources" / "emep"
prefix = "0410-emep-istanbul-sozlesmesi"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")


def read(path):
    return json.loads(path.read_bytes())


base_paths = [
    practices / f"04-emep{suffix}.json" for suffix in ("", "-review")
]
assert [sha256(path.read_bytes()).hexdigest() for path in base_paths] == [
    "276844791716e0f4080dd4150425362dc6bd340f6f33e1a798001b2d4a2bce11",
    "2694a8b41ac5b561b96f3d137f5fd7f6c482053209c2144243de9a68a26fde4a",
]
package, review = map(read, base_paths)
entries, records = package["entries"], package["practice_records"]


def insert(table, **values):
    entries.append({"kind": table, "values": values})


def add(table, **values):
    records[table].append(values)


def identifier(key):
    return f"{prefix}-{key}"


def store(path, content, *, original=None):
    target = source_root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes() == content, target
    elif original:
        os.link(original, target)
    else:
        target.write_bytes(content)


tip_checks = checks.parent / "04-05-checks"
government = tip_checks / "istanbul-sozlesmesi-case-sources"
local = {row["path"]: row for row in read(government / "reading.json")["captures"] if row["status"]==200}
captures = {row["key"]: row for row in read(source_folder / "capture.json")}
sources = {}
for key, path, capture, day, pub_day, kind, publisher, author, title, basis in (
    ("stance", source_folder/"stance.html.bin", captures["stance"], "2020-08-28", "2020-08-28",
     "party_publication", "Emek Partisi", "Şükran Doğan", "Kadınlar Eşitlik Talebinden Vazgeçmeyecek",
     "28 Ağustos 2020 tarihli Emek Partisi genel başkan yardımcısı imzası; API’de aynı özgün gövdeyle iki yayın kodu var."),
    ("reaction", source_folder/"reaction.html.bin", captures["reaction"], "2021-03-20", "2021-03-20",
     "party_publication", "Emek Partisi", "Selma Gürkan", "İstanbul Sözleşmesi’nden Vazgeçmiyoruz",
     "20 Mart 2021 tarihli parti yayınında Emek Partisi genel başkan yardımcısının imzası ve feshe itirazı."),
    ("3718", government/"rg-3718.pdf", local["rg-3718.pdf"], "2021-03-19", "2021-03-20",
     "official", "Resmî Gazete", "Cumhurbaşkanlığı", "19 Mart 2021 tarihli 3718 sayılı Cumhurbaşkanı Kararı",
     "31429 sayılı Resmî Gazete’nin karar sayfası. Fesih hükmü görsel olarak okundu."),
    ("3928", government/"rg-3928.pdf", local["rg-3928.pdf"], "2021-04-29", "2021-04-30",
     "official", "Resmî Gazete", "Cumhurbaşkanlığı", "29 Nisan 2021 tarihli 3928 sayılı Cumhurbaşkanı Kararı",
     "31470 sayılı Resmî Gazete’nin karar sayfası. Türkiye bakımından 1 Temmuz 2021 sona erme tarihi görsel olarak okundu."),
):
    raw = path.read_bytes()
    assert sha256(raw).hexdigest()==capture["sha256"] and capture["status"]==200
    pdf = path.suffix == ".pdf"
    archive = Path("objects", capture["sha256"])
    original, readable = archive/("original.pdf" if pdf else "original.html.bin"), archive/"readable.html"
    store(original, raw, original=path if pdf else None)
    store(readable, readable_bytes(raw,"pdf" if pdf else "html",legacy=False))
    document, version = identifier(key), identifier(f"{key}-v1")
    url = capture["final_url"]
    insert("document", id=document, party_id="emep", title=title, source_kind="official" if kind=="official" else "party")
    insert("document_version", id=version, document_id=document, original_url=capture["url"], final_url=url,
           document_date=day, date_precision="day", date_unknown_reason=None, version_label=title,
           accessed_at=capture["retrieved_at_utc"], verified_at=now, mime="application/pdf" if pdf else "text/html",
           sha256=capture["sha256"], original_path=str(original), readable_path=str(readable))
    insert("source_attribution", version_id=version, kind=kind, publisher=publisher, author=author, social_handle=None,
           published_at=pub_day, date_precision="day", public_url=url, basis=basis)
    if not pdf:
        view=build_view(raw,url,source_root,fetch_assets=False)
        validate_view(source_root,view)
        insert("archive_view",**view,version_id=version)
    sources[key]=path,version,url,day

passages={}
for key, source, page, exact, section in (
    ("stance-text","stance",None,"sözleşmeyi derhal uygulamalıdır.",
     "28 Ağustos 2020 parti yayını. Şükran Doğan’ın sözleşmeden çekilme gündemini bitirme ve sözleşmeyi uygulama çağrısı."),
    ("stance-withdrawal","stance",None,"sözleşmeden çekilme gündeminin kalıcı olarak ortadan kaldırıldığını",
     "Açıklamanın sözleşmeden çekilmeye ilişkin aynı paragrafı."),
    ("reaction-text","reaction",None,"İstanbul Sözleşmesi’nden vazgeçmiyoruz!</strong>",
     "20 Mart 2021 parti yayını, Selma Gürkan’ın fesih kararına ilişkin açık itirazı."),
    ("withdrawal-id","3718",0,"Karar Sayısı: 3718\n19 Mart 2021",
     "3718 karar başlığı ve karar günü. Görsel gövdede fesih hükmü."),
    ("withdrawal-publication","3718",0,"20 Mart 2021 CUMARTESİ\nSayı : 31429",
     "3718 sayılı kararın yayım günü ve Resmî Gazete sayısı."),
    ("effect-id","3928",0,"Karar Sayısı: 3928\n29 Nisan 2021",
     "3928 karar başlığı ve karar günü. Görsel gövde 1 Temmuz 2021 sona erme tarihini tespit ediyor."),
    ("effect-publication","3928",0,"30 Nisan 2021 CUMA\nSayı : 31470",
     "3928 sayılı kararın yayım günü ve Resmî Gazete sayısı."),
):
    path, version, _, _ = sources[source]
    content=html_source_text(path.read_bytes()) if page is None else pdf_page_text(path,page)
    assert exact in content,(key,repr(exact))
    row=dict(id=identifier(key),version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,
             pdf_page_index=page,printed_page=None)
    insert("passage",**row)
    passages[key]=row

scope_rows = {
    (row["topic_id"], row["research_kind"]): row
    for row in read(practices / "04-inventory.json")["cells"] if row["party_id"] == "emep"
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
    insert("finding", id=ident, party_id="emep", heading="Belgelenmiş uygulamalar", pair_id=quote_pair or ident,
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
add_scope(topic,"statement","stance")
for source in ("3718","3928","reaction"):
    event_scope=add_scope(topic,"event",source)
summary=finding("stance-summary",
    "EMEP Genel Başkan Yardımcısı Şükran Doğan, 28 Ağustos 2020’de çekilme gündeminin bitirilmesini ve İstanbul Sözleşmesi’nin uygulanmasını istedi.",
    ("stance-text","stance-withdrawal"))
quote=finding("stance-quote",passages["stance-text"]["exact"],("stance-text",),quote_pair=summary)
statement=identifier("statement")
add("practice_statement",id=statement,party_id="emep",topic_id=topic,taxonomy_version=4,summary_finding_id=summary,
    quote_finding_id=quote,statement_at="2020-08-28",date_precision="day",version_id=sources["stance"][1],
    period_basis="28 Ağustos tarihli EMEP yayını ve genel başkan yardımcısı imzası.",
    uncertainty_reason="Aynı gövdenin API’de iki kayıt kodu var. Bu paket tek açıklama kullanıyor.",
    comparison_row_id="04-03-v3-0309-emep-program-030-1-row")
event=identifier("event")
tip=read(tip_checks/"tip-istanbul-sozlesmesi-draft.json")
tip_event=next(r for r in tip["practice_records"]["practice_event"] if r["id"]=="0405-tip-istanbul-sozlesmesi-withdrawal-event")
assert tip_event["common_event_key"]=="cumhurbaskanligi-2021-03-19-3718"
add("practice_event",id=event,common_event_key=tip_event["common_event_key"],event_at=tip_event["event_at"],
    date_precision="day",date_unknown_reason=None,title=tip_event["title"],scope_context=tip_event["scope_context"],
    occurrence_basis="Resmî Gazete’nin 31429 sayısındaki 3718 kararı ve 31470 sayısındaki 3928 kararı.")
points=(("withdrawal-id","action"),("withdrawal-publication","result"),("effect-id","result"),("effect-publication","result"))
limit="Sözleşmeden ayrılmanın fiilî sonuçları ve EMEP’in karar alma sürecinde rolü için ayrı kanıt gerekiyor."
for key,stage in points:
    row=passages[key]
    add("practice_event_evidence",event_id=event,passage_id=row["id"],stage=stage,supported_point=row["section"],
        concrete_basis=row["section"],limitation=limit,epistemic_type="claim")
    add("practice_evidence_assessment",event_id=event,passage_id=row["id"],stage=stage,basis_kind="document")
official=tuple(key for key,_ in points)
result=finding("result","3718 sayılı fesih kararı 20 Mart 2021’de yayımlandı. 3928 sayılı karar Türkiye bakımından sona erme tarihini 1 Temmuz olarak tespit etti.",official)
explanation=finding("comparison",
    "EMEP’in Ağustos açıklaması sözleşmenin uygulanmasını istedi. Cumhurbaşkanı 19 Mart’ta feshe karar verdi. EMEP genel başkan yardımcısı 20 Mart’ta karara itirazını yayımladı.",
    ("stance-text","stance-withdrawal","reaction-text",*official))
relation=identifier("relation")
add("practice_relation",id=relation,party_id="emep",topic_id=topic,scope_id=event_scope,statement_id=statement,
    event_id=event,target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,
    comparability_reason="Dönem açıklaması ve Cumhurbaşkanı kararı aynı sözleşmeye ilişkin. Faz 3 satırı ayrımcılık ve şiddet konusuna bağlanıyor.",
    temporal_context="28 Ağustos 2020 EMEP çağrısı. 19 Mart 2021 fesih, 20 Mart yayım ve EMEP itirazı. 29 Nisan 3928 sayılı karar, 1 Temmuz sona erme.",
    authority_context="Kararları Cumhurbaşkanı verdi. EMEP’in belgelenen rolü, 20 Mart tarihli parti açıklamasında itirazını yayımlamak.",
    uncertainty_reason=limit)
add("practice_candidate",id=identifier("candidate"),scope_id=event_scope,event_id=event,relation_id=relation,
    state="eligible",reason="Aynı sözleşmenin uygulanmasına ilişkin parti tutumu ve fesih işlemi.",
    passage_ids=json.dumps([passages[key]["id"] for key in official]))
actor=identifier("institution")
insert("actor",id=actor,kind="institution",party_id="emep",person_id=None,authorization_passage_id=None)
role=finding("published-objection",
    "EMEP Genel Başkan Yardımcısı Selma Gürkan, 20 Mart 2021 tarihli parti açıklamasında feshe itiraz etti.",
    ("reaction-text","withdrawal-id"))
add("practice_contribution",id=identifier("objection"),event_id=event,party_id="emep",actor_id=actor,
    contribution_kind="objection",finding_id=role,authority_passage_id=None,membership_passage_id=None,
    responsibility_limit="Rol, yayımlanmış itirazla sınırlı. Cumhurbaşkanı kararına katılım ve yargı davası için ayrı kanıt gerekir.")

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
    snapshot, records, {row["values"]["id"] for row in entries if row["kind"] == "passage"}, party_id="emep"
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
        limitations="EMEP’in açıklama ve itirazı, 3718 ile 3928 sayılı kararların tarih ve yetkisinden ayrı incelendi.",
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün belge pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id="emep", target_keys=set(targets))
refs = [{key: row[key] for key in ("subject_kind", "subject_id")} for row in reviews]
assert [len(records[table]) for table in ("practice_event", "practice_relation", "practice_closure")] == [88, 82, 0]
for suffix, value in (("", package), ("-review", review)):
    value["source_review_refs"] = refs
    path = output_dir / f"emep-istanbul-sozlesmesi{suffix}-draft.json"
    with path.open("x") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(sha256(path.read_bytes()).hexdigest(), path)
