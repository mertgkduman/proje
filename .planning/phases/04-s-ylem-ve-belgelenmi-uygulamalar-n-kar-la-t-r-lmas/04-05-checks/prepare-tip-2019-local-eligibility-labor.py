"""Build Damal, election qualification and Özsüt research records."""

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
case = "0405-tip-2019-local-eligibility-labor"
party = "tip"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
assert not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(content):
    return hashlib.sha256(content).hexdigest()


pair = (working / "04-tip.json", working / "04-tip-review.json")
expected_base = (
    "0504a9693d484a2a9467b8bc6e1c60bdfe3884c87276c7d8117e5f538079944c",
    "113edf0ecd2955d25a0f8c78fadaa5e877d206cf39b8ff597468e5689520cda1",
)
assert tuple(sha(path.read_bytes()) for path in pair) == expected_base
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [49, 46, 0]


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


source_dir = checks / "2019-local-eligibility-and-labor-sources"
source_rows = {row["path"]: (source_dir / row["path"], row)
               for row in read(source_dir / "reading.json")["linked_material"]}
for number in (4, 5, 6):
    issue = checks / "tip-cark-basak-catalog" / f"issue-{number:02}"
    row = read(issue / "reading-01.json")["source"]
    source_rows[row["path"]] = issue / row["path"], row

