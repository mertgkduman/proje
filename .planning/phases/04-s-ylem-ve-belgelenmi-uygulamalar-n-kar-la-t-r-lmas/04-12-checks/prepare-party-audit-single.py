"""Append three Demokrat Parti audit decisions to the verified pair."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
import uygulamalar as rules
from arsiv import pdf_page_text, readable_bytes

checks = Path(__file__).resolve().parent
source_dir = checks / "party-financial-audit-sources"
working = Path("data/practices")
source_root = working / "sources" / "demokrat"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
case = "0412-party-audit-single"
party = "demokrat"
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

pair = (working / "04-demokrat.json", working / "04-demokrat-review.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "c59a6d87c95ab466afadd7adc5f76438e3bf29d02f7a550fb6b2d3c0b02bcefe",
    "3f043616ba1a95ad72320a46a4f19f824974bccecf9256d7a08ceeaf67d1aaa9",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert tuple(len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")) == (75,50,0)
receipt = read(source_dir / "single-decisions-reading.json")
scopes = {row["research_kind"]:row["id"] for row in records["practice_scope_v2"] if row["topic_id"]=="mali-kesin-hesap"}

def insert(table, **row):
    entries.append(dict(kind=table, values=row))

def add(table, **row):
    records[table].append(row)

clauses = {
    2014: ("2015-65-2019-15", 4, "3.618.990,00 TL gelir", "179.880,38 TL gider karşılığı",
           "2014 hükmünde 3.618.990,00 TL gelir ve 5.421.416,72 TL gider var. 179.880,38 TL için Hazineye irat ve kalan bölüm için uygunluk kararı verildi."),
    2015: ("2016-65-2019-33", 6, "1.848.862,00 TL gelir", "1.809,98 TL gider karşılığı",
           "2015 hükmünde 1.848.862,00 TL gelir ve 5.519.493,82 TL gider var. 1.809,98 TL için Hazineye irat, kalan bölüm için uygunluk kararı verildi."),
    2016: ("2017-28-2020-22", 2, "1.523.775 TL gelir", "1.763.474,89 TL gider",
           "2016 gerekçesinde 1.532.775,00 TL, hükümde 1.523.775 TL gelir yazıyor. Hükümde gider 1.763.474,89 TL. AYM oybirliğiyle uygunluk kararı verdi. 9.000 TL fark açık."),
}

bounds = ("Mahkemenin kararı ilgili hesap yılı ve eldeki bilgi ve belgelerle sınırlı. "
          "Parti içi yetkili organ kararı ve irat hükmünün fiilî tahsilatı açık. "
          "18 Haziran 2022’de yakalanan tüzüğün bu yıllardaki yürürlük durumu açık.")
claims = {}
for row in receipt["sources"]:
    year = row["accounting_year"]
    docket, page, figure, verdict, point = clauses[year]
    stem = f"{case}-{year}"
    vid = f"{stem}-v1"
    title = f"Demokrat Parti {year} kesin hesabına ilişkin AYM kararı"
    path = source_dir / row["original_path"]
    raw = path.read_bytes()
    assert sha(raw)==row["sha256"]
    original = Path("objects") / row["sha256"] / "original.pdf"
    readable = original.with_name("readable.html")
    (source_root / original).parent.mkdir(parents=True, exist_ok=True)
    for relative, value in ((original, raw),(readable, readable_bytes(raw,"pdf"))):
        destination = source_root / relative
        if destination.exists():
            assert destination.read_bytes()==value
        else:
            destination.write_bytes(value)
    insert("document", id=stem, party_id=party, title=title, source_kind="official")
    insert("document_version", id=vid, document_id=stem, original_url=row["url"], final_url=row["url"],
        document_date=row["decision_day"], date_precision="day", date_unknown_reason=None,
        version_label=f"AYM Kararlar Bilgi Bankası, {year} tekil karar", accessed_at=row["retrieved_at_utc"],
        verified_at=now, mime="application/pdf", sha256=row["sha256"], original_path=str(original), readable_path=str(readable))
    insert("source_attribution", version_id=vid, kind="official", publisher="Anayasa Mahkemesi", author=None,
        social_handle=None, published_at=None, date_precision="unknown", public_url=row["url"], basis=f"AYM tekil PDF. Resmî Gazete {row['gazette_day']}, sayı {row['gazette_number']}. {row['reading']}")
    event = f"{stem}-event"
    add("practice_event", id=event, common_event_key=f"aym-spmd-{docket}-demokrat-{year}",
        event_at=row["decision_day"], date_precision="day", date_unknown_reason=None, title=title,
        scope_context=f"Demokrat Parti’nin {year} hesap yılı ve AYM mali denetimi.",
        occurrence_basis="AYM Kararlar Bilgi Bankasındaki tekil kararın hüküm bölümü.")
    evidences = [
        ("case", row["pages_zero_based"][0], None,
         f"{year} yılı kesin hesabının incelenmesidir.", "Mali denetimin konusu ve hesap yılı", "action", f"{year} kesin hesabı, {row['case']}."),
        ("figures", page, None, figure, "Hükümde hesap tutarları", "result", point),
        ("verdict", page, None, verdict, "Hükmün karar şekli ve sınırlaması", "result", point),
    ]
    if year==2014:
        evidences.extend([
            ("reply-balance", 1, None, "Partisi mali tablosundan intikal eden verilerden oluştuğu",
             "Kararda aktarılan parti cevabı ve geçmiş dönem bakiyesi", "action",
             "Parti, bakiyenin büyük bölümünü 2009 birleşmesinde Anavatan Partisi mali tablosundan devraldığını ve arşiv ayrıntısına erişemediğini bildirdi."),
            ("reply-error", 2, None, "söz konusu gidere ilişkin işlemin sehven yapıldığı",
             "Kararda aktarılan sehven işlem cevabı", "action",
             "Parti, ilgili gider işleminin sehven yapıldığını bildirdi."),
            ("reply-withholding", 3, None, "bu sebeple stopaj kesintisinin yapılamadığı ifade edilmiştir.",
             "Kararda aktarılan gider pusulası cevabı", "action",
             "Parti, onaylı gider pusulası bulunmadığı için stopaj yapamadığını bildirdi."),
        ])
    if year==2015:
        evidences.extend([
            ("unproved", 5, None, "edilmeyen 1.250,00 TL gider", "Belgesiz gider hakkında gerekçe",
             "result", "AYM 1.250,00 TL gideri tevsik edilmemiş olarak değerlendirdi."),
            ("separate", 5, None, "559,98 TL tutarındaki harcama karşılığı", "Parti tüzel kişiliği dışında gider",
             "result", "AYM 559,98 TL harcamayı parti tüzel kişiliği adına yapılmamış olarak değerlendirdi."),
            ("reply-expense", 4, None, "verilen cevapta söz konusu giderlerin siyasi faaliyetler kapsamında",
             "Kararda aktarılan gider belgesi cevabı", "action",
             "Parti, giderlerin siyasi faaliyetlere ilişkin olduğunu ve yazar kasa fişlerini sunduğunu bildirdi."),
            ("reply-travel", 5, None, "bileti harcamasına ilişkin olduğu ve faturalarının sunulduğu belirtilmiştir.",
             "Kararda aktarılan uçak bileti cevabı", "action",
             "Parti, harcamanın iki yöneticinin uçak biletiyle ilgili olduğunu ve faturaları sunduğunu bildirdi."),
        ])
    if year==2016:
        evidences.append(("grounds", 1, None, "1.532.775,00 TL, önceki yıldan devreden nakit",
                          "Gerekçe 4. paragraftaki gelir toplamı", "result",
                          "Gerekçenin 4. paragrafında 1.532.775,00 TL gelir yazıyor."))
    refs, sections = [], []
    for suffix,index,printed_page,exact,section,stage,detail in evidences:
        assert exact in pdf_page_text(path,index), (year,suffix,exact)
        passage=f"{stem}-{suffix}-p"
        insert("passage", id=passage, version_id=vid, exact=exact, prefix=None, suffix=None,
            article=None, section=section, pdf_page_index=index, printed_page=printed_page)
        add("practice_event_evidence", event_id=event, passage_id=passage, stage=stage,
            supported_point=detail, concrete_basis=section, limitation=bounds, epistemic_type="claim")
        add("practice_evidence_assessment", event_id=event, passage_id=passage, stage=stage, basis_kind="document")
        claims[passage] = detail
        refs.append(passage)
        sections.append(section)
    scope = scopes["event"]
    attempt = f"{stem}-reading"
    add("practice_scope_source", scope_id=scope, version_id=vid, inspected_at=now,
        inspected_sections=json.dumps(sections,ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=row["url"], url=row["url"],
        result="examined", reason=f"{year} denetiminin ilk incelemesi, gerekçesi ve hükmü özgün sayfalardan okundu.", source_version_id=vid)
    add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=row["url"],
        relevance_reason=f"Demokrat Parti’nin {year} yılı mali denetim kararı.", state="examined", attempt_ids=json.dumps([attempt]))
    add("practice_candidate", id=f"{stem}-candidate", scope_id=scope, event_id=event,
        relation_id=None, state="unmatched", passage_ids=json.dumps(refs),
        reason=f"{year} hesabına özgü bağımsız dönemsel parti açıklaması bu aramada doğrulanmadı. {point}")

    if year==2016:
        dispute = f"{stem}-income-dispute"
        summary = f"{dispute}-finding"
        grounds = f"{stem}-grounds-p"
        judgement = f"{stem}-figures-p"
        insert("finding",id=summary,party_id=party,heading="Belgelenmiş uygulamalar",pair_id=summary,
               text=point,provenance="summary",epistemic_type="claim")
        insert("review",id=f"review-{summary}",kind="finding",subject_id=summary,reviewer_kind="agent",
               reviewed_at=now,result="reviewed",reason="AYM gerekçesi ve hükmündeki iki gelir toplamı kendi sayfasından okundu.")
        for pid in (grounds,judgement,f"{stem}-verdict-p"):
            insert("finding_evidence",finding_id=summary,passage_id=pid,role="support")
            insert("verification",finding_id=summary,passage_id=pid,checked_at=now,result="confirmed",
                   reason="İlgili gerekçe ve hüküm sayfaları AYM’nin özgün tekil PDF’sinde okundu.")
        add("practice_dispute",id=dispute,event_id=event,summary_finding_id=summary,
            supported_points="AYM oybirliğiyle eldeki belgeler üzerinden 2016 hesabının uygunluğuna karar verdi.",
            disputed_points="Gerekçe 1.532.775,00 TL, hüküm 1.523.775 TL gelir gösteriyor.",
            unresolved_points="9.000 TL farkın açıklaması ve tashih kaydı açık.")
        add("practice_dispute_evidence",dispute_id=dispute,passage_id=grounds,
            point="Gerekçede 1.532.775,00 TL toplam gelir.",source_position="AYM gerekçesi 4. paragraf",role="conflict")
        add("practice_dispute_evidence",dispute_id=dispute,passage_id=judgement,
            point="Hükümde 1.523.775 TL gelir.",source_position="AYM kararının IV. Sonuç bölümü",role="support")

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
    {row["values"]["id"] for row in entries if row["kind"]=="passage"}, party_id=party)
passages = {row["id"]:row for row in snapshot["passage"]}
reviews = review["practice_source_review"]
existing = {(row["subject_kind"],row["subject_id"]) for row in reviews}
assert existing <= targets.keys()
for kind,ident in sorted(targets.keys()-existing):
    refs,_ = targets[kind,ident]
    inspected = [passages[ref] for ref in sorted(refs)]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind="agent", reviewed_at=now,
        source_version_ids=json.dumps(sorted({row["version_id"] for row in inspected})),
        passage_ids=json.dumps([row["id"] for row in inspected]),
        inspected_sections=json.dumps(sorted({row["section"] for row in inspected}),ensure_ascii=False),
        supported_claim=" ".join(dict.fromkeys(claims[ref] for ref in sorted(refs))), limitations=bounds,
        result="reviewed", reason=f"{ident} kaydındaki {kind} için AYM’nin ilgili hesap yılı ve hüküm sayfası okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{key:row[key] for key in ("subject_kind","subject_id")} for row in reviews]
for payload in (package,review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft",package),("review-draft",review)):
        with (checks / f"party-audit-single-{suffix}.json").open("x") as stream:
            stream.write(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
print("DEMOCRAT_PARTY_AUDIT_SINGLE_OK",len(records["practice_event"]),len(records["practice_relation"]))
