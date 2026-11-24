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
prefix = "UNION_REHEARSAL_PREVIEW_OK "
log = checks / f"wave4-merge-rehearsal-15-{job}-slurm.log"
frozen = json.loads((checks / "wave4-merge-rehearsal-15.json").read_bytes())
previous = json.loads((checks / "wave4-merge-rehearsal-12-62615150-independent.json").read_bytes())
line, = (line for line in log.read_text().splitlines() if line.startswith(prefix))
receipt = json.loads(line.removeprefix(prefix))
assert receipt["job"] == receipt["validation_job"] == job and receipt["rehearsal"] == "15"
folder = Path(receipt["preview"])


def digest(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


assert digest(folder / "manifest.json") == receipt["manifest_sha256"]
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
assert all(digest(folder / name) == identity for name, identity in manifest["files"].items())
assert digest(Path("data/current.json")) == receipt["canonical_pointer_sha256"] == frozen["canonical_pointer_sha256"]
records = json.loads((folder / "records.json").read_bytes())
assert {name: len(records[name]) for name in frozen["counts"]} == frozen["counts"]
assert len(records["practice_event_alias"]) == frozen["aliases"]
assert Counter(row["decision"] for row in records["practice_event_decision"]) == Counter(
    same=frozen["same_candidates"], unresolved=frozen["unresolved_candidates"])
origins = sum(row["origin_kind"] == "review_origins" for row in records["practice_merge_origin"])
assert origins == frozen["review_origins"]
assert receipt["source_permissions"] == 616
assert frozen["expanded_reviewed_candidates"] == ["halic-emek-ozgurluk-2022-09-24"]
halic_key = "halic-emek-ozgurluk-2022-09-24"
yok_key = "yok-2023-03-30-bahar-yuzyuze-secenegi"
assert set(receipt["shared_keys"]) == set(previous["shared_keys"]) | {halic_key, yok_key}

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
)
assert set(expected_relations) <= relations.keys()
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

candidates = {row["id"]: row["state"] for row in records["practice_candidate"]}
for row in sorted(records["practice_candidate_revision"], key=lambda row: datetime.fromisoformat(row["recorded_at"])):
    candidates[row["candidate_id"]] = row["state"]
assert candidates["0406-tasimali-101783-candidate"] == candidates["0405-tip-election-finland-2023-nato-vote-candidate"] == "unmatched"
unmatched = sorted(key for key, state in candidates.items() if state == "unmatched")
assert len(unmatched) == receipt["active_unmatched"] == 205
assert candidates["0406-halic-2022-candidate"] == candidates["0409-halic-2022-dbp-unmatched"] == "unmatched"
html = (folder / "index.html").read_text()
for kind, identities in (("practice", relations), ("unmatched", unmatched)):
    for ident in identities:
        for view in ("party", "comparison"):
            anchor = f"{view}-{kind}-{ident}"
            assert html.count(f'id="{anchor}"') == 1 and f'href="#{anchor}"' in html, anchor
for relation, phrases in {
    "0405-tip-halic-cemevi-2022-halic-relation": ("25 Ağustos", "24 Eylül", "25 Eylül", "Erkan Baş"),
    "0410-halic-2022-relation": ("14 Eylül", "24 Eylül", "Ercüment Akdeniz"),
    "0405-tip-earthquake-2023-education-relation": ("14 Şubat", "30 Mart", "3 Nisan"),
    "0411-saadet-education-2023-relation": ("22 Şubat", "30 Mart", "3 Nisan"),
    "0406-van-2024-relation": ("2 Nisan", "3 Nisan", "2024/25", "Abdullah Zeydan"),
    "0405-tip-amasra-saopaulo-2022-mine-relation": ("14 Ekim", "19 Ekim", "22 Ekim", "1344"),
    "0405-tip-amasra-saopaulo-2022-ship-relation": ("28 Temmuz", "26 Ağustos", "29 Eylül"),
}.items():
    for view in ("party", "comparison"):
        card = html.split(f'id="{view}-practice-{relation}"', 1)[1].split("</article>", 1)[0]
        assert all(phrase in card for phrase in phrases), (view, relation)

receipt.update(independently_verified=True, terminal_validation_exit="0:0",
               reference_counts={table: len(records[table]) for table in compare},
               matched_reader_links=2 * len(relations), unmatched_reader_links=2 * len(unmatched),
               source_review_origins=origins, frozen_output_sha256=frozen["output_sha256"],
               shared_events=dict(previous["shared_events"], **{halic_key: {"event_id": halic, "aliases": 4},
                   yok_key: {"event_id": yok, "aliases": 2}}),
               halic_contributions=sorted(roles, key=lambda row: (row[0], row[1] or "", row[2])),
               audited_new_relations=list(expected_relations),
               verified_separate_akbelen_events=[relations["0407-akbelen-2023-relation"], relations["0410-akbelen-meeting-relation"]])
with (checks / f"wave4-merge-rehearsal-15-{job}-independent.json").open("x") as stream:
    stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
print("REHEARSAL_15_INDEPENDENT_OK", receipt["events"], receipt["relations"], len(unmatched), origins, flush=True)
