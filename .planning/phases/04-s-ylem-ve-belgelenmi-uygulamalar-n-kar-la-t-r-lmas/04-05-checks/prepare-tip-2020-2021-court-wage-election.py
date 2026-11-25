"""Build TİP court, wage, local election and joint statement records."""

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
catalogue = checks / "tip-publication-catalog"
source_root = working / "sources" / "tip"
case = "0405-tip-2020-2021-court-wage-election"
party = "tip"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight-draft"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


pair = (checks / "tip-school-montro-paris-draft.json", checks / "tip-school-montro-paris-review-draft.json") if preflight else (
    working / "04-tip.json", working / "04-tip-review.json")
expected_base = (
    "fb5fda689b60a3a6b138be49777b9c296d1fc62f813bb6e25864a4127005387b",
    "a8a38f732f5b87d535bbf156f0064ab0a8d9d8f779c1c532c792ec0a5140ab45",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [42, 40, 0]


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
for tranche in (19, 22, 24):
    directory = catalogue / f"party-statements-{tranche}"
    for row in read(directory / "capture.json"):
        source_rows[row["path"]] = (directory / row["path"], row)
institutions = checks / "2020-2021-institution-sources"
for row in read(institutions / "reading.json")["linked_material"]:
    path = Path(row["repository_path"]) if "repository_path" in row else institutions / row["path"]
    source_rows[row["path"]] = (path, row)

sources = {}
for key, name, day, title, kind, publisher, author, basis in (
    ("court-statement", "149.html.bin", "2020-10-14", "14 Ekim TİP Berberoğlu açıklaması",
     "party_publication", "Türkiye İşçi Partisi", None, "İlk AYM kararından sonra yerel mahkemeye ve milletvekilliğine ilişkin parti yayımı."),
    ("court-aym-first", "rg-berber-2.pdf", "2020-10-09", "AYM 2018/30030, Resmî Gazete 31269",
     "official", "Anayasa Mahkemesi", None, "17 Eylül 2020 kararı, 9 Ekim 2020 Resmî Gazete yayımı."),
    ("court-aym-second", "rg-berber-3.pdf", "2021-02-03", "AYM 2020/32949, Resmî Gazete 31384",
     "official", "Anayasa Mahkemesi", None, "21 Ocak 2021 kararı, 13 Ekim işleminin anlatımı ve 3 Şubat yayımı."),
    ("court-tbmm", "tbmm-berber-20210211.pdf", "2021-02-11", "TBMM 46. birleşim, 3/1518 sayılı tezkere",
     "official", "TBMM", None, "Basılı sayfa 46, 8 Şubat ek kararın 10 Şubat bildirimi ve 11 Şubat Genel Kurula sunuş."),
    ("wage-statement", "146.html.bin", "2020-12-09", "9 Aralık TİP asgari ücret açıklaması",
     "party_publication", "Türkiye İşçi Partisi", None, "Yaşam gereksinimlerini karşılayacak ücret talebi."),
    ("wage-result", "csgb-asgari-20201228.html.bin", "2020-12-28", "Komisyonun 2021 asgari ücret duyurusu",
     "official", "Çalışma ve Sosyal Güvenlik Bakanlığı", None, "Bakanlık arşivinde Komisyonun brüt ve bekâr çocuksuz çalışan için net tutarı."),
    ("election-statement", "174.html.bin", "2019-06-21", "21 Haziran TİP İstanbul seçim çağrısı",
     "party_publication", "Türkiye İşçi Partisi", None, "Yenilenen İstanbul seçimi öncesinde Ekrem İmamoğlu'na oy çağrısı."),
    ("election-result", "ysk-2019-ibb-tr.pdf", None, "YSK 23 Haziran İstanbul yenileme seçimi sonucu",
     "official", "Yüksek Seçim Kurulu", None, "EK-1 kesin oy dağılımı, olay günü 23 Haziran."),
    ("joint-published", "155.html.bin", "2020-05-18", "Yerel yönetimler ortak bildirisi, TİP yayımı",
     "party_publication", "Türkiye İşçi Partisi", None, "TİP sitesindeki ortak metin TİP'i ayrı imzacı olarak listeler."),
    ("joint-birgun", "birgun-20200519.pdf", "2020-05-19", "19 Mayıs BirGün, Sessiz kalmayacağız haberi",
     "journalism", "BirGün", None, "Basılı sayfa 8, 18 Mayıs bildirisi ve 13 imzacının gazete aktarımı."),
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
        date_unknown_reason=None if day else "Tabloda oylama günü var, yayım tarihi gösterilmiyor.", version_label=title,
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
for key, source, page, printed, exact, label in (
    ("court-call", "court-statement", None, None, "Seçilmiş milletvekilleri, meclisteki sıralarına dönerek görevlerine başlamalıdır.",
     "14 Ekim TİP açıklamasında milletvekilliği ve görev çağrısı"),
    ("court-first-response", "court-statement", None, None,
     "İstanbul 14. Ağır Ceza Mahkemesi ise dün Anayasa Mahkemesi kararını tanımadığını ilan ederek",
     "Partinin 13 Ekim yerel mahkeme işlemine ilişkin açıklaması"),
    ("court-first-order", "court-aym-first", 30, None, "yeniden yargılama yapılmak üzere İstanbul 14. Ağır Ceza Mahkemesine",
     "2018/30030 sayılı AYM kararının hüküm D fıkrasında yeniden yargılama"),
    ("court-october-order", "court-aym-second", 7, None, "yeniden yargılama yapılmasına yer olmadığına karar vermiştir.",
     "2020/32949 sayılı AYM kararının 40. paragrafında 13 Ekim yerel mahkeme kararı"),
    ("court-second-order", "court-aym-second", 35, None, "mahkûmiyet hükmünün infazının",
     "2020/32949 sayılı AYM kararının hüküm C fıkrasında yeniden yargılama ve infazın durdurulması"),
    ("court-local", "court-tbmm", 45, 46, "hükümlünün yeniden yargılama talebinin kabulü ile infazın durdurulmasına",
     "3/1518 tezkeresinde 8 Şubat mahkeme ek kararının içerik aktarımı"),
    ("court-notified", "court-tbmm", 45, 46, "Ceza Mahkemesinin 10/02/2021 tarihli yazısı ile Başkanlığımıza",
     "8 Şubat kararının TBMM Başkanlığına 10 Şubat yazısıyla bildirimi"),
    ("court-presented", "court-tbmm", 45, 46, "BAŞKAN – Bilgilerinize sunulmuştur.",
     "11 Şubat Genel Kurulunda 3/1518 tezkeresinin okunması"),
    ("wage-call", "wage-statement", None, None, "belirlenecek ücret en temel insani gereksinimleri karşılasın.",
     "9 Aralık TİP yayımında ücretin yaşam gereksinimlerini karşılaması talebi"),
    ("wage-decided", "wage-result", None, None, "brüt 3.577,50 TL, bekar ve çocuksuz bir işçi için net 2.825,90 TL",
     "Bakanlık 28 Aralık duyurusundaki 2021 brüt ve örnek net tutar"),
    ("election-call", "election-statement", None, None, "Ekrem İmamoğlu'na oy vermeye çağırıyoruz.",
     "21 Haziran TİP yayımında Ekrem İmamoğlu'na destek"),
    ("election-day", "election-result", 0, None, "23 HAZİRAN 2019",
     "YSK EK-1 yenileme seçiminin oylama tarihi"),
    ("election-vote", "election-result", 0, None, "CUMHURİYET HALK PARTİSİ 4.742.082 54,22",
     "YSK EK-1 yenileme seçiminde kesin CHP oy sayısı ve oranı"),
    ("election-total", "election-result", 0, None, "8.746.566 100,0",
     "YSK EK-1 yenileme seçiminde toplam geçerli oy"),
    ("joint-day", "joint-published", None, None, "18 Mayıs 2020", "Ortak bildirinin kendi tarihi"),
    ("joint-tip", "joint-published", None, None, "Türkiye İşçi Partisi (TİP)", "TİP yayımındaki ayrı imzacı satırı"),
    ("joint-press", "joint-birgun", 7, 8, "İşçi Partisi (TİP), Türkiye Komünist",
     "19 Mayıs BirGün haberinde TİP imzası, parti adı önceki satırdaki Türkiye ile başlıyor"),
):
    path = sources[source][0]
    content = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    manual = key in {"court-first-order", "court-october-order", "court-second-order"}
    if manual:
        assert pdf_page_exists(path, page) and not content.strip(), (key, page)
    else:
        assert exact in content, (key, exact)
    passage = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None, article=None,
        section=label, pdf_page_index=page, printed_page=printed)
    insert("passage", passage)
    if manual:
        insert("manual_passage", dict(passage_id=pid(key), checked_at=now,
            method="Özgün Resmî Gazete PDF sayfası Poppler görüntüsünde okundu.",
            reason="İlgili sayfanın metin katmanı boş."))
    passages[key] = passage

topics = {"court": "yargi-bagimsizligi", "wage": "asgari-ucret",
          "election": "yerel-demokrasi", "joint": "yerel-demokrasi"}
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
    topic = topics[key.split("-")[0]]
    lane = "statement" if key.endswith("-statement") else "event"
    scope = scopes[topic, lane]
    version = vid(key)
    sections = [row["section"] for row in passages.values() if row["version_id"] == version]
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(sections, ensure_ascii=False))
    attempt = f"{case}-{key}-reading"
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url, result="examined",
        reason="Tarih, işlem, yetki ve kaynak sınırı özgün pasajlarda okundu.", source_version_id=version)
    if not any(row["scope_id"] == scope and row["url"] == url for row in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
            relevance_reason="Bu tarihli parti açıklaması, kurum işlemi veya imzacı bulgusuna kaynak.",
            state="examined", attempt_ids=json.dumps([attempt]))

