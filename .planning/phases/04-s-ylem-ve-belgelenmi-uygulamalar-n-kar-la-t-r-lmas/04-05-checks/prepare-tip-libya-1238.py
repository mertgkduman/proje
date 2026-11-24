"""Assemble the 3/1044 parliamentary comparison from the archived records."""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
import uygulamalar as rules
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

checks = Path(__file__).resolve().parent
working = Path("data/practices")
source_dir = checks / "tip-libya-1238-sources"
source_root = working / "sources" / "tip"
case = "0405-tip-libya-1238"
party = "tip"
topic = "dis-guvenlik"
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
preflight = sys.argv[1:] == ["--preflight"]
assert preflight or not sys.argv[1:]

def read(path):
    return json.loads(path.read_bytes())

def sha(content):
    return hashlib.sha256(content).hexdigest()

pair = (checks / "tip-7242-draft.json", checks / "tip-7242-review-draft.json")
assert tuple(sha(path.read_bytes()) for path in pair) == (
    "895205aaeff4c56d02993ddbaf040557fa361fa65f5ec880eb1bbc48011650ae",
    "dbb9d6da3f1c782e4e3e6adb4bcf4f2412baa87d9533f17c5c3057c36d5e6492",
)
package, review = map(read, pair)
entries, records = package["entries"], package["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [22, 21, 0]
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
for key, name, label in (
    ("party", "tip-libya.html.bin", "TİP Libya Tezkeresine Hayır açıklaması"),
    ("floor", "tbmm-41-tam.pdf", "TBMM 2 Ocak 2020 tarihli 41. birleşim tutanağı"),
    ("roll", "tbmm-41-oy.html.bin", "TBMM 41. birleşim kesin açık oy cetveli"),
    ("registry", "tbmm-1238-sicil.html.bin", "TBMM 1238 karar ve yayım sicili"),
):
    source = source_rows[name]
    raw_path = source_dir / name
    raw = raw_path.read_bytes()
    assert sha(raw) == source["sha256"], raw_path
    kind = "pdf" if name.endswith(".pdf") else "html"
    object_dir = Path("objects") / source["sha256"]
    original = object_dir / ("original.pdf" if kind == "pdf" else "original.html.bin")
    readable = object_dir / "readable.html"
    copy_verified(source_root / original, raw)
    copy_verified(source_root / readable, readable_bytes(raw, kind))
    doc_id = f"{case}-{key}"
    is_party = key == "party"
    date = source["document_date"]
    publish_date = source["published_at"]
    insert("document", dict(id=doc_id, party_id=party, title=label,
                            source_kind="party" if is_party else "official"))
    insert("document_version", dict(id=vid(key), document_id=doc_id, original_url=source["url"],
        final_url=source["url"], document_date=date, date_precision="day" if date else "unknown",
        date_unknown_reason=None if date else "Birçok karar içeren elektronik sicilin derleme tarihi açık.",
        version_label=label, accessed_at=source["retrieved_at_utc"], verified_at=now,
        mime="application/pdf" if kind=="pdf" else "text/html", sha256=source["sha256"],
        original_path=str(original), readable_path=str(readable)))
    insert("source_attribution", dict(version_id=vid(key), kind="party_publication" if is_party else "official",
        publisher=source["publisher"], author=None, social_handle=None, published_at=publish_date,
        date_precision="instant" if publish_date else "unknown", public_url=source["url"], basis=source["reading"]))
    if kind == "html":
        view = build_view(raw, source["url"], source_root, fetch_assets=False,
                          http_charset=source.get("http_charset"))
        validate_view(source_root, view)
        insert("archive_view", dict(view, version_id=vid(key)))
    sources[key] = source, raw_path

roll_text = html_source_text(sources["roll"][1].read_bytes())
def vote_cells(name, last_name, outcome):
    start = roll_text.index(f"<td>{last_name}</td>" + " " * 24 + f"<td>{name}</td>")
    end = roll_text.index("</tr>", start)
    line = roll_text[start:end]
    assert "T&#252;rkiye İş&#231;i Partisi" in line
    assert line.count(f">{outcome}<") == 2
    return line[:line.index(f">{outcome}<") + len(outcome) + 2]

passages = {}
for key, source, page, exact, section in (
    ("party-quote", "party", None, "bugüne kadar görülmemiş yetkiler verilmek istenmektedir.", "TİP’in Cumhurbaşkanına verilecek yetkiye ilişkin itirazı"),
    ("party-opposition", "party", None, "süren kirli savaşın parçası haline getirmesini kabul etmiyoruz.", "TİP’in tezkerede asker gönderilmesine itirazı"),
    ("filing", "floor", 0, "30 Aralık 2019 tarihinde Meclis Başkanlığına sunulan (3/1044)", "3/1044 numaralı tezkerenin sunuş günü"),
    ("authority", "floor", 7, "1) Erkan Baş, İstanbul Milletvekili, Türkiye İşçi Partisi Genel Başkanı.", "Grubu bulunmayan siyasi parti temsilcileri arasında Baş’ın tanıtımı"),
    ("speaker", "floor", 18, "İstanbul Milletvekili ve Türkiye İşçi Partisi Genel Başkanı Sayın Erkan Baş.", "Başkanın Erkan Baş’a bu sıfatlarla söz vermesi"),
    ("speech", "floor", 18, "herhangi bir ülkenin başka bir ülkeye dönük her tür\naskerî operasyonuna karşı olduğunu paylaşmak istiyorum.", "Erkan Baş’ın parti tutumunu Genel Kurulda açıklaması"),
    ("tally-chair", "floor", 26, "Kullanılan oy sayısı : 509\nKabul : 325\nRet : 184", "Kürsüde ilk duyurulan sayılar"),
    ("tally-appendix", "floor", 26, "Açık oylama kesin sonuçlarını gösteren tablo tutanağa eklidir.", "Tutanağın kesin açık oy cetveline dipnotu"),
    ("roll-yes", "roll", None, "Kabul Edenler </td>" + " " * 16 + '<td align="left">:&nbsp;332', "Kesin cetvelde 332 kabul"),
    ("roll-no", "roll", None, "Reddedenler </td>" + " " * 16 + '<td align="left">:&nbsp;183', "Kesin cetvelde 183 ret"),
    ("roll-duplicate", "roll", None, "Mükerrer Oylar </td>" + " " * 16 + '<td align="left">:&nbsp;6', "Kesin cetvelde 6 mükerrer oy"),
    ("roll-total", "roll", None, "Toplam </td>" + " " * 16 + '<td align="left" style="">:&nbsp;521', "Kesin cetvelde 521 toplam"),
    ("roll-bas", "roll", None, vote_cells("Erkan", "BAŞ", "RED"), "İstanbul TİP Erkan Baş kişisel Red satırı"),
    ("roll-atay", "roll", None, vote_cells("Barış Atay", "MENG&#220;LL&#220;OĞLU", "KATILMADI"), "Hatay TİP Barış Atay Mengüllüoğlu Katılmadı satırı"),
    ("decision", "registry", None, "KARAR NO:1238", "TBMM 1238 sayılı kararın sicil kaydı"),
    ("publication", "registry", None, "03.01.2020 No: 30997", "Sicilde 1238 için Resmî Gazete yayım günü ve sayısı"),
):
    raw = sources[source][1]
    body = html_source_text(raw.read_bytes()) if page is None else pdf_page_text(raw,page)
    assert exact in body, (key,exact)
    row = dict(id=pid(key), version_id=vid(source), exact=exact, prefix=None, suffix=None,
               article=None, section=section, pdf_page_index=page, printed_page=None)
    insert("passage",row)
    passages[key]=row

inventory = read(working / "04-inventory.json")
scopes = {}
for row in inventory["cells"]:
    if row["party_id"] != party or row["topic_id"] != topic:
        continue
    lane, cell = row["research_kind"], row["cell_id"]
    scopes[lane] = cell
    if not any(item["id"] == cell for item in records["practice_scope_v2"]):
        add("practice_scope_v2", id=cell, **{key:row[key] for key in (
            "party_id", "topic_id", "taxonomy_version", "period_start", "cutoff_at", "research_kind")},
            boundary_reason="2 Ocak 2020 TİP tutumu ve 3/1044 kabulünün kaynakları okundu.")
assert len(scopes)==2
for key,(source,_) in sources.items():
    lane = "statement" if key == "party" else "event"
    scope = scopes[lane]
    version = vid(key)
    sections = sorted(row["section"] for row in passages.values() if row["version_id"] == version)
    attempt = f"{version}-{lane}-reading"
    add("practice_scope_source", scope_id=scope, version_id=version, inspected_at=now,
        inspected_sections=json.dumps(sections,ensure_ascii=False))
    add("practice_attempt_v2", id=attempt, scope_id=scope, attempted_at=now, query=source["url"],
        url=source["url"], result="examined", reason="2 Ocak TİP yayımı veya 3/1044 ve 1238 işlem zinciri okundu.",
        source_version_id=version)
    add("practice_lead", id=f"lead-{attempt}", scope_id=scope, url=source["url"],
        relevance_reason="Libya tezkeresi 3/1044 için dönemsel tutum veya kabul kaydı.", state="examined",
        attempt_ids=json.dumps([attempt]))

bounds = ("Kesin cetvel ile kürsü sayımı ayrı kaynaklarda. İki sayım arasındaki farkın hesap ayrıntısı, "
          "Mengüllüoğlu’nun katılmama nedeni, iznin fiilî kullanımı ve sonuçları açık.")

def finding(suffix, content, refs, *, quote=False, pair=None):
    ident = f"{case}-{suffix}"
    insert("finding",dict(id=ident,party_id=party,heading="Belgelenmiş uygulamalar",pair_id=pair or ident,
        text=content,provenance="quote" if quote else "summary",epistemic_type="claim"))
    insert("review",dict(id=f"review-{ident}",kind="finding",subject_id=ident,reviewer_kind="agent",
        reviewed_at=now,result="reviewed",reason="Özgün TİP yayımı, TBMM tutanağı ve kesin oy cetveli okundu."))
    for ref in refs:
        insert("finding_evidence",dict(finding_id=ident,passage_id=pid(ref),role="quotation" if quote else "support"))
        insert("verification",dict(finding_id=ident,passage_id=pid(ref),checked_at=now,result="confirmed",
            reason=passages[ref]["section"]))
    return ident

summary = finding("statement-summary", "TİP’in 2 Ocak 2020 açıklaması Libya’ya asker gönderilmesine ve Cumhurbaşkanına verilecek yetkinin kapsamına karşı çıktı.", ("party-opposition","party-quote"))
quote = finding("statement-quote", passages["party-quote"]["exact"], ("party-quote",), quote=True, pair=summary)
statement = f"{case}-statement"
add("practice_statement", id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at="2020-01-02", date_precision="day",
    version_id=vid("party"), period_basis="TİP yayımının 2 Ocak 2020 tarihli kaynak üst verisi ve aynı günkü açıklaması.",
    comparison_row_id="04-03-v3-0304-tip-program-sosyalist-dis-silah-row", uncertainty_reason=bounds)

event = f"{case}-event"
relation = f"{case}-relation"
add("practice_event",id=event,common_event_key=receipt["common_event_key"],event_at="2020-01-02",date_precision="day",
    date_unknown_reason=None,title="3/1044 Libya tezkeresinin 1238 sayılı kararla kabulü",
    scope_context="TBMM 27. dönem 3. yasama yılı 41. birleşim, 3/1044 açık oylaması",
    occurrence_basis="2 Ocak Genel Kurul tutanağı, kesin oy cetveli ve 1238 karar sicili.")
result = finding("result", "TBMM 2 Ocak’ta Libya tezkeresini kabul etti. Kesin cetvel 332 kabul, 183 ret, 6 mükerrer ve toplam 521 oy kaydediyor. 1238 sayılı karar 3 Ocak’ta yayımlandı.", ("decision","publication","roll-yes","roll-no","roll-duplicate","roll-total"))
explanation = finding("comparison", "TİP’in 2 Ocak açıklamasında ve Erkan Baş’ın aynı gün temsilci olarak yaptığı konuşmada tezkereye itiraz var. Kesin cetvelde Erkan Baş için Red, Barış Atay Mengüllüoğlu için Katılmadı yazıyor. Kürsüde 325 kabul, 184 ret ve 509 toplam okundu. Tutanak kesin cetvele ayrıca işaret ediyor.", ("party-opposition","speaker","speech","roll-bas","roll-atay","tally-chair","tally-appendix"))
speech = finding("represented-objection", "Baş, TİP Genel Başkanı ve grubu bulunmayan parti temsilcisi sıfatıyla kürsüde sınır ötesi askerî müdahalelere itirazı açıkladı.", ("authority","speaker","speech"))
vote = finding("personal-vote", "Erkan Baş’ın kesin kişisel oy satırı Red.", ("roll-bas",))

points = {
    "filing":("initiative","3/1044 tezkerenin 30 Aralık 2019’da sunulduğu kaydedildi."),
    "authority":("action","Erkan Baş, grubu bulunmayan parti temsilcileri arasında yazılı."),
    "speech":("action","Erkan Baş tezkerenin görüşülmesi sırasında parti tutumunu açıkladı."),
    "tally-chair":("action","Kürsü 509 toplam, 325 kabul ve 184 ret duyurdu."),
    "tally-appendix":("action","Tutanak kesin cetvele ayrı dipnotla bağlanıyor."),
    "roll-yes":("result","Kesin cetvel 332 kabul gösteriyor."),
    "roll-no":("result","Kesin cetvel 183 ret gösteriyor."),
    "roll-duplicate":("result","Kesin cetvel 6 mükerrer gösteriyor."),
    "roll-total":("result","Kesin cetvel toplam 521 gösteriyor."),
    "roll-bas":("result","Erkan Baş kesin cetvelde Red."),
    "roll-atay":("result","Barış Atay Mengüllüoğlu kesin cetvelde Katılmadı."),
    "decision":("result","1238 TBMM kararı sicilde kayıtlı."),
    "publication":("result","1238 sayılı kararın 3 Ocak 2020 tarihli 30997 sayılı Resmî Gazete’de yayımı."),
}
for key,(stage,point) in points.items():
    add("practice_event_evidence", event_id=event, passage_id=pid(key), stage=stage, supported_point=point,
        concrete_basis=passages[key]["section"],limitation=bounds,epistemic_type="claim")
    add("practice_evidence_assessment",event_id=event,passage_id=pid(key),stage=stage,basis_kind="document")

for label, role, claim, identity, authority, membership, limit in (
    ("speech","authorized_representative",speech,"authority","authority",None,
     "Aynı oturumun TİP temsilci konuşması. Kişisel oy ayrı cetvelde."),
    ("vote","individual_mp",vote,"authority",None,"speaker",
     "Erkan Baş’ın kişisel oyu. TBMM oylamasıyla kabul yetkisi Genel Kurula ait."),
):
    actor = f"{case}-{label}-actor"
    contribution = f"{case}-{label}-contribution"
    insert("actor",dict(id=actor,kind=role,party_id=party,person_id="0405-tip-erkan-bas",
        authorization_passage_id=pid(authority) if authority else None))
    add("practice_contribution",id=contribution,event_id=event,party_id=party,actor_id=actor,
        contribution_kind="objection",finding_id=claim,authority_passage_id=pid(authority) if authority else None,
        membership_passage_id=pid(membership) if membership else None,responsibility_limit=limit)
    add("practice_actor_period",contribution_id=contribution,valid_from="2020-01-02",valid_to="2020-01-02",
        identity_passage_id=pid(identity))

add("practice_relation",id=relation,party_id=party,topic_id=topic,scope_id=scopes["event"],statement_id=statement,
    event_id=event,target_finding_id=summary,result_finding_id=result,explanation_finding_id=explanation,
    temporal_context="30 Aralık 2019 sunuşu, 2 Ocak 2020 açıklama, görüşme ve kabul, 3 Ocak 2020 yayım.",
    comparability_reason="TİP açıklaması ve Genel Kurul kararı aynı 3/1044 Libya tezkeresini ele alıyor.",
    authority_context="TİP yayım ve temsilci konuşması, Erkan Baş’ın kişisel oyu, Genel Kurulun kabulü ve 1238 kararı kendi kaynaklarında.",
    uncertainty_reason=bounds)
add("practice_candidate",id=f"{case}-candidate",scope_id=scopes["event"],event_id=event,relation_id=relation,
    state="eligible",reason="2 Ocak 2020 parti açıklaması ve Genel Kuruldaki 3/1044 kabulü aynı düzenleme.",
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
        result="reviewed", reason=f"{kind} türündeki {ident} kaydı için ilgili 2 Ocak TİP yayımı ve 3/1044 pasajları okundu."))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
references = [{k: row[k] for k in ("subject_kind","subject_id")} for row in reviews]
for payload in (package, review):
    payload["source_review_refs"] = references
if not preflight:
    for suffix, payload in (("draft", package), ("review-draft", review)):
        with (checks / f"tip-libya-1238-{suffix}.json").open("x") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
print("TIP_LIBYA_1238_SEMANTIC_OK", len(records["practice_event"]), len(records["practice_relation"]))
