"""Build two TİP comparisons with the Idlib protocol and April labour law."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
import uygulamalar as rules


checks = Path(__file__).resolve().parent
assert len(sys.argv) in (1, 2)
output_dir = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else checks
practices = Path("data/practices")
source_root = practices / "sources" / "tip"
prefix = "0405-tip-2020-policy"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")


def read(path):
    return json.loads(path.read_bytes())


base_paths = [
    checks / f"tip-2020-local-events{suffix}-draft.json" for suffix in ("", "-review")
]
assert [sha256(path.read_bytes()).hexdigest() for path in base_paths] == [
    "5314a31eb4ae250319aaa9cf102eb1a0385c23495ec394582af12341cd35c576",
    "c06cfb76bad60b39d9939673f1cf97f6c6df175f2cf13b19b78bd88121068665",
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


april = checks / "april-2020-event-sources"
captures = {
    row["capture"]["path"]: (april, row["capture"])
    for row in read(april / "reading.json")["sources"]
}
for batch, index in ((22, 160), (23, 162)):
    folder = checks / "tip-publication-catalog" / f"party-statements-{batch}"
    path = f"{index}.html.bin"
    capture = next(row for row in read(folder / "capture.json") if row["path"] == path)
    receipt = next(row for row in read(folder / "reading.json")["records"] if row["i"] == index)
    assert capture["sha256"] == receipt["original_sha256"]
    captures[path] = folder, capture

sources = {}
for key, filename, day, kind, publisher, title, basis in (
    ("idlib-call", "162.html.bin", "2020-02-03", "party_publication", "Türkiye İşçi Partisi",
     "Saraylar Savaş, Halklar Barış İstiyor", "TİP’in 3 Şubat tarihli özgün parti açıklaması."),
    ("idlib-bm", "un-s-2020-187.pdf", "2020-03-06", "official", "Birleşmiş Milletler Güvenlik Konseyi",
     "S/2020/187, Türkiye ve Rusya temsilcilerinin ortak iletimi ve eki",
     "6 Mart tarihli iletimin ekinde 5 Mart Moskova protokolü."),
    ("izin-call", "160.html.bin", "2020-03-12", "party_publication", "Türkiye İşçi Partisi",
     "Salgına Karşı Kamusal Çözüm!", "TİP’in 12 Mart tarihli özgün parti açıklaması."),
    ("izin-rg", "rg-7244.html.bin", "2020-04-17", "official", "Resmî Gazete",
     "7244 sayılı Kanun, Resmî Gazete 31102", "16 Nisan kabul edilen metnin 17 Nisan yayımı."),
):
    folder, capture = captures[filename]
    path = folder / filename
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == capture["sha256"]
    pdf = path.suffix == ".pdf"
    media = "pdf" if pdf else "html"
    mime = "application/pdf" if pdf else "text/html"
    storage = Path("objects", capture["sha256"])
    original = storage / ("original.pdf" if pdf else "original.html.bin")
    readable = storage / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, media, legacy=False))
    document, version = identifier(key), identifier(f"{key}-v1")
    url = capture["final_url"]
    insert("document", id=document, party_id="tip", title=title, source_kind="official" if kind == "official" else "party")
    insert("document_version", id=version, document_id=document, original_url=capture["url"], final_url=url,
           document_date=day, date_precision="day", date_unknown_reason=None, version_label=title,
           accessed_at=capture["retrieved_at_utc"], verified_at=now, mime=mime, sha256=capture["sha256"],
           original_path=str(original), readable_path=str(readable))
    insert("source_attribution", version_id=version, kind=kind, publisher=publisher, author=None,
           social_handle=None, published_at=day, date_precision="day", public_url=url, basis=basis)
    if not pdf:
        view = build_view(raw, url, source_root, fetch_assets=False)
        validate_view(source_root, view)
        insert("archive_view", **view, version_id=version)
    sources[key] = path, version, url, day

passages = {}
for key, source, page, article, exact, section in (
    ("idlib-target", "idlib-call", None, None, "TSK Suriye’den çekilmeli, Ankara ile Şam arasında doğrudan temas",
     "3 Şubat TİP açıklaması, askerlerin çekilmesi ve Ankara–Şam teması."),
    ("idlib-signature", "idlib-bm", 1, None, "Done in Moscow on 5 March, 2020",
     "S/2020/187 eki, 5 Mart Moskova imzası."),
    ("idlib-start", "idlib-bm", 1, "1", "starting from 00:01 of March 6, 2020.",
     "S/2020/187 eki madde 1, İdlib temas hattında ateşkesin öngörülen başlangıcı."),
    ("idlib-patrol", "idlib-bm", 1, "3", "joint Turkish-Russian patrolling will begin",
     "S/2020/187 eki madde 3, 15 Mart için ortak devriye düzenlemesi."),
    ("idlib-transmission", "idlib-bm", 0, None, "Letter dated 6 March 2020",
     "S/2020/187 mektubu, BM’ye 6 Mart iletimi."),
    ("izin-target", "izin-call", None, None, "en az iki hafta ücretli idari izin verilmelidir.",
     "12 Mart TİP açıklaması, kalabalık ortamlarda çalışan emekçiler için ücretli izin talebi."),
    ("izin-accept", "izin-rg", None, None, "16/4/2020</span>",
     "7244 başlığı, 16 Nisan kabul ve 17 Nisan Resmî Gazete yayımı."),
    ("izin-protection", "izin-rg", None, "9", "dışında işveren tarafından feshedilemez.",
     "Madde 9 ile eklenen geçici madde 10, istisnalı fesih sınırlaması."),
    ("izin-unpaid", "izin-rg", None, "9", "işveren işçiyi tamamen veya kısmen ücretsiz",
     "Geçici madde 10, ilk halinde üç ayı geçmeyen tam veya kısmi ücretsiz izin yetkisi."),
    ("izin-support", "izin-rg", None, "7", "kısa\r\n    çalışma ödeneğinden yararlanamayan işçiler",
     "Madde 7, nakdi ücret desteği için ayrı koşullar."),
    ("izin-effective", "izin-rg", None, "17", "Diğer maddeleri yayımı tarihinde,",
     "Madde 17(c), 9. maddenin 17 Nisan yayımıyla yürürlüğe girmesi."),
):
    path, version, url, _ = sources[source]
    content = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in content, (key, repr(exact))
    row = dict(id=identifier(key), version_id=version, exact=exact, prefix=None, suffix=None,
               article=article, section=section, pdf_page_index=page, printed_page="2" if page == 1 else None)
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


cases = (
    dict(key="idlib", topic="dis-politika", row="04-03-v3-0304-tip-program-ortadogu-row", source="idlib-bm",
         day="2020-03-05", common="idlib-2020-03-05-moskova-ek-protokol",
         title="Türkiye ve Rusya’nın İdlib ek protokolü",
         summary="TİP, 3 Şubat’ta Türk Silahlı Kuvvetlerinin Suriye’den çekilmesini ve Ankara ile Şam arasında doğrudan temas kurulmasını istedi.",
         context="TİP’in İdlib bağlamındaki çekilme ve diplomasi talebi ile Türkiye ve Rusya arasındaki İdlib protokolü aynı bölgesel gelişmeyle ilgili.",
         event_context="5 Mart 2020’de Moskova’da Türkiye ve Rusya’nın İdlib Gerginliği Azaltma Bölgesi için imzaladığı ek protokol.",
         occurrence="Türkiye ve Rusya temsilcilerinin 6 Mart tarihli S/2020/187 ortak iletimi ve ekindeki protokol.",
         outcome="Türkiye ve Rusya 5 Mart’ta Moskova’da İdlib protokolünü imzaladı. Metin, temas hattında askerî faaliyetlerin 6 Mart 00.01’den itibaren durdurulmasını öngördü.",
         comparison="TİP’in talebi Suriye’den çekilme ve Ankara–Şam temasıydı. Protokol, Türkiye ile Rusya arasında İdlib’de çatışmanın durdurulması ve devriye düzenlemeleri getirdi. Taraflar ve düzenlemenin kapsamı farklı.",
         authority="TİP açıklamayı yayımladı. Protokolün tarafları Türkiye ve Rusya, mektubun muhatabı BM Güvenlik Konseyi Başkanı.",
         timeline="3 Şubat parti açıklaması. 5 Mart protokol imzası. 6 Mart 00.01 öngörülen ateşkes başlangıcı ve 6 Mart tarihli BM iletimi.",
         uncertainty="Ateşkesin sahadaki seyri, asker çekilmesi, doğrudan temas ve partinin karara etkisi için ayrı kanıt gerekir.",
         points=(("idlib-signature", "action"), ("idlib-start", "result"), ("idlib-patrol", "result"), ("idlib-transmission", "result"))),
    dict(key="izin", topic="ekonomi-emek-v2", row="04-03-v3-0304-tip-program-ucret-row", source="izin-rg",
         day="2020-04-16", common="tbmm-2020-04-16-7244-kabul",
         title="7244 sayılı Kanunla fesih sınırı ve ücretsiz izin düzenlemesi",
         summary="TİP, 12 Mart’ta salgın nedeniyle kalabalık ortamlarda çalışan emekçilere en az iki hafta ücretli idari izin verilmesini istedi.",
         context="Salgında çalışma ilişkileri ve gelir güvencesi hakkında 12 Mart tarihli parti açıklaması ile Nisan ayındaki yasal düzenleme.",
         event_context="7244 sayılı Kanunun 9. maddesiyle getirilen fesih sınırı ve tam veya kısmi ücretsiz izin düzenlemesi.",
         occurrence="7244’ün 17 Nisan 2020 tarih ve 31102 sayılı Resmî Gazete’deki ilk metni.",
         outcome="7244 sayılı Kanun 16 Nisan’da kabul edildi. 9. madde, istisnalı bir fesih sınırı ile üç ayı geçmeyen tam veya kısmi ücretsiz izin yetkisi getirdi.",
         comparison="Parti, ücretli idari izin önerdi. İlk kanun metni ücretsiz izni mümkün kılıyor ve işten çıkarma için istisnalı bir sınır koyuyor. Nakdi ücret desteği ayrı şartlara bağlı.",
         authority="TİP açıklamayı yayımladı. Kanunu TBMM kabul etti. Geçici düzenleme işverenin izin yetkisini ve fesih sınırlarını düzenledi.",
         timeline="12 Mart parti açıklaması. 16 Nisan TBMM kabulü. 17 Nisan sayısında yayımlanan 9. madde o tarihte yürürlüğe girdi.",
         uncertainty="Sonraki değişiklikler, kişi bazında işveren uygulaması ve fiilî ödemeler ayrı kaynak gerektiriyor. Parti katkısına dair kanıt yok.",
         points=(("izin-accept", "action"), ("izin-protection", "result"), ("izin-unpaid", "result"), ("izin-support", "result"), ("izin-effective", "result"))),
)

for case in cases:
    key, topic = case["key"], case["topic"]
    source, target = f"{key}-call", f"{key}-target"
    add_scope(topic, "statement", source)
    event_scope = add_scope(topic, "event", case["source"])
    _, version, _, day = sources[source]
    summary = finding(f"{key}-summary", case["summary"], (target,))
    quote = finding(f"{key}-quote", passages[target]["exact"], (target,), quote_pair=summary)
    statement = identifier(f"{key}-statement")
    add("practice_statement", id=statement, party_id="tip", topic_id=topic, taxonomy_version=4,
        summary_finding_id=summary, quote_finding_id=quote, statement_at=day, date_precision="day", version_id=version,
        period_basis="TİP sitesinin tarihli özgün parti açıklaması.", uncertainty_reason=case["uncertainty"],
        comparison_row_id=case["row"])
    event = identifier(f"{key}-event")
    add("practice_event", id=event, common_event_key=case["common"], event_at=case["day"], date_precision="day",
        date_unknown_reason=None, title=case["title"], scope_context=case["event_context"], occurrence_basis=case["occurrence"])
    refs = tuple(ref for ref, _ in case["points"])
    for ref, stage in case["points"]:
        row = passages[ref]
        add("practice_event_evidence", event_id=event, passage_id=row["id"], stage=stage, supported_point=row["section"],
            concrete_basis=row["section"], limitation=case["uncertainty"], epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=row["id"], stage=stage, basis_kind="document")
    result = finding(f"{key}-result", case["outcome"], refs)
    explanation = finding(f"{key}-comparison", case["comparison"], (target, *refs))
    relation = identifier(f"{key}-relation")
    add("practice_relation", id=relation, party_id="tip", topic_id=topic, scope_id=event_scope, statement_id=statement,
        event_id=event, target_finding_id=summary, result_finding_id=result, explanation_finding_id=explanation,
        comparability_reason=case["context"], temporal_context=case["timeline"], authority_context=case["authority"],
        uncertainty_reason=case["uncertainty"])
    add("practice_candidate", id=identifier(f"{key}-candidate"), scope_id=event_scope, event_id=event, relation_id=relation,
        state="eligible", reason=case["context"], passage_ids=json.dumps([passages[ref]["id"] for ref in refs]))

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
        limitations="Parti talebi, kurumun yetkisi, kararın tarihi ve uygulama sınırı ayrı incelendi.",
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün belge pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id="tip", target_keys=set(targets))
refs = [{key: row[key] for key in ("subject_kind", "subject_id")} for row in reviews]
assert [len(records[table]) for table in ("practice_event", "practice_relation", "practice_closure")] == [65, 56, 0]
for suffix, value in (("", package), ("-review", review)):
    value["source_review_refs"] = refs
    path = output_dir / f"tip-2020-policy{suffix}-draft.json"
    with path.open("x") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(sha256(path.read_bytes()).hexdigest(), path)
