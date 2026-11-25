"""Build early TİP representation, local meeting and election qualification records."""

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
catalogue = checks / "tip-publication-catalog"
source_root = working / "sources" / "tip"
case = "0405-tip-2018-institution"
party = "tip"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight-draft"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


pair = (checks / "tip-2020-2021-court-wage-election-draft.json", checks / "tip-2020-2021-court-wage-election-review-draft.json") if preflight else (
    working / "04-tip.json", working / "04-tip-review.json")
expected_base = (
    "4e8f6f21d714dad973f2300706cfc5f3ed7a84ebb61abcf1ceb727ff9784dd9b",
    "c32de81f85f7a35fab30ca2c945a454b549cf619cbd3c1000e32e320833a84d8",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [46, 43, 0]


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


source_dir = checks / "2018-institution-sources"
source_rows = {row["path"]: (source_dir / row["path"], row)
               for row in read(source_dir / "reading.json")["linked_material"]}
publisher_archive = catalogue / "party-statements-26"
member_publication = next(row for row in read(publisher_archive / "capture.json") if row["path"] == "186.html.bin")
source_rows["186.html.bin"] = publisher_archive / "186.html.bin", member_publication
cark = checks / "tip-cark-basak-catalog" / "issue-01"
cark_meta = read(cark / "reading-01.json")["source"]
source_rows["cark-basak-01.pdf"] = cark / "cark-basak-01.pdf", cark_meta

sources = {}
for key, name, day, title, kind, publisher, author, basis in (
    ("member-statement", "186.html.bin", "2018-10-06", "6 Ekim TİP Merkez Komitesi açıklaması",
     "party_publication", "Türkiye İşçi Partisi", None, "HDP listeleri ve Meclis'te TİP üyeliğiyle devamına ilişkin parti metni."),
    ("member-tbmm", "tbmm-20181010.pdf", "2018-10-10", "10 Ekim TBMM 6. birleşim tutanağı",
     "official", "TBMM", None, "PDF indeks 49, kişisel söz sırasında Baş'ın TİP temsilini açıklaması."),
    ("member-istanbul", "ysk-2018-istanbul1.pdf", None, "YSK İstanbul 1. seçim çevresi kesin sonuç",
     "official", "Yüksek Seçim Kurulu", None, "İndeks 0, Erkan Baş'ın HDP satırı. Oylama 24 Haziran."),
    ("member-hatay", "ysk-2018-hatay.pdf", None, "YSK Hatay seçim çevresi kesin sonuç",
     "official", "Yüksek Seçim Kurulu", None, "İndeks 0, Barış Atay Mengüllüoğlu'nun HDP satırı. Oylama 24 Haziran."),
    ("edition", "cark-basak-01.pdf", None, "ÇarkBaşak, Kasım 2018, sayı 1",
     "party_publication", "Türkiye İşçi Partisi", None,
     "Sayı 1 künyesinde Türkiye İşçi Partisi adına sahiplik ve Merkez Yürütme Kurulunca yayın. Ekim 2018 taslağı, 26 Ekim Örgüt Bürosu kararı ve kuruluş etkinliğindeki yedi söz."),
    ("meeting-news", "demokrat-tip-gazi-2018.html.bin", "2018-12-04", "4 Aralık Gazi Cemevi halk toplantısı",
     "journalism", "Demokrat Haber", "Merve Akbaş (İleri Haber, aktarım)", "Gazi Cemevi toplantısının aynı gün haber aktarımı."),
    ("elig-ysk", "ysk-2019-1.pdf", "2019-01-02", "2 Ocak 2019 YSK 2019/1 kararı",
     "official", "Yüksek Seçim Kurulu", None, "31 Mart seçimi, katılma yeterliliği ve 13 parti listesi."),
):
    path, row = source_rows[name]
    raw = path.read_bytes()
    assert sha(raw) == row["sha256"]
    media = "pdf" if path.suffix == ".pdf" else "html"
    folder = Path("objects") / row["sha256"]
    original = folder / ("original.pdf" if media == "pdf" else "original.html.bin")
    readable = folder / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, media, legacy=False))
    url = row["final_url"]
    document = f"{case}-{key}"
    source_kind = "party" if kind == "party_publication" else kind
    insert("document", dict(id=document, party_id=party, title=title, source_kind=source_kind))
    precision = "day" if day else "unknown"
    insert("document_version", dict(id=vid(key), document_id=document, original_url=row["url"], final_url=url,
        document_date=day, date_precision=precision,
        date_unknown_reason=None if day else "Kaynak ay veya olay günü gösteriyor. Kesin yayım günü açık.", version_label=title,
        accessed_at=row["retrieved_at_utc"], verified_at=now,
        mime="application/pdf" if media == "pdf" else "text/html", sha256=row["sha256"],
        original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=vid(key), kind=kind, publisher=publisher, author=author,
        social_handle=None, published_at=day, date_precision=precision, public_url=url, basis=basis))
    if media == "html":
        view = build_view(raw, url, source_root, fetch_assets=False)
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=vid(key)))
    sources[key] = path, url

