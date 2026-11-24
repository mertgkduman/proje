"""Build TİP’s school, Montreux and Paris source comparisons."""

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
source_dir = checks / "tip-publication-catalog" / "party-statements-16"
source_root = working / "sources" / "tip"
case = "0405-tip-school-montro-paris"
party = "tip"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight-draft"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


pair = (checks / "tip-amasra-saopaulo-2022-draft.json", checks / "tip-amasra-saopaulo-2022-review-draft.json") if preflight else (
    working / "04-tip.json", working / "04-tip-review.json")
expected_base = (
    "f15b6ec948575b4962f6d640d68c2e861dbff079a5abf5ca4777466dedc63036",
    "74fc3636a7b53aa9db27e5a2a37a5c37ce7caf1e5bcbd1d020eb8f9b3d8400af",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [39, 37, 0]


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


source_rows = {}
for directory in (source_dir, source_dir.with_name("party-statements-17")):
    for row in read(directory / "capture.json"):
        source_rows[row["path"]] = (directory / row["path"], row)
    institution_dir = directory / "linked-institutions"
    for row in read(institution_dir / "reading.json")["linked_material"]:
        source_rows[row["path"]] = (institution_dir / row["path"], row)

sources = {}
for key, name, day, title, kind, publisher, author, basis in (
    ("school-statement", "129.html.bin", "2021-08-10", "10 Ağustos TİP okul açılışı çağrısı",
     "party_publication", "Türkiye İşçi Partisi", None, "Yüz yüze eğitim ve okul sağlığı koşullarına ilişkin tarihli TİP yayımı."),
    ("school-plan", "meb-20210819.html.bin", "2021-08-19", "MEB’in 6 Eylül yüz yüze eğitim duyurusu",
     "official", "Millî Eğitim Bakanlığı", None, "6 Eylül hedefi ve haftalık eğitim biçimi."),
    ("school-guide", "meb-covid-rehber-2021.pdf", None, "Okullarda salgın önlemleri rehberi",
     "official", "Millî Eğitim Bakanlığı", None, "2021’de yayımlanan rehberin aşı, maske, sınıf, havalandırma ve temizlik bölümleri."),
    ("school-aa", "aa-meb-20210906.html.bin", "2021-09-06", "6 Eylül yüz yüze eğitimin başlaması",
     "journalism", "Anadolu Ajansı", None, "Yeni eğitim yılının başladığı günkü haber ve yüz yüze eğitim paragrafı."),
    ("montro-statement", "121.html.bin", "2022-02-24", "24 Şubat TİP Montrö açıklaması",
     "party_publication", "Türkiye İşçi Partisi", None, "Montrö’yü ihlal edecek taleplere ilişkin TİP’in tarihli açıklaması."),
    ("montro-aa", "aa-montro-20220302.html.bin", "2022-03-02", "Dışişleri Bakanı’nın 19. madde açıklaması",
     "journalism", "Anadolu Ajansı", "Mustafa Deveci, Fuat Kabakcı",
     "2 Mart haberi Bakanın geçiş kurallarına ve istisnaya ilişkin açıklamasını aktarıyor."),
    ("montro-report", "mfa-2022-activity.pdf", None, "2022 Dışişleri Bakanlığı idare faaliyet raporu",
     "official", "Dışişleri Bakanlığı", None, "2022 raporu PDF indeks 83, 19. madde ve geçiş bildirimi."),
    ("paris-statement", "130.html.bin", "2021-08-05", "5 Ağustos TİP Paris Anlaşması çağrısı",
     "party_publication", "Türkiye İşçi Partisi", None, "Orman yangınları açıklamasında Paris Anlaşması’nın onaylanması talebi."),
    ("paris-law", "tbmm-paris-7335.html.bin", "2021-10-06", "7335 sayılı uygun bulma kanunu",
     "official", "TBMM", None, "6 Ekim kabulü ve beyanla birlikte onayın uygun bulunması."),
    ("paris-un", "un-paris-cn294.pdf", "2021-10-13", "BM Paris Anlaşması depoziter bildirimi",
     "official", "Birleşmiş Milletler", None, "C.N.294.2021, 11 Ekim depo ve 10 Kasım yürürlüğe giriş."),
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
    precision = "day" if day else "unknown"
    insert("document_version", dict(id=vid(key), document_id=document, original_url=row["url"], final_url=url,
        document_date=day, date_precision=precision, date_unknown_reason=None if day else "Kaynakta kesin yayım günü gösterilmiyor.",
        version_label=title, accessed_at=row["retrieved_at_utc"], verified_at=now,
        mime="application/pdf" if media == "pdf" else "text/html", sha256=row["sha256"],
        original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=vid(key), kind=kind, publisher=publisher, author=author,
        social_handle=None, published_at=day, date_precision=precision, public_url=url, basis=basis))
    if media == "html":
        view = build_view(raw, url, source_root, fetch_assets=False)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=vid(key)))
    sources[key] = path, url