sources = {}
for key, name, day, title, kind, publisher, author, basis in (
    ("damal-statement", "cark-basak-04.pdf", None, "ÇarkBaşak, Şubat 2019, sayı 4", "party_publication",
     "Türkiye İşçi Partisi", None, "Sayı künyesi TİP adına sahipliği veriyor, Şubat sayısının kesin yayım günü açık."),
    ("damal-candidate", "damal-ysk-candidates.pdf", None, "YSK 31 Mart 2019 İlçe Belediye Başkanlığı kesin aday listesi", "official",
     "Yüksek Seçim Kurulu", None, "138/143 basılı sayfada Damal için bağımsız Tolga Erezer satırı."),
    ("damal-result", "damal-sozcu.html.bin", None, "31 Mart 2019 Damal belediye başkanlığı seçim sonuçları", "journalism",
     "Sözcü", "Anadolu Ajansı (seçim verisi)", "Damal sayfasında data sağlayıcısı açık, tarih ve aday sonuçları seçim panelinde."),
    ("damal-account", "cark-basak-05.pdf", None, "ÇarkBaşak, Temmuz 2019, sayı 5", "party_publication",
     "Türkiye İşçi Partisi", "Cem Güleş, Örgüt Bürosu", "Sayı künyesi TİP adına sahipliği veriyor, Damal metni Örgüt Bürosu imzalı."),
    ("elig21-statement", "elig-2020-abc.html.bin", "2020-06-30", "Erkan Baş'ın örgütlenme yeterliliği açıklaması", "journalism",
     "ABC Gazetesi", None, "30 Haziran tarihli haber Erkan Baş'ın kendi sözlerini doğrudan aktarıyor."),
    ("elig21-decision", "rg-2021-22.pdf", "2021-01-30", "26 Ocak 2021 YSK/22 kararı, Resmî Gazete 31380", "official",
     "Resmî Gazete", "Yüksek Seçim Kurulu", "30 Ocak Resmî Gazete nüshasında karar ve 17 partilik liste."),
    ("elig22-statement", "cark-basak-06.pdf", None, "ÇarkBaşak, Ekim 2019, sayı 6", "party_publication",
     "Türkiye İşçi Partisi", "Erkan Baş", "Sayı künyesi TİP adına sahipliği veriyor, yazı konferansta alınan kararı bildiriyor."),
    ("elig22-decision", "ysk-2022-13.pdf", "2022-01-12", "12 Ocak 2022 YSK/13 kararı", "official",
     "Yüksek Seçim Kurulu", None, "Karar, 24 parti ve TİP'in sıralandığı hüküm."),
    ("ozsut-support", "ozsut-cumhuriyet.html.bin", "2019-07-17", "Kadıköy Özsüt eylemi ve destek haber kaydı", "journalism",
     "Cumhuriyet", None, "17 Temmuz güncellemeli haber, işçi Umut Marangoz anlatımı ve parti desteği."),
    ("ozsut-jul", "ozsut-gazetekadikoy-jul.pdf", None, "Gazete Kadıköy, 26 Temmuz–1 Ağustos 2019", "journalism",
     "Gazete Kadıköy", None, "Basılı 4. sayfada ödeme sözü, yeniden eylem ve sendika desteği."),
    ("ozsut-aug", "ozsut-gazetekadikoy-aug.pdf", None, "Gazete Kadıköy, 2–8 Ağustos 2019", "journalism",
     "Gazete Kadıköy", None, "Basılı 3. sayfada bazı çalışanların alacakları ve sonraki ödeme taahhüdü."),
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
    ("damal-call", "damal-statement", 6, "Bağımsız adayımız Tolga\nErezer’in kazanma olasılığı var.",
     "Şubat sayısı basılı 5, Damal’da bağımsız aday desteği ve parti beklentisi"),
    ("damal-ysk", "damal-candidate", 137, "EREZER", "YSK kesin listesinin 138/143 sayfasında Damal, BAĞIMSIZ, Tolga Erezer satırı görsel okundu."),
    ("damal-returns", "damal-result", None, "TOLGA EREZER", "31 Mart Damal seçim panelinde Tolga Erezer bağımsız ve 75 oy, yüzde 4,13."),
    ("damal-aa", "damal-result", None, "Anadolu Ajansı tarafından sağlanmaktadır", "Seçim paneli ortak veri sağlayıcısı Anadolu Ajansı."),
    ("damal-later", "damal-account", 8, "Tolga Erezer’i destekleme kararı aldı.", "Temmuz sayısı basılı 7, Örgüt Bürosunun geriye dönük teyidi."),
    ("elig21-call", "elig21-statement", None, "41 il ve ilçelerinde örgütlenmesini tamamlamış", "Baş'ın 30 Haziran 2020 sözünün haber aktarımı."),
    ("elig21-yskat", "elig21-decision", 4, "26/01/2021 tarihinde oy birliğiyle karar verildi.", "26 Ocak YSK/22 karar günü, 30 Ocak RG 31380."),
    ("elig21-list", "elig21-decision", 3, "l) Türkiye Komünist Partisi,\nm) Vatan Partisi,\nn) Yeniden Refah Partisi", "17 partilik listenin son üçü. Listenin tam hali PDF indeks 1–3."),
    ("elig21-check", "elig21-decision", 2, "01/07/2020 tarihi itibariyle illerin en az yarısında teşkilatını kurmuş", "2021/22 hükmündeki tarih ve teşkilatlanma eşiği."),
    ("elig22-call", "elig22-statement", 10, "Konferans kararlarımız arasında yer alan partimize seçime girme hakkı\nkazandırılması kararıyla", "Erkan Baş'ın Ekim 2019 sayısında aktardığı konferans kararı."),
    ("elig22-yskat", "elig22-decision", 3, "12.01.2022 tarihinde oy birliği ile karar verildi.", "12 Ocak 2022 YSK/13 hüküm günü."),
    ("elig22-list", "elig22-decision", 2, "20- Türkiye İşçi Partisi,", "YSK/13 sonuç listesinde TİP, 20. sıra. Liste 24 parti."),
    ("elig22-2020", "elig21-statement", None, "yasal örgütlenme barajını aşmış", "30 Haziran 2020 beyanı, sonraki YSK tespiti ayrı."),
    ("ozsut-press", "ozsut-support", None, "Eyleme, CHP ve TİP gibi siyasi partiler de destek olurken", "17 Temmuz Cumhuriyet haberi, TİP desteği."),
    ("ozsut-promise", "ozsut-jul", 3, "17\nTemmuz da işçilere verilen, maaşları ile birlik-", "Gazete Kadıköy, 17 Temmuz ödeme taahhüdü."),
    ("ozsut-partial", "ozsut-aug", 2, "maaşların bir\nkısmının yatırıldığını, geri kalan", "Gazete Kadıköy, yönetimin kısmi ödeme açıklaması ve Ağustos sözü."),
):
    path = sources[source][0]
    content = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    manual = source == "elig21-decision"
    if manual:
        assert pdf_page_exists(path, page) and not content.strip(), (key, page)
    else:
        assert exact in content, (key, repr(exact))
    passage = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None, article=None,
        section=label, pdf_page_index=page, printed_page=None)
    insert("passage", passage)
    if manual:
        insert("manual_passage", dict(passage_id=pid(key), checked_at=now,
            method="Özgün Resmî Gazete nüshasının PDF sayfası görsel olarak okundu.",
            reason="İlgili sayfanın metin katmanı boş."))
    passages[key] = passage

topics = {"damal": "yerel-demokrasi", "elig21": "secim-siyasi-partiler",
          "elig22": "secim-siyasi-partiler", "ozsut": "sendika-grev"}
