"""Append TİP's Bakırköy decision and its attributed report of participation."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from arsiv import pdf_page_text, readable_bytes
import uygulamalar as rules

checks = Path(__file__).resolve().parent
root = Path("data/practices")
source_root = root / "sources" / "tip"
case = "0405-tip-bakirkoy-2019"
topic = "demokrasi-katilim"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
read = lambda path: json.loads(path.read_bytes())
pair = (root / "04-tip.json", root / "04-tip-review.json")
assert tuple(sha256(path.read_bytes()).hexdigest() for path in pair) == (
    "eded6eda1883d0d080a59c4763027ff344525638238d1bbcbc66e591db7befe2",
    "a3affbf70d334323a4cdc780123a822945858d0c1c5b1232b71995b7bb2d137a",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
catalog = checks / "tip-cark-basak-catalog"
edition8_version = "0405-tip-2019-campaign-edition-v1"
edition8_meta = next(row["values"] for row in entries if row["kind"] == "document_version" and row["values"]["id"] == edition8_version)
edition8 = source_root / edition8_meta["original_path"]
edition9_meta = read(catalog / "issue-09/reading-01.json")["source"]
hkmo_meta = next(row for row in read(checks / "2019-campaign-sources/reading.json")["linked_material"] if row["path"] == "hkmo-bakirkoy-2019.pdf")


def entry(table, **values):
    entries.append(dict(kind=table, values=values))


def add(table, **row):
    records[table].append(row)


def archive(suffix, source, capture, kind, publisher, title, basis):
    raw = source.read_bytes()
    assert sha256(raw).hexdigest() == capture["sha256"]
    object_dir = Path("objects", capture["sha256"])
    original, readable = object_dir / "original.pdf", object_dir / "readable.html"
    (source_root / object_dir).mkdir(parents=True, exist_ok=True)
    for path, data in ((original, raw), (readable, readable_bytes(raw, "pdf", legacy=False))):
        destination = source_root / path
        if destination.exists():
            assert destination.read_bytes() == data
        else:
            destination.write_bytes(data)
    document = f"{case}-{suffix}"
    version = f"{document}-v1"
    entry("document", id=document, party_id="tip", title=title, source_kind="party" if kind == "party_publication" else kind)
    entry("document_version", id=version, document_id=document, original_url=capture["url"], final_url=capture["final_url"],
          document_date=None, date_precision="unknown", date_unknown_reason=basis, version_label=title,
          accessed_at=capture["retrieved_at_utc"], verified_at=now, mime="application/pdf",
          sha256=capture["sha256"], original_path=str(original), readable_path=str(readable))
    entry("source_attribution", version_id=version, kind=kind, publisher=publisher, author=None, social_handle=None,
          published_at=None, date_precision="unknown", public_url=capture["final_url"], basis=basis)
    return version


edition9 = catalog / "issue-09" / edition9_meta["path"]
edition9_version = archive("edition", edition9, edition9_meta, "party_publication", "Türkiye İşçi Partisi",
    "ÇarkBaşak, Ocak 2020, sayı 9", "Künyede TİP adına sahiplik. Ocak 2020 sayısı, kesin yayım günü açık.")
hkmo = checks / "2019-campaign-sources" / hkmo_meta["path"]
hkmo_version = archive("hkmo", hkmo, hkmo_meta, "official", "TMMOB Harita ve Kadastro Mühendisleri Odası İstanbul Şubesi",
    "HKMO İstanbul Şubesi 25. Dönem Çalışma Raporu", "25. dönem raporunun tam yayım günü bilinmiyor; kapak Şubat 2020 der.")
assert hkmo_meta["sha256"] == "71d7365d5b82963fa8cf3de2c928cc2b032101f9135e3e192760d1ec1e24d00b"

passages = {}
for key, path, version, index, printed, exact, section in (
    ("decision", edition8, edition8_version, 4, "5",
     "düzenlenecek mitinge kitlesel olarak katılım\nkararı aldı.",
     "Aralık 2019 sayı 8, Bakırköy’deki 8 Aralık mitingine TİP İstanbul İl Örgütünün katılım kararı."),
    ("party-role", edition9, edition9_version, 1, "2",
     "“İnsanca Yaşamak İstiyoruz” mitingine katıldık.",
     "Ocak 2020 sayı 9, İstanbul mitingi hakkında TİP’in fotoğraflı katılım bildirimi."),
    ("occurrence", hkmo, hkmo_version, 99, "99",
     "8 Aralık 2019 tarihinde İstanbul Emek, Demokrasi ve Barış Koordinasyonu",
     "HKMO 25. Dönem Çalışma Raporu, miting tarihi ve düzenleyici."),
    ("venue", hkmo, hkmo_version, 99, "99",
     "Bakırköy Halk Pazarında", "HKMO 25. Dönem Çalışma Raporu, miting yeri."),
):
    assert exact in pdf_page_text(path, index), key
    row = dict(id=f"{case}-{key}-p", version_id=version, exact=exact, prefix=None, suffix=None,
               article=None, section=section, pdf_page_index=index, printed_page=printed)
    entry("passage", **row)
    passages[key] = row

scopes = {row["research_kind"]: row for row in read(root / "04-inventory.json")["cells"]
          if row["party_id"] == "tip" and row["topic_id"] == topic}
for lane in ("statement", "event"):
    row = scopes[lane]
    if not any(scope["id"] == row["cell_id"] for scope in records["practice_scope_v2"]):
        add("practice_scope_v2", id=row["cell_id"], **{key: row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="Mitinge katılım kararı ve olay için özgün yayınlar okundu. Kapsam araştırması sürüyor.")
for suffix, lane, url, keys in (
    ("call", "statement", edition8_meta["final_url"], ("decision",)),
    ("participation", "event", edition9_meta["final_url"], ("party-role",)),
    ("occurrence", "event", hkmo_meta["final_url"], ("occurrence", "venue")),
):
    scope = scopes[lane]["cell_id"]
    source = passages[keys[0]]["version_id"]
    add("practice_scope_source", scope_id=scope, version_id=source, inspected_at=now,
        inspected_sections=json.dumps([passages[key]["section"] for key in keys], ensure_ascii=False))
    attempt = f"{case}-{suffix}-reading"
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=url, url=url,
        result="examined", reason="Özgün PDF, tarih, yer ve atıf için okundu.", source_version_id=source)
    if not any(lead["scope_id"] == scope and lead["url"] == url for lead in records["practice_lead"]):
        add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=url, relevance_reason="Katılım kararı veya etkinlik kaydı.",
            state="examined", attempt_ids=json.dumps([attempt]))

limitation = ("Dergi sayılarının tam yayım günü açık. Oda raporu etkinliği ve düzenleyiciyi, TİP dergisi partinin "
              "kendi katılım bildirimini belgeliyor. TİP kortejinin sayısı, düzenleme görevi ve kişisel konuşmalar açık.")


def finding(suffix, text, keys, *, provenance="summary", group=None):
    ident = f"{case}-{suffix}"
    entry("finding", id=ident, party_id="tip", heading="Belgelenmiş uygulamalar", pair_id=group or ident,
          text=text, provenance=provenance, epistemic_type="claim")
    entry("review", id=f"review-{ident}", kind="finding", subject_id=ident, reviewer_kind="agent",
          reviewed_at=now, result="reviewed", reason="Özgün sayfa, yayıncı ve atıf okundu.")
    for key in keys:
        passage = passages[key]
        entry("finding_evidence", finding_id=ident, passage_id=passage["id"],
              role="quotation" if provenance == "quote" else "support")
        entry("verification", finding_id=ident, passage_id=passage["id"], checked_at=now,
              result="confirmed", reason=passage["section"])
    return ident


target = finding("target", "TİP İstanbul İl Örgütü, 8 Aralık Bakırköy mitingine katılma kararı aldığını açıkladı.", ("decision",))
quote = finding("quote", passages["decision"]["exact"], ("decision",), provenance="quote", group=target)
result = finding("result", "Oda raporuna göre miting 8 Aralık 2019’da Bakırköy Halk Pazarı’nda yapıldı. TİP, Ocak 2020 sayısında İstanbul mitingine katıldığını fotoğraflı haberle bildirdi.", ("occurrence", "venue", "party-role"))
explanation = finding("comparison", "Aralık sayısı belirli tarih ve yer için katılım kararını, Ocak sayısı aynı etkinliğe katılımı bildiriyor. Oda raporu tarih, yer ve ortak düzenleyiciyi doğruluyor. Partinin katılım kapsamı kendi yayınındaki bilgiyle sınırlı.", tuple(passages))
contribution = finding("party-contribution", "TİP, ÇarkBaşak’ta İstanbul’daki 8 Aralık mitingine katıldığını bildirdi.", ("party-role", "occurrence"))
event, statement, relation = (f"{case}-{kind}" for kind in ("event", "statement", "relation"))
add("practice_event", id=event, common_event_key="bakirkoy-2019-12-08-insanca-yasamak-istiyoruz", event_at="2019-12-08",
    date_precision="day", date_unknown_reason=None, title="Bakırköy’de İnsanca Yaşamak İstiyoruz mitingi",
    scope_context="8 Aralık 2019’da İstanbul Bakırköy Halk Pazarı’nda düzenlenen İnsanca Yaşamak İstiyoruz mitingi.",
    occurrence_basis="TMMOB Harita ve Kadastro Mühendisleri Odası İstanbul Şubesinin 25. Dönem Çalışma Raporu, PDF sayfa indeksi 99.")
add("practice_statement", id=statement, party_id="tip", topic_id=topic, taxonomy_version=4, summary_finding_id=target,
    quote_finding_id=quote, statement_at=None, date_precision="unknown", version_id=edition8_version,
    period_basis="Aralık 2019 sayı 8, 8 Aralık mitingi gelecek zamanla duyuruluyor. Kesin yayım günü açık.",
    uncertainty_reason=limitation, comparison_row_id="04-03-v3-03-v2-tip-demokrasi")
for key, stage, fact in (
    ("occurrence", "result", "HKMO, 8 Aralık mitingini ve ortak düzenleyiciyi bildiriyor."),
    ("venue", "action", "8 Aralık mitingi Bakırköy Halk Pazarı’nda yapıldı."),
):
    passage = passages[key]
    add("practice_event_evidence", event_id=event, passage_id=passage["id"], stage=stage,
        supported_point=fact, concrete_basis=passage["section"], limitation=limitation, epistemic_type="claim")
    add("practice_evidence_assessment", event_id=event, passage_id=passage["id"], stage=stage, basis_kind="document")
event_scope = scopes["event"]["cell_id"]
add("practice_relation", id=relation, party_id="tip", topic_id=topic, scope_id=event_scope, statement_id=statement,
    event_id=event, target_finding_id=target, result_finding_id=result, explanation_finding_id=explanation,
    comparability_reason="Aynı şehir mitingine katılım kararı ve partinin sonraki katılım bildirimi.",
    temporal_context="Aralık 2019 parti yayımı, 8 Aralık 2019 Bakırköy mitingi ve Ocak 2020 parti yayımı.",
    authority_context="TİP İstanbul İl Örgütü katılım kararı aldı. Oda raporu miting düzenleyicisini İstanbul Emek, Demokrasi ve Barış Koordinasyonu olarak anıyor.",
    uncertainty_reason=limitation)
add("practice_candidate", id=f"{case}-candidate", scope_id=event_scope, event_id=event, relation_id=relation,
    state="eligible", reason="Parti kararının konusu ile oda ve parti yayınlarındaki etkinlik aynı.",
    passage_ids=json.dumps([row["id"] for key, row in passages.items() if key != "decision"]))
actor = f"{case}-party-actor"
entry("actor", id=actor, kind="institution", party_id="tip", person_id=None, authorization_passage_id=None)
add("practice_contribution", id=f"{case}-participation", event_id=event, party_id="tip", actor_id=actor,
    contribution_kind="support", finding_id=contribution, authority_passage_id=None, membership_passage_id=None,
    responsibility_limit="Kendi yayımına atıflı kurumsal katılım. Düzenleyici görev, kişi, sayı ve sonraki sonuç ayrı.")

snapshot = read(Path("data/releases") / package["base_release"] / "records.json")
for row in entries:
    if row["values"] not in snapshot.setdefault(row["kind"], []):
        snapshot[row["kind"]].append(row["values"])
snapshot["practice_contract"] = records["practice_contract"]
for table, rows in records.items():
    target_rows = snapshot.setdefault(table, [])
    target_rows.extend(row for row in rows if row not in target_rows)
rules.validate_practices(snapshot)
targets = rules.practice_review_package_targets(snapshot, records,
    {row["values"]["id"] for row in entries if row["kind"] == "passage"}, party_id="tip")
reviews = review["practice_source_review"]
old_targets = {(row["subject_kind"], row["subject_id"]) for row in reviews}
assert old_targets <= targets.keys()
by_id = {row["id"]: row for row in passages.values()}
for kind, ident in sorted(targets.keys() - old_targets):
    refs, _ = targets[kind, ident]
    inspected = [by_id[ref] for ref in sorted(refs)]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        source_version_ids=json.dumps(sorted({row["version_id"] for row in inspected})), passage_ids=json.dumps(sorted(refs)),
        inspected_sections=json.dumps([row["section"] for row in inspected], ensure_ascii=False),
        supported_claim=" ".join(row["section"] for row in inspected), limitations=limitation,
        result="reviewed", reason=f"{kind} türündeki {ident} için etkinlik ve parti rolünün ayrı kanıtları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id="tip", target_keys=set(targets))
references = [{key: row[key] for key in ("subject_kind", "subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
assert [len(records[table]) for table in ("practice_event", "practice_relation", "practice_closure")] == [58, 54, 0]
for suffix, value in (("", package), ("-review", review)):
    path = checks / f"tip-bakirkoy-2019{suffix}-draft.json"
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    print(sha256(path.read_bytes()).hexdigest(), path)