passages = {}
for key, source, page, exact, label in (
    ("member-call", "member-statement", None, "HDP grubunda sürdürdüğümüz mücadeleyi",
     "6 Ekim Merkez Komitesi açıklamasında iki milletvekilinin Meclis'te devamı"),
    ("member-tip", "member-statement", None, "Türkiye İşçi Partisi üyeleri olarak sürdüreceğimizi",
     "6 Ekim açıklamasında TİP üyeliğiyle faaliyet duyurusu"),
    ("member-atay", "member-hatay", 0, "BARIŞ ATAY MENGÜLLÜOĞLU",
     "Hatay seçim çevresi YSK cetveli, seçilenler ve HDP adı aynı satırda"),
    ("member-bas", "member-istanbul", 0, "ERKAN BAŞ",
     "İstanbul 1. seçim çevresi YSK cetveli, seçilenler ve HDP adı aynı satırda"),
    ("member-floor", "member-tbmm", 49, "yoldaşım Barış Atay, Türkiye İşçi Partisini temsilen bu Mecliste bulunuyoruz.",
     "10 Ekim Genel Kurulunda Erkan Baş’ın temsil açıklaması"),
    ("member-chair", "member-tbmm", 49, "Şahıslar adına ilk söz, İstanbul Milletvekilimiz Sayın Erkan Baş’a ait.",
     "Oturum Başkanının verdiği kişisel söz"),
    ("meeting-call", "edition", 19, "Meclis’i halka, halkı Meclis’e taşıyacağız",
     "ÇarkBaşak sayısında 21 Ekim etkinliğinde duyurulan yedi sözden biri"),
    ("meeting-resolution", "edition", 10, "başlatılmasına karar verildi.",
     "26 Ekim Örgüt Bürosunun halk toplantılarına başlama kararı"),
    ("meeting-gazi", "meeting-news", None, "Gazi Cemevi'nde yapılan",
     "4 Aralık haberinde Gazi Cemevi toplantısının gerçekleşmesi"),
    ("meeting-speaker", "meeting-news", None, "Barış Atay'ın katılımıyla Gazi Cemevi'nde",
     "4 Aralık Gazi Cemevi etkinliğine Barış Atay katılımı"),
    ("elig-call", "edition", 9, "Türkiye İşçi Partisi’nin önümüzdeki yerel seçimlere kendi adı ve adaylarıyla girmesi",
     "Ekim taslağından Kasım yayımında kendi adıyla katılmaya ilişkin değerlendirme"),
    ("elig-date", "elig-ysk", 2, "02/01/2019 tarihinde oybirliği ile karar verildi.",
     "2019/1 sayılı YSK kararının tarihi"),
    ("elig-list", "elig-ysk", 2, "12. Türkiye Komünist Partisi\n13. Vatan Partisi",
     "YSK kesin sonuç bölümündeki 13 partilik listenin sonu, TİP listede yok"),
    ("elig-general", "elig-ysk", 1, "Diğer partilerin ise genel kongre veya teşkilatlanma koşulunu yerine",
     "Listede yer verilmeyen partiler hakkında YSK'nın genel değerlendirmesi"),
):
    path = sources[source][0]
    content = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in content, (key, exact)
    passage = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None, article=None,
        section=label, pdf_page_index=page, printed_page=None)
    insert("passage", passage)
    passages[key] = passage

