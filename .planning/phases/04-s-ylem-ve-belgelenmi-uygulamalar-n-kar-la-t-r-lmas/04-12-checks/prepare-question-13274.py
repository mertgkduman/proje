"""Build the signed 7/13274 question and its distinct later accounts."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
import uygulamalar as rules
from arsiv import html_source_text, pdf_page_exists, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(__file__).resolve().parent
working = Path("data/practices")
party = "demokrat"
topic = "nato-iliskileri"
stem = "0412-question-13274"
sources_dir = checks / "party-news-access-039"
source_root = working / "sources" / party
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]


def read(path):
    return json.loads(path.read_bytes())


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def store(relative, raw):
    path = source_root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == raw, path
    else:
        path.write_bytes(raw)


pair = (working / "04-demokrat.json", working / "04-demokrat-review.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "b83b8ac7fc38655dd404b641637a9c721605d52394b71124510fff44272d9685",
    "b2301cfdaa72f3943a624fab1a648add66711f35e04bceccb2becc6afaeebe10",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [78, 50, 0]


def insert(table, **row):
    entries.append(dict(kind=table, values=row))


def add(table, **row):
    records[table].append(row)


capture = {row["path"]: row for row in read(sources_dir / "capture.json")}
capture.update(read(sources_dir / "reading.json")["official_sources"])
sources = {}
for key, filename, date, title, kind, publisher, author, basis in (
    ("signed", "257-tbmm-signed.pdf", "2024-06-25", "Haydar Altıntaş’ın imzalı 7/13274 yazılı sorusu",
     "official", "TBMM", "Haydar Altıntaş", "TBMM’nin tek sayfalık özgün imzalı önerge taraması."),
    ("detail", "257-tbmm-detail.html.bin", None, "TBMM yazılı soru 7/13274 işlem kaydı",
     "official", "TBMM", None, "TBMM işlem kaydındaki önerge numarası, geliş tarihi ve son durum."),
    ("party", "257-party.html.bin", "2024-06-28", "Demokrat Parti’nin 7/13274 konulu sonraki yayımı",
     "party_publication", "Demokrat Parti", "DP Basın Merkezi", "Sayfa üstünde 28 Haziran, gövde imzasında 27 Haziran 2024 yazıyor."),
):
    info = capture[filename]
    path = sources_dir / filename
    raw = path.read_bytes()
    assert info["status"] == 200 and sha(raw) == info["sha256"]
    media = "pdf" if path.suffix == ".pdf" else "html"
    directory = Path("objects") / info["sha256"]
    original = directory / ("original.pdf" if media == "pdf" else "original.html.bin")
    readable = directory / "readable.html"
    store(original, raw)
    store(readable, readable_bytes(raw, media))
    doc = f"{stem}-{key}"
    version = f"{doc}-v1"
    url = info["final_url"]
    insert("document", id=doc, party_id=party, title=title,
           source_kind="party" if key == "party" else "official")
    insert("document_version", id=version, document_id=doc, original_url=info.get("url", url), final_url=url,
           document_date=date, date_precision="day" if date else "unknown",
           date_unknown_reason=None if date else "İşlem sayfasının yayımlanma günü gösterilmiyor.",
           version_label=title, accessed_at=info["retrieved_at_utc"], verified_at=now,
           mime="application/pdf" if media == "pdf" else "text/html", sha256=info["sha256"],
           original_path=str(original), readable_path=str(readable))
    insert("source_attribution", version_id=version, kind=kind, publisher=publisher, author=author,
           social_handle=None, published_at=date if key == "party" else None,
           date_precision="day" if key == "party" else "unknown", public_url=url, basis=basis)
    if media == "html":
        view = build_view(raw, url, source_root, fetch_assets=False)
        validate_view(source_root, view)
        insert("archive_view", version_id=version, **view)
    sources[key] = (path, version, url)

event = f"{stem}-event"
limitations = ("Parti sayfasında 28 Haziran 2024 yayın tarihi ve gövdede DP Basın Merkezi’nin 27 Haziran 2024 tarihi var. "
               "TBMM ayrıntı kaydındaki son durumun ilan günü ve imzalı bakanlık cevabı açık. "
               "Üyelik hedefinin resmî durumu, NATO ile temas ve sonraki sonuçlar için ayrı kanıt gerekiyor.")
add("practice_event", id=event, common_event_key="tbmm-28-2-7-13274-yazili-soru", event_at="2024-06-25",
    date_precision="day", date_unknown_reason=None, title="Haydar Altıntaş’ın NATO ve ŞİÖ hakkında 7/13274 yazılı sorusu",
    scope_context="28. Dönem 2. Yasama Yılında Dışişleri Bakanına yöneltilen yazılı soru.",
    occurrence_basis="25 Haziran 2024 tarihli imzalı önerge ve aynı tarihli TBMM Başkanlığına geliş kaydı.")

passages = {}
event_passages = []
source_passages = {key: [] for key in sources}
for suffix, source, exact, section, stage, point in (
    ("number", "detail", "7 / 13274", "TBMM esas numarası", "initiative", "TBMM işlemi 7/13274 numarasıyla kaydetti."),
    ("arrival", "detail", "25.06.2024", "TBMM Başkanlığına geliş tarihi", "action", "Önerge 25 Haziran 2024’te Başkanlığa geldi."),
    ("date", "signed", "Saygılarımla. 25.06.2024", "İmzalı önerge tarihi", "initiative", "Haydar Altıntaş’ın imzalı metni 25 Haziran 2024 tarihli."),
    ("recipient", "signed", "Dışişleri Bakanı Sayın Hakan Fidan tarafından yazılı olarak", "İmzalı önergede muhatap ve usul", "initiative", "Altıntaş Dışişleri Bakanı Hakan Fidan’dan yazılı cevap istedi."),
    ("question-four", "signed", "NATO üyeliğimizin devam etmesi ile eş zamanlı olarak ŞİÖ'ye üyelik hedeflenmekte",
     "İmzalı önergenin 4. sorusu", "action", "Altıntaş aynı anda NATO üyeliğinin sürdürülmesi ve ŞİÖ üyeliğinin hedeflenmesi konusunu sordu."),
    ("question-five", "signed", "diplomatik temas yapılmış mıdır?", "İmzalı önergenin 5. sorusu", "action",
     "Altıntaş NATO müttefiklerinin yaklaşımını ve görüşme veya diplomatik temas bulunup bulunmadığını sordu."),
    ("status", "detail", "Cevaplanmad&#x131;&#x11F;&#x131; Gelen Ka&#x11F;&#x131;tlarda &#x130;lan Edildi",
     "TBMM işlem kaydının son durum alanı", "result", "TBMM ayrıntı kaydında cevaplanmadığının Gelen Kağıtlarda ilan edildiği yazıyor."),
    ("party-day", "party", "28/06/2024", "Parti sayfasının görünen yayın günü", None, "Parti sayfasında 28 Haziran 2024 yayın tarihi var."),
    ("party-dateline", "party", "DP Basın Merkezi &ndash; 27 Haziran 2024", "Parti yayımının gövde imzası ve tarihi", None,
     "Parti yayımının gövdesinde DP Basın Merkezi ve 27 Haziran 2024 yazıyor."),
):
    path, version, _ = sources[source]
    is_scan = source == "signed"
    if is_scan:
        assert pdf_page_exists(path, 0)
    else:
        assert exact in html_source_text(path.read_bytes()), suffix
    ident = f"{stem}-{suffix}-p"
    insert("passage", id=ident, version_id=version, exact=exact, prefix=None, suffix=None,
           article=None, section=section, pdf_page_index=0 if is_scan else None, printed_page=None)
    if is_scan:
        insert("manual_passage", passage_id=ident, checked_at=now, method="Özgün PDF sayfası Poppler ile görüntülendi.",
               reason="Metin katmanı boş. İmzalı önergenin tek sayfasındaki ifade görselden okundu.")
    if stage:
        add("practice_event_evidence", event_id=event, passage_id=ident, stage=stage, supported_point=point,
            concrete_basis=section, limitation=limitations, epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=ident, stage=stage, basis_kind="document")
        event_passages.append(ident)
    passages[ident] = (section, point)
    source_passages[source].append(section)

scopes = {}
for row in read(working / "04-inventory.json")["cells"]:
    if row["party_id"] == party and row["topic_id"] == topic:
        scopes[row["research_kind"]] = row["cell_id"]
        add("practice_scope_v2", id=row["cell_id"], **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="25 Haziran 2024 yazılı sorusu ve önceki denk söylem için dar okuma.")
assert set(scopes) == {"statement", "event"}
for source, (_, version, url) in sources.items():
    scope = scopes["statement" if source == "party" else "event"]
    attempt = f"{version}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(source_passages[source], ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url,
        result="examined", reason="Özgün soru, işlem ayrıntısı veya sonraki parti yayımı ilgili pasajlardan okundu.",
        source_version_id=version)
    add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url,
        relevance_reason="Haydar Altıntaş’ın ŞİÖ ve NATO konulu 7/13274 yazılı sorusu.",
        state="examined", attempt_ids=json.dumps([attempt]))
add("practice_candidate", id=f"{stem}-candidate", scope_id=scopes["event"], event_id=event,
    relation_id=None, state="unmatched", passage_ids=json.dumps(event_passages),
    reason="İmzalı soru 25 Haziran 2024 tarihli. Parti sayfası 28 Haziran, gövde 27 Haziran tarihli. Önceki karşılaştırılabilir söylem bu aramada doğrulanmadı.")

snapshot = read(Path("data/releases") / package["base_release"] / "records.json")
for entry in entries:
    rows = snapshot.setdefault(entry["kind"], [])
    if entry["values"] not in rows:
        rows.append(entry["values"])
for table, rows in records.items():
    target = snapshot.setdefault(table, [])
    target.extend(row for row in rows if row not in target)
rules.validate_practices(snapshot)
targets = rules.practice_review_package_targets(snapshot, records,
    {row["values"]["id"] for row in entries if row["kind"] == "passage"}, party_id=party)
by_id = {row["id"]: row for row in snapshot["passage"]}
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
        supported_claim=" ".join(passages[ref][1] for ref in sorted(refs)), limitations=limitations,
        result="reviewed", reason=f"{kind} türündeki {ident} kaydına bağlı 7/13274 kaynakları ayrı okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{key: row[key] for key in ("subject_kind", "subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"question-13274-{suffix}.json").open("x") as stream:
            stream.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print("DEMOCRAT_QUESTION_13274_OK", len(records["practice_event"]), len(records["practice_relation"]))
