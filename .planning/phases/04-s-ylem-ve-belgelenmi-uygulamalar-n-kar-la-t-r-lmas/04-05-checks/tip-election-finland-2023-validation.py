"""Verify the TİP election and Finland records in both reader views."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "practice_validation", checks.parent / "04-04-checks" / "samsun-reply-validation.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / "practices" / "sources" / "tip"
case = "tip-election-finland-2023"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [33, 31, 0]
receipt = harness.main(package, review, case, f"{stem}-election-event", f"{stem}-election-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, names in {
        "practice_event": ("election-event", "nato-event", "nato-vote-event"),
        "practice_relation": ("election-relation", "nato-relation"),
        "practice_candidate": ("election-candidate", "nato-candidate", "nato-vote-candidate"),
    }.items():
        for name in names:
            ident = f"{stem}-{name}"
            row = next(data for data in records[table] if data["id"] == ident)
            actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (ident,)).fetchone()
            assert dict(actual) == row and row in export[table], (table, ident)
    pages = {"election-total": (3, "MM/24"), "election-seats": (4, "MM/25")}
    for name, expected in pages.items():
        selected = db.execute(
            "SELECT p.pdf_page_index,p.printed_page FROM passage p JOIN manual_passage m ON p.id=m.passage_id WHERE p.id=?",
            (f"{stem}-{name}-p",)).fetchone()
        assert tuple(selected) == expected, name
for view in ("party", "comparison"):
    markers = {
        f"{view}-practice-{stem}-election-relation": ("956.057", "1,75", "1,76", "dört sandalye"),
        f"{view}-practice-{stem}-nato-relation": ("4 Nisan", "30 Mart", "2/5005", "7448"),
        f"{view}-unmatched-{stem}-nato-vote-candidate": ("30 Mart", "öncesi"),
    }
    for anchor, phrases in markers.items():
        marker = f'id="{anchor}"'
        assert report.count(marker) == 1 and f'href="#{anchor}"' in report
        card = report.split(marker, 1)[1].split("</article>", 1)[0]
        assert all(phrase in card for phrase in phrases), (view, anchor)
print("TIP_ELECTION_FINLAND_2023_BOTH_VIEWS_OK", folder, flush=True)
