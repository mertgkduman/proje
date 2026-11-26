"""Prepare five dated civic and labour events from the September to November record."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path

from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
import uygulamalar as rules

checks = Path(__file__).resolve().parent
root = Path("data/practices")
source_root = root / "sources" / "tip"
prefix = "0405-tip-2020-autumn"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")


def read(path):
    return json.loads(path.read_bytes())


baseline = [checks / f"tip-2020-civic-labour{suffix}-draft.json" for suffix in ("", "-review")]
assert [sha256(path.read_bytes()).hexdigest() for path in baseline] == [
    "39a1bec163da1ef88163ee9ea196edb05c56670f54d1f3206657132289c24473",
    "614e5fff7d1568c1895a0329cf03b26c0151d72d06c2eb561ab44dec64d70209",
]
package, review = map(read, baseline)
records, entries = package["practice_records"], package["entries"]


def entry(table, **values):
    entries.append(dict(kind=table, values=values))


def add(table, **row):
    records[table].append(row)


def new_id(key):
    return f"{prefix}-{key}"


def store(path, raw, *, archive_path=None):
    dest = source_root / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        assert dest.read_bytes() == raw, dest
    elif archive_path:
        os.link(archive_path, dest)
    else:
        dest.write_bytes(raw)


captures = {}
for folder in ("september-2020-civic-sources", "november-2020-civic-sources"):
    for row in read(checks / folder / "reading.json")["sources"]:
        capture = row.get("capture", row)
        if capture["status"] == 200:
            captures[capture["path"]] = checks / folder / capture["path"], capture
for number in (17, 19, 20):
    folder = checks / "tip-cark-basak-catalog" / f"issue-{number}"
    capture = read(folder / "reading-01.json")["source"]
    captures[capture["path"]] = folder / capture["path"], capture

sources = {}
for key, filename, published, kind, name, author, title, basis in (
    ("cark17", "cark-basak-17.pdf", None, "party_publication", "Türkiye İşçi Partisi", None,
     "ÇarkBaşak, Eylül 2020, sayı 17", "Dergi künyesi ve 1 Eylül açıklamasının parti tarafından yayımlanan metni. Kesin dergi yayım günü açık."),
    ("cark19", "cark-basak-19.pdf", None, "party_publication", "Türkiye İşçi Partisi", "Ekin Kanar",
     "ÇarkBaşak, Kasım 2020, sayı 19", "Dergi künyesi ve İzmir İl Komitesi sıfatıyla imzalı yazı. Kesin dergi yayım günü açık."),
    ("cark20", "cark-basak-20.pdf", None, "party_publication", "Türkiye İşçi Partisi", None,
     "ÇarkBaşak, Aralık 2020, sayı 20", "Derginin kendi parti haberleri ve Kadıköy fotoğrafı. Kesin dergi yayım günü açık."),
    ("bianet", "bianet-atay-31aug.html.bin", "2020-08-31", "journalism", "bianet", None,
     "Barış Atay’a yönelik saldırı ve Şentop açıklaması", "31 Ağustos dönem haberi. 17 Ekim güncellemesi. Açıklama olay sonrasındaki beyan."),
    ("trt", "trt-atay-2sep.html.bin", "2020-09-02", "journalism", "TRT Haber / DHA", None,
     "Barış Atay soruşturması ve 2 Eylül tutuklamaları", "TRT Haber yayımcısı. Haber, DHA kaynaklı ve 2 Eylül tarihli."),
    ("sozcu", "sozcu-atay-trial.html.bin", "2022-01-11", "journalism", "Sözcü", "Sevgim Begüm Yavuz",
     "Barış Atay dosyasında ilk derece kararı", "11 Ocak 2022 duruşma haberi. İddianame tarihi ve mahkeme sonuçları ayrı aktarılıyor."),
    ("statement", "tip-yogurtcu.html.bin", "2020-09-01", "party_publication", "Türkiye İşçi Partisi", None,
     "1 Eylül 2020 TİP açıklaması", "Parti adı ve tarih imzası. Açıklamanın siyasi değerlendirmeleri yayımlayan kuruma aittir."),
    ("bold", "bold-yogurtcu.html.bin", "2020-09-01", "journalism", "Bold Medya", None,
     "Barış Atay’ın Kadıköy Yoğurtçu Parkı açıklaması", "1 Eylül haberi, yer ve kişinin açıklamasını ayrı tanımlıyor."),
    ("izmir", "izmir-belediye.html.bin", "2020-10-31", "official", "İzmir Büyükşehir Belediyesi", None,
     "İzmir Büyükşehir Belediyesi ekipleri teyakkuzda", "Belediyenin 31 Ekim 2020 tarihli kendi çalışma açıklaması."),
    ("ozgur", "25-kasim-ozgur-gelecek.html.bin", "2020-11-25", "journalism", "Özgür Gelecek", None,
     "25 Kasım 2020 Kadıköy eylemi", "25 Kasım tarihli saha haberi. Etkinliğin çağrısı ve açıklamanın okunması ayrı aktarılıyor."),
    ("anka", "ermenek-anka-26kasim.html.bin", "2020-11-26", "journalism", "ANKA Haber", None,
     "Ermenekli madencilerin 26 Kasım’da serbest bırakılması", "26 Kasım haberi. 1 Haziran 2026 güncellemesi. Bir önceki günün gözaltıları ve sonraki işlemler ayrı."),
):
    path, capture = captures[filename]
    raw = path.read_bytes()
    assert sha256(raw).hexdigest() == capture["sha256"]
    kind_by_document = {"party_publication": "party"}
    media = "pdf" if filename.endswith(".pdf") else "html"
    folder = Path("objects", capture["sha256"])
    original = folder / ("original.pdf" if media == "pdf" else "original.html.bin")
    readable = folder / "readable.html"
    store(original, raw, archive_path=path)
    store(readable, readable_bytes(raw, media, legacy=False))
    doc = new_id(key)
    version = f"{doc}-v1"
    precision = "day" if published else "unknown"
    entry("document", id=doc, party_id="tip", title=title, source_kind=kind_by_document.get(kind, kind))
    entry("document_version", id=version, document_id=doc, original_url=capture["url"], final_url=capture["final_url"],
          document_date=published, date_precision=precision, date_unknown_reason=None if published else basis,
          version_label=title, accessed_at=capture["retrieved_at_utc"], verified_at=now,
          mime="application/pdf" if media == "pdf" else "text/html", sha256=capture["sha256"],
          original_path=str(original), readable_path=str(readable))
    entry("source_attribution", version_id=version, kind=kind, publisher=name, author=author, social_handle=None,
          published_at=published, date_precision=precision, public_url=capture["final_url"], basis=basis)
    if media == "html":
        view = build_view(raw, capture["final_url"], source_root, fetch_assets=False)
        validate_view(source_root, view)
        entry("archive_view", **view, version_id=version)
    sources[key] = (path, version, capture["final_url"])

passages = {}
for key, source, page, printed, exact, label in (
    ("atay-night", "bianet", None, None, "saat 01.30 sularında Kadıköy",
     "bianet, 31 Ağustos 2020’de Kadıköy’deki saldırıyı aktardı."),
    ("atay-date", "sozcu", None, None, "31 Ağustos 2020 tarihinde Türkiye İşçi Partisi",
     "Sözcü duruşma haberinde olay günü 31 Ağustos 2020 ve yer Kadıköy."),
    ("atay-pretrial", "trt", None, None, "her üç şüphelinin de atılı suçtan tutuklanmasına karar verdi",
     "TRT Haber ve DHA, 2 Eylül 2020’de üç şüpheli hakkında tutuklama kararı bildiriyor."),
    ("atay-trial", "sozcu", None, None, "bir sanık hakkında ise beraat kararı verildi",
     "11 Ocak 2022 duruşma haberinde dört mahkûmiyet ve bir beraat bildirildi. Kesinleşme ayrı."),
    ("yogurtcu-report", "bold", None, None, "olayla ilgili açıklama yaptı",
     "Bold Medya, 1 Eylül’de Kadıköy Yoğurtçu Parkı’ndaki açıklama ve Barış Atay’ı bildiriyor."),
    ("yogurtcu-published", "statement", None, None, "01.09.2020",
     "TİP’in parti adı ve 1 Eylül 2020 tarihli imzayı taşıyan özgün açıklaması."),
    ("yogurtcu-party", "cark17", 4, "5", "Yoğurtçu Parkı’nda gerçekleştirdiğimiz basın açıklamasının tam metnidir.",
     "ÇarkBaşak 17, Yoğurtçu Parkı’ndaki açıklamayı parti atfıyla yayımladı."),
    ("izmir-day", "cark19", 3, "4", "30 Ekim Cuma günü öğleden sonra İzmir’de yaşanan",
     "Ekin Kanar, İzmir İl Komitesi, depremin 30 Ekim gününü ve Bayraklı saha başlangıcını anlatıyor."),
    ("izmir-aid", "cark19", 4, "5", "oldu, battaniye, gıda yetiştirdiğimiz de.",
     "Ekin Kanar, parti yayımında çadır, battaniye ve gıda desteğini aktarıyor."),
    ("izmir-city", "izmir", None, None, "İzmir’i sarsan depremin ardından Büyükşehir Belediyesi’ne bağlı ekipler",
     "İzmir Büyükşehir Belediyesinin 31 Ekim açıklaması, İzmir depremi ve belediye müdahalesini kayda alıyor."),
    ("izmir-city-result", "izmir", None, None, "33 bin 255 kişilik çorba",
     "31 Ekim belediye açıklamasında dağıtıldığı bildirilen yemekler kuruma ait."),
    ("women-meeting", "ozgur", None, None, "25 Kasım Platformu saat:19.30",
     "25 Kasım 2020 Kadıköy saha haberi, İstanbul 25 Kasım Platformu ve buluşmayı bildiriyor."),
    ("women-public", "ozgur", None, None, "Eylem basın açıklamasının okunmasıyla sona erdi.",
     "Kadıköy’de eylem ve basın açıklaması bildirildi; uygulama veya mevzuat sonucu açık."),
    ("women-photo", "cark20", 19, None, "25 Kasım 2020 - Kadıköy/İstanbul",
     "ÇarkBaşak 20 arka kapak fotoğraf alt yazısı etkinliğin yerini ve gününü gösteriyor."),
    ("miners-25", "anka", None, None, "9&rsquo;u d&uuml;n jandarma tarafından",
     "26 Kasım ANKA haberi, Ermenek’te 25 Kasım’daki dokuz jandarma gözaltısını ve hastanedeki ayrı gözaltıyı aktarıyor."),
    ("miners-26", "anka", None, None, "4 kişi adli kontrol şartıyla salıverildi",
     "26 Kasım ANKA haberi 10 serbest bırakma ve dört adli kontrolü bildiriyor."),
):
    source_path, version, url = sources[source]
    text = html_source_text(source_path.read_bytes()) if page is None else pdf_page_text(source_path, page)
    assert exact in text, (key, repr(exact))
    row = dict(id=new_id(key), version_id=version, exact=exact, prefix=None, suffix=None, article=None,
               section=label, pdf_page_index=page, printed_page=printed)
    entry("passage", **row)
    passages[key] = (row, url)

scope_rows = {row["topic_id"]:row for row in read(root / "04-inventory.json")["cells"]
              if row["party_id"] == "tip" and row["research_kind"] == "event"}
series = (
    ("atay", "ic-guvenlik", "2020-08-31", "kadikoy-2020-08-31-baris-atay-saldiri",
     "31 Ağustos 2020 Kadıköy’de Barış Atay’a saldırı",
     "Kadıköy’de 31 Ağustos saldırısı, 2 Eylül tutuklama ve 11 Ocak 2022 ilk derece kararı.",
     "Olay ve sonraki işlemler bianet, TRT Haber/DHA ve Sözcü haberlerinin ilgili pasajlarında.",
     "Saldırı, şüphelilerin tutuklanması ve beş sanıklı ilk derece kararı ayrı. Gerekçeli karar ve kesinleşme açık. Siyasi sorumluluk açıklamalarında ileri sürülen nedensellik doğrulanmadı.",
     (("atay-night","action","independent_report"),("atay-date","action","independent_report"),
      ("atay-pretrial","result","independent_report"),("atay-trial","result","independent_report")),
     None, None, None),
    ("yogurtcu", "parti-halk-etkinligi", "2020-09-01", "kadikoy-2020-09-01-tip-yogurtcu-aciklama",
     "1 Eylül 2020 Yoğurtçu Parkı basın açıklaması",
     "Saldırı sonrasında Kadıköy Yoğurtçu Parkı’nda açıklama ve TİP’in 1 Eylül tarihli kurumsal metni.",
     "Bold Medya aynı gün yer ve Barış Atay’ın sözlerini bildiriyor. TİP metni ve dergisi parti açısından ayrı dayanak.",
     "Kişinin sözleri, partinin imzalı açıklaması ve saldırı hakkındaki isnatlar ayrı. Kalabalık büyüklüğü ve siyasi nedensellik açık.",
     (("yogurtcu-report","action","independent_report"),),
     "yogurtcu-party", "TİP, 1 Eylül Yoğurtçu Parkı basın açıklamasını kendi dergisinde ve sitesinde yayımladı.", "task"),
    ("izmir", "parti-yardim-kampanya", "2020-10-30", "izmir-2020-10-30-seferihisar-depremi",
     "30 Ekim 2020 İzmir depremi ve yerel dayanışma",
     "30 Ekim 2020 depreminden sonra Bayraklı için parti yayımındaki yardım bildirimi ve belediyenin 31 Ekim çalışmaları.",
     "TİP İzmir İl Komitesinden Ekin Kanar’ın imzalı metni ve İzmir Büyükşehir Belediyesinin ayrı kurum açıklaması.",
     "Belediye sayıları kendi çalışmasına ait. Partinin bildirdiği çadır, battaniye ve gıda için miktar, teslim günü, harcama ve yararlanıcı kapsamı açık.",
     (("izmir-city","action","document"),("izmir-city-result","result","document")),
     "izmir-aid", "Ekin Kanar, TİP İzmir İl Komitesi atfıyla çadır, battaniye ve gıda sağladıklarını bildirdi.", "support"),
    ("women", "sivil-toplum", "2020-11-25", "kadikoy-2020-11-25-kadin-platformu-aciklama",
     "25 Kasım 2020 Kadıköy Kadın Platformu eylemi",
     "Kadına yönelik şiddete karşı 25 Kasım 2020 Kadıköy buluşması ve basın açıklaması.",
     "Özgür Gelecek’in aynı gün haberi. ÇarkBaşak’ın fotoğraf alt yazısı günü ve Kadıköy’ü gösteriyor.",
     "Çağrının sahibi İstanbul 25 Kasım Platformu. ÇarkBaşak genel olarak 10 şehirde katılımı bildiriyor. Bu etkinlikteki belirli parti katkısı, katılım sayısı ve kurumsal uygulama sonucu ayrı kanıt gerektiriyor.",
     (("women-meeting","action","independent_report"),("women-public","result","independent_report")),
     None, None, None),
    ("ermenek", "sendika-grev", "2020-11-25", "ermenek-2020-11-25-yuruyus-girisimi",
     "25 Kasım 2020 Ermenek yürüyüş girişimi ve gözaltılar",
     "25 Kasım Ermenek’te yürüyüş girişimi ve gözaltılar. 26 Kasım serbest bırakma ve adli kontrol.",
     "ANKA Haber’in 26 Kasım tarihli dönem haberi 25 ve 26 Kasım işlemlerini ayrı aktarıyor.",
     "Erkan Baş’ın partinin duyurduğu basın açıklamasına katılımının kesin günü açık. 12 Ekim yürüyüşü, ekim ziyareti, 25 Kasım gözaltıları ve sonraki ödeme süreci ayrı.",
     (("miners-25","action","independent_report"),("miners-26","result","independent_report")),
     None, None, None),
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
    context_refs = {
        "yogurtcu": ("yogurtcu-published",), "izmir": ("izmir-day",), "women": ("women-photo",),
    }
    refs = [ref for ref,*_ in evidence] + list(context_refs.get(key, ()))
    if role:
        refs.append(role)
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
assert [len(records[table]) for table in ("practice_event","practice_relation","practice_closure")] == [75,57,0]
for suffix,value in (("",package),("-review",review)):
    value["source_review_refs"] = references
    output = checks / f"tip-2020-autumn-civic{suffix}-draft.json"
    output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n")
    print(sha256(output.read_bytes()).hexdigest(),output)
