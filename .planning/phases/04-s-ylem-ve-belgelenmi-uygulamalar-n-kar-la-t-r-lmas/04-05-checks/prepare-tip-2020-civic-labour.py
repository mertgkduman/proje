"""Build the July bar comparison and four separately dated evidence records."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
import uygulamalar as rules


checks = Path(__file__).resolve().parent
root = Path("data/practices")
source_root = root / "sources" / "tip"
prefix = "0405-tip-2020-civic"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")


def read(path):
    return json.loads(path.read_bytes())


base_files = [checks / f"tip-2020-policy{suffix}-draft.json" for suffix in ("", "-review")]
assert [sha256(path.read_bytes()).hexdigest() for path in base_files] == [
    "56f351d7e0537d7640533392784c6408ac449c433637bc3657864d2a9a28083f",
    "d4cbce3ba31b2861f85e41c9d4b634fea238a4e0e7efddff9af8ed6f357c79cf",
]
package, review = map(read, base_files)
records, entries = package["practice_records"], package["entries"]


def identifier(key):
    return f"{prefix}-{key}"


def entry(table, **values):
    entries.append({"kind": table, "values": values})


def add(table, **row):
    records[table].append(row)


def store(relative, raw):
    dest = source_root / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        assert dest.read_bytes() == raw
    else:
        dest.write_bytes(raw)


captures = {}
for name in ("may-july-2020-event-sources", "october-2020-civic-sources"):
    folder = checks / name
    for item in read(folder / "reading.json")["sources"]:
        capture = item["capture"]
        captures[capture["path"]] = folder / capture["path"], capture
folder = checks / "tip-cark-basak-catalog" / "issue-14"
capture = read(folder / "reading-01.json")["source"]
captures[capture["path"]] = folder / capture["path"], capture

sources = {}
for key, filename, when, kind, publisher, author, title, basis in (
    ("bar-issue", "cark-basak-14.pdf", None, "party_publication", "Türkiye İşçi Partisi",
     "Ümit Bayrak ve Özgür Urfa", "ÇarkBaşak sayı 14, Meslek Odalarımız Teslim Alınamayacak",
     "TİP künyeli Haziran 2020 sayısındaki imzalı yazı. Kesin yayım günü açık."),
    ("bar-proposal", "tbmm-2999-direct.html.bin", None, "official", "TBMM", None,
     "TBMM 2/2999, Avukatlık Kanunu değişikliği teklifi",
     "Sicil sayfasının kesin yayım günü açık. Başkanlığa geliş tarihi 30 Haziran 2020."),
    ("bar-floor", "tbmm-2-2999-floor-110.html.bin", None, "official", "TBMM Tutanak Hizmetleri Başkanlığı", None,
     "27. dönem 3. yıl 110. birleşim tutanağı",
     "9 Temmuz 2020 tarihli birleşimde teklifin ikinci bölümü. Tutanağın kesin yayım günü açık."),
    ("bar-law", "tbmm-7249-original.html.bin", None, "official", "TBMM", None,
     "7249 sayılı Kanun, TBMM özgün kabul metni",
     "Kanun metni kabul günü 11 Temmuz. TBMM HTML yayım günü açık."),
    ("bar-registry", "tbmm-7249.html.bin", None, "official", "TBMM", None,
     "7249 sayılı Kanun TBMM sicili", "Sicil sayfasında kabul, onay ve Resmî Gazete yayımı ayrı."),
    ("yks-plan", "osym-yks-initial.html.bin", "2020-02-06", "official", "ÖSYM", None,
     "6 Şubat 2020 YKS başvuru duyurusu", "ÖSYM’nin ilandaki ilk sınav günlerini verdiği açıklama."),
    ("yks-held", "osym-yks-held.html.bin", "2020-07-27", "official", "ÖSYM", None,
     "2020 YKS sonuç duyurusu", "ÖSYM’nin fiilen uygulanan sınav günlerini ve sonuç ilanını verdiği açıklama."),
    ("may-disk", "disk-may1.html.bin", "2020-05-01", "other", "DİSK", None,
     "DİSK’in 1 Mayıs anma girişimine ilişkin açıklaması", "Olay tarafı olan konfederasyonun dönem açıklaması."),
    ("may-tihv", "tihv-may1.html.bin", None, "other", "Türkiye İnsan Hakları Vakfı", None,
     "1–4 Mayıs 2020 Günlük İnsan Hakları Raporu", "Rapor dönemi 1–4 Mayıs. Kesin yayımlanma günü açık."),
    ("tempo-paper", "mucadelebirligi-tempo.pdf", "2020-08-14", "journalism", "Mücadele Birliği", None,
     "14 Ağustos 2020 sayısı, Tempo Genel Merkezi önündeki işçi eylemi",
     "Üçüncü sayfada 12 Ağustos İstanbul ve İzmir eylemleri. TİP katılımı Şişli paragrafında."),
    ("tempo-result", "evrensel-tempo-414601.html.bin", "2020-09-21", "journalism", "Evrensel", None,
     "Tempo Çağrı Merkezi işçileri işe geri alındı",
     "21 Eylül yayımı ve İletişim-İş yönetim kurulu üyesinin doğrudan aktarımı."),
):
    path, capture = captures[filename]
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == capture["sha256"]
    pdf = path.suffix == ".pdf"
    media = "pdf" if pdf else "html"
    folder = Path("objects", capture["sha256"])
    original = folder / ("original.pdf" if pdf else "original.html.bin")
    readable = folder / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, media, legacy=False))
    document, version = identifier(key), identifier(f"{key}-v1")
    source_kind = {"party_publication": "party", "other": "unknown"}.get(kind, kind)
    precision = "day" if when else "unknown"
    url = capture["final_url"]
    entry("document", id=document, party_id="tip", title=title, source_kind=source_kind)
    entry("document_version", id=version, document_id=document, original_url=capture["url"], final_url=url,
          document_date=when, date_precision=precision, date_unknown_reason=None if when else basis,
          version_label=title, accessed_at=capture["retrieved_at_utc"], verified_at=now,
          mime="application/pdf" if pdf else "text/html", sha256=capture["sha256"],
          original_path=str(original), readable_path=str(readable))
    entry("source_attribution", version_id=version, kind=kind, publisher=publisher, author=author, social_handle=None,
          published_at=when, date_precision=precision, public_url=url, basis=basis)
    if not pdf:
        view = build_view(raw, url, source_root, fetch_assets=False)
        validate_view(source_root, view)
        entry("archive_view", **view, version_id=version)
    sources[key] = (path, version, url)

passages = {}
for key, source, page, printed, exact, section in (
    ("bar-target", "bar-issue", 8, "9", "bu saldırıyı geri püskürtecek direncin", "Sayı 14, baroların yapısını değiştirme önerisine itiraz."),
    ("bar-entry", "bar-proposal", None, None, "2 / 2999", "TBMM, teklif numarası."),
    ("bar-received", "bar-proposal", None, None, "30/06/2020", "TBMM, 30 Haziran Başkanlığa geliş."),
    ("bar-speaker", "bar-floor", None, None, "&#351;ahs&#305; ad&#305;na ilk olarak Hatay Milletvekili",
     "TBMM 110. birleşim, Barış Atay Mengüllüoğlu’nun şahsı adına söz alması."),
    ("bar-accept", "bar-law", None, None, "Kabul Tarihi: 11/7/2020", "7249 metninde 11 Temmuz kabul tarihi."),
    ("bar-rule", "bar-law", None, None, "asgari ikibin avukatla bir baro kurulabilir.",
     "7249, 5.000’den fazla avukat bulunan illerde yeni baro için en az 2.000 avukat koşulu."),
    ("bar-effective", "bar-law", None, None, "Bu Kanun yayımı tarihinde yürürlüğe girer.", "7249 madde 27, yayım tarihinde yürürlük."),
    ("bar-published", "bar-registry", None, None, "15/07/2020", "TBMM sicili ve 31186 sayısında 15 Temmuz yayımı."),
    ("yks-initial", "yks-plan", None, None, "20-21&nbsp;Haziran 2020", "ÖSYM ilk takvimi 20–21 Haziran günlerini verdi."),
    ("yks-actual", "yks-held", None, None, "27-28 Haziran 2020", "ÖSYM sonuç duyurusunda sınavın uygulandığı günler."),
    ("yks-results", "yks-held", None, None, "27 Temmuz 2020", "ÖSYM sonuç duyurusu 27 Temmuz."),
    ("may-disk", "may-disk", None, None, "15 kişi gözaltına alındı.", "DİSK açıklaması, genel merkez çevresindeki anma girişimine müdahale ve 15 gözaltı."),
    ("may-tihv", "may-tihv", None, None, "Gözaltına alınanların isimleri: Arzu Çerkezoğlu", "TİHV raporu, aynı 1 Mayıs olayındaki gözaltı kaydı."),
    ("tempo-august", "tempo-paper", 2, None, "Ağustos'ta İzmir ve İstanbul'da", "14 Ağustos sayısında 12 Ağustos eylemlerinin tarih ve illeri."),
    ("tempo-role", "tempo-paper", 2, None, "TİP de katılarak destek verdi.", "Mücadele Birliği, Şişli eylemi için doğrudan parti katılımı."),
    ("tempo-report", "tempo-result", None, None, "19 işçi, geçmişe dönük hakları da ödenmek üzere", "21 Eylül Evrensel haberi, işe iade ve geçmiş alacakların bildirimi."),
):
    path, version, url = sources[source]
    body = html_source_text(path.read_bytes()) if page is None else pdf_page_text(path, page)
    assert exact in body, (key, repr(exact))
    row = dict(id=identifier(key), version_id=version, exact=exact, prefix=None, suffix=None,
               article=None, section=section, pdf_page_index=page, printed_page=printed)
    entry("passage", **row)
    passages[key] = (row, url)


scope_rows = {
    (row["topic_id"], row["research_kind"]): row
    for row in read(root / "04-inventory.json")["cells"] if row["party_id"] == "tip"
}


def inspect(topic, lane, event_key, refs):
    scope = scope_rows[topic, lane]
    scope_id = scope["cell_id"]
    if not any(row["id"] == scope_id for row in records["practice_scope_v2"]):
        add("practice_scope_v2", id=scope_id, **{k: scope[k] for k in
            ("party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="İşlem ve kaynak ilişkileri incelendi. Kapsam araştırması sürüyor.")
    groups = {}
    for ref in refs:
        p, url = passages[ref]
        groups.setdefault((p["version_id"], url), []).append(p["section"])
    for (version, url), sections in groups.items():
        add("practice_scope_source", scope_id=scope_id, version_id=version, inspected_at=now,
            inspected_sections=json.dumps(sections, ensure_ascii=False))
        attempt = identifier(f"{event_key}-{version}-reading")
        add("practice_attempt_v2", id=attempt, scope_id=scope_id, attempted_at=now, query=url,
            url=url, result="examined", reason="Özgün kaynakta tarih, aktör ve aşama okundu.", source_version_id=version)
        if not any(row["scope_id"] == scope_id and row["url"] == url for row in records["practice_lead"]):
            add("practice_lead", id=f"lead-{attempt}", scope_id=scope_id, url=url,
                relevance_reason="Dönem açıklaması, bağımsız olay kaydı veya kurum işlemi.",
                state="examined", attempt_ids=json.dumps([attempt]))
    return scope_id


def finding(key, content, refs, *, quote_pair=None):
    ident = identifier(key)
    entry("finding", id=ident, party_id="tip", heading="Belgelenmiş uygulamalar", pair_id=quote_pair or ident,
          text=content, provenance="quote" if quote_pair else "summary", epistemic_type="claim")
    entry("review", id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent",
          reviewed_at=now, result="reviewed", reason="Özgün kanıt pasajları okundu.")
    for ref in refs:
        row, _ = passages[ref]
        entry("finding_evidence", finding_id=ident, passage_id=row["id"], role="quotation" if quote_pair else "support")
        entry("verification", finding_id=ident, passage_id=row["id"], checked_at=now,
              result="confirmed", reason=row["section"])
    return ident


cases = (
    dict(key="bar", topic="sivil-toplum", day="2020-07-11", common="tbmm-27-3-111-2-2999-7249-kabul",
         title="Baro düzenlemesinin 7249 sayılı Kanun olarak kabulü",
         context="2/2999 sayılı teklifin 11 Temmuz 2020’de TBMM’de kabul edilmesi ve 15 Temmuz’da yürürlüğe girmesi.",
         basis="TBMM teklif kaydı, 110. birleşim ve 7249 metniyle kabul ve yayım sicili.",
         limit="Yazarların itirazı, milletvekilinin şahsı adına konuşması ve Genel Kurul kararı farklı. Kişisel oylar, her ildeki kuruluş işlemi ve uygulama etkisi için ayrı kanıt gerekir.",
         points=(("bar-entry","initiative","document"),("bar-received","initiative","document"),
                 ("bar-speaker","initiative","document"),("bar-accept","action","document"),
                 ("bar-rule","result","document"),("bar-effective","result","document"),("bar-published","result","document"))),
    dict(key="yks", topic="egitime-erisim", day="2020-06-27", common="osym-2020-06-27-28-yks-uygulama",
         title="ÖSYM’nin 27–28 Haziran 2020 YKS uygulaması",
         context="ÖSYM’nin 2020 YKS için ilk ilanı ve uygulanan iki sınav günü.",
         basis="ÖSYM 6 Şubat ilk duyurusu ile 27 Temmuz sonuç duyurusunun tarihleri.",
         limit="İlk tarih 20–21 Haziran. Kesin uygulama 27–28 Haziran. Ara kararların özgün belgeleri, imza kampanyasının aslı ve partinin yetkili katkısı açık.",
         points=(("yks-initial","initiative","document"),("yks-actual","action","document"),("yks-results","result","document"))),
    dict(key="may", topic="sendika-grev", day="2020-05-01", common="disk-2020-05-01-genel-merkez-anma-mudahale",
         title="DİSK’in 1 Mayıs anma girişimine müdahale ve gözaltılar",
         context="DİSK’in genel merkezi çevresinde 1 Mayıs 2020’deki anma girişimi.",
         basis="DİSK ve TİHV aynı olayda 15 gözaltı bildiriyor.",
         limit="Olay, aynı gün yapılan diğer mahalle etkinliklerinden ayrı. Bu yere ilişkin önceki TİP açıklaması veya yetkili katılım açık. Sonraki adli kararın aslı araştırılıyor.",
         points=(("may-disk","action","document"),("may-tihv","result","independent_report"))),
    dict(key="tempo-august", topic="sendika-grev", day="2020-08-12", common="tempo-2020-08-12-sisli-dayanisma",
         title="Tempo Çağrı Merkezi işçileri için Şişli dayanışma eylemi",
         context="12 Ağustos’ta Tempo Çağrı Merkezi Genel Müdürlüğü önündeki Şişli eylemi.",
         basis="Mücadele Birliği’nin 14 Ağustos yayımı, PDF indeks 2.",
         limit="Şişli kaydı 25 Ağustos’taki ayrı eylemden farklı. İlk etkinliğe TİP’in destek katılımı bildiriliyor. Önceki tarihli yetkili parti açıklaması ve eylemin işe dönüşe etkisi açık.",
         points=(("tempo-august","action","independent_report"),("tempo-role","action","independent_report"))),
    dict(key="tempo-report", topic="sendika-grev", day="2020-09-21", common="tempo-2020-09-21-ise-iade-haberi",
         title="Tempo işçilerinin işe dönüşünün 21 Eylül’de bildirilmesi",
         context="Batman’daki Tempo işçilerinin dönüşü hakkında 21 Eylül 2020’de yayımlanan haber.",
         basis="Evrensel, 19 işçinin dönüşünü ve sendika temsilcisinin açıklamasını aktarıyor.",
         limit="21 Eylül haberin yayım tarihi. İşe başlama günleri ve geçmiş alacakların fiilî ödemesi açık. Bildirilen sonuç için partinin rolü veya nedensel etkisi kaynaklardan çıkarılmadı.",
         points=(("tempo-report","result","independent_report"),)),
)

for case in cases:
    key, topic = case["key"], case["topic"]
    refs = [ref for ref, *_ in case["points"]]
    scope = inspect(topic, "event", key, refs)
    event = identifier(f"{key}-event")
    add("practice_event", id=event, common_event_key=case["common"], event_at=case["day"], date_precision="day",
        date_unknown_reason=None, title=case["title"], scope_context=case["context"], occurrence_basis=case["basis"])
    for ref, stage, basis in case["points"]:
        row, _ = passages[ref]
        add("practice_event_evidence", event_id=event, passage_id=row["id"], stage=stage,
            supported_point=row["section"], concrete_basis=row["section"], limitation=case["limit"], epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=row["id"], stage=stage, basis_kind=basis)
    relation = None
    candidate_state = "unmatched"
    if key == "bar":
        target = passages["bar-target"][0]
        inspect(topic, "statement", key, ("bar-target",))
        summary = finding("bar-summary", "ÇarkBaşak’ta Ümit Bayrak ile Özgür Urfa, baroları değiştirme girişimine karşı örgütlü itirazı savundu.", ("bar-target",))
        quote = finding("bar-quote", target["exact"], ("bar-target",), quote_pair=summary)
        statement, relation = identifier("bar-statement"), identifier("bar-relation")
        add("practice_statement", id=statement, party_id="tip", topic_id=topic, taxonomy_version=4,
            summary_finding_id=summary, quote_finding_id=quote, statement_at=None, date_precision="unknown",
            version_id=target["version_id"], period_basis="Haziran 2020 ÇarkBaşak, sayı 14. Kesin yayım günü açık.",
            comparison_row_id="04-03-v3-0304-tip-program-context-sivil-row", uncertainty_reason=case["limit"])
        result = finding("bar-result", "2/2999 teklifi 11 Temmuz’da kabul edildi. 7249, 5.000’den fazla avukat bulunan illerde en az 2.000 avukatla yeni baro kurulabilmesini öngördü. Kanun 15 Temmuz’da yürürlüğe girdi.", refs)
        explanation = finding("bar-comparison", "Haziran parti yayımındaki itiraz ile yeni baro ve temsil koşullarını düzenleyen kanun aynı meslek örgütlenmesi konusuyla ilgili. Barış Atay Mengüllüoğlu 110. birleşimde teklif üzerine şahsı adına konuştu.", ("bar-target", *refs))
        add("practice_relation", id=relation, party_id="tip", topic_id=topic, scope_id=scope, statement_id=statement,
            event_id=event, target_finding_id=summary, result_finding_id=result, explanation_finding_id=explanation,
            comparability_reason=case["context"],
            temporal_context="Haziran dergi yazısı, 30 Haziran teklif gelişi, 9 Temmuz başlıklı birleşim, 11 Temmuz kabul ve 15 Temmuz yürürlük.",
            authority_context="Dergi yazısı imzalı. Meclis konuşması şahsı adına, kanun kabulü Genel Kurulun işlemi.",
            uncertainty_reason=case["limit"])
        candidate_state = "eligible"
    if key == "tempo-august":
        actor = identifier("tempo-august-actor")
        entry("actor", id=actor, kind="institution", party_id="tip", person_id=None, authorization_passage_id=None)
        role = finding("tempo-august-support", "Mücadele Birliği, TİP’in Şişli’deki Tempo eylemine katılarak destek verdiğini bildirdi.", ("tempo-role",))
        add("practice_contribution", id=identifier("tempo-august-contribution"), event_id=event, party_id="tip",
            actor_id=actor, contribution_kind="support", finding_id=role, authority_passage_id=None,
            membership_passage_id=None, responsibility_limit=case["limit"])
    add("practice_candidate", id=identifier(f"{key}-candidate"), scope_id=scope, event_id=event, relation_id=relation,
        state=candidate_state, reason=case["limit"],
        passage_ids=json.dumps([passages[ref][0]["id"] for ref in refs]))

snapshot = read(Path("data/releases") / package["base_release"] / "records.json")
for row in entries:
    table = snapshot.setdefault(row["kind"], [])
    if row["values"] not in table:
        table.append(row["values"])
snapshot["practice_contract"] = records["practice_contract"]
for name, rows in records.items():
    table = snapshot.setdefault(name, [])
    table.extend(row for row in rows if row not in table)
rules.validate_practices(snapshot)
targets = rules.practice_review_package_targets(
    snapshot, records, {e["values"]["id"] for e in entries if e["kind"] == "passage"}, party_id="tip"
)
reviews = review["practice_source_review"]
existing = {(r["subject_kind"], r["subject_id"]) for r in reviews}
assert existing <= targets.keys()
by_id = {p["id"]: p for p, _ in passages.values()}
for kind, ident in sorted(targets.keys() - existing):
    refs, _ = targets[kind, ident]
    inspected = [by_id[ref] for ref in sorted(refs)]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        source_version_ids=json.dumps(sorted({p["version_id"] for p in inspected})),
        passage_ids=json.dumps(sorted(refs)),
        inspected_sections=json.dumps([p["section"] for p in inspected], ensure_ascii=False),
        supported_claim=" ".join(p["section"] for p in inspected),
        limitations="İşlem, kaynak atfı, tarih ve sonuç kapsamı ayrı incelendi.",
        result="reviewed", reason=f"{kind} türündeki {ident} için özgün kaynak pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id="tip", target_keys=set(targets))
refs = [{name: row[name] for name in ("subject_kind", "subject_id")} for row in reviews]
assert [len(records[t]) for t in ("practice_event", "practice_relation", "practice_closure")] == [70, 57, 0]
for suffix, payload in (("", package), ("-review", review)):
    payload["source_review_refs"] = refs
    path = checks / f"tip-2020-civic-labour{suffix}-draft.json"
    with path.open("x") as stream:
        stream.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(sha256(path.read_bytes()).hexdigest(), path)
