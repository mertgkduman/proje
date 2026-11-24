"""Verify dated pension laws and the separate SGK payment record."""

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
case = "pension-5000"
stem = "0412-pension-5000"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert harness.sha(package) == "824f4e233da39555a29618317a79274e49eef97f5b6165767c5787c36814b66d"
assert harness.sha(review) == "f855b0e9d1c45d01796f5301b637fd60b55f0c0d0ff2ed99547c68932672c13b"
records = json.loads(package.read_bytes())["practice_records"]
assert (len(records["practice_event"]), len(records["practice_relation"]),
        len(records["practice_closure"])) == (49, 40, 0)
receipt = harness.main(package, review, case, stem + "-eligibility-event", stem + "-eligibility-relation",
                       None, expected_party="demokrat", namespace="gsd-0412")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
report = (folder / "index.html").read_text()
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ("practice_statement", (stem + "-statement",)),
        ("practice_event", tuple(stem + "-" + k + "-event" for k in ("initial", "eligibility", "payment"))),
        ("practice_relation", tuple(stem + "-" + k + "-relation" for k in ("eligibility", "payment"))),
        ("practice_candidate", tuple(stem + "-" + k + "-candidate" for k in ("initial", "eligibility", "payment"))),
    ):
        for identity in identities:
            row = next(item for item in records[table] if item["id"] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f"SELECT * FROM {table} WHERE id=?", (identity,)).fetchone())
    assert tuple(db.execute("SELECT state,relation_id FROM practice_candidate WHERE id=?",
                           (stem + "-initial-candidate",)).fetchone()) == ("unmatched", None)
    for tag, date in (("initial", "2023-11-02"), ("eligibility", "2023-12-28"), ("payment", None)):
        query = "SELECT event_at,date_precision FROM practice_event WHERE id=?"
        assert tuple(db.execute(query, (stem + "-" + tag + "-event",)).fetchone()) == (
            date, "day" if date else "unknown")

for view in ("party", "comparison"):
    for key, phrases in (
        (f"unmatched-{stem}-initial-candidate", ("7464", "5.000 TL", "2 Kasım")),
        (f"practice-{stem}-eligibility-relation", ("7491", "54. madde", "28 Aralık")),
        (f"practice-{stem}-payment-relation", ("23,4 milyar TL", "4.688.945", "Ocak 2024")),
    ):
        anchor = f"{view}-{key}"
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split("</article>", 1)[0].casefold()
        for phrase in phrases:
            assert escape(phrase).casefold() in card, (view, key, phrase)
print("DEMOCRAT_PENSION_5000_BOTH_VIEWS_OK", folder, flush=True)