limitations = ("Hukuk dosyası 11 Şubat TBMM işlemiyle sınırlı. Ücrette fiilen ödenen tutar ve alım gücü, "
               "seçimde parti desteğinin oy üzerindeki etkisi, ayrıca bireysel imza yetkisi ayrı kanıt gerektirir.")

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
    "court", "yargi-bagimsizligi", "04-03-v3-0304-tip-program-adalet-row", "2020-10-14", "2021-02-11",
    "Berberoğlu hakkındaki 3/1518 tezkeresinin Genel Kurula sunulması", "tbmm-27-4-46-3-1518-berberoglu",
    "14 Ekim TİP çağrısı, 8 Şubat 2021 ek karar ve 11 Şubat Genel Kurul işlemi.",
    "TBMM 46. birleşim tutanağı, 3/1518 tezkere ve basılı sayfa 46.",
    "TİP 14 Ekim’de yerel mahkemenin tutumunu eleştirdi ve seçilmiş milletvekillerinin Meclis görevine dönmesini istedi.",
    "8 Şubat ek kararı yeniden yargılamayı kabul etti, infazı durdurdu ve kesin hükmün sonuçlarını ortadan kaldırdı. 10 Şubat bildiriminden sonra 3/1518 tezkere 11 Şubat’ta Genel Kurulun bilgisine sunuldu.",
    "14 Ekim çağrısı 13 Ekim yerel mahkeme işlemine tepkiydi. Sonraki AYM kararı 21 Ocak’ta verildi. 8 Şubat ek kararının 11 Şubat’ta Genel Kurula duyurulması Berberoğlu dosyasındaki sonraki işlemdir. Açıklamada ayrıca anılan Leyla Güven ve Musa Farisoğulları dosyaları ayrı.",
    "TİP kamuya açıklama yaptı. Yargı kararlarını mahkemeler, Genel Kurula bildirim işlemini TBMM yürüttü.",
    "13 Ekim yerel mahkeme işlemi, 14 Ekim TİP açıklaması, 21 Ocak AYM kararı, 8 Şubat ek karar, 10 Şubat yazı ve 11 Şubat Genel Kurula sunuş.",
    (("court-first-order", "initiative", "İlk AYM hükmü yeniden yargılama için dosyayı gönderdi.", "document"),
     ("court-october-order", "initiative", "Sonraki AYM kararı, 13 Ekim yerel mahkeme kararını kaydetti.", "document"),
     ("court-second-order", "initiative", "İkinci AYM kararı giderim için yeniden yargılama ve infazın durdurulmasını istedi.", "document"),
     ("court-local", "action", "3/1518 tezkeresinin aktardığı yeniden yargılama kabulü ve infazın durdurulması.", "document"),
     ("court-notified", "action", "10 Şubat kararı bildiren mahkeme yazısının tarihi.", "document"),
     ("court-presented", "result", "Genel Kurulda tezkere okundu.", "document")),
    ("court-first-response",),
)
add_case(
    "wage", "asgari-ucret", "04-03-v3-0304-tip-program-asgari-baglam-row", "2020-12-09", "2020-12-28",
    "2021 için Asgari Ücret Tespit Komisyonu tutarının belirlenmesi", "asgari-ucret-2020-12-28-2020-1",
    "9 Aralık TİP açıklaması ile 28 Aralık Komisyon kararı.",
    "Çalışma ve Sosyal Güvenlik Bakanlığı arşivindeki 28 Aralık tarihli duyuru.",
    "TİP 9 Aralık açıklamasında ücretin temel insani gereksinimleri karşılamasını istedi. Belirli bir hedef tutar açıklamadı.",
    "Komisyonun 28 Aralık toplantısından sonra Bakanlık, 2021 için aylık brüt 3.577,50 TL ve bekâr, çocuksuz bir çalışan için net 2.825,90 TL açıkladı.",
    "TİP açıklamasındaki yaşam gereksinimleri ölçütü ile Bakanlığın açıklanan tutarı karşılaştırma için farklı türde kanıt sunuyor. 2.825,90 TL belirtilen hane varsayımındaki net tutar. Alım gücü hakkında bu belgelerle hüküm kurulmaz.",
    "TİP görüş açıkladı. Asgari ücreti belirleyen Asgari Ücret Tespit Komisyonu.",
    "9 Aralık TİP açıklaması ve 28 Aralık Bakanlık duyurusu. Tutar 2021 yılı için duyuruldu.",
    (("wage-decided", "result", "Bakanlığın aylık brüt ve örnek net tutar duyurusu.", "document"),),
)
add_case(
    "election", "yerel-demokrasi", "04-03-v3-0304-tip-program-yerel-demokrasi-row", "2019-06-21", "2019-06-23",
    "23 Haziran 2019 İstanbul Büyükşehir Belediye Başkanlığı yenileme seçimi", "ysk-2019-06-23-ibb-yenileme",
    "21 Haziran TİP desteği, 23 Haziran İstanbul Büyükşehir Belediye Başkanlığı yenileme oylaması.",
    "Yüksek Seçim Kurulunun EK-1 kesin sonuç tablosu.",
    "TİP 21 Haziran’da seçmenleri yenilenen İstanbul seçiminde Ekrem İmamoğlu’na oy vermeye çağırdı.",
    "YSK’nın kesin oy tablosunda CHP 4.742.082 oy ve yüzde 54,22 ile ilk sırada. Geçerli oy sayısı 8.746.566.",
    "TİP’in 21 Haziran desteğini, 23 Haziran yenileme seçiminin YSK’daki kesin oy dağılımı izledi. TİP desteğinin kaç oyu etkilediği araştırma kapsamında ölçülemedi.",
    "TİP oy çağrısını yayımladı. Oy sayımı ve kesin sonuç YSK’ya ait.",
    "21 Haziran oy çağrısı ve 23 Haziran yenilenen oylama.",
    (("election-day", "result", "YSK kesin sonuç belgesindeki oylama tarihi.", "document"),
     ("election-vote", "result", "CHP kesin oy sayısı ve oranı.", "document"),
     ("election-total", "result", "Toplam geçerli oy.", "document")),
)