source_versions = {key: vid(key) for key in sources}
passages = {}
for key, source, page, exact, label in (
    ("school-call", "school-statement", None, "okulların açılmasını sağlamalıdır.",
     "10 Ağustos TİP çağrısında okul açılışı"),
    ("school-classrooms", "school-statement", None, "Kalabalık sınıflar seyreltilmelidir.",
     "10 Ağustos TİP çağrısında sınıf mevcudu"),
    ("school-announcement", "school-plan", None, "haftada beş gün yüz yüze eğitime başlanacağını",
     "MEB 19 Ağustos haftalık yüz yüze eğitim planı"),
    ("school-start", "school-aa", None, "haftada 5 gün sürecek yüz yüze eğitime başlandı.",
     "6 Eylül AA haberinde eğitim yılının açılışı"),
    ("school-guidance", "school-guide", 3, "öğrenci sayısına dik-\nkat edilerek okul yönetimi tarafından sosyal mesafeye uygun düzenleme yapılır.",
     "Rehberin derslik ve öğrenci sayısına göre düzenleme hükmü"),
    ("montro-call", "montro-statement", None,
     "Montrö Boğazlar Sözleşmesi’nin ihlali anlamına gelecek tüm talepler reddedilmelidir.",
     "24 Şubat TİP açıklamasında Montrö"),
    ("montro-art19", "montro-aa", None, "19. maddesini uygulamak durumundayız.",
     "2 Mart AA haberinde Bakanın 19. madde açıklaması"),
    ("montro-exception", "montro-aa", None, "bağlama limanına dönecekse",
     "2 Mart haberinde limana dönüş istisnasına ilişkin Bakan açıklaması"),
    ("montro-application", "montro-report", 83,
     "Türk Boğazları savaşan tarafların savaş gemilerine kapatılmıştır.",
     "2022 faaliyet raporunda savaşan taraflara ilişkin uygulama"),
    ("montro-other", "montro-report", 83, "savaş gemisi geçirmemeleri yönünde telkinlerde\nbulunulmuştur.",
     "Faaliyet raporunda diğer ülkelere telkin"),
    ("paris-call", "paris-statement", None, "Paris İklim Anlaşması onaylanmalıdır.",
     "5 Ağustos orman yangınları açıklamasında Paris Anlaşması"),
    ("paris-law-adopted", "paris-law", None, "6/10/2021",
     "7335 sayılı kanunun kabul tarihi"),
    ("paris-law-scope", "paris-law", None, "beyan ile birlikte onaylanması uygun",
     "7335 sayılı kanun madde 1, beyanla birlikte uygun bulma"),
    ("paris-deposit", "paris-un", 0, "11 October 2021", "BM bildiriminde onay belgesinin depo günü"),
    ("paris-effective", "paris-un", 0, "10 November 2021", "BM bildiriminde Türkiye için yürürlük günü"),
):
    path = sources[source][0]
    original = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in original, (key, exact)
    passage = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None, article=None,
        section=label, pdf_page_index=page, printed_page=None)
    insert("passage", passage)
    passages[key] = passage

