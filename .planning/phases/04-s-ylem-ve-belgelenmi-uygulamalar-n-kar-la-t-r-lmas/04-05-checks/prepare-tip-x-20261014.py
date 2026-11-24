"""Compare the TİP and EngelliWeb accounts of the October 2026 X restriction."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
import uygulamalar as rules
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(__file__).resolve().parent
working = Path("data/practices")
source_dir = checks / "tip-x-20261014-sources"
source_root = working / "sources" / "tip"
case = "0405-tip-x-20261014"
party = "tip"
topic = "ifade-basin-ozgurlugu"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(content):
    return hashlib.sha256(content).hexdigest()

pair = (working / "04-tip.json", working / "04-tip-review.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "e907eb2b76ee3a7881ed48b96bce2b24696133832bb88e7fbcf6a2a835a34f87",
    "21ddf3d0622c5e23697ffc766665261f87ea75ac6268373d5a893a26e70ca62d",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [23, 22, 0]
receipt = read(source_dir / "reading.json")
source_rows = {row["original_path"]: row for row in receipt["sources"]}

def insert(kind, row):
    entries.append({"kind": kind, "values": row})

def add(table, **row):
    records[table].append(row)

def vid(suffix):
    return f"{case}-{suffix}-v1"

def pid(suffix):
    return f"{case}-{suffix}-p"

def copy_verified(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == content, path
    else:
        path.write_bytes(content)

sources = {}
for name, match, label in (
    ("party","003.html.bin","TİP’in 14 Ekim X hesapları açıklaması"),
    ("observation","ifod-1014.html.bin","İFÖD EngelliWeb, TİP Genel Merkez X hesabı"),
    ("monthly","ifod-1102.html.bin","İFÖD, Ekim 2026 erişim engeli değerlendirmesi"),
):
    source = next(row for path,row in source_rows.items() if Path(path).name==match)
    raw = (source_dir/source["original_path"]).read_bytes()
    assert sha(raw)==source["sha256"]
    obj = Path("objects")/source["sha256"]
    original,readable = obj/"original.html.bin",obj/"readable.html"
    copy_verified(source_root/original,raw)
    copy_verified(source_root/readable,readable_bytes(raw,"html"))
    date, url = source["publication_date"],source["source_url"]
    insert("document",dict(id=f"{case}-{name}",party_id=party,title=label,source_kind=source["kind"]))
    insert("document_version",dict(id=vid(name),document_id=f"{case}-{name}",original_url=url,final_url=url,
        document_date=date,date_precision="day",date_unknown_reason=None,version_label=label,
        accessed_at=source["retrieved_at_utc"],verified_at=now,mime="text/html",sha256=source["sha256"],
        original_path=str(original),readable_path=str(readable)))
    insert("source_attribution",dict(version_id=vid(name),kind="party_publication" if name=="party" else "other",
        publisher=source["publisher"],author=None,social_handle=None,published_at=date,date_precision="day",
        public_url=url,basis=source["reading"]))
    view=build_view(raw,url,source_root,fetch_assets=False)
    validate_view(source_root,view)
    insert("archive_view",dict(view,version_id=vid(name)))
    sources[name]=(raw,url)

passages={}
for key,source,exact,section in (
    ("party-claim","party","Partimizin Genel Merkez ve İstanbul İl Başkanlığı X hesaplarına erişim engeli kararı verildiğini sosyal medya aracılığıyla öğrendik.",
     "Partinin iki hesap hakkında öğrendiğini bildirdiği karar"),
    ("party-quote","party","Söz konusu kararlar ise henüz uygulamaya konmamıştır.","Partinin yayın anındaki teknik durum beyanı"),
    ("party-view","party","fon vurgununu ifşa ettiğimiz",
     "Partinin gerekçeye ilişkin değerlendirmesi"),
    ("observer","observation","5651 sayılı Kanun’un 8/A maddesi kapsamında erişime engellendi.",
     "İFÖD’ün 14 Ekim’de Genel Merkez hesabına ilişkin aktarımı"),
    ("account","observation","(@tipgenelmerkez)","İFÖD’ün adını verdiği X hesabı"),
    ("platform","observation","Hesap, X tarafından henüz Türkiye’den görünmez kılınmadı.",
     "İFÖD’ün yayın anındaki platform durumu"),
    ("monthly-mentioned","monthly","Halk TV, T24, Türkiye İşçi Partisi ve gazetecilerin hesaplarının yanı sıra İFÖD ve EngelliWeb hesapları da yer aldı.",
     "İFÖD’ün Ekim dönemi hakkında 2 Kasım açıklamasında TİP kaydı"),
):
    assert exact in html_source_text(sources[source][0]),(key,exact)
    row=dict(id=pid(key),version_id=vid(source),exact=exact,prefix=None,suffix="</p>" if key=="platform" else None,
             article=None,section=section,pdf_page_index=None,printed_page=None)
    insert("passage",row)
    passages[key]=row

inventory=read(working/"04-inventory.json")
scopes={}
for row in inventory["cells"]:
    if row["party_id"]!=party or row["topic_id"]!=topic:
        continue
    lane,cell=row["research_kind"],row["cell_id"]
    scopes[lane]=cell
    if not any(r["id"]==cell for r in records["practice_scope_v2"]):
        add("practice_scope_v2",id=cell,**{k:row[k] for k in (
            "party_id","topic_id","taxonomy_version","period_start","cutoff_at","research_kind")},
            boundary_reason="14 Ekim TİP açıklaması ve bağımsız EngelliWeb kaydı okundu.")
assert len(scopes)==2
for key,(_,url) in sources.items():
    scope=scopes["statement" if key=="party" else "event"]
    version=vid(key)
    sections=[r["section"] for r in passages.values() if r["version_id"]==version]
    attempt=f"{version}-reading"
    add("practice_scope_source",scope_id=scope,version_id=version,inspected_at=now,
        inspected_sections=json.dumps(sections,ensure_ascii=False))
    add("practice_attempt_v2",id=attempt,scope_id=scope,attempted_at=now,query=url,url=url,result="examined",
        reason="14 Ekim X hesabı açıklaması veya bağımsız EngelliWeb izlemesi okundu.",source_version_id=version)
    add("practice_lead",id=f"lead-{attempt}",scope_id=scope,url=url,
        relevance_reason="14 Ekim’de bildirilen TİP Genel Merkez X hesabı erişim kararı.",state="examined",
        attempt_ids=json.dumps([attempt]))
for i, query in enumerate(receipt["queries"]):
    add("practice_attempt_v2",id=f"{case}-query-{i+1}",scope_id=scopes["event"],attempted_at=now,
        query=query,url=None,result="results",reason="İFÖD Genel Merkez hesabını izledi. Özgün karar ve il hesabı için bağımsız belge açık.",
        source_version_id=None)

bounds=("Özgün karar, makamı, dosya numarası, gerekçesi ve sonradan uygulanıp uygulanmadığı açık. İstanbul hesabı parti açıklamasında. İFÖD kendi yayınında Genel Merkez hesabını adlandırıyor.")

def finding(suffix,text,refs,*,quote=False,pair=None):
    ident=f"{case}-{suffix}"
    insert("finding",dict(id=ident,party_id=party,heading="Belgelenmiş uygulamalar",pair_id=pair or ident,
        text=text,provenance="quote" if quote else "summary",epistemic_type="claim"))
    insert("review",dict(id=f"review-{ident}",kind="finding",subject_id=ident,reviewer_kind="agent",
        reviewed_at=now,result="reviewed",reason="TİP yayımı ve İFÖD EngelliWeb duyurusu kendi kaynaklarında okundu."))
    for ref in refs:
        insert("finding_evidence",dict(finding_id=ident,passage_id=pid(ref),role="quotation" if quote else "support"))
        insert("verification",dict(finding_id=ident,passage_id=pid(ref),checked_at=now,result="confirmed",
            reason=passages[ref]["section"]))
    return ident

summary=finding("statement-summary","TİP, 14 Ekim’de iki X hesabı için erişim engeli kararı öğrendiğini ve kararın henüz uygulanmadığını bildirdi.",
                ("party-claim","party-quote"))
quote=finding("statement-quote",passages["party-quote"]["exact"],("party-quote",),quote=True,pair=summary)
statement=f"{case}-statement"
add("practice_statement",id=statement,party_id=party,topic_id=topic,taxonomy_version=4,
    summary_finding_id=summary,quote_finding_id=quote,statement_at="2026-10-14",date_precision="day",
    version_id=vid("party"),period_basis="TİP’in 14 Ekim 2026 tarihli özgün yayımı.",
    comparison_row_id="04-03-v3-0304-tip-program-ifade-row",uncertainty_reason=bounds)

event=f"{case}-event"
add("practice_event",id=event,common_event_key="ifod-2026-10-14-tip-merkez-x",event_at="2026-10-14",date_precision="day",
    date_unknown_reason=None,title="İFÖD’ün TİP Genel Merkez X hesabına ilişkin 14 Ekim bildirimi",
    scope_context="14 Ekim 2026 EngelliWeb izlemesinde @tipgenelmerkez ve 5651 sayılı Kanun 8/A.",
    occurrence_basis="İFÖD EngelliWeb’in tarihli duyurusu ve yayındaki görsel. Asıl karar tarihi açık.")
points={
    "observer":("action","İFÖD 14 Ekim’de 5651 sayılı Kanun’un 8/A maddesi kapsamında Genel Merkez hesabı için erişim engeli bildirdi."),
    "account":("action","EngelliWeb kaydında hesap @tipgenelmerkez."),
    "platform":("action","İFÖD, yayın sırasında X’in hesabı Türkiye’den gizlemediğini bildirdi."),
    "monthly-mentioned":("action","İFÖD 2 Kasım Ekim değerlendirmesinde TİP’i andı."),
}
for key,(stage,claim) in points.items():
    add("practice_event_evidence",event_id=event,passage_id=pid(key),stage=stage,supported_point=claim,
        concrete_basis=passages[key]["section"],limitation=bounds,epistemic_type="claim")
    add("practice_evidence_assessment",event_id=event,passage_id=pid(key),stage=stage,basis_kind="document")
explanation=finding("comparison","İFÖD, @tipgenelmerkez hesabı için 8/A kapsamında karar bildiriyor ve X’in hesabı o anda Türkiye’den gizlemediğini belirtiyor. İstanbul İl Başkanlığı hesabı parti açıklamasında yer alıyor. Fon açıklamalarıyla bağ partinin değerlendirmesi. Özgün karar ve sonraki teknik uygulama açık.",
                    ("party-claim","party-view","observer","account","platform","monthly-mentioned"))
relation=f"{case}-relation"
add("practice_relation",id=relation,party_id=party,topic_id=topic,scope_id=scopes["event"],statement_id=statement,event_id=event,
    target_finding_id=summary,result_finding_id=None,explanation_finding_id=explanation,
    comparability_reason="İki 14 Ekim yayımı TİP Genel Merkez X hesabını ele alıyor. İl hesabı parti yayınında.",
    temporal_context="İFÖD ve TİP’in 14 Ekim yayınları ile İFÖD’ün 2 Kasım Ekim değerlendirmesi.",
    authority_context="TİP kendi açıklamasını yayımladı. İFÖD bağımsız izleme duyurusu yayımladı. Karar makamı açık.",
    uncertainty_reason=bounds)
add("practice_candidate",id=f"{case}-candidate",scope_id=scopes["event"],event_id=event,relation_id=relation,
    state="eligible",reason="Parti ve İFÖD 14 Ekimde Genel Merkez hesabına ilişkin bildirimde bulundu.",
    passage_ids=json.dumps([pid(ref) for ref in points]))

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
claims.update({pid(ref): point for ref, (_, point) in points.items()})
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
        supported_claim=" ".join(claims[ref] for ref in sorted(refs)), limitations=bounds,
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için ilgili 14 Ekim parti yayımı ve İFÖD pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-x-20261014-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_X_20261014_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
