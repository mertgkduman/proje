"""Verify the frozen rehearsal independently from the preview producer."""

from collections import Counter
from datetime import datetime
from hashlib import file_digest
from pathlib import Path
from sys import argv
import json
import sqlite3

checks = Path(__file__).resolve().parent
job = argv[1]
number = argv[2] if len(argv) == 3 else "16"
assert number in {"16", "17", "18", "19", "20"}
prefix = "UNION_REHEARSAL_PREVIEW_OK "
log = checks / f"wave4-merge-rehearsal-{number}-{job}-slurm.log"
frozen = json.loads((checks / f"wave4-merge-rehearsal-{number}.json").read_bytes())
previous = json.loads((checks / "wave4-merge-rehearsal-12-62615150-independent.json").read_bytes())
line, = (line for line in log.read_text().splitlines() if line.startswith(prefix))
receipt = json.loads(line.removeprefix(prefix))
assert receipt["job"] == receipt["validation_job"] == job and receipt["rehearsal"] == number
folder = Path(receipt["preview"])


def digest(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


assert digest(folder / "manifest.json") == receipt["manifest_sha256"]
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
assert all(digest(folder / name) == identity for name, identity in manifest["files"].items())
assert all(digest(folder.parents[1] / name) == identity for name, identity in manifest["asset_files"].items())
assert digest(Path("data/current.json")) == receipt["canonical_pointer_sha256"] == frozen["canonical_pointer_sha256"]
records = json.loads((folder / "records.json").read_bytes())
assert {name: len(records[name]) for name in frozen["counts"]} == frozen["counts"]
assert len(records["practice_event_alias"]) == frozen["aliases"]
assert Counter(row["decision"] for row in records["practice_event_decision"]) == Counter(
    same=frozen["same_candidates"], unresolved=frozen["unresolved_candidates"])
origins = sum(row["origin_kind"] == "review_origins" for row in records["practice_merge_origin"])
assert origins == frozen["review_origins"]
joint_key = "yerel-yonetimler-2020-05-18-ortak-bildiri"
bakirkoy_key = "bakirkoy-2019-12-08-insanca-yasamak-istiyoruz"
presentation_key = "six-party-2022-11-28-constitutional-proposal-presentation"
meeting_key = "six-leaders-2022-11-28-dp-meeting"
november_keys = {presentation_key, meeting_key}
expanded_keys = {bakirkoy_key, *november_keys} if number in {"19", "20"} else set()
idlib_key = "idlib-2020-03-05-moskova-ek-protokol"
if number == "20":
    expanded_keys.add(idlib_key)
assert receipt["source_permissions"] == {"19": 669, "20": 677}.get(number, 655)
expected_added = {"16": {joint_key}, "20": {idlib_key}}.get(number, expanded_keys)
assert set(frozen["added_reviewed_candidates"]) == expected_added
halic_key = "halic-emek-ozgurluk-2022-09-24"
yok_key = "yok-2023-03-30-bahar-yuzyuze-secenegi"
assert set(receipt["shared_keys"]) == set(previous["shared_keys"]) | {halic_key, yok_key, joint_key} | expanded_keys

compare = ("practice_event", "practice_relation", "practice_closure", "practice_candidate", "practice_candidate_revision",
           "practice_contribution", "practice_event_decision", "practice_event_alias", "practice_source_party",
           "practice_merge_origin")
relations = {row["id"]: row["event_id"] for row in records["practice_relation"]}
expected_relations = (
    "0405-tip-election-finland-2023-election-relation",
    "0405-tip-election-finland-2023-nato-relation",
    "0405-tip-earthquake-2023-housing-relation",
    "0405-tip-earthquake-2023-education-relation",
    "0407-akbelen-2023-relation",
    "0410-akbelen-meeting-relation",
    "0411-saadet-retired-2023-relation",
    "0412-yassiada-2022-dp-relation",
    "0405-tip-halic-cemevi-2022-halic-relation",
    "0410-halic-2022-relation",
    "0411-saadet-education-2023-relation",
    "0405-tip-halic-cemevi-2022-cemevi-relation",
    "0406-van-2024-relation",
    "0405-tip-amasra-saopaulo-2022-mine-relation",
    "0405-tip-amasra-saopaulo-2022-ship-relation",
    "0405-tip-school-montro-paris-school-relation",
    "0405-tip-school-montro-paris-montro-relation",
    "0405-tip-school-montro-paris-paris-relation",
    "0405-tip-2020-2021-court-wage-election-court-relation",
    "0405-tip-2020-2021-court-wage-election-wage-relation",
    "0405-tip-2020-2021-court-wage-election-election-relation",
    "0411-saadet-election-2023-relation",
)
assert set(expected_relations) <= relations.keys()
assert relations["0411-saadet-election-2023-relation"] != relations["0405-tip-election-finland-2023-election-relation"]
assert relations["0407-akbelen-2023-relation"] != relations["0410-akbelen-meeting-relation"]

with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    for table in compare:
        dumped = Counter(json.dumps(row, sort_keys=True) for row in records[table])
        sql = Counter(json.dumps(dict(row), sort_keys=True) for row in db.execute(f"SELECT * FROM {table}"))
        assert dumped == sql, table
    for key, shared in previous["shared_events"].items():
        assert db.execute("SELECT id FROM practice_event WHERE common_event_key=?", (key,)).fetchone()[0] == shared["event_id"]
        assert db.execute("SELECT COUNT(*) FROM practice_event_alias WHERE decision_id=?", (key,)).fetchone()[0] == shared["aliases"]
    for key, rows in (("ankara-2025-11-01-02-demokrasi-baris-calistayi", previous["workshop_contributions"]),
                      ("six-leaders-2022-10-02-chp-second-round-meeting", previous["meeting_contributions"])):
        event = previous["shared_events"][key]["event_id"]
        assert set(tuple(row) for row in rows) == {tuple(row) for row in db.execute(
            "SELECT party_id, actor_id, authority_passage_id FROM practice_contribution WHERE event_id=?", (event,))}
    vote_ids = {row[0] for row in db.execute(
        "SELECT passage_id FROM practice_event_evidence WHERE event_id=?", (previous["shared_7527_event"],))}
    assert set(previous["separate_7527_vote_passages"]) <= vote_ids
    key = "tbmm-27-3-84-2-2762-law-7242"
    assert [row[0] for row in db.execute(
        "SELECT id FROM practice_event WHERE common_event_key=? ORDER BY id", (key,))] == [
        "0405-tip-7242-event", "0410-law-7242-event"]
    assert db.execute("SELECT decision FROM practice_event_decision WHERE id=?", (key,)).fetchone()[0] == "unresolved"

    halic = "0405-tip-halic-cemevi-2022-halic-event"
    yok = "0405-tip-earthquake-2023-education-event"
    for key, identity, aliases, parties, digest in (
        (halic_key, halic, 4, {"tip", "emep"},
         "a086de25cf9ac44d84a409f658b25d16a6e9f33b801089d56e066806fd10625e"),
        (yok_key, yok, 2, {"tip", "saadet"},
         "61aaf2ac82bfbf8cf5e9c47a95695899c2d1037fd1f58d90d3bf03ea5c307a5c"),
    ):
        assert db.execute("SELECT id FROM practice_event WHERE common_event_key=?", (key,)).fetchone()[0] == identity
        assert db.execute("SELECT COUNT(*) FROM practice_event_alias WHERE decision_id=?", (key,)).fetchone()[0] == aliases
        assert {r[0] for r in db.execute("SELECT party_id FROM practice_relation WHERE event_id=?", (identity,))} == parties
        digests = {r[0] for r in db.execute(
            "SELECT v.sha256 FROM practice_event_evidence e JOIN passage p ON e.passage_id=p.id "
            "JOIN document_version v ON p.version_id=v.id WHERE e.event_id=? AND e.stage!='initiative'", (identity,))}
        assert digests == {digest}
    roles = {tuple(r) for r in db.execute(
        "SELECT c.party_id,p.name,c.contribution_kind FROM practice_contribution c JOIN actor a ON c.actor_id=a.id "
        "LEFT JOIN person p ON a.person_id=p.id WHERE c.event_id=?", (halic,))}
    assert roles == {("tip", None, "support"), ("tip", "Erkan Baş", "task"), ("emep", None, "task"),
                     ("dem", "Ayşe Erdem", "unknown"), ("dem", "İbrahim Akın", "unknown"),
                     ("dbp", "Keskin Bayındır", "unknown")}
    assert not db.execute("SELECT 1 FROM practice_contribution WHERE event_id=?", (yok,)).fetchall()
    joint_event = "0406-yesilsol-2020-event"
    assert tuple(db.execute("SELECT id,event_at FROM practice_event WHERE common_event_key=?", (joint_key,)).fetchone()) == (
        joint_event, "2020-05-18")
    assert db.execute("SELECT COUNT(*) FROM practice_event_alias WHERE decision_id=?", (joint_key,)).fetchone()[0] == 4
    assert not db.execute("SELECT id FROM practice_relation WHERE event_id=?", (joint_event,)).fetchall()
    joint_roles = {tuple(row) for row in db.execute(
        "SELECT c.party_id,c.contribution_kind,a.kind FROM practice_contribution AS c JOIN actor AS a ON a.id=c.actor_id "
        "WHERE c.event_id=?", (joint_event,),
    )}
    assert joint_roles == {(party, "support", "institution") for party in ("tip", "dbp", "emep")} | {
        ("dem", "unknown", "institution")}
    newspaper = {tuple(row) for row in db.execute(
        "SELECT DISTINCT d.party_id,v.sha256,p.pdf_page_index FROM practice_event_evidence AS e "
        "JOIN passage AS p ON p.id=e.passage_id JOIN document_version AS v ON v.id=p.version_id "
        "JOIN document AS d ON d.id=v.document_id JOIN source_attribution AS a ON a.version_id=v.id "
        "WHERE e.event_id=? AND a.publisher='BirGün'", (joint_event,),
    )}
    assert newspaper == {
        (party, "ff2a7d6312825665a6e74c54f5b1164045c0cc0324eef5237400bb9507085d22", 7)
        for party in ("tip", "dem", "dbp", "emep")
    }
    expanded_events = {}
    if expanded_keys:
        for key in sorted(expanded_keys):
            filled = db.execute(
                "SELECT id,event_at FROM practice_event WHERE common_event_key=?", (key,)
            ).fetchall()
            assert len(filled) == 1
            event_id, date = filled[0]
            assert date == {bakirkoy_key: "2019-12-08", idlib_key: "2020-03-05"}.get(key, "2022-11-28")
            count = db.execute(
                "SELECT COUNT(*) FROM practice_event_alias WHERE decision_id=? AND canonical_event_id=?",
                (key, event_id),
            ).fetchone()[0]
            assert count == 2
            actual_relations = {tuple(row) for row in db.execute(
                "SELECT id,party_id FROM practice_relation WHERE event_id=?", (event_id,)
            )}
            actual_roles = {tuple(row) for row in db.execute(
                "SELECT party_id,contribution_kind FROM practice_contribution WHERE event_id=?", (event_id,)
            )}
            if key == bakirkoy_key:
                assert actual_relations == {("0405-tip-bakirkoy-2019-relation", "tip")}
                assert actual_roles == {("tip", "support"), ("emep", "unknown")}
                by_source = db.execute(
                    "SELECT DISTINCT d.party_id,v.sha256,p.pdf_page_index FROM practice_event_evidence e "
                    "JOIN passage p ON p.id=e.passage_id JOIN document_version v ON v.id=p.version_id "
                    "JOIN document d ON d.id=v.document_id WHERE e.event_id=? AND p.pdf_page_index=99",
                    (event_id,),
                )
                assert {tuple(row) for row in by_source} == {
                    (party, "71d7365d5b82963fa8cf3de2c928cc2b032101f9135e3e192760d1ec1e24d00b", 99)
                    for party in ("tip", "emep")
                }
            elif key == idlib_key:
                assert actual_relations == {
                    ("0405-tip-2020-policy-idlib-relation", "tip"), ("0410-idlib-2020-relation", "emep"),
                }
                assert not actual_roles
                by_source = db.execute(
                    "SELECT d.party_id,v.sha256,p.pdf_page_index,p.exact FROM practice_event_evidence e "
                    "JOIN passage p ON p.id=e.passage_id JOIN document_version v ON v.id=p.version_id "
                    "JOIN document d ON d.id=v.document_id WHERE e.event_id=? AND e.stage='action'",
                    (event_id,),
                )
                assert {tuple(row) for row in by_source} == {
                    (party, "041fbaf925821e6ca8b9397167017e5bcd5dd3da695159daec66ed0ef9aac92d", 1, "Done in Moscow on 5 March, 2020")
                    for party in ("tip", "emep")
                }
            else:
                suffix = "presentation" if key == presentation_key else "meeting"
                assert actual_relations == {
                    (f"0411-saadet-nov-2022-{suffix}-relation", "saadet"),
                    (f"0412-six-leaders-2022-11-28-{suffix}-relation", "demokrat"),
                }
                assert actual_roles == {("demokrat", "task")}
            expanded_events[key] = {"event_id": event_id, "aliases": count}
        assert expanded_events[presentation_key]["event_id"] != expanded_events[meeting_key]["event_id"]
    for suffix, page in (("court-first-order", 30), ("court-october-order", 7), ("court-second-order", 35)):
        row = db.execute(
            "SELECT p.pdf_page_index FROM passage AS p JOIN manual_passage AS m ON m.passage_id=p.id WHERE p.id=?",
            (f"0405-tip-2020-2021-court-wage-election-{suffix}-p",),
        ).fetchone()
        assert tuple(row) == (page,), suffix

candidates = {row["id"]: row["state"] for row in records["practice_candidate"]}
for row in sorted(records["practice_candidate_revision"], key=lambda row: datetime.fromisoformat(row["recorded_at"])):
    candidates[row["candidate_id"]] = row["state"]
assert candidates["0406-tasimali-101783-candidate"] == candidates["0405-tip-election-finland-2023-nato-vote-candidate"] == "unmatched"
unmatched = sorted(key for key, state in candidates.items() if state == "unmatched")
assert len(unmatched) == receipt["active_unmatched"]
if number in {"19", "20"}:
    assert candidates["0410-bakirkoy-2019-emep-unmatched"] == "unmatched"
    if number == "19":
        assert len(unmatched) == 212
    else:
        local = {key for key in unmatched if key.startswith("0405-tip-2020-local-")}
        assert len(local) == 5
        assert len(unmatched) == frozen["active_unmatched"]
else:
    assert len(unmatched) == (211 if number == "18" else 209)
assert candidates["0406-halic-2022-candidate"] == candidates["0409-halic-2022-dbp-unmatched"] == "unmatched"
joint_candidates = {
    "0405-tip-2020-2021-court-wage-election-joint-unmatched", "0406-yesilsol-2020-candidate",
    "0409-joint-2020-dbp-unmatched", "0410-joint-2020-emep-unmatched",
}
assert joint_candidates <= set(unmatched)
html = (folder / "index.html").read_text()
for candidate in sorted(joint_candidates):
    for view in ("party", "comparison"):
        card = html.split(f'id="{view}-unmatched-{candidate}"', 1)[1].split("</article>", 1)[0]
        assert "18 Mayıs" in card and "BirGün" in card, (view, candidate)
for kind, identities in (("practice", relations), ("unmatched", unmatched)):
    for ident in identities:
        for view in ("party", "comparison"):
            anchor = f"{view}-{kind}-{ident}"
            assert html.count(f'id="{anchor}"') == 1 and f'href="#{anchor}"' in html, anchor
new_relations = {
    "0405-tip-2018-institution-member-relation": ("6 Ekim", "10 Ekim", "24 Haziran", "HDP"),
    "0405-tip-2018-institution-meeting-relation": ("21 Ekim", "26 Ekim", "4 Aralık", "Gazi Cemevi"),
    "0405-tip-2018-institution-elig-relation": ("2 Ocak", "13 parti", "TİP"),
} if number in {"17", "18", "19", "20"} else {}
if number in {"18", "19", "20"}:
    new_relations.update({
        "0405-tip-2019-local-eligibility-labor-damal-relation": ("Damal", "75 oy", "bağımsız"),
        "0405-tip-2019-local-eligibility-labor-elig21-relation": ("26 Ocak", "2021/22"),
        "0405-tip-2019-local-eligibility-labor-elig22-relation": ("12 Ocak", "YSK/13", "20. sırada"),
        "0405-tip-2019-campaign-wage-relation": ("3.000 TL", "2.324,70 TL", "27 Aralık"),
        "0405-tip-2019-campaign-budget-relation": ("20 Aralık", "21 Aralık", "31 Aralık", "329 kabul", "159 ret"),
        "0405-tip-2019-campaign-eyt-relation": ("30 Ocak", "1 Mart", "3 Mart", "yaş dışındaki şartları"),
        "0405-tip-2019-campaign-cyprus-relation": ("11–12 Ekim", "19 Kasım", "iki bölgeli", "Sol Hareket"),
    })
    for candidate, phrases in {
        "0405-tip-2019-local-eligibility-labor-ozsut-unmatched": ("Özsüt", "17 Temmuz"),
        "0406-3961-commission-candidate": ("27 Ekim", "2/3961", "Ceylan Akça Cupolo"),
    }.items():
        assert candidate in unmatched
        for view in ("party", "comparison"):
            card = html.split(f'id="{view}-unmatched-{candidate}"', 1)[1].split("</article>", 1)[0]
            assert all(phrase in card for phrase in phrases), (view, candidate)
    events = {row["id"]: row for row in records["practice_event"]}
    commission = events["0406-3961-commission-event"]
    assert commission["event_at"] == "2026-10-27"
    assert commission["id"] not in relations.values()
    vote = events["0406-2026-3961-vote"]
    assert vote["event_at"] == "2026-11-05" and "2/3961" in vote["scope_context"]
if number in {"19", "20"}:
    new_relations.update({
        "0405-tip-bakirkoy-2019-relation": ("8 Aralık", "Bakırköy", "Halk Pazarı"),
        "0411-saadet-nov-2022-presentation-relation": ("14 Kasım", "28 Kasım", "Bilkent"),
        "0411-saadet-nov-2022-meeting-relation": ("14 Kasım", "28 Kasım", "Demokrat Parti"),
        "0412-six-leaders-2022-11-28-presentation-relation": ("14 Kasım", "28 Kasım", "Bilkent"),
        "0412-six-leaders-2022-11-28-meeting-relation": ("14 Kasım", "28 Kasım", "Demokrat Parti"),
    })
if number == "20":
    new_relations.update({
        "0405-tip-2020-policy-idlib-relation": ("3 Şubat", "5 Mart", "S/2020/187"),
        "0410-idlib-2020-relation": ("28 Şubat", "5 Mart", "15 Mart"),
    })
assert set(new_relations) <= set(relations)
for relation, phrases in {
    "0405-tip-halic-cemevi-2022-halic-relation": ("25 Ağustos", "24 Eylül", "25 Eylül", "Erkan Baş"),
    "0410-halic-2022-relation": ("14 Eylül", "24 Eylül", "Ercüment Akdeniz"),
    "0405-tip-earthquake-2023-education-relation": ("14 Şubat", "30 Mart", "3 Nisan"),
    "0411-saadet-education-2023-relation": ("22 Şubat", "30 Mart", "3 Nisan"),
    "0406-van-2024-relation": ("2 Nisan", "3 Nisan", "2024/25", "Abdullah Zeydan"),
    "0405-tip-amasra-saopaulo-2022-mine-relation": ("14 Ekim", "19 Ekim", "22 Ekim", "1344"),
    "0405-tip-amasra-saopaulo-2022-ship-relation": ("28 Temmuz", "26 Ağustos", "29 Eylül"),
    "0405-tip-school-montro-paris-school-relation": ("10 Ağustos", "19 Ağustos", "6 Eylül"),
    "0405-tip-school-montro-paris-montro-relation": ("24 Şubat", "2 Mart", "19. madde"),
    "0405-tip-school-montro-paris-paris-relation": ("6 Ekim", "11 Ekim", "10 Kasım"),
    "0405-tip-2020-2021-court-wage-election-court-relation": ("14 Ekim", "21 Ocak", "11 Şubat"),
    "0405-tip-2020-2021-court-wage-election-wage-relation": ("9 Aralık", "28 Aralık", "2.825,90"),
    "0405-tip-2020-2021-court-wage-election-election-relation": ("21 Haziran", "23 Haziran", "4.742.082"),
    "0411-saadet-election-2023-relation": ("18 Ocak", "10 Mart", "14 Mayıs"),
    **new_relations,
}.items():
    for view in ("party", "comparison"):
        card = html.split(f'id="{view}-practice-{relation}"', 1)[1].split("</article>", 1)[0]
        assert all(phrase in card for phrase in phrases), (view, relation)

receipt.update(independently_verified=True, terminal_validation_exit="0:0",
               reference_counts={table: len(records[table]) for table in compare},
               matched_reader_links=2 * len(relations), unmatched_reader_links=2 * len(unmatched),
               verified_assets=len(manifest["asset_files"]),
               source_review_origins=origins, frozen_output_sha256=frozen["output_sha256"],
               shared_events=dict(previous["shared_events"], **{halic_key: {"event_id": halic, "aliases": 4},
                   yok_key: {"event_id": yok, "aliases": 2},
                   joint_key: {"event_id": joint_event, "aliases": 4}}, **expanded_events),
               joint_statement_candidates=sorted(joint_candidates), joint_statement_roles=sorted(joint_roles),
               halic_contributions=sorted(roles, key=lambda row: (row[0], row[1] or "", row[2])),
               audited_new_relations=[*expected_relations, *new_relations],
               verified_separate_akbelen_events=[relations["0407-akbelen-2023-relation"], relations["0410-akbelen-meeting-relation"]])
with (checks / f"wave4-merge-rehearsal-{number}-{job}-independent.json").open("x") as stream:
    stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
print(f"REHEARSAL_{number}_INDEPENDENT_OK", receipt["events"], receipt["relations"], len(unmatched), origins, flush=True)
