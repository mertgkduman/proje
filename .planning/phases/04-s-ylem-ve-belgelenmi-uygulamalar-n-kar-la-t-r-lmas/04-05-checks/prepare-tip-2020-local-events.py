"""Prepare dated early-2020 events with their own evidence and participation limits."""

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
prefix = "0405-tip-2020-local"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")


def read(path):
    return json.loads(path.read_bytes())


baseline = [checks / f"tip-bakirkoy-2019{suffix}-draft.json" for suffix in ("", "-review")]
assert [sha256(path.read_bytes()).hexdigest() for path in baseline] == [
    "5e4cb398734473f6258e35bf956f154ce0ac246cd719347dc7d30aacab9bf32a",
    "d8d81ce38bff0823183ce4f6b90d11038a21d75ad07781018b5963474dc50c2e",
]
package, review = map(read, baseline)
records, entries = package["practice_records"], package["entries"]


def entry(table, **values):
    entries.append(dict(kind=table, values=values))


def add(table, **row):
    records[table].append(row)


def new_id(key):
    return f"{prefix}-{key}"


def store(path, raw):
    dest = source_root / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        assert dest.read_bytes() == raw, dest
    else:
        dest.write_bytes(raw)


captures = {}
for folder, field in (("early-2020-local-sources", "linked_material"), ("march-2020-event-sources", "sources")):
    for item in read(checks / folder / "reading.json")[field]:
        capture = item["capture"]
        captures[capture["path"]] = checks / folder / capture["path"], capture
for number in (10, 11):
    folder = checks / "tip-cark-basak-catalog" / f"issue-{number}"
    capture = read(folder / "reading-01.json")["source"]
    captures[capture["path"]] = folder / capture["path"], capture

sources = {}
for key, filename, published, kind, name, title, basis in (
    ("cark10", "cark-basak-10.pdf", None, "party_publication", "Türkiye İşçi Partisi", "ÇarkBaşak, Şubat 2020, sayı 10", "Dergi künyesinde TİP adına sahiplik. Kesin yayım günü açık."),
    ("cark11", "cark-basak-11.pdf", None, "party_publication", "Türkiye İşçi Partisi", "ÇarkBaşak, Mart 2020, sayı 11", "Dergi künyesinde TİP adına sahiplik. Kesin yayım günü açık."),
    ("zincir", "bianet-insan-zinciri.html.bin", "2020-01-12", "journalism", "bianet", "12 Ocak Kanal İstanbul insan zinciri", "Dönem saha haberi, yer ve koordinasyonun çağrısı."),
    ("grev", "petrol-is-trelleborg-12834.html.bin", "2020-01-22", "other", "Petrol-İş Sendikası", "Trelleborg İşyerinde TİS İmzalandı", "Taraf sendikanın açıklaması. 22 Ocak 2020 yayımı, 9 Ocak 2023 güncellemesi."),
    ("yemek", "bianet-iu-iptal-218126.html.bin", "2020-01-06", "journalism", "bianet", "İstanbul Üniversitesi yemekhane kararının iptali", "Dönem haberi ve üniversitenin kendi açıklamasına açık atıf."),
    ("yemek-ilk", "bianet-iu-ilk-217936.html.bin", "2019-12-31", "journalism", "bianet", "İstanbul Üniversitesi öğrencilerinin yemekhane tepkisi", "31 Aralık haberinin 6 Ocak 2020 güncellenmiş hali."),
    ("tarife", "trt-ulasim-460060.html.bin", "2020-02-10", "journalism", "TRT Haber", "İstanbul’da yeni ulaşım tarifesinin uygulanması", "TRT yayımlıyor, kaynak Anadolu Ajansı olarak kaydedilmiş."),
    ("mahkeme", "echr-kavala-001-218516.pdf", "2022-07-11", "official", "Avrupa İnsan Hakları Mahkemesi", "Kavala / Türkiye, 46 § 4 usulü", "Büyük Daire kararı, 24–28. paragraflarda 2020 işlemlerinin seyri."),
):
    path, capture = captures[filename]
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == capture["sha256"]
    media = "pdf" if filename.endswith(".pdf") else "html"
    folder = Path("objects", capture["sha256"])
    original = folder / ("original.pdf" if media == "pdf" else "original.html.bin")
    readable = folder / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, media, legacy=False))
    doc = new_id(key)
    version = f"{doc}-v1"
    source_kind = {"other": "unknown", "party_publication": "party"}.get(kind, kind)
    date_precision = "day" if published else "unknown"
    entry("document", id=doc, party_id="tip", title=title, source_kind=source_kind)
    entry("document_version", id=version, document_id=doc, original_url=capture["url"], final_url=capture["final_url"],
          document_date=published, date_precision=date_precision, date_unknown_reason=None if published else basis,
          version_label=title, accessed_at=capture["retrieved_at_utc"], verified_at=now, mime="application/pdf" if media == "pdf" else "text/html",
          sha256=capture["sha256"], original_path=str(original), readable_path=str(readable))
    entry("source_attribution", version_id=version, kind=kind, publisher=name, author=None,
          social_handle=None, published_at=published, date_precision=date_precision, public_url=capture["final_url"], basis=basis)
    if media == "html":
        view = build_view(raw, capture["final_url"], source_root, fetch_assets=False)
        validate_view(source_root, view)
        entry("archive_view", **view, version_id=version)
    sources[key] = (path, version, capture["final_url"])

