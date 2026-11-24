"""Verify the TBMM question in both partial practice views."""

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "practice_validation", checks.parent / "04-04-checks" / "samsun-reply-validation.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / "practices" / "sources" / "demokrat"
with_bulletins = sys.argv[3:] == ["--with-bulletins"]
assert with_bulletins or not sys.argv[3:]
case = "question-13274-bulletins" if with_bulletins else "question-13274"
stem = "0412-question-13274"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:3]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [79, 50, 0]
receipt = harness.main(package, review, case, "0412-law-7253-adoption-event", "0412-law-7253-adoption-relation",
                       None, expected_party="demokrat", namespace="gsd-0412")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
report = (folder / "index.html").read_text()
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, suffix in (("practice_event", "event"), ("practice_candidate", "candidate")):
        ident = f"{stem}-{suffix}"
        expected = next(row for row in records[table] if row["id"] == ident)
        actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (ident,)).fetchone()
        assert expected in export[table] and expected == dict(actual), ident
    count = db.execute("SELECT count(*) FROM manual_passage WHERE passage_id LIKE ?", (stem + "%",)).fetchone()[0]
    assert count == 4
    event_id = f"{stem}-event"
    evidence = [row for row in export["practice_event_evidence"] if row["event_id"] == event_id]
    assert len(evidence) == (12 if with_bulletins else 7)
    assert all(row["event_id"] != event_id for row in export["practice_relation"])
    party_version = next(row for row in export["source_attribution"] if row["version_id"] == f"{stem}-party-v1")
    assert (party_version["kind"], party_version["author"], party_version["published_at"]) == (
        "party_publication", "DP Basın Merkezi", "2024-06-28")
    if with_bulletins:
        assert {row["passage_id"]: row["stage"] for row in evidence if row["passage_id"].endswith("-line-p")} == {
            f"{stem}-registered-line-p": "action", f"{stem}-overdue-line-p": "result",
        }
    for prefix in ("party", "comparison"):
        anchor = f"{prefix}-unmatched-{stem}-candidate"
        marker = f'id="{anchor}"'
        assert report.count(marker) == 1 and f'href="#{anchor}"' in report
        card = report.split(marker, 1)[1].split("</article>", 1)[0]
        pieces = ("7/13274", "25 Haziran 2024", "cevaplanmadığının", "27 Haziran")
        if with_bulletins:
            pieces += ("4 Temmuz 2024", "19 Temmuz 2024", "süresinde cevaplanmayan soru olarak ilan edildi")
        assert all(piece in card for piece in pieces), prefix
marker = "DEMOCRAT_QUESTION_13274_BULLETINS_BOTH_VIEWS_OK" if with_bulletins else "DEMOCRAT_QUESTION_13274_BOTH_VIEWS_OK"
print(marker, folder, flush=True)
