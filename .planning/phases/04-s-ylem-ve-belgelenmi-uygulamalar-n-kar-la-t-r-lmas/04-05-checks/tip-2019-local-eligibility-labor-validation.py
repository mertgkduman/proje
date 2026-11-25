"""Verify the Damal, election qualification and Özsüt records in both reader views."""

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "practice_validation", checks.parent / "04-04-checks" / "samsun-reply-validation.py"
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / "practices" / "sources" / "tip"
case = "tip-2019-local-eligibility-labor"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [53, 49, 0]
receipt = harness.main(
    package, review, case, f"{stem}-damal-event", f"{stem}-damal-relation",
    None, expected_party="tip", namespace="gsd-0405",
)
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ("practice_event", "practice_relation", "practice_candidate", "practice_statement", "practice_contribution"):
        for row in records[table]:
            if row["id"].startswith(stem):
                actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(actual), row["id"]
    expected_stages = {
        "damal-ysk": "action", "damal-returns": "result", "elig21-yskat": "action",
        "elig21-list": "result", "elig22-yskat": "action", "elig22-list": "result",
        "ozsut-press": "action", "ozsut-promise": "initiative", "ozsut-partial": "result",
    }
    for passage, expected in expected_stages.items():
        row = db.execute("SELECT stage FROM practice_event_evidence WHERE passage_id=?", (f"{stem}-{passage}-p",)).fetchone()
        assert tuple(row) == (expected,), passage
    assert db.execute("SELECT state FROM practice_candidate WHERE id=?", (f"{stem}-ozsut-unmatched",)).fetchone()[0] == "unmatched"
    assert db.execute("SELECT contribution_kind FROM practice_contribution WHERE id=?", (f"{stem}-ozsut-support",)).fetchone()[0] == "support"

markers = {
    f"practice-{stem}-damal-relation": ("Şubat", "31 Mart", "75 oy", "bağımsız"),
    f"practice-{stem}-elig21-relation": ("30 Haziran", "26 Ocak", "17 parti", "TİP listede yok"),
    f"practice-{stem}-elig22-relation": ("14–15 Eylül", "Ekim 2019", "12 Ocak 2022", "24 parti", "20. sıra"),
    f"unmatched-{stem}-ozsut-unmatched": ("Özsüt", "17 Temmuz", "kısmi ödeme", "Ağustos"),
}
for anchor, phrases in markers.items():
    for view in ("party", "comparison"):
        marker = f'id="{view}-{anchor}"'
        assert report.count(marker) == 1 and f'href="#{view}-{anchor}"' in report
        block = report.split(marker, 1)[1].split("</article>", 1)[0]
        assert all(phrase in block for phrase in phrases), (view, anchor, phrases)
print("TIP_2019_LOCAL_ELIGIBILITY_LABOR_BOTH_VIEWS_OK", folder, flush=True)