passages = {}
for key, source, page, printed, exact, label in (
    ("zincir-olay", "zincir", None, None, "Avcılar Paşaeli",
     "12 Ocak bianet sayfasındaki insan zinciri ve koordinasyon aktarımı."),
    ("zincir-katilim", "cark10", 1, "2", "Avcılar\nİlçe Örgütümüz",
     "ÇarkBaşak 10, İstanbul ve Avcılar örgütlerinin katılımı parti atfıyla."),
    ("grev-baslangic", "grev", None, None, "10 Aralık 2019 tarihinde başlanan grev uygulaması",
     "Petrol-İş sayfa gövdesinde grevin başlangıcı."),
    ("grev-bitis", "grev", None, None, "22 Ocak Çarşamba günü imzalanan toplu iş sözleşmesi",
     "Petrol-İş sözleşme imzası ve grev bitişi açıklaması."),
    ("grev-ziyaret", "cark10", 1, "2", "Grevin 33. gününde genel\nbaşkanımız Erkan Baş ve İşçi Meclisleri grev çadırını\nziyaret etti.",
     "ÇarkBaşak 10, ziyareti grev günü sayısıyla verir."),
    ("yemek-once", "yemek-ilk", None, None, "indirimli öğün sayısını ise bire",
     "İlk haberde indirimli öğün sayısındaki değişiklik."),
    ("yemek-iptal", "yemek", None, None, "yemekhane ile ilgili alınan kararı iptal ederek",
     "6 Ocak haberi, rektörlük açıklamasını doğrudan aktarır."),
    ("tarife-karar", "tarife", None, None, "6 Şubat'taki toplantısında",
     "TRT/AA haberi 6 Şubat UKOME kararını aktarır."),
    ("tarife-uygulama", "tarife", None, None, "2,60 lira olan tam elektronik bilet 3,50 lira",
     "TRT/AA 10 Şubat uygulaması ve tam bilet fiyatı."),
    ("tarife-tepki", "cark11", 1, "2", "bildiri dağıtımları gerçekleştirildi.",
     "ÇarkBaşak 11, İstanbul İl Örgütünün zamma itiraz eden bildiri dağıtımını bildirir."),
    ("gezi-beraat", "mahkeme", 6, "6", "By a judgment dated 18 February 2020",
     "AİHM 24. paragraf, 18 Şubat beraat ve tahliye kararı."),
    ("gezi-gozalti", "mahkeme", 7, "7", "Mr Kavala was arrested and placed in police custody",
     "AİHM 26. paragraf, aynı gün yeniden gözaltı."),
    ("gezi-tutuklama", "mahkeme", 7, "7", "28. On 19 February 2020",
     "AİHM 28. paragraf, ertesi gün yeniden tutuklama."),
    ("gezi-katilim", "cark11", 1, "2", "Silivri’deydi.",
     "ÇarkBaşak 11, genel başkan ve İstanbul İl Örgütü üyelerinin karar duruşmasına katılımını bildirir."),
):
    source_path, version, url = sources[source]
    text = html_source_text(source_path.read_bytes()) if page is None else pdf_page_text(source_path, page)
    assert exact in text, (key, repr(exact))
    row = dict(id=new_id(key),version_id=version,exact=exact,prefix=None,suffix=None,article=None,
               section=label,pdf_page_index=page,printed_page=printed)
    entry("passage", **row)
    passages[key] = (row,url)

