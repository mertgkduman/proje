"""Confirm TİP's Bakırköy source attributions in both preview views."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "practice_validation", checks.parent / "04-04-checks" / "samsun-reply-validation.py"
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / "practices" / "sources" / "tip"
case = "tip-bakirkoy-2019"
ident = f"0405-{case}"
package, review = [checks / f"{case}{suffix}-draft.json" for suffix in ("", "-review")]
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [58, 54, 0]
receipt = harness.main(package, review, case, f"{ident}-event", f"{ident}-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ("practice_event", "practice_relation", "practice_candidate", "practice_contribution"):
        row, = (row for row in records[table] if row["id"].startswith(ident))
        assert row == dict(db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone())
        assert row in export[table]
    assert {tuple(row) for row in db.execute(
        "SELECT v.sha256, p.pdf_page_index FROM practice_event_evidence AS e "
        "JOIN passage AS p ON p.id=e.passage_id JOIN document_version AS v ON v.id=p.version_id WHERE e.event_id=?",
        (f"{ident}-event",))} == {("71d7365d5b82963fa8cf3de2c928cc2b032101f9135e3e192760d1ec1e24d00b", 99)}
report = (folder / "index.html").read_text()
for view in ("party", "comparison"):
    anchor = f"{view}-practice-{ident}-relation"
    marker = f'id="{anchor}"'
    assert report.count(marker) == 1 and f'href="#{anchor}"' in report
    block = report.split(marker, 1)[1].split("</article>", 1)[0]
    assert all(word in block for word in ("8 Aralık", "Bakırköy Halk Pazarı", "katılım", "Ocak 2020", "Oda raporu")), view
print("TIP_BAKIRKOY_BOTH_VIEWS_OK", folder, flush=True)