topic_by_case = {"school": "egitime-erisim", "montro": "rusya-iliskileri", "paris": "doga-ekoloji"}
scopes = {}
for row in read(working / "04-inventory.json")["cells"]:
    topic = row["topic_id"]
    if row["party_id"] != party or topic not in topic_by_case.values():
        continue
    scope = row["cell_id"]
    scopes[topic, row["research_kind"]] = scope
    if not any(existing["id"] == scope for existing in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope, **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="2021–2022 tarihli okul, Montrö ve Paris açıklamaları ve işlem belgeleri okundu.")
assert len(scopes) == 6
for key, (_, url) in sources.items():
    topic = topic_by_case[key.split("-")[0]]
    lane = "statement" if key.endswith("-statement") else "event"
    scope = scopes[topic, lane]
    version = source_versions[key]
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    if not any(row["scope_id"] == scope and row["version_id"] == version for row in records["practice_scope_source"]):
        add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
            inspected_sections=json.dumps(sections, ensure_ascii=False))
    attempt = f"{case}-{key}-reading"
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="Tarih, işlem ve yetki bağlamı özgün kaynak pasajlarında okundu.", source_version_id=version)
    if not any(row["scope_id"] == scope and row["url"] == url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
            relevance_reason="2021 okul, Paris veya 2022 Montrö olayına ilişkin tarihli kaynak.",
            state="examined", attempt_ids=json.dumps([attempt]))

