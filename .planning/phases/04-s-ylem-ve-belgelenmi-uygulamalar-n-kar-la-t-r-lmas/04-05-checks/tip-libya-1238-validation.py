"""Verify the archived 3/1044 comparison in both reader views."""

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
case = "tip-libya-1238"
prefix = f"0405-{case}"
package_path = checks / f"{case}-draft.json"
review_path = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package_path, review_path)] == sys.argv[1:]
records = json.loads(package_path.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [23,22,0]
receipt = harness.main(package_path, review_path, case, f"{prefix}-event", f"{prefix}-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
with sqlite3.connect((folder / "records.sqlite3").as_uri()+"?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, suffix in (
        ("practice_statement", "statement"), ("practice_event", "event"), ("practice_relation", "relation"),
        ("practice_candidate", "candidate"), ("practice_contribution", "speech-contribution"),
        ("practice_contribution", "vote-contribution"),
    ):
        ident = f"{prefix}-{suffix}"
        expected = next(row for row in records[table] if row["id"] == ident)
        actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (ident,)).fetchone()
        assert expected in export[table] and expected == dict(actual), ident
    points = dict(db.execute(
        "SELECT passage_id,supported_point FROM practice_event_evidence WHERE event_id=?", (f"{prefix}-event",)))
    assert set(points) >= {f"{prefix}-{key}-p" for key in (
        "tally-chair", "roll-yes", "roll-no", "roll-duplicate", "roll-total", "roll-bas", "roll-atay", "publication")}
    assert "509 toplam, 325 kabul ve 184 ret" in points[f"{prefix}-tally-chair-p"]
    assert points[f"{prefix}-roll-bas-p"] == "Erkan Baş kesin cetvelde Red."
    assert points[f"{prefix}-roll-atay-p"] == "Barış Atay Mengüllüoğlu kesin cetvelde Katılmadı."
report = (folder / "index.html").read_text()
for view in ("party", "comparison"):
    anchor = f"{view}-practice-{prefix}-relation"
    marker = f'id="{anchor}"'
    assert report.count(marker) == 1 and f'href="#{anchor}"' in report
    card = report.split(marker,1)[1].split("</article>",1)[0]
    for phrase in ("332 kabul", "183 ret", "6 mükerrer", "521 oy", "325 kabul", "184 ret", "Katılmadı", "3 Ocak"):
        assert phrase in card, (view, phrase)
print("TIP_LIBYA_1238_BOTH_VIEWS_OK", folder, flush=True)
