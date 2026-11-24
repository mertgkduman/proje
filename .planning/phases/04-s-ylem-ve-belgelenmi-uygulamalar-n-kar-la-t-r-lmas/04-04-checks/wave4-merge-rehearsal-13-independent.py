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
log = checks / f"wave4-merge-rehearsal-13-{job}-slurm.log"
frozen = json.loads((checks / "wave4-merge-rehearsal-13.json").read_bytes())
previous = json.loads((checks / "wave4-merge-rehearsal-12-62615150-independent.json").read_bytes())
line, = (line for line in log.read_text().splitlines() if line.startswith(prefix))
receipt = json.loads(line.removeprefix(prefix))
assert receipt["job"] == receipt["validation_job"] == job and receipt["rehearsal"] == "13"
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
assert receipt["source_permissions"] == previous["source_permissions"]
assert receipt["shared_keys"] == previous["shared_keys"]

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

candidates = {row["id"]: row["state"] for row in records["practice_candidate"]}
for row in sorted(records["practice_candidate_revision"], key=lambda row: datetime.fromisoformat(row["recorded_at"])):
    candidates[row["candidate_id"]] = row["state"]
assert candidates["0406-tasimali-101783-candidate"] == candidates["0405-tip-election-finland-2023-nato-vote-candidate"] == "unmatched"
unmatched = sorted(key for key, state in candidates.items() if state == "unmatched")
assert len(unmatched) == receipt["active_unmatched"]
html = (folder / "index.html").read_text()
for kind, identities in (("practice", relations), ("unmatched", unmatched)):
    for ident in identities:
        for view in ("party", "comparison"):
            anchor = f"{view}-{kind}-{ident}"
            assert html.count(f'id="{anchor}"') == 1 and f'href="#{anchor}"' in html, anchor
receipt.update(independently_verified=True, terminal_validation_exit="0:0",
               reference_counts={table: len(records[table]) for table in compare},
               matched_reader_links=2 * len(relations), unmatched_reader_links=2 * len(unmatched),
               source_review_origins=origins, frozen_output_sha256=frozen["output_sha256"],
               shared_events=previous["shared_events"], audited_new_relations=list(expected_relations),
               verified_separate_akbelen_events=[relations["0407-akbelen-2023-relation"], relations["0410-akbelen-meeting-relation"]])
with (checks / f"wave4-merge-rehearsal-13-{job}-independent.json").open("x") as stream:
    stream.write(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
print("REHEARSAL_13_INDEPENDENT_OK", receipt["events"], receipt["relations"], len(unmatched), origins, flush=True)
