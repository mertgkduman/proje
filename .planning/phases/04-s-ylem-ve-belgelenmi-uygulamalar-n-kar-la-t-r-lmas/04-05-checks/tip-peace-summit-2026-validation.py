"""Verify the dates and evidence for the Istanbul peace summit in both views."""

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
harness.SOURCE = harness.DATA / "practices" / "sources" / "tip"

case = "tip-peace-summit-2026"
prefix = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [25, 24, 0]
receipt = harness.main(package, review, case, f"{prefix}-event", f"{prefix}-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())

with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, suffix in (
        ("practice_statement", "statement"), ("practice_event", "event"),
        ("practice_relation", "relation"), ("practice_candidate", "candidate"),
    ):
        identity = f"{prefix}-{suffix}"
        expected = next(row for row in records[table] if row["id"] == identity)
        actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (identity,)).fetchone()
        assert dict(actual) == expected and expected in export[table], identity

    dates = {
        "announcement": ("2026-05-15", "day"),
        "organizer": ("2026-07-05", "day"),
        "attendee": (None, "unknown"),
        "declaration": ("2026-07-25", "day"),
        "nato": ("2026-07-08", "day"),
    }
    for name, expected in dates.items():
        row = db.execute("SELECT document_date,date_precision FROM document_version WHERE id=?",
                         (f"{prefix}-{name}-v1",)).fetchone()
        assert tuple(row) == expected, name

    result_refs = db.execute(
        "SELECT passage_id FROM practice_event_evidence WHERE event_id=? AND stage='result'",
        (f"{prefix}-event",)).fetchall()
    assert [row[0] for row in result_refs] == [f"{prefix}-attendee-p"]

report = (folder / "index.html").read_text()
for view in ("party", "comparison"):
    anchor = f"{view}-practice-{prefix}-relation"
    marker = f'id="{anchor}"'
    assert report.count(marker) == 1 and f'href="#{anchor}"' in report
    card = report.split(marker, 1)[1].split("</article>", 1)[0]
    for phrase in ("15 Mayıs", "4 Temmuz", "7 Temmuz", "25 Temmuz", "Ankara NATO zirvesi",
                   "politika hedeflerinin uygulanması açık"):
        assert phrase in card, (view, phrase)
print("TIP_PEACE_SUMMIT_2026_BOTH_VIEWS_OK", folder, flush=True)