scope_rows = {row["topic_id"]:row for row in read(root / "04-inventory.json")["cells"]
              if row["party_id"] == "tip" and row["research_kind"] == "event"}
series = (
    ("zincir", "doga-ekoloji", "2020-01-12", "kanal-istanbul-2020-01-12-avcilar-insan-zinciri",
     "Küçükçekmece Gölü çevresinde Kanal İstanbul insan zinciri",
     "12 Ocak 2020 Avcılar ve Küçükçekmece kıyısında düzenlenen insan zinciri.",
     "12 Ocak bianet saha haberi. Belediye raporunun basılı 156. sayfası tarih ve yeri ayrıca gösteriyor.",
     "Parti dergisi İstanbul İl Örgütü ile Avcılar örgütünün katıldığını bildiriyor. Bianet etkinliği belgeliyor. Belirli tarihli önceki TİP katılım çağrısı ve katılım sayısı açık.",
     (("zincir-olay","action","independent_report"),), "zincir-katilim",
     "ÇarkBaşak’a göre TİP İstanbul ve Avcılar örgütleri insan zincirine katıldı.", "support"),
    ("grev", "sendika-grev", "2019-12-10", "trelleborg-2019-12-10-grev",
     "Trelleborg grevinin başlaması ve toplu sözleşmeyle sona ermesi",
     "10 Aralık 2019’da başlayan Gebze grevi ve 22 Ocak 2020’de sözleşmeyle sonlanması.",
     "Toplu sözleşmenin tarafı olan Petrol-İş sendikasının kendi açıklaması.",
     "Erkan Baş ile İşçi Meclislerinin ziyareti, Şubat parti dergisinde grevin 33. günü diye bildirildi. Kesin ziyaret günü, sözleşme maddeleri ve parti katkısının sözleşmeye etkisi ayrı.",
     (("grev-baslangic","action","document"),("grev-bitis","result","document")), "grev-ziyaret",
     "ÇarkBaşak, Erkan Baş ile İşçi Meclislerinin grevin 33. gününde çadırı ziyaret ettiğini bildiriyor.", "support"),
    ("yemek", "egitime-erisim", "2020-01-06", "istanbul-universitesi-2020-01-06-yemekhane-iptal",
     "İstanbul Üniversitesi yemekhane düzenlemesinin iptali",
     "2 Ocak için duyurulan indirimli öğün düzenlemesinin 6 Ocak’ta iptali.",
     "bianet’in 6 Ocak haberi rektörlük açıklamasını doğrudan aktarır.",
     "TİP Öğrenci Bürosu yazarı gelişmeyi değerlendirdi. Eylemin ayrı öğrenci bileşenleri ile TİP adına önceki açıklama veya yetkili katkı açık.",
     (("yemek-once","initiative","independent_report"),("yemek-iptal","result","independent_report")), None, None, None),
    ("tarife", "ulasim-iletisim", "2020-02-10", "istanbul-2020-02-10-ukome-ulasim-tarife",
     "İstanbul’da Şubat 2020 ulaşım tarifesinin uygulanması",
     "6 Şubat UKOME kararı sonrası yeni ücretler 10 Şubat’ta uygulanmaya başladı.",
     "10 Şubat TRT Haber yayımı ve Anadolu Ajansı kaynak atfı.",
     "Parti, Mart yayımında zamların geri alınmasını isteyen bildiri dağıtımını bildirdi. Bildirinin güncel aslı, dağıtım günü ve karar üzerindeki sonuç açık.",
     (("tarife-karar","initiative","independent_report"),("tarife-uygulama","result","independent_report")), "tarife-tepki",
     "TİP İstanbul İl Örgütü, zamma itiraz eden bildiriyi dağıttığını kendi dergisinde bildirdi.", "objection"),
    ("gezi", "yargi-bagimsizligi", "2020-02-18", "istanbul-30-acm-2020-02-18-kavala-gezi-beraat",
     "Gezi davasında 18 Şubat beraat ve tahliye kararı",
     "18 Şubat 2020 İstanbul 30. Ağır Ceza Mahkemesi kararı ve sonraki soruşturma işlemleri.",
     "AİHM Büyük Daire 11 Temmuz 2022 kararı, 24–28. paragraflar.",
     "Parti, genel başkan ve İstanbul üyelerinin duruşma için Silivri’de bulunduğunu bildirdi. Beraat, aynı gün yeniden gözaltı ve ertesi gün tutuklama farklı işlemler. Partinin hukuki taraf sıfatı veya karar üzerinde etkisi açık.",
     (("gezi-beraat","action","document"),("gezi-gozalti","result","document"),("gezi-tutuklama","result","document")), "gezi-katilim",
     "TİP, karar duruşması için genel başkanı ve İstanbul İl Örgütü üyelerinin Silivri’de olduğunu bildirdi.", "unknown"),
)

