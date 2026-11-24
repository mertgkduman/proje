"""Verify the distinct 2023 candidacy and vote result records."""

from html import escape
import importlib.util
import json
from pathlib import Path
import sqlite3

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "practice_validation", checks.parent / "04-04-checks" / "samsun-reply-validation.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / "practices" / "sources" / "demokrat"
case = "election-2023"
stem = "0412-election-2023"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert harness.sha(package) == "8d713724de98c6184da3b82c5e3c93a5df624a43dbdce7c74d0220e055043bc7"
assert harness.sha(review) == "21c9887190fe1f515caff264f9058b522e9af63d9f5fc342f2caa0ceaed06ef2"
records = json.loads(package.read_bytes())["practice_records"]
assert (len(records["practice_event"]), len(records["practice_relation"]),
        len(records["practice_closure"])) == (52, 43, 0)
receipt = harness.main(package, review, case, stem + "-application-event", stem + "-application-relation",
                       None, expected_party="demokrat", namespace="gsd-0412")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
report = (folder / "index.html").read_text()
events = {"application": "2023-03-24", "definitive": "2023-03-30", "runoff": "2023-05-28"}
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ("practice_statement", (stem + "-statement",)),
        ("practice_event", tuple(stem + "-" + k + "-event" for k in events)),
        ("practice_relation", tuple(stem + "-" + k + "-relation" for k in events)),
        ("practice_candidate", tuple(stem + "-" + k + "-candidate" for k in events)),
    ):
        for identity in identities:
            row = next(item for item in records[table] if item["id"] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f"SELECT * FROM {table} WHERE id=?", (identity,)).fetchone())
    for label, day in events.items():
        assert db.execute("SELECT event_at FROM practice_event WHERE id=?",
                          (stem + "-" + label + "-event",)).fetchone()[0] == day
    assert db.execute("SELECT document_date FROM document_version WHERE id=?",
                      (stem + "-definitive-v1",)).fetchone()[0] == "2023-03-31"
    assert db.execute("SELECT count(*) FROM manual_passage WHERE passage_id LIKE ?",
                      (stem + "-%",)).fetchone()[0] == 2
    assert 27_834_589 + 25_504_724 == 53_339_313
for view in ("party", "comparison"):
    for label, phrases in (
        ("application", ("24 Mart", "CHP", "İYİ Parti", "2023/254")),
        ("definitive", ("30 Mart", "31 Mart", "dört aday")),
        ("runoff", ("28 Mayıs", "52,18", "47,82", "25.504.724")),
    ):
        anchor = f"{view}-practice-{stem}-{label}-relation"
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split("</article>", 1)[0].casefold()
        for phrase in phrases:
            assert escape(phrase).casefold() in card, (view, label, phrase)
print("DEMOCRAT_ELECTION_2023_BOTH_VIEWS_OK", folder, flush=True)
