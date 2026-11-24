"""Verify the 2018 and 2019 audit records in both reader views."""

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
case = "party-audit-followup"
base = f"0412-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [75,50,0]
receipt = harness.main(package, review, case, "0412-law-7253-adoption-event", "0412-law-7253-adoption-relation",
                       None, expected_party="demokrat", namespace="gsd-0412")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
report = (folder / "index.html").read_text()
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for year, phrases in (
        (2018,("6.641.061,27 TL", "6.640.527,90 TL", "1.704,82 TL")),
        (2019,("7.017.267,12 TL", "7.018.363,30 TL", "608,64 TL")),
    ):
        ident = f"{base}-{year}"
        for table, suffix in (("practice_event", "event"),("practice_candidate", "candidate")):
            key = f"{ident}-{suffix}"
            expected = next(row for row in records[table] if row["id"] == key)
            actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (key,)).fetchone()
            assert expected in export[table] and expected == dict(actual), key
        for view in ("party","comparison"):
            anchor = f"{view}-unmatched-{ident}-candidate"
            marker = f'id="{anchor}"'
            assert report.count(marker)==1 and f'href="#{anchor}"' in report
            card = report.split(marker,1)[1].split("</article>",1)[0]
            assert all(phrase in card for phrase in phrases), (view, year)
print("DEMOCRAT_PARTY_AUDIT_FOLLOWUP_BOTH_VIEWS_OK", folder, flush=True)