joint_event = f"{case}-joint-event"
joint_refs = ("joint-day", "joint-tip", "joint-press")
joint_finding = finding("joint-contribution", (
    "TİP, yerel yönetimlere ilişkin 18 Mayıs 2020 ortak bildirisi imzacıları arasında. TİP sitesindeki imzacı listesi ve "
    "19 Mayıs BirGün haberi bu katkıyı belgeliyor. Bireysel imza yetkilisi ve idari atama işlemleri ayrı araştırılıyor."
), joint_refs)
joint_actor = f"{case}-joint-actor"
insert("actor", dict(id=joint_actor, kind="institution", party_id=party, person_id=None,
                     authorization_passage_id=None))
add("practice_event", id=joint_event, common_event_key="yerel-yonetimler-2020-05-18-ortak-bildiri",
    event_at="2020-05-18", date_precision="day", date_unknown_reason=None,
    title="Yerel yönetimlere ilişkin 18 Mayıs 2020 ortak bildirisi",
    scope_context="18 Mayıs 2020 tarihli ortak bildirinin yayımlanması.",
    occurrence_basis="18 Mayıs tarihli ortak açıklama ve 19 Mayıs BirGün basılı sayı, sayfa 8.")
joint_press = passages["joint-press"]
add("practice_event_evidence", event_id=joint_event, passage_id=joint_press["id"], stage="action",
    supported_point=joint_press["section"], concrete_basis="BirGün, 19 Mayıs 2020, basılı sayfa 8",
    limitation="Ortak bildirinin yayımlanması ve TİP imzasıyla sınırlı.", epistemic_type="claim")
add("practice_evidence_assessment", event_id=joint_event, passage_id=joint_press["id"], stage="action",
    basis_kind="independent_report")
event_claims[joint_press["id"]] = joint_press["section"]
add("practice_contribution", id=f"{case}-joint-signature", event_id=joint_event, party_id=party, actor_id=joint_actor,
    contribution_kind="support", finding_id=joint_finding, authority_passage_id=None, membership_passage_id=None,
    responsibility_limit="TİP'in ortak metindeki kurumsal imzası. İmzalayan kişi, atama veya kamu işlemi atfedilmedi.")
add("practice_candidate", id=f"{case}-joint-unmatched", scope_id=scopes["yerel-demokrasi", "event"],
    event_id=joint_event, relation_id=None, state="unmatched", reason="Önceki ayrı parti söylemi açık. Ortak bildiri ayrı olay.",
    passage_ids=json.dumps([joint_press["id"]]))
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [46, 43, 0]

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
        with (checks / f"tip-2020-2021-court-wage-election-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_2020_2021_COURT_WAGE_ELECTION_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
