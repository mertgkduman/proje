"""Verify the Yassıada comparison and its scope limits in both reader views."""

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
harness.SOURCE = harness.DATA / "practices" / "sources" / "demokrat"
case = "yassiada-2022-dp"
stem = f"0412-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [81, 52, 0]
receipt = harness.main(package, review, case, f"{stem}-event", f"{stem}-relation",
                       None, expected_party="demokrat", namespace="gsd-0412")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for suffix in ("statement", "event", "relation", "candidate"):
        table = "practice_" + suffix
        ident = f"{stem}-{suffix}"
        expected = next(row for row in records[table] if row["id"] == ident)
        row = db.execute(f"SELECT * FROM {table} WHERE id=?", (ident,)).fetchone()
        assert dict(row) == expected and expected in export[table], ident
    assert db.execute("SELECT result_finding_id FROM practice_relation WHERE id=?",
                      (f"{stem}-relation",)).fetchone()[0] is None
    evidence = db.execute("SELECT stage, count(*) FROM practice_event_evidence WHERE event_id=? GROUP BY stage",
                          (f"{stem}-event",)).fetchall()
    assert dict(map(tuple, evidence)) == {"action": 2, "initiative": 2}
    evidence_pages = db.execute("SELECT pdf_page_index FROM passage WHERE version_id=? ORDER BY pdf_page_index",
                                (f"{stem}-terms-v1",)).fetchall()
    assert [row[0] for row in evidence_pages] == [4, 8]
for view in ("party", "comparison"):
    anchor = f"{view}-practice-{stem}-relation"
    marker = f'id="{anchor}"'
    assert report.count(marker) == 1 and f'href="#{anchor}"' in report
    card = report.split(marker, 1)[1].split("</article>", 1)[0]
    assert all(phrase in card for phrase in ("5 Eylül", "18 Ekim", "iki şirket", "tahsis kararı", "devir")), view
print("DP_YASSIADA_2022_BOTH_VIEWS_OK", folder, flush=True)
