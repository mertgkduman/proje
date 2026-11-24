"""Verify four historical audit cards and their data exports."""

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
case = "party-financial-audits"
base = f"0412-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [73,50,0]
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
        (2011,("300 TL", "Hazineye irat", "24.950.172,00 TL")),
        (2012,("2.904,36 TL", "Üç karşıoy", "5.853.864,60 TL")),
        (2013,("3.179.378,16 TL", "5.700.224,17 TL", "oybirliğiyle")),
        (2017,("6.229.333,19 TL", "2.438.709,12 TL", "oybirliğiyle")),
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
print("DEMOCRAT_PARTY_FINANCIAL_AUDITS_BOTH_VIEWS_OK", folder, flush=True)
