"""Confirm the Amasra and São Paulo source stages in both reader views."""

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
case = "tip-amasra-saopaulo-2022"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [39, 37, 0]
receipt = harness.main(package, review, case, f"{stem}-mine-event", f"{stem}-mine-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
markers = {
    f"{stem}-mine-relation": ("14 Ekim", "19 Ekim", "22 Ekim", "1344", "yargı"),
    f"{stem}-ship-relation": ("28 Temmuz", "26 Ağustos", "29 Eylül", "şartlı"),
}
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ("practice_event", "practice_relation", "practice_candidate", "practice_statement"):
        for row in records[table]:
            if row["id"].startswith(stem):
                actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(actual), row["id"]
    for suffix, page_index, stage in (
        ("mine-approved", 44, "action"), ("mine-published", 46, "result"),
        ("ship-init", 2, "initiative"), ("ship-cancel", 2, "result"),
    ):
        actual = db.execute("SELECT p.pdf_page_index, e.stage FROM practice_event_evidence AS e "
                            "JOIN passage AS p ON p.id=e.passage_id WHERE e.passage_id=?",
                            (f"{stem}-{suffix}-p",)).fetchone()
        assert tuple(actual) == (page_index, stage), suffix
for anchor, phrases in markers.items():
    for view in ("party", "comparison"):
        marker = f'id="{view}-practice-{anchor}"'
        assert report.count(marker) == 1 and f'href="#{view}-practice-{anchor}"' in report
        block = report.split(marker, 1)[1].split("</article>", 1)[0]
        assert all(phrase in block for phrase in phrases), (view, anchor, phrases)
print("TIP_AMASRA_SAOPAULO_2022_BOTH_VIEWS_OK", folder, flush=True)
