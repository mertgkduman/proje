"""Build wage, social security, budget and Cyprus comparisons."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
import uygulamalar as rules
from arsiv import html_source_text, pdf_page_exists, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(__file__).resolve().parent
working = Path("data/practices")
source_root = working / "sources" / "tip"
case = "0405-tip-2019-campaign"
party = "tip"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
assert not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


pair = (working / "04-tip.json", working / "04-tip-review.json")
expected_base = (
    "dc2638b909616d108899020497fa9f3a08624684d9388d4308b8373c525b1112",
    "751d36d98823aa75b8fb52ab115afb267eeba6833ab489ef4e778455c066f2b9",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [53, 49, 0]


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


source_dir = checks / "2019-campaign-sources"
source_rows = {row["path"]: (source_dir / row["path"], row)
               for row in read(source_dir / "reading.json")["linked_material"]}
for number in (4, 8):
    issue = checks / "tip-cark-basak-catalog" / f"issue-{number:02}"
    row = read(issue / "reading-01.json")["source"]
    source_rows[row["path"]] = issue / row["path"], row

sources = {}
for key, name, day, title, kind, publisher, author, basis in (
    ("edition", "cark-basak-08.pdf", None, "ÇarkBaşak, Aralık 2019, sayı 8", "party_publication",
     "Türkiye İşçi Partisi", None, "Künyede TİP adına sahiplik. Aralık sayısında kampanya ve bütçe metinleri."),
    ("wage-decision", "rg-wage-2020.pdf", "2019-12-27", "2019/1 Asgari Ücret Tespit Komisyonu kararı", "official",
     "Resmî Gazete", "Asgari Ücret Tespit Komisyonu", "30991 sayılı Resmî Gazete yayımı. Karar 26 Aralık."),
    ("wage-ministry", "wage-2020-csgb.html.bin", "2019-12-26", "2020 brüt ve net asgari ücret açıklaması", "official",
     "Çalışma ve Sosyal Güvenlik Bakanlığı", None, "Çalışma Genel Müdürlüğü arşivi. Bakan Selçuk açıklaması."),
    ("budget-floor", "tbmm-27-3-39.html.bin", None, "TBMM 39. birleşiminde 2020 bütçesi", "official",
     "TBMM Tutanak Hizmetleri Başkanlığı", None, "39. birleşim 20 Aralık başlığını taşıyor, kapanış 00.11. TBMM sicilinde kabul 21 Aralık. Tutanak yayım günü açık."),
    ("budget-register", "tbmm-budget-7197.html.bin", None, "7197 sayılı 2020 bütçe kanunu sicil kaydı", "official",
     "TBMM", None, "Kabul günü 21 Aralık ve Resmî Gazete yayımı 31 Aralık. Sicil sayfasının yayım günü açık."),
    ("eyt-initial", "tbmm-eyt-4914.html.bin", None, "TBMM 2/4914 EYT teklifi", "official",
     "TBMM", None, "Teklif numarası, 30 Ocak 2023 geliş ve 7438 sonucu."),
    ("eyt-law", "rg-eyt-7438.html.bin", "2023-03-03", "7438 sayılı Kanun, Resmî Gazete 32121", "official",
     "Resmî Gazete", "Türkiye Büyük Millet Meclisi", "Kanun başlığı, geçici madde 95 ve yürürlük maddesi."),
    ("cyprus-edition", "cark-basak-04.pdf", None, "ÇarkBaşak, Şubat 2019, Kıbrıs yazısı", "party_publication",
     "Türkiye İşçi Partisi", None, "Sayı 4'te Kıbrıs ve federasyon değerlendirmesi. Parti yayımındaki öneri."),
    ("cyprus-joint", "akel-joint-declaration-2019.html.bin", "2019-11-19", "AKEL, TİP ve Sol Hareket ortak deklarasyonu", "other",
     "AKEL", None, "AKEL sitesindeki Yunanca özgün ortak metin ve imzacı listesi."),
    ("cyprus-press", "kibris-genctv-joint-2019.html.bin", "2019-11-19", "Kıbrıs ortak deklarasyonunun Türkçe haber aktarımı", "journalism",
     "Kıbrıs Genç TV", None, "19 Kasım haberinde Sol Hareket Basın Bürosu aktarımı ve 11–12 Ekim görüşmeleri."),
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
    source_kind = {"party_publication": "party", "other": "unknown"}.get(kind, kind)
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
    ("wage-call", "edition", 9, "asgari ücret en az 3000 TL olarak belirlenmeli,", "ÇarkBaşak sayı 8, basılı 10, kampanya kutusu."),
    ("wage-pub", "wage-decision", 0, "27 Aralık 2019 CUMA", "30991 sayılı Resmî Gazete yayım günü. Karar gövdesi görsel okundu."),
    ("wage-net", "wage-ministry", None, "2 Bin 943 Lira, Net 2 Bin 324 Lira 70 Kuruş", "26 Aralık Bakanlık başlığı, brüt ve net tutarlar."),
    ("budget-call", "edition", 4, "sağlığı öncelikli alanlar olarak gören bir bütçe", "Barbaros Köroğlu, sayı 8, bütçe ve sağlık eğitimi önceliği."),
    ("budget-speech", "budget-floor", None, "2020 bütçesine dair", "39. birleşim, Erkan Baş’ın TİP adına yaptığı bütçe konuşması."),
    ("budget-total", "budget-floor", None, "\r\n329</span>", "39. birleşimde 488 oyun 329'u kabul ve 159'u ret, açık oylama kesin toplamı."),
    ("budget-accept", "budget-register", None, "21/12/2019", "7197 bütçe kanunu TBMM kabul tarihi."),
    ("budget-pub", "budget-register", None, "31/12/2019", "7197 Resmî Gazete yayım günü, 30995 birinci mükerrer."),
    ("eyt-call", "edition", 10, "EYT’lilerin mağduriyeti derhal giderilmeli,", "ÇarkBaşak sayı 8, basılı 11, EYT teklif kutusu."),
    ("eyt-entry", "eyt-initial", None, "2 / 4914", "30 Ocak 2023 tarihli teklif ve 7438 bağlantısı."),
    ("eyt-accept", "eyt-law", None, "1/3/2023", "7438 sayılı Kanun kabul tarihi."),
    ("eyt-scope", "eyt-law", None, "yaş dışındaki diğer şartları taşımaları halinde", "Geçici madde 95, aylık için diğer şartların korunması."),
    ("eyt-effective", "eyt-law", None, "Bu Kanun yayımı tarihinde yürürlüğe girer.", "3 Mart 2023 sayısı ve 3. madde yürürlük."),
    ("cyprus-call", "cyprus-edition", 37, "Kıbrıs Cumhuriyeti hedefini savunmalı,", "Şubat 2019 sayı 4, eşit iki toplum ve federatif cumhuriyet önerisi."),
    ("cyprus-meet", "cyprus-press", None, "11-12 Ekim tarihlerinde", "Kıbrıs Genç TV haberinde iki gün süren toplantılar."),
    ("cyprus-release", "cyprus-joint", None, "19 Νοεμβρίου 2019", "AKEL yayın tarihi 19 Kasım 2019."),
    ("cyprus-form", "cyprus-joint", None, "διζωνική, δικοινοτική ομοσπονδία", "AKEL özgün ortak metninde iki bölgeli, iki toplumlu federasyon."),
    ("cyprus-party", "cyprus-joint", None, "Εργατικό Κόμμα Τουρκίας (TİP)", "AKEL ortak metninde TİP, AKEL ve Sol Hareket imzacıları."),
):
    path = sources[source][0]
    content = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in content, (key, repr(exact))
    passage = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None, article=None,
        section=label, pdf_page_index=page, printed_page=None)
    insert("passage", passage)
    passages[key] = passage

topics = {"wage": "asgari-ucret", "budget": "mali-butce", "eyt": "sosyal-guvenlik", "cyprus": "kibris"}
source_scopes = {
    "edition": (("wage", "statement"), ("budget", "statement"), ("eyt", "statement")),
    "wage-decision": (("wage", "event"),),
    "wage-ministry": (("wage", "event"),),
    "budget-floor": (("budget", "event"),),
    "budget-register": (("budget", "event"),),
    "eyt-initial": (("eyt", "event"),),
    "eyt-law": (("eyt", "event"),),
    "cyprus-edition": (("cyprus", "statement"),),
    "cyprus-joint": (("cyprus", "event"),),
    "cyprus-press": (("cyprus", "event"),),
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
assert len(scopes) == 8
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
        comparison_row_id=comparison_row, uncertainty_reason=limitations[key])
    event = f"{case}-{key}-event"
    add("practice_event", id=event, common_event_key=common_key, event_at=occurrence_day, date_precision="day",
        date_unknown_reason=None, title=title, scope_context=context, occurrence_basis=occurrence_basis)
    for ref, stage, point, basis in points:
        add("practice_event_evidence", event_id=event, passage_id=pid(ref), stage=stage, supported_point=point,
            concrete_basis=passages[ref]["section"], limitation=limitations[key], epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=pid(ref), stage=stage, basis_kind=basis)
        event_claims[pid(ref)] = point
    refs = tuple(point[0] for point in points)
    result = finding(f"{key}-result", outcome, refs)
    explanation = finding(f"{key}-comparison", comparison, (call, *refs, *extra_refs))
    relation = f"{case}-{key}-relation"
    add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes[topic,"event"], statement_id=statement,
        event_id=event, target_finding_id=summary_id, result_finding_id=result, explanation_finding_id=explanation,
        comparability_reason=context, temporal_context=timeline, authority_context=authority, uncertainty_reason=limitations[key])
    add("practice_candidate", id=f"{case}-{key}-candidate", scope_id=scopes[topic,"event"], event_id=event, relation_id=relation,
        state="eligible", reason=context, passage_ids=json.dumps([pid(ref) for ref in refs]))


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
        comparison_row_id=comparison_row, uncertainty_reason=limitations[key])
    event = f"{case}-{key}-event"
    add("practice_event", id=event, common_event_key=common_key, event_at=occurrence_day, date_precision="day",
        date_unknown_reason=None, title=title, scope_context=context, occurrence_basis=occurrence_basis)
    for ref, stage, point, basis in points:
        add("practice_event_evidence", event_id=event, passage_id=pid(ref), stage=stage, supported_point=point,
            concrete_basis=passages[ref]["section"], limitation=limitations[key], epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=pid(ref), stage=stage, basis_kind=basis)
        event_claims[pid(ref)] = point
    refs = tuple(point[0] for point in points)
    result = finding(f"{key}-result", outcome, refs)
    explanation = finding(f"{key}-comparison", comparison, (call, *refs, *extra_refs))
    relation = f"{case}-{key}-relation"
    add("practice_relation", id=relation, party_id=party, topic_id=topic, scope_id=scopes[topic,"event"], statement_id=statement,
        event_id=event, target_finding_id=summary_id, result_finding_id=result, explanation_finding_id=explanation,
        comparability_reason=context, temporal_context=timeline, authority_context=authority, uncertainty_reason=limitations[key])
    add("practice_candidate", id=f"{case}-{key}-candidate", scope_id=scopes[topic,"event"], event_id=event, relation_id=relation,
        state="eligible", reason=context, passage_ids=json.dumps([pid(ref) for ref in refs]))


limitations = {
    "damal": "Bağımsız aday için ilçe seçim kurulu birleştirme tutanağı ve bildirinin kesin yayım günü açık.",
    "elig21": "YSK’nın TİP için hangi ölçütü hangi belgeyle değerlendirdiği ve olası itiraz kararı açık.",
    "elig22": "YSK tespiti kararın kendi tarihli eşiklerine dayanıyor. İlk yeterlilik günü veya partiye özgü sicil yazısı açık.",
    "ozsut": "Eylem dizisinin başlangıcı, sonraki ödemelerin tamamı, ödeme belgeleri ve katkının ödeme üzerindeki etkisi açık.",
}

limitations = {
    "wage": "Parti yayınındaki 3.000 TL’nin brüt ya da net niteliği ve kesin yayım günü açık. Karar fiilî ücret ödemesi değildir.",
    "budget": "Kişisel oylar için açık oy eki ve fiilî bütçe gerçekleşmeleri ayrı. Konuşma, oy veya ödenek gerçekleşmesi olarak sayılmadı.",
    "eyt": "Kanunun şartları ve bireysel aylık işlemleri ayrı. Başvuru sayısı, ödeme ve TİP’in kabuldeki etkisi bu kaynaklardan çıkarılmadı.",
    "cyprus": "Ortak bildiri tarafların siyasi açıklaması. Görüşmelerdeki kişisel imza yetkisi ve devletler arası uygulama bakımından kaynak sınırı var.",
}
add_case(
    "wage", "asgari-ucret", "04-03-v3-0304-tip-program-asgari-baglam-row", None, "2019-12-26",
    "2020 asgari ücretinin belirlenmesi", "asgari-ucret-2019-12-26-2019-1",
    "Aralık 2019 TİP kampanya hedefi ve Asgari Ücret Tespit Komisyonu kararının açıklanması.",
    "26 Aralık Bakanlık açıklaması ve 27 Aralık Resmî Gazete 30991 yayımı.",
    "TİP, Aralık 2019 parti dergisinde asgari ücretin en az 3.000 TL olmasını, aile ölçütünü ve ücretin vergi dışında bırakılmasını önerdi.",
    "26 Aralık Bakanlık açıklamasında 1 Ocak 2020’den geçerli aylık brüt 2.943 TL ve net 2.324,70 TL duyuruldu. Resmî karar 27 Aralık’ta yayımlandı.",
    "TİP’in kampanya hedefi ile Komisyon sonucu aynı asgari ücret konusu altında karşılaştırıldı. Parti önerisindeki brüt veya net taban belirtilmediği için parasal fark hesaplanmadı.",
    "2019/1 kararını Asgari Ücret Tespit Komisyonu, aylık tutarları Bakanlık açıkladı. Parti öneri yayımladı.",
    "Aralık kampanya metni, 26 Aralık karar ve açıklama, 27 Aralık yayım, 1 Ocak 2020 uygulanma başlangıcı.",
    (("wage-net", "result", "Bakanlık 2.943 TL brüt ve 2.324,70 TL net açıkladı.", "document"),
     ("wage-pub", "action", "2019/1 kararı Resmî Gazete’de 27 Aralık’ta yayımlandı.", "document")),
    statement_version=vid("edition"), period_basis="Aralık 2019 ÇarkBaşak sayı 8, kesin gün açık.",
)
add_case(
    "budget", "mali-butce", "04-03-v3-0304-tip-mali-butce-row", None, "2019-12-21",
    "2020 bütçe kanununun TBMM’de kabulü", "tbmm-27-3-39-1-278-7197-kabul",
    "Aralık sayısındaki bütçe yaklaşımı, 39. birleşimde TİP konuşması ve 7197 sayılı kanun.",
    "TBMM 39. birleşim açık oylama sonucu ve 7197 yasama sicili.",
    "TİP dergisinde Barbaros Köroğlu, eğitim ve sağlığı önceleyen bir bütçeyi savundu ve 2020 bütçe teklifini eleştirdi.",
    "39. birleşimde Erkan Baş TİP adına bütçeyi eleştirdi. Genel Kurul 329 kabul ve 159 ret oyuyla 7197 sayılı bütçeyi kabul etti.",
    "Aralık 2019 dergi yazısı ile TİP adına bütçe eleştirisi, genel bütçe yaklaşımında ilişkili. TBMM sicilinde 21 Aralık kabul ve 31 Aralık yayım ayrı.",
    "Erkan Baş’a grubu bulunmayan parti temsilcisi olarak söz verildi. Bütçe, TBMM Genel Kurulunun kararı.",
    "20 Aralık başlıklı birleşim, 21 Aralık TBMM kabul kaydı, 31 Aralık 30995 birinci mükerrer yayım.",
    (("budget-speech", "action", "39. birleşimde Erkan Baş TİP adına bütçe konuşması yaptı.", "document"),
     ("budget-total", "result", "Genel Kurulda 329 kabul ve 159 ret oyu kaydedildi.", "document"),
     ("budget-accept", "result", "TBMM sicili kabulü 21 Aralık’a kaydetti.", "document"),
     ("budget-pub", "result", "TBMM sicilinde 31 Aralık Resmî Gazete yayımı.", "document")),
    statement_version=vid("edition"), period_basis="Aralık 2019 sayı 8, Barbaros Köroğlu’nun imzalı yazısı.",
)
add_case(
    "eyt", "sosyal-guvenlik", "04-03-v3-0304-tip-program-scope-sigorta-row", None, "2023-03-01",
    "EYT düzenlemesinin 7438 sayılı Kanun olarak kabulü", "tbmm-27-6-66-2-4914-7438-kabul",
    "TİP’in 2019 EYT talebi ve yaş şartına ilişkin 7438 düzenlemesi.",
    "TBMM 2/4914 teklif sicili ve 3 Mart 2023 Resmî Gazete’de 7438.",
    "TİP, Aralık 2019’da EYT mağduriyetinin giderilmesini, prim ve gün şartını tamamlayanlara emeklilik hakkı verilmesini istedi.",
    "7438 sayılı Kanun 1 Mart’ta kabul edildi ve 3 Mart’ta yürürlüğe girdi. Geçici 95, ilgili hükümlerde yaş dışındaki şartları taşıyanları kapsıyor.",
    "TİP’in 2019 talebi yaş engelinin kaldırılması açısından 7438’le karşılaştırılabilir. Kanun belirli sigortalılık hükümlerine bağlı koşullar ve geriye dönük ödeme sınırı içeriyor. Dergideki daha geniş emeklilik ve refah payı talepleri ayrı.",
    "Teklif sahibi imza listesi TBMM sicilinde, kabul Genel Kurul işlemi. Parti talebi ve kanun yayın tarihi kendi kaynaklarında.",
    "Aralık 2019 TİP yayımı, 30 Ocak 2023 teklif, 1 Mart kabul ve 3 Mart yürürlük.",
    (("eyt-entry", "initiative", "2/4914 teklifinin Başkanlığa gelişi 30 Ocak 2023.", "document"),
     ("eyt-accept", "action", "7438 sayılı Kanun 1 Mart 2023’te kabul edildi.", "document"),
     ("eyt-scope", "result", "Geçici madde 95, yaş dışındaki şartları koruyor.", "document"),
     ("eyt-effective", "result", "7438, 3 Mart yayımıyla yürürlüğe girdi.", "document")),
    statement_version=vid("edition"), period_basis="Aralık 2019 ÇarkBaşak sayı 8, basılı 11.",
)
add_case(
    "cyprus", "kibris", "04-03-v3-0304-tip-program-context-kibris-row", None, "2019-11-19",
    "AKEL, TİP ve Sol Hareket’in Kıbrıs ortak deklarasyonu", "kibris-2019-11-19-akel-tip-sol-ortak-deklarasyon",
    "Şubat parti yayımındaki federal çözüm önerisi, Ekim görüşmeleri ve Kasım ortak metni.",
    "19 Kasım AKEL özgün ortak açıklaması ve Kıbrıs Genç TV’nin aynı gün aktarımı.",
    "Şubat 2019 ÇarkBaşak yazısında, eşit iki kurucu toplumun uzlaşması ve federatif Kıbrıs Cumhuriyeti önerildi.",
    "AKEL 19 Kasım’da TİP ve Sol Hareket ile iki bölgeli, iki toplumlu federasyonu savunan ortak deklarasyonu yayımladı.",
    "11–12 Ekim’deki görüşmeler sonrasında açıklanan Kasım deklarasyonu federal çözüm başlığını taşıyor. Şubat yazısının sosyalist cumhuriyet hedefi ile ortak metnin müzakere çerçevesi ayrı.",
    "Metin üç örgütün ortak açıklaması ve AKEL yayımı. Devletin müzakere, antlaşma veya uygulama kararı ayrı.",
    "Şubat 2019 parti yayımı, 11–12 Ekim görüşmeleri, 19 Kasım ortak metin.",
    (("cyprus-meet", "initiative", "Kıbrıs Genç TV, 11–12 Ekim görüşmelerini aktardı.", "independent_report"),
     ("cyprus-release", "action", "AKEL 19 Kasım’da ortak metni yayımladı.", "document"),
     ("cyprus-form", "result", "Ortak metin iki bölgeli iki toplumlu federasyonu savunuyor.", "document"),
     ("cyprus-party", "result", "TİP, AKEL ve Sol Hareket ortak metnin tarafları.", "document")),
    statement_version=vid("cyprus-edition"), period_basis="Şubat 2019 sayı 4, basılı 37, kesin yayım günü açık.",
)
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [57, 53, 0]

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
        supported_claim=" ".join(claims[ref] for ref in sorted(refs)), limitations="Ücret tabanı, bütçe oyu, EYT kapsamı ve ortak deklarasyonda tarih, yetki ve kanıt sınırı kaydedildi.",
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün parti metni, tarihli kurum belgesi veya basın haberi okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
for suffix, payload in (("draft", package), ("review-draft", review)):
    with (checks / f"tip-2019-campaign-{suffix}.json").open("x") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
print("TIP_2019_CAMPAIGN_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
