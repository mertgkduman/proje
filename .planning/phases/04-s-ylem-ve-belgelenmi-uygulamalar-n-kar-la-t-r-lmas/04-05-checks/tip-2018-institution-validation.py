"""Check the early TİP representation, local meeting and election qualification records."""

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
case = "tip-2018-institution"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [49, 46, 0]
receipt = harness.main(
    package, review, case, f"{stem}-member-event", f"{stem}-member-relation",
    None, expected_party="tip", namespace="gsd-0405",
)
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
markers = {
    "member": ("6 Ekim", "10 Ekim", "24 Haziran", "HDP"),
    "meeting": ("21 Ekim", "26 Ekim", "4 Aralık", "Gazi Cemevi"),
    "elig": ("2 Ocak", "13 parti", "TİP"),
}
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ("practice_event", "practice_relation", "practice_candidate", "practice_statement"):
        for row in records[table]:
            if row["id"].startswith(stem):
                actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(actual), row["id"]
    for suffix, stage in (
        ("member-chair", "action"),
        ("member-floor", "result"),
        ("meeting-resolution", "initiative"),
        ("meeting-gazi", "result"),
        ("elig-date", "action"),
        ("elig-list", "result"),
    ):
        row = db.execute(
            "SELECT stage FROM practice_event_evidence WHERE passage_id=?",
            (f"{stem}-{suffix}-p",),
        ).fetchone()
        assert tuple(row) == (stage,), suffix
for key, phrases in markers.items():
    for view in ("party", "comparison"):
        anchor = f"{view}-practice-{stem}-{key}-relation"
        marker = f'id="{anchor}"'
        assert report.count(marker) == 1 and f'href="#{anchor}"' in report
        block = report.split(marker, 1)[1].split("</article>", 1)[0]
        assert all(phrase in block for phrase in phrases), (view, key, phrases)
print("TIP_2018_INSTITUTION_BOTH_VIEWS_OK", folder, flush=True)