topics = {"member": "siyasal-ittifaklar", "meeting": "demokrasi-katilim", "elig": "secim-siyasi-partiler"}
source_scopes = {
    "member-statement": (("member", "statement"),),
    "member-tbmm": (("member", "event"),),
    "member-istanbul": (("member", "event"),),
    "member-hatay": (("member", "event"),),
    "edition": (("meeting", "statement"), ("meeting", "event"), ("elig", "statement")),
    "meeting-news": (("meeting", "event"),),
    "elig-ysk": (("elig", "event"),),
}
scopes = {}
for row in read(working / "04-inventory.json")["cells"]:
    topic = row["topic_id"]
    if row["party_id"] != party or topic not in topics.values():
        continue
    scope = row["cell_id"]
    scopes[topic, row["research_kind"]] = scope
    if not any(existing["id"] == scope for existing in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope, **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="İlgili tarihli parti yayımı ve işlem kaynakları incelendi. Kapsam araştırması sürüyor.")
assert len(scopes) == 6
for key, (_, url) in sources.items():
    version = vid(key)
    for section_name, lane in source_scopes[key]:
        scope = scopes[topics[section_name], lane]
        sections = [row["section"] for ref, row in passages.items()
                    if row["version_id"] == version and ref.startswith(section_name + "-")]
        assert sections
        add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
            inspected_sections=json.dumps(sections, ensure_ascii=False))
        attempt = f"{case}-{key}-{section_name}-{lane}-reading"
        add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url,
            result="examined", reason="Özgün kaynakta tarih, taraf ve işlem ayrımı okundu.", source_version_id=version)
        if not any(row["scope_id"] == scope and row["url"] == url for row in records["practice_lead"]):
            add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
                relevance_reason="Dönemsel parti açıklaması, kurumsal karar veya uygulama kanıtı.",
                state="examined", attempt_ids=json.dumps([attempt]))

