"""Verify the October EngelliWeb comparison and its evidence limits."""

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
case = "tip-x-20261014"
prefix = f"0405-{case}"
package_path = checks / f"{case}-draft.json"
review_path = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package_path, review_path)] == sys.argv[1:]
records = json.loads(package_path.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [24,23,0]
receipt = harness.main(package_path, review_path, case, f"{prefix}-event", f"{prefix}-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
with sqlite3.connect((folder / "records.sqlite3").as_uri()+"?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, suffix in (
        ("practice_statement", "statement"), ("practice_event", "event"),
        ("practice_relation", "relation"), ("practice_candidate", "candidate"),
    ):
        identity = f"{prefix}-{suffix}"
        expected = next(row for row in records[table] if row["id"] == identity)
        actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (identity,)).fetchone()
        assert dict(actual) == expected and expected in export[table], identity
    outcome = db.execute("SELECT result_finding_id FROM practice_relation WHERE id=?", (f"{prefix}-relation",)).fetchone()
    assert tuple(outcome) == (None,)
    sources = db.execute(
        "SELECT a.publisher,d.source_kind FROM document_version v JOIN document d ON d.id=v.document_id "
        "JOIN source_attribution a ON a.version_id=v.id WHERE v.id IN (?,?)",
        (f"{prefix}-party-v1",f"{prefix}-observation-v1"))
    assert {tuple(row) for row in sources} == {
        ("Türkiye İşçi Partisi","party"), ("İfade Özgürlüğü Derneği","independent_report")}
report = (folder / "index.html").read_text()
for view in ("party", "comparison"):
    anchor = f"{view}-practice-{prefix}-relation"
    marker = f'id="{anchor}"'
    assert report.count(marker) == 1 and f'href="#{anchor}"' in report
    card = report.split(marker,1)[1].split("</article>",1)[0]
    for phrase in ("@tipgenelmerkez", "8/A", "Türkiye’den gizlemediğini", "İstanbul İl Başkanlığı", "sonraki teknik uygulama açık"):
        assert phrase in card, (view, phrase)
print("TIP_X_20261014_BOTH_VIEWS_OK", folder, flush=True)
