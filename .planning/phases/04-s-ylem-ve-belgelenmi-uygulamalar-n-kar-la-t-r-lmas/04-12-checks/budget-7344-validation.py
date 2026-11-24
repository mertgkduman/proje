"""Check the 7344 candidate in both HTML views and its two data exports."""

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
case = "budget-7344"
base = f"0412-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event","practice_relation","practice_closure")] == [62,48,0]
receipt = harness.main(package, review, case, f"{base}-adoption-event", f"{base}-adoption-relation",
                       None, expected_party="demokrat", namespace="gsd-0412")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, suffixes in (
        ("practice_statement", ("statement",)),
        ("practice_event", ("filing-event", "adoption-event")),
        ("practice_candidate", ("filing-candidate", "adoption-candidate")),
        ("practice_relation", ("adoption-relation",)),
    ):
        for suffix in suffixes:
            ident = f"{base}-{suffix}"
            expected = next(row for row in records[table] if row["id"] == ident)
            actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (ident,)).fetchone()
            assert expected in export[table] and expected == dict(actual), ident
    found = dict(db.execute("SELECT passage_id, supported_point FROM practice_event_evidence WHERE event_id=?",
                            (f"{base}-adoption-event",)))
    for suffix, phrases in (
        ("chair-votes", ("327 kabul", "197 ret")),
        ("roll-uysal", ("22.50", "320 kabul", "195 ret", "9 mükerrer", "Gültekin Uysal (DP) Ret")),
        ("roll-enginyurt", ("Cemal Enginyurt (DP) Ret",)),
        ("publication", ("31 Aralık 2021", "31706")),
        ("effective", ("1 Ocak 2022",)),
    ):
        assert all(phrase in found[f"{base}-{suffix}-p"] for phrase in phrases), suffix
report = (folder / "index.html").read_text()
for view in ("party", "comparison"):
    for anchor, phrases in (
        (f"{view}-practice-{base}-adoption-relation", ("7344", "Gültekin Uysal ve Cemal Enginyurt", "320 kabul", "1 Ocak 2022")),
        (f"{view}-unmatched-{base}-filing-candidate", ("1/283", "15 Ekim 2021")),
    ):
        marker = f'id="{anchor}"'
        assert report.count(marker) == 1 and f'href="#{anchor}"' in report
        card = report.split(marker, 1)[1].split("</article>",1)[0]
        assert all(phrase in card for phrase in phrases), (view, anchor)
print("DEMOCRAT_BUDGET_7344_BOTH_VIEWS_OK", folder, flush=True)