limitations = ("Milletvekillerinin resmî üyelik işlem günleri, toplantıların ülke geneli sırası ve YSK’nın "
               "TİP’e ilişkin bireysel gerekçesi bu belgelerde açık.")

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
             summary, outcome, comparison, authority, timeline, points, extra_refs=(), *, statement_version=None, period_basis=None):
    call = f"{key}-call"
    summary_id = finding(f"{key}-summary", summary, (call,))
    quote = finding(f"{key}-quote", passages[call]["exact"], (call,), quote=True, pair=summary_id)
    statement = f"{case}-{key}-statement"
    add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
        summary_finding_id=summary_id, quote_finding_id=quote, statement_at=source_day,
        date_precision="day" if source_day else "unknown", version_id=statement_version or vid(f"{key}-statement"),
        period_basis=period_basis or "TİP’in tarihli özgün parti yayımı.",
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
    "member", "siyasal-ittifaklar", "04-03-v3-0304-tip-program-sinif-ittifak-row", "2018-10-06", "2018-10-10",
    "Erkan Baş’ın TBMM’de TİP temsilini açıklaması", "tbmm-27-2-6-2018-10-10-tip-temsili",
    "6 Ekim TİP Merkez Komitesi açıklaması ve 10 Ekim Genel Kurul konuşması.",
    "10 Ekim TBMM 6. birleşim tutanağı. Önceki seçim sonucu için ayrı YSK cetvelleri.",
    "TİP 6 Ekim’de İstanbul ve Hatay milletvekillerinin çalışmalarını TİP üyesi olarak sürdüreceğini duyurdu.",
    "10 Ekim’de Genel Kurulda şahıslar adına söz alan Erkan Baş, kendisiyle Barış Atay’ın TİP’i temsil ettiğini açıkladı.",
    "24 Haziran’da Erkan Baş ve Barış Atay, YSK İstanbul 1 ve Hatay cetvellerinde HDP ile seçildi. 6 Ekim TİP duyurusu ve 10 Ekim Genel Kurul beyanı, seçim listesinden sonraki temsil bağlamını belgeliyor.",
    "YSK seçimi ve parti listesini kaydeder. Baş’ın tutanağa giren beyanı, TBMM’de söz alma usulü ve üyelik işlemi farklı kayıtlar.",
    "24 Haziran oylaması, 6 Ekim Merkez Komitesi duyurusu, 10 Ekim Genel Kurul beyanı.",
    (("member-chair", "action", "Oturum Başkanı Baş’a şahıslar adına söz verdi.", "document"),
     ("member-floor", "result", "Baş, iki milletvekilinin TİP adına görev yaptığını açıkladı.", "document")),
    ("member-tip", "member-bas", "member-atay"),
)
add_case(
    "meeting", "demokrasi-katilim", "04-03-v3-03-v2-tip-demokrasi", "2018-10-21", "2018-12-04",
    "Gazi Cemevi halk toplantısı", "tip-2018-12-04-gazi-cemevi-halk-toplantisi",
    "21 Ekim halk toplantısı sözü, 26 Ekim Örgüt Bürosu kararı ve 4 Aralık Gazi Cemevi örneği.",
    "ÇarkBaşak sayı 1’deki karar ve 4 Aralık Demokrat Haber aktarımı.",
    "TİP kuruluş etkinliğinde Meclis çalışmalarını halka taşıma ve halk toplantıları düzenleme sözü yayımladı.",
    "4 Aralık haberi, Gazi Cemevi halk toplantısının Barış Atay’ın katılımıyla yapıldığını bildiriyor.",
    "21 Ekim’de açıklanan toplantı sözü 26 Ekim büro kararında mahalli toplantı planına dönüştü. 4 Aralık Gazi Cemevi bu başlıkta gerçekleştiği bildirilen bir örnek. Kasım ayı Samandağ toplantıları ayrı.",
    "Plan Örgüt Bürosu kaydına, Gazi toplantısı haberin tarihli anlatımına dayanıyor. Haberde Atay konuşmacı.",
    "21 Ekim söz; 26 Ekim karar; 4 Aralık Gazi Cemevi toplantısı.",
    (("meeting-resolution", "initiative", "Örgüt Bürosu mahalli halk toplantılarına başlanmasına karar verdi.", "document"),
     ("meeting-gazi", "result", "Haber Gazi Cemevi toplantısını aktardı.", "independent_report"),
     ("meeting-speaker", "action", "Haberde Barış Atay toplantıda konuşmacı.", "independent_report")),
    statement_version=vid("edition"), period_basis="Sayı 1, indeks 10 ve 19, sözün 21 Ekim kuruluş etkinliğinde açıklandığını bildiriyor.",
)
add_case(
    "elig", "secim-siyasi-partiler", "04-03-v3-0304-tip-program-secim-sistem-row", None, "2019-01-02",
    "YSK’nın 31 Mart 2019 seçimi için katılma yeterliliği tespiti", "ysk-2019-01-02-2019-1-yeterlilik",
    "Kasım ÇarkBaşak değerlendirmesi ve 2 Ocak YSK 2019/1 kararı.",
    "YSK 2019/1 gerekçesi ve 2 Ocak tarihli hüküm.",
    "TİP’in Kasım 2018 yayımındaki taslak, yaklaşan yerel seçime kendi adı ve adaylarıyla katılmasına engel bulunduğunu belirtiyor.",
    "YSK 2 Ocak’ta yeterli gördüğü 13 partiyi belirledi. TİP bu listede yer almadı.",
    "Parti yayımındaki katılma beklentisi ile YSK’nın sonraki listesi bu seçim dönemi için karşılaştırılabilir. Karar teşkilatlanma ve kongre koşullarını genel olarak açıklar. TİP’e ait ayrı gerekçe, itiraz kararı veya bağımsız aday desteğinin sonucu ayrıca araştırılıyor.",
    "Yeterliliği saptayan kurum YSK. Parti metni kendi değerlendirmesini yayımlıyor.",
    "Ekim taslağının Kasım yayımı ve 2 Ocak 2019 YSK kararı.",
    (("elig-date", "action", "YSK kararının tarihi.", "document"),
     ("elig-list", "result", "13 partilik katılma listesi, TİP adı yok.", "document"),
     ("elig-general", "result", "YSK’nın diğer partiler hakkındaki genel gerekçesi.", "document")),
    statement_version=vid("edition"), period_basis="Ekim 2018 tarihli taslak Kasım 2018 sayısında çıktı. Kesin yayım günü yok.",
)
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [49, 46, 0]

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
        with (checks / f"tip-2018-institution-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_2018_INSTITUTION_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