for key, topic, day, common, title, context, occurrence, limit, evidence, role, role_text, role_kind in series:
    scope = scope_rows[topic]
    scope_id = scope["cell_id"]
    if not any(row["id"] == scope_id for row in records["practice_scope_v2"]):
        add("practice_scope_v2",id=scope_id,**{name:scope[name] for name in
            ("party_id","topic_id","taxonomy_version","period_start","cutoff_at","research_kind")},
            boundary_reason="Dönem olay kaynakları incelendi. Kapsam araştırması sürüyor.")
    event = new_id(f"{key}-event")
    add("practice_event",id=event,common_event_key=common,event_at=day,date_precision="day",date_unknown_reason=None,
        title=title,scope_context=context,occurrence_basis=occurrence)
    by_version = {}
    refs = [ref for ref,*_ in evidence] + ([role] if role else [])
    for ref in refs:
        passage,url = passages[ref]
        by_version.setdefault((passage["version_id"],url),[]).append(passage["section"])
    for (version,url),sections in by_version.items():
        add("practice_scope_source",scope_id=scope_id,version_id=version,inspected_at=now,inspected_sections=json.dumps(sections,ensure_ascii=False))
        attempt = new_id(f"{key}-{version}-read")
        add("practice_attempt_v2",id=attempt,scope_id=scope_id,attempted_at=now,query=url,url=url,result="examined",
            reason="Tarih, işlem ve kaynak sahibinin atfı okundu.",source_version_id=version)
        if not any(row["scope_id"] == scope_id and row["url"] == url for row in records["practice_lead"]):
            add("practice_lead",id=f"lead-{attempt}",scope_id=scope_id,url=url,relevance_reason="Dönem olayını veya parti rolünü açıklar.",
                state="examined",attempt_ids=json.dumps([attempt]))
    for ref,stage,basis in evidence:
        passage,_ = passages[ref]
        add("practice_event_evidence",event_id=event,passage_id=passage["id"],stage=stage,
            supported_point=passage["section"],concrete_basis=passage["section"],limitation=limit,epistemic_type="claim")
        add("practice_evidence_assessment",event_id=event,passage_id=passage["id"],stage=stage,basis_kind=basis)
    add("practice_candidate",id=new_id(f"{key}-unmatched"),scope_id=scope_id,event_id=event,relation_id=None,state="unmatched",
        reason=limit,passage_ids=json.dumps([passages[ref][0]["id"] for ref, *_ in evidence]))
    if role:
        finding = new_id(f"{key}-role")
        entry("finding",id=finding,party_id="tip",heading="Belgelenmiş uygulamalar",pair_id=finding,text=role_text,
              provenance="summary",epistemic_type="claim")
        entry("review",id=f"review-{finding}",kind="finding",subject_id=finding,reviewer_kind="agent",
              reviewed_at=now,result="reviewed",reason="Parti bildirimi ve bağımsız olay kaydı okundu.")
        for ref in (role,evidence[0][0]):
            passage,_ = passages[ref]
            entry("finding_evidence",finding_id=finding,passage_id=passage["id"],role="support")
            entry("verification",finding_id=finding,passage_id=passage["id"],checked_at=now,result="confirmed",reason=passage["section"])
        actor = new_id(f"{key}-institution")
        entry("actor",id=actor,kind="institution",party_id="tip",person_id=None,authorization_passage_id=None)
        add("practice_contribution",id=new_id(f"{key}-contribution"),event_id=event,party_id="tip",actor_id=actor,contribution_kind=role_kind,
            finding_id=finding,authority_passage_id=None,membership_passage_id=None,responsibility_limit=limit)