limitations = ("Okul bazındaki uygulamalar, Montrö’nin tek tek geçiş işlemleri ve Paris Anlaşmasına ilişkin sonraki "
               "politika uygulamaları ayrı araştırma konuları.")

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
    "school", "egitime-erisim", "04-03-v3-0304-tip-program-egitim-row", "2021-08-10", "2021-09-06",
    "2021–2022 öğretim yılının 6 Eylül yüz yüze açılışı", "meb-2021-09-06-yuz-yuze-egitim",
    "10 Ağustos okul açılışı çağrısı, 19 Ağustos MEB planı ve 6 Eylül yüz yüze eğitim başlangıcı.",
    "19 Ağustos MEB duyurusu, okul önlemleri rehberi ve 6 Eylül Anadolu Ajansı haberi.",
    "TİP 10 Ağustos’ta okulların açılması için plan ve pandemi önlemlerinin açıklanmasını, kalabalık sınıfların seyreltilmesini istedi.",
    "MEB 19 Ağustos’ta 6 Eylül için haftada beş gün yüz yüze eğitimi duyurdu. 6 Eylül haberi yüz yüze başlangıcı bildiriyor. Rehber okul yönetimlerine derslik ve öğrenci sayısına göre düzenleme görevi veriyor.",
    "10 Ağustos TİP çağrısından sonra Bakanlık takvimi duyurdu ve 6 Eylül’de eğitim başladı. Sınıf mevcudu, yeni derslikler veya ilave öğretmen ve personel ihtiyacı her okul için ayrı veriler gerektiriyor.",
    "TİP görüş açıkladı. Açılış takvimi ve kılavuz Bakanlık kaynağında, kurum düzeyindeki uygulama ayrı.",
    "10 Ağustos TİP açıklaması, 19 Ağustos Bakanlık planı ve 6 Eylül yüz yüze açılış.",
    (("school-announcement", "initiative", "MEB’in haftada beş gün yüz yüze açılış planı.", "document"),
     ("school-start", "action", "6 Eylül’de yüz yüze eğitime başlandığı bildirildi.", "independent_report"),
     ("school-guidance", "result", "Rehber derslik ve öğrenci sayısına göre okul düzeyinde düzenleme istiyor.", "document")),
    ("school-classrooms",),
)
add_case(
    "montro", "rusya-iliskileri", "04-03-v3-0304-tip-program-context-rusya-row", "2022-02-24", "2022-03-02",
    "Dışişleri’nin Montrö’nün 19. maddesine ilişkin 2 Mart açıklaması", "montro-2022-03-02-madde-19-aciklama",
    "24 Şubat TİP Montrö çağrısı ve 2 Mart 19. madde uygulaması açıklaması.",
    "2 Mart Anadolu Ajansı haberi ve Dışişleri Bakanlığı 2022 idare faaliyet raporu.",
    "TİP 24 Şubat’ta Montrö Boğazlar Sözleşmesi’ni ihlal edecek taleplerin reddedilmesini istedi.",
    "Dışişleri Bakanı 2 Mart haberinde 19. madde uygulamasını açıkladı. Bakanlık raporu savaşan taraflara uygulanan kısıtı ve diğer ülkelere yapılan telkini ayrı bildiriyor.",
    "TİP’in 24 Şubat Montrö çağrısı ile Dışişleri’nin 2 Mart’taki 19. madde açıklaması aynı savaş bağlamında. Bakanlık raporundaki kısıtın kapsamı savaşan taraflar. Bakan diğer ülkelere de telkin edildiğini ve sözleşmede limana dönüş istisnası bulunduğunu anlatıyor.",
    "TİP kamuya görüş duyurdu. Sözleşmenin uygulanması Türkiye’nin yetkili idari makamlarının işlemleriyle ilgilidir.",
    "24 Şubat parti açıklaması. 2 Mart Bakanın haberle belgelenen açıklaması. Daha sonra 2022 dönemini özetleyen faaliyet raporu.",
    (("montro-art19", "action", "Bakan 19. maddenin uygulanacağını belirtti.", "independent_report"),
     ("montro-exception", "action", "Bakan limana dönüş istisnasını açıkladı.", "independent_report"),
     ("montro-application", "result", "Bakanlık raporu savaşan tarafların savaş gemilerine ilişkin kısıtı bildiriyor.", "document"),
     ("montro-other", "result", "Rapor diğer ülkelere de telkinde bulunulduğunu bildiriyor.", "document")),
)
add_case(
    "paris", "doga-ekoloji", "04-03-v3-0304-tip-program-doga-row", "2021-08-05", "2021-10-11",
    "Türkiye’nin Paris Anlaşması onay belgesini BM’ye depo etmesi", "paris-2021-10-11-turkiye-onay-depo",
    "5 Ağustos TİP Paris çağrısı, 7335 uygun bulma kanunu ve BM’ye onay belgesinin depo işlemi.",
    "7335 sayılı TBMM kanunu ve 13 Ekim 2021 BM depoziter bildirimi.",
    "TİP 5 Ağustos orman yangınları açıklamasında Paris Anlaşması’nın onaylanmasını istedi.",
    "TBMM 6 Ekim’de onayı 7335 sayılı kanunla uygun buldu. BM bildirimi, 11 Ekim’de onay belgesinin depo edildiğini ve 10 Kasım’da Anlaşmanın Türkiye için yürürlüğe gireceğini kaydediyor.",
    "5 Ağustos çağrısını 6 Ekim yasama adımı, 11 Ekim onay belgesinin depo edilmesi ve 10 Kasım yürürlük izledi. Anlaşmanın onaylanması ve uygulanmasına ilişkin önlemler farklı araştırma konuları.",
    "TİP görüşünü açıkladı. Uygun bulma TBMM’nin işlemi, onay belgesinin teslimi ve bildirimi uluslararası süreç.",
    "5 Ağustos parti açıklaması, 6 Ekim 7335 kabulü, 11 Ekim depo, 13 Ekim bildirim ve 10 Kasım yürürlük.",
    (("paris-law-adopted", "initiative", "7335’in 6 Ekim’de kabulü.", "document"),
     ("paris-law-scope", "initiative", "Anlaşmanın beyanla birlikte onaylanması uygun bulundu.", "document"),
     ("paris-deposit", "action", "BM onay belgesinin 11 Ekim’de depo edildiğini bildiriyor.", "document"),
     ("paris-effective", "result", "Türkiye için yürürlük günü 10 Kasım.", "document")),
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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün parti metni, tarihli kurum belgesi veya basın haberi okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-school-montro-paris-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_SCHOOL_MONTRO_PARIS_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
