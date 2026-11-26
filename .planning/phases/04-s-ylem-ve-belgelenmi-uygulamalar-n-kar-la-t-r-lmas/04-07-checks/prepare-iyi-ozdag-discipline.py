"""Stage the İYİ Parti disciplinary decision and subsequent judicial review."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
import uygulamalar as rules


checks = Path(__file__).resolve().parent
source_folder = Path(sys.argv[1]).resolve()
output_dir = Path(sys.argv[2]).resolve()
practices = Path("data/practices")
source_root = practices / "sources" / "iyi"
prefix = "0407-iyi-ozdag-2020-2021"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")


def read(path):
    return json.loads(path.read_bytes())


base_paths = [
    practices / f"04-iyi{suffix}.json" for suffix in ("", "-review")
]
assert [sha256(path.read_bytes()).hexdigest() for path in base_paths] == [
    "1a0960a4d5eac4c029cfad9e985bc13c1c46ae05a3834cd887e5ccb0e66835bf",
    "e10e4e42084be8a82108dd93b13a0c7a30cd92e68de84f80e11d3962121ff0ad",
]
package, review = map(read, base_paths)
entries, records = package["entries"], package["practice_records"]


def insert(table, **values):
    entries.append({"kind": table, "values": values})


def add(table, **values):
    records[table].append(values)


def identifier(key):
    return f"{prefix}-{key}"


def store(path, content):
    target = source_root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes() == content, target
    else:
        target.write_bytes(content)


captures = {row["key"]: row for row in read(source_folder / "capture.json")}
captures.update({row["key"]:row for row in read(source_folder / "capture-retry.json") if row["status"] == 200})
sources = {}
for key, title, author, basis in (
    ("aa-decision", "Ümit Özdağ hakkında 16 Kasım 2020 tarihli ihraç kararı", "Ferdi Türkten, Esin Işık",
     "Anadolu Ajansı’nın olay günündeki haberi. Müşterek Disiplin Kurulu ve kesin çıkarma hükmünü aktarıyor."),
    ("sozcu-decision", "Sözcü’nün aktardığı İYİ Parti ihraç açıklaması", None,
     "16 Kasım haberi, İYİ Parti açıklamasını ayrı alıntı olarak aktarıyor. Sayfa 27 Kasım’da güncellendi."),
    ("aa-ruling", "Ankara 1. Asliye Hukuk Mahkemesinin ihraç kararı hakkında hükmü", "Serdar Açıl",
     "Anadolu Ajansı’nın 13 Ocak 2021 duruşma haberi, vekil beyanları ve mahkemenin kısa hükmü."),
    ("aa-reasons", "13 Ocak hükmünün gerekçesi hakkında 20 Ocak haberi", "Tanju Özkaya, Serdar Açıl",
     "Anadolu Ajansı, taraflara tebliğ edilen gerekçeli kararın ilgili bölümünü aktarıyor. Tam karar nüshası açık."),
    ("aa-reaction", "İYİ Parti Genel Sekreterinin iptal kararına açıklaması", "Esin Işık",
     "Anadolu Ajansı, Uğur Poyraz’ın 14 Ocak tarihli Habertürk açıklamasını aktarıyor. Gerekçeli karar öncesindeki parti beyanı."),
):
    capture = captures[key]
    path = Path(capture["path"])
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == capture["sha256"] and capture["status"] == 200
    storage = Path("objects", capture["sha256"])
    original = storage / "original.html.bin"
    readable = storage / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, "html", legacy=False))
    document, version = identifier(key), identifier(f"{key}-v1")
    url, day = capture["final_url"], capture["publication_day"]
    insert("document", id=document, party_id="iyi", title=title, source_kind="journalism")
    insert("document_version", id=version, document_id=document, original_url=capture["url"], final_url=url,
           document_date=day, date_precision="day", date_unknown_reason=None, version_label=title,
           accessed_at=capture["retrieved_at_utc"], verified_at=now, mime="text/html", sha256=capture["sha256"],
           original_path=str(original), readable_path=str(readable))
    insert("source_attribution", version_id=version, kind="journalism", publisher=capture["publisher"], author=author,
           social_handle=None, published_at=day, date_precision="day", public_url=url, basis=basis)
    view = build_view(raw, url, source_root, fetch_assets=False)
    validate_view(source_root, view)
    insert("archive_view", **view, version_id=version)
    sources[key] = path, version, url, day

base = read(Path("data/releases") / package["base_release"] / "records.json")
charter = next(row for row in base["document_version"] if row["id"] == "0205-iyi-charter-istanbul-v1")
charter_path = Path("data") / charter["original_path"]
assert sha256(charter_path.read_bytes()).hexdigest() == charter["sha256"]
sources["charter"] = charter_path, charter["id"], charter["final_url"], charter["document_date"]

passages = {}
for key, source, page, article, exact, section in (
    ("charter-board","charter",45,"75","İYİ Partili milletvekilleri hakkındaki partiden geçici veya kesin olarak çıkarma cezasını gerektiren fiil ve eylemlerle\nilgili soruşturmaları kesin olarak karara bağlar.",
     "20 Eylül 2020 değişiklikli tüzüğün 75. maddesi. Kurul, parti milletvekillerine ilişkin geçici veya kesin çıkarma soruşturmalarını karara bağlar."),
    ("charter-sevk","charter",44,"71","Disiplin kuruluna sevk kararlarının isnat olunan fiil ile uygulanması istenen disiplin cezasını ve nedenlerini açıklar\nşekilde gerekçeli olması zorunludur.",
     "Madde 71. Disipline sevkin isnat ve ceza bakımından gerekçeli olması."),
    ("charter-review","charter",47,"76","nihai karar niteliğindeki son karara karşı otuz gün içinde nihai kararı veren mercinin bulunduğu yerdeki Asliye Hukuk\nMahkemesi’ne itiraz edebilir.",
     "Madde 76. Şekil, usul ve yetki itirazlarında parti içi yolların ardından asliye hukuk mahkemesine başvuru."),
    ("charter-finality","charter",47,"76","Siyasi Partiler Kanunu’nun 57’nci maddesine göre verilen bu karar kesindir.",
     "Madde 76. Tüzükteki yargı kararının kesinliği hükmü."),
    ("board-decision","aa-decision",None,None,"kesin olarak çıkarılmasına oy birliğiyle karar verildi.",
     "Anadolu Ajansı, Müşterek Disiplin Kurulunun 16 Kasım’da oybirliğiyle kesin çıkarma kararı verdiğini aktarıyor."),
    ("board-date","sozcu-decision",None,None,"16.11.2020 tarihli toplantısında",
     "Sözcü’nün alıntıladığı İYİ Parti açıklaması, Müşterek Disiplin Kurulu toplantısını 16 Kasım olarak tarihlendiriyor."),
    ("board-membership","sozcu-decision",None,None,"Kurucular Kurulu Üyeliği de dahil olmak üzere KESİN OLARAK ÇIKARILMASINA",
     "Parti açıklamasının Sözcü’deki aktarımı, çıkarma kararının kurucular kurulu üyeliğini de kapsadığını belirtiyor."),
    ("court-ruling","aa-ruling",None,None,"Disiplin Kurulu kararının iptaline kesin olarak hükmetti.",
     "13 Ocak duruşma haberi, Ankara 1. Asliye Hukuk Mahkemesinin iptal hükmü."),
    ("court-defense","aa-ruling",None,None,"Genel Sekreterlik makamının sadece yazışma işlemini yürüttüğünü savundu.",
     "Aynı duruşma haberinde İYİ Parti vekilinin sevk yetkisi ve yazışma ayrımına dair savunması."),
    ("court-reasons","aa-reasons",None,None,"hakkındaki soruşturma sebeplerinin farklı olması",
     "20 Ocak yazısında aktarılan gerekçe, sevk ve soruşturma konularının ayrıca ihraç gerekçelerinin ayrışmasını usul sorunu olarak veriyor."),
    ("party-reaction","aa-reaction",None,None,"Bize göre, partideki tüzüğe aykırı hiçbir eylem yok.",
     "Uğur Poyraz’ın 14 Ocak açıklaması. Gerekçeli karar yayımlanmadan önceki parti görüşü."),
):
    path, version, _, _ = sources[source]
    content = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in content, (key, repr(exact))
    row=dict(id=identifier(key),version_id=version,exact=exact,prefix=None,suffix=None,article=article,section=section,
             pdf_page_index=page,printed_page=str(page) if page is not None else None)
    insert("passage", **row)
    passages[key]=row

scope_rows = {
    (row["topic_id"], row["research_kind"]): row
    for row in read(practices / "04-inventory.json")["cells"] if row["party_id"] == "iyi"
}


def add_scope(topic, lane, source):
    scope = scope_rows[topic, lane]
    scope_id = scope["cell_id"]
    if not any(row["id"] == scope_id for row in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope_id, **{key: scope[key] for key in
            ("party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="20 Eylül 2020 değişiklikli tüzük ve dönem olayı kaynakları incelendi. Kapsam açık.")
    _, version, url, _ = sources[source]
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    add("practice_scope_source", scope_id=scope_id, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(sections, ensure_ascii=False))
    attempt = identifier(f"{topic}-{lane}-{source}-reading")
    add("practice_attempt_v2", id=attempt, scope_id=scope_id, attempted_at=now, query=url, url=url, result="examined",
        reason="Tarih, yetki, kaynak metni ve işlem sınırları incelendi.", source_version_id=version)
    if not any(row["scope_id"] == scope_id and row["url"] == url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope_id, url=url,
            relevance_reason="Dönem tüzüğü, kurul kararı açıklaması veya olay günündeki duruşma haberi.",
            state="examined", attempt_ids=json.dumps([attempt]))
    return scope_id


def finding(key, content, refs, *, quote_pair=None):
    ident = identifier(key)
    provenance = "quote" if quote_pair else "summary"
    insert("finding", id=ident, party_id="iyi", heading="Belgelenmiş uygulamalar", pair_id=quote_pair or ident,
           text=content, provenance=provenance, epistemic_type="claim")
    insert("review", id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent",
           reviewed_at=now, result="reviewed", reason="Tarihli özgün kaynak pasajları incelendi.")
    for ref in refs:
        row = passages[ref]
        insert("finding_evidence", finding_id=ident, passage_id=row["id"], role="quotation" if quote_pair else "support")
        insert("verification", finding_id=ident, passage_id=row["id"], checked_at=now,
               result="confirmed", reason=row["section"])
    return ident


actor=identifier("institution")
insert("actor",id=actor,kind="institution",party_id="iyi",person_id=None,authorization_passage_id=None)
cases=(
    dict(key="board",topic="musterek-disiplin",row="04-03-v3-0306-iyi-musterek-disiplin-row",ref="charter-board",
         summary="20 Eylül 2020 değişiklikli tüzük, milletvekillerinin kesin çıkarma soruşturmalarında Müşterek Disiplin Kuruluna karar yetkisi veriyor.",
         day="2020-11-16",common="iyi-2020-11-16-musterek-disiplin-ozdag",
         title="İYİ Parti Müşterek Disiplin Kurulunun Ümit Özdağ kararı",
         context="Dönem tüzüğünde Müşterek Disiplin Kurulunun yetkisi ve bir milletvekili hakkındaki fiilî karar.",
         event_context="Kurulun İstanbul Milletvekili Ümit Özdağ hakkında 16 Kasım 2020 tarihli kesin çıkarma kararı.",
         occurrence="Anadolu Ajansı’nın olay günü haberi ve Sözcü’nün aktardığı İYİ Parti açıklaması.",
         outcome="İki dönem kaynağına göre Müşterek Disiplin Kurulu, 16 Kasım’da kurucular kurulu üyeliğini de kapsayan kesin çıkarma kararı verdi.",
         comparison="Müşterek Disiplin Kurulu dönem tüzüğünde belirtilen karar organı olarak hareket etti. Sevk ve savunma işlemlerinin usulü, daha sonraki yargı kararında ayrıca ele alındı.",
         authority="Kararı İYİ Parti Müşterek Disiplin Kurulu verdi. 13 Ocak 2021 iptalini Ankara 1. Asliye Hukuk Mahkemesi karara bağladı.",
         timeline="20 Eylül 2020 değişiklikli tüzük. 16 Kasım 2020 kurul kararı. 13 Ocak 2021 mahkeme kararı ayrı aşama.",
         limit="İmzalı kurul kararının tam nüshası, iç tebligat ve üye sicilinin işlem günleri açık.",
         evidence=(("board-decision","action"),("board-date","action"),("board-membership","result")),
         sources=("aa-decision","sozcu-decision"),extra=("charter-sevk",),role="İYİ Parti Müşterek Disiplin Kurulu, Ümit Özdağ hakkında kesin çıkarma kararını verdi."),
    dict(key="court",topic="disiplin-yargi-itiraz",row="04-03-v3-0306-iyi-disiplin-yargi-itiraz-row",ref="charter-review",
         summary="20 Eylül 2020 değişiklikli tüzük, kesin çıkarma kararına yetki, şekil ve usul bakımından asliye hukuk mahkemesinde itiraz yolunu düzenliyor.",
         day="2021-01-13",common="ankara-1-asliye-2021-01-13-ozdag-iyi-ihrac-iptal",
         title="Ümit Özdağ’ın İYİ Parti’den çıkarılmasına ilişkin yargı kararı",
         context="Dönem tüzüğünde yargı itiraz yolu ve 16 Kasım 2020 tarihli çıkarma kararına karşı açılan dava.",
         event_context="Ankara 1. Asliye Hukuk Mahkemesinin 13 Ocak 2021’de açıkladığı iptal hükmü.",
         occurrence="Anadolu Ajansı’nın 13 Ocak duruşma haberi ve gerekçeli kararın 20 Ocak aktarımı.",
         outcome="13 Ocak duruşma haberine göre Ankara 1. Asliye Hukuk Mahkemesi çıkarma kararını kesin olarak iptal etti. 20 Ocak haberi sevk, soruşturma ve karar gerekçelerindeki farkı usul sorunu olarak aktardı.",
         comparison="Dönem tüzüğünde yer alan yargı yoluna başvuruldu. 14 Ocak’ta İYİ Parti Genel Sekreteri parti işleminin tüzüğe uygun olduğu görüşünü açıkladı. Kararın gerekçesi 20 Ocak haberinde ayrı aktarıldı.",
         authority="Ümit Özdağ davacı, İYİ Parti davalı. İptal kararı Ankara 1. Asliye Hukuk Mahkemesine ait.",
         timeline="13 Ocak 2021 iptal hükmü, 14 Ocak parti açıklaması, 20 Ocak gerekçeli karar haberi.",
         limit="Gerekçeli mahkeme kararının tam nüshası, dosya numarası ve kişiye tebliğ günü açık.",
         evidence=(("court-ruling","action"),("court-reasons","result")),
         sources=("aa-ruling","aa-reasons","aa-reaction"),extra=("charter-finality","party-reaction","court-defense"),
         role="İYİ Parti davalı olarak duruşmada sevk işlemini savundu ve davanın reddini istedi."),
)
for case in cases:
    key, topic = case["key"], case["topic"]
    add_scope(topic,"statement","charter")
    for source in case["sources"]:
        event_scope=add_scope(topic,"event",source)
    target=case["ref"]
    summary=finding(f"{key}-summary",case["summary"],(target,))
    quote=finding(f"{key}-quote",passages[target]["exact"],(target,),quote_pair=summary)
    statement=identifier(f"{key}-statement")
    add("practice_statement",id=statement,party_id="iyi",topic_id=topic,taxonomy_version=4,
        summary_finding_id=summary,quote_finding_id=quote,statement_at=sources["charter"][3],date_precision="day",
        version_id=charter["id"],period_basis="20 Eylül 2020 değişiklikleri işlenmiş 54 sayfalık tüzük nüshası.",
        uncertainty_reason="Tüzük hükmünün yürütümü ayrı olay belgeleriyle değerlendirilir.",comparison_row_id=case["row"])
    event=identifier(f"{key}-event")
    add("practice_event",id=event,common_event_key=case["common"],event_at=case["day"],date_precision="day",
        date_unknown_reason=None,title=case["title"],scope_context=case["event_context"],occurrence_basis=case["occurrence"])
    refs=tuple(ref for ref,_ in case["evidence"])
    for ref,stage in case["evidence"]:
        row=passages[ref]
        add("practice_event_evidence",event_id=event,passage_id=row["id"],stage=stage,supported_point=row["section"],
            concrete_basis=row["section"],limitation=case["limit"],epistemic_type="claim")
        add("practice_evidence_assessment",event_id=event,passage_id=row["id"],stage=stage,basis_kind="independent_report")
    result=finding(f"{key}-result",case["outcome"],refs)
    explanation=finding(f"{key}-comparison",case["comparison"],(target,*refs,*case["extra"]))
    relation=identifier(f"{key}-relation")
    add("practice_relation",id=relation,party_id="iyi",topic_id=topic,scope_id=event_scope,statement_id=statement,
        event_id=event,target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,
        comparability_reason=case["context"],temporal_context=case["timeline"],authority_context=case["authority"],
        uncertainty_reason=case["limit"])
    add("practice_candidate",id=identifier(f"{key}-candidate"),scope_id=event_scope,event_id=event,relation_id=relation,
        state="eligible",reason=case["context"],passage_ids=json.dumps([passages[ref]["id"] for ref in refs]))
    role_refs=refs if key=="board" else ("court-ruling","court-defense")
    role=finding(f"{key}-role",case["role"],role_refs)
    add("practice_contribution",id=identifier(f"{key}-contribution"),event_id=event,party_id="iyi",
        actor_id=actor,contribution_kind="task" if key=="board" else "objection",finding_id=role,
        authority_passage_id=None,membership_passage_id=None,responsibility_limit=case["authority"])

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
    snapshot, records, {row["values"]["id"] for row in entries if row["kind"] == "passage"}, party_id="iyi"
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
        limitations="2020 tüzüğü, kurul ve mahkeme yetkileri ile açıklama ve karar tarihleri ayrı incelendi.",
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün belge pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id="iyi", target_keys=set(targets))
refs = [{key: row[key] for key in ("subject_kind", "subject_id")} for row in reviews]
assert [len(records[table]) for table in ("practice_event", "practice_relation", "practice_closure")] == [23, 15, 0]
for suffix, value in (("", package), ("-review", review)):
    value["source_review_refs"] = refs
    path = output_dir / f"iyi-ozdag-discipline{suffix}-draft.json"
    with path.open("x") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(sha256(path.read_bytes()).hexdigest(), path)