snapshot = read(Path("data/releases") / package["base_release"] / "records.json")
for row in entries:
    target = snapshot.setdefault(row["kind"], [])
    if row["values"] not in target:
        target.append(row["values"])
snapshot["practice_contract"] = records["practice_contract"]
for table, rows in records.items():
    target = snapshot.setdefault(table, [])
    target.extend(row for row in rows if row not in target)
rules.validate_practices(snapshot)
targets = rules.practice_review_package_targets(snapshot, records,
    {row["values"]["id"] for row in entries if row["kind"] == "passage"}, party_id="tip")
reviews = review["practice_source_review"]
existing = {(row["subject_kind"],row["subject_id"]) for row in reviews}
assert existing <= targets.keys()
by_id = {row["id"]:row for row,_ in passages.values()}
for kind,ident in sorted(targets.keys()-existing):
    refs,_ = targets[kind,ident]
    inspected = [by_id[ref] for ref in sorted(refs)]
    reviews.append(dict(subject_kind=kind,subject_id=ident,reviewer_kind="agent",reviewed_at=now,
        source_version_ids=json.dumps(sorted({row["version_id"] for row in inspected})),passage_ids=json.dumps(sorted(refs)),
        inspected_sections=json.dumps([row["section"] for row in inspected],ensure_ascii=False),
        supported_claim=" ".join(row["section"] for row in inspected),
        limitations="Kaynakta parti katkısı, olay oluşu ve sonraki işlemler kendi dayanağıyla incelendi.",
        result="reviewed",reason=f"{kind} türündeki {ident} için özgün pasajlar okundu."))
rules.validate_practice_source_review(snapshot,reviews,party_id="tip",target_keys=set(targets))
references = [{name:row[name] for name in ("subject_kind","subject_id")} for row in reviews]
assert [len(records[table]) for table in ("practice_event","practice_relation","practice_closure")] == [63,54,0]
for suffix,value in (("",package),("-review",review)):
    value["source_review_refs"] = references
    output = checks / f"tip-2020-local-events{suffix}-draft.json"
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n")
    print(sha256(output.read_bytes()).hexdigest(),output)