source_scopes = {
    "damal-statement": (("damal", "statement"),),
    "damal-candidate": (("damal", "event"),),
    "damal-result": (("damal", "event"),),
    "damal-account": (("damal", "event"),),
    "elig21-statement": (("elig21", "statement"), ("elig22", "event")),
    "elig21-decision": (("elig21", "event"),),
    "elig22-statement": (("elig22", "statement"),),
    "elig22-decision": (("elig22", "event"),),
    "ozsut-support": (("ozsut", "event"),),
    "ozsut-jul": (("ozsut", "event"),),
    "ozsut-aug": (("ozsut", "event"),),
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
add_case(
    "damal", "yerel-demokrasi", "04-03-v3-0304-tip-program-yerel-demokrasi-row", None, "2019-03-31",
    "Damal belediye başkanlığı seçiminde bağımsız aday sonucu", "ysk-damal-belediye-baskanligi-2019-03-31",
    "TİP’in Şubat dergisi, YSK kesin aday listesi ve Damal 31 Mart seçim paneli.",
    "YSK kesin aday listesi ile Sözcü’nün Anadolu Ajansı verili Damal seçim paneli.",
    "TİP Şubat sayısında Damal’da bağımsız Tolga Erezer’i desteklediğini ve adayın kazanma olasılığı bulunduğunu belirtti.",
    "YSK listesi Erezer’i bağımsız aday olarak gösteriyor. Anadolu Ajansı verili seçim paneli, 31 Mart’ta 75 oy aldığını gösteriyor.",
    "TİP’in Şubat ayındaki aday desteğinin ardından Tolga Erezer 31 Mart’ta bağımsız aday olarak seçime girdi ve seçilmedi. Temmuz parti dergisi de desteği ve sonucu kendi anlatımıyla kaydetti.",
    "Parti destek kararını açıklar. Kesin aday statüsü YSK’dan, yerel oy sayısı Anadolu Ajansı verili seçim panelinden.",
    "Şubat 2019 parti yayımı, 31 Mart oylaması, Temmuz 2019 parti değerlendirmesi.",
    (("damal-ysk", "action", "Damal kesin aday cetvelinde Erezer bağımsız.", "document"),
     ("damal-returns", "result", "Anadolu Ajansı verili Damal sonuç paneli 75 oy gösteriyor.", "independent_report")),
    ("damal-aa", "damal-later"),
    period_basis="Şubat 2019 ÇarkBaşak sayı 4. Kesin yayım günü açık.",
)
add_case(
    "elig21", "secim-siyasi-partiler", "04-03-v3-0304-tip-program-secim-sistem-row", "2020-06-30", "2021-01-26",
    "YSK’nın Ocak 2021 seçime katılma yeterliliği listesi", "ysk-2021-01-26-2021-22-yeterlilik",
    "Erkan Baş’ın örgütlenme açıklaması ve YSK/22 kararındaki 1 Temmuz 2020 eşiği.",
    "30 Ocak 2021 Resmî Gazete’de yayımlanan 26 Ocak 2021 YSK/22 kararı.",
    "Erkan Baş 30 Haziran 2020’de TİP’in 41 il ve ilçelerinde örgütlenmesini tamamladığını ve seçime girme şartlarını yerine getirdiğini açıkladı.",
    "26 Ocak 2021 kararında yeterli görülen 17 parti belirtiliyor. TİP listede yok.",
    "30 Haziran parti açıklaması ile YSK’nın 1 Temmuz 2020 ölçüt tarihine dayanan 26 Ocak 2021 listesi aynı dönemin farklı kanıtları. Açıklama partinin beyanını, karar ise Kurulun o tarihteki tespitini gösteriyor.",
    "Baş parti adına beyan verdi. YSK yeterliliği kanun ve kendi incelemesine göre tespit etti.",
    "30 Haziran 2020 açıklama, 1 Temmuz 2020 ölçüt tarihi, 26 Ocak 2021 karar, 30 Ocak yayım.",
    (("elig21-yskat", "action", "26 Ocak YSK karar günü.", "document"),
     ("elig21-list", "result", "17 parti listesinde Türkiye İşçi Partisi adı yok.", "document"),
     ("elig21-check", "result", "YSK kararının baktığı tarih 1 Temmuz 2020.", "document")),
    period_basis="30 Haziran 2020 başkan beyanının aynı gün haber aktarımı.",
)
add_case(
    "elig22", "secim-siyasi-partiler", "04-03-v3-0304-tip-program-secim-sistem-row", None, "2022-01-12",
    "YSK’nın Ocak 2022 seçime katılma yeterliliği listesi", "ysk-2022-01-12-2022-13-yeterlilik",
    "2019 parti konferansındaki hedef ve 12 Ocak 2022 YSK/13 kararı.",
    "YSK/13 kararının tarihli hükmü, sonuç A listesi.",
    "Erkan Baş, Ekim 2019 dergisinde partinin seçime girme yeterliliğini kazanmasının konferans kararı olduğunu belirtti.",
    "YSK 12 Ocak 2022’de Türkiye İşçi Partisini 24 partilik listede 20. sırada kaydetti.",
    "Eylül 2019 konferans hedefinin Ekim yayımı ve Haziran 2020 parti beyanından sonra TİP, 12 Ocak 2022 kararına girdi. 2021 listesi kendi ölçüt tarihi ve ayrı kararıyla korunuyor.",
    "Parti konferansı hedef koydu. Katılma yeterliliğini tarihli usul ve ölçütlerle YSK tespit etti.",
    "Ekim 2019 parti yayımı, 30 Haziran 2020 parti açıklaması, 12 Ocak 2022 YSK/13.",
    (("elig22-yskat", "action", "12 Ocak karar günü.", "document"),
     ("elig22-list", "result", "TİP 24 partilik listede 20. sırada.", "document")),
    ("elig22-2020",),
    period_basis="Ekim 2019 ÇarkBaşak sayı 6. Kesin yayım günü açık.",
)

labor_scope = scopes[topics["ozsut"], "event"]
labor_statement_scope = scopes[topics["ozsut"], "statement"]
add("practice_attempt_v2", id=f"{case}-ozsut-statement-search", scope_id=labor_statement_scope, attempted_at=now,
    query='site:tip.org.tr "Özsüt" 2019 Türkiye İşçi Partisi Temmuz Kadıköy destek',
    url="https://tip.org.tr/assets/carkbasak/CarkBasak_Sayi6_201910.pdf", result="inconclusive",
    reason="Ekim sayısında eylem sonrası tanıklık bulundu. Olay öncesi tarihli özgül parti açıklaması bu aramada bulunamadı.",
    source_version_id=None)
labor_event = f"{case}-ozsut-event"
add("practice_event", id=labor_event, common_event_key="ozsut-kadikoy-ucret-direnisi-2019-temmuz",
    event_at=None, date_precision="unknown",
    date_unknown_reason="17 Temmuz haberi süren eylemi bildiriyor. Farklı haberler farklı başlangıç ve ödeme aşamaları veriyor.",
    title="Kadıköy Özsüt ücret eylemi ve TİP desteği",
    scope_context="Temmuz 2019 Kadıköy eyleminde ücret ve tazminat talepleri, destek ve haberlerdeki ödeme aşamaları.",
    occurrence_basis="17 Temmuz Cumhuriyet haberi ve Temmuz sonu ile Ağustos başı Gazete Kadıköy haberleri.")
labor_refs = ("ozsut-press", "ozsut-promise", "ozsut-partial")
for ref, stage, point in (
    ("ozsut-press", "action", "Cumhuriyet, eyleme TİP ve CHP desteği bildiriyor."),
    ("ozsut-promise", "initiative", "17 Temmuz ödeme taahhüdü ve alacağı süren iki çalışan."),
    ("ozsut-partial", "result", "Yönetim kısmi ödeme ve kalan ücret için Ağustos sözü verdi."),
):
    add("practice_event_evidence", event_id=labor_event, passage_id=pid(ref), stage=stage, supported_point=point,
        concrete_basis=passages[ref]["section"], limitation=limitations["ozsut"], epistemic_type="claim")
    add("practice_evidence_assessment", event_id=labor_event, passage_id=pid(ref), stage=stage,
        basis_kind="independent_report")
    event_claims[pid(ref)] = point
labor_finding = finding("ozsut-contribution", "Temmuz 2019’da Kadıköy’deki Özsüt ücret eylemine TİP’in verdiği desteği Cumhuriyet haberleştirdi. Gazete Kadıköy, bazı ödemelerle sonraki ödeme sözünü ayrı bildiriyor.", labor_refs)
labor_actor = f"{case}-ozsut-actor"
insert("actor", dict(id=labor_actor, kind="institution", party_id=party, person_id=None,
    authorization_passage_id=None))
add("practice_contribution", id=f"{case}-ozsut-support", event_id=labor_event, party_id=party, actor_id=labor_actor,
    contribution_kind="support", finding_id=labor_finding, authority_passage_id=None, membership_passage_id=None,
    responsibility_limit="Haberdeki kurumsal destek. Ödeyen şirket, ödeme kanıtı ve sonuç etkisi ayrı.")
add("practice_candidate", id=f"{case}-ozsut-unmatched", scope_id=labor_scope, event_id=labor_event,
    relation_id=None, state="unmatched", reason="17 Temmuz haberinde parti desteği var. Önceki tarihli özgül parti açıklaması açık.",
    passage_ids=json.dumps([pid(ref) for ref in labor_refs]))
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [53, 49, 0]

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
        supported_claim=" ".join(claims[ref] for ref in sorted(refs)), limitations="Ödeme, seçim yeterliliği ve aday desteğinde kurum, tarih ve kaynak sınırı ayrı kaydedildi.",
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için özgün parti metni, tarihli kurum belgesi veya basın haberi okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
for suffix, payload in (("draft", package), ("review-draft", review)):
    with (checks / f"tip-2019-local-eligibility-labor-{suffix}.json").open("x") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
print("TIP_2019_LOCAL_ELIGIBILITY_LABOR_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
