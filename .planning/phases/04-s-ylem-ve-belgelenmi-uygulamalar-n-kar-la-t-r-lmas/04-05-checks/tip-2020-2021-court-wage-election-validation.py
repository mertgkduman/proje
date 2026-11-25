"""Check the court, wage, election and joint statement source stages."""

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
case = "tip-2020-2021-court-wage-election"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [46, 43, 0]
receipt = harness.main(
    package, review, case, f"{stem}-court-event", f"{stem}-court-relation",
    None, expected_party="tip", namespace="gsd-0405",
)
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
markers = {
    "court": ("14 Ekim", "21 Ocak", "8 Şubat", "10 Şubat", "11 Şubat"),
    "wage": ("9 Aralık", "28 Aralık", "3.577,50", "2.825,90"),
    "election": ("21 Haziran", "23 Haziran", "4.742.082", "54,22"),
}
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ("practice_event", "practice_relation", "practice_candidate", "practice_statement"):
        for row in records[table]:
            if row["id"].startswith(stem):
                actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(actual), row["id"]
    for suffix, stage in (
        ("court-first-order", "initiative"),
        ("court-october-order", "initiative"),
        ("court-second-order", "initiative"),
        ("court-local", "action"),
        ("court-presented", "result"),
        ("wage-decided", "result"),
        ("election-vote", "result"),
        ("joint-press", "action"),
    ):
        row = db.execute(
            "SELECT stage FROM practice_event_evidence WHERE passage_id=?",
            (f"{stem}-{suffix}-p",),
        ).fetchone()
        assert tuple(row) == (stage,), suffix
    for key, page in (("court-first-order", 30), ("court-october-order", 7), ("court-second-order", 35)):
        row = db.execute(
            "SELECT p.pdf_page_index FROM passage AS p JOIN manual_passage AS m ON m.passage_id=p.id WHERE p.id=?",
            (f"{stem}-{key}-p",),
        ).fetchone()
        assert tuple(row) == (page,), key
for view in ("party", "comparison"):
    anchor = f"{view}-unmatched-{stem}-joint-unmatched"
    assert report.count(f'id="{anchor}"') == 1 and f'href="#{anchor}"' in report
    card = report.split(f'id="{anchor}"', 1)[1].split("</article>", 1)[0]
    assert "18 Mayıs" in card and "BirGün" in card
for key, phrases in markers.items():
    for view in ("party", "comparison"):
        anchor = f"{view}-practice-{stem}-{key}-relation"
        marker = f'id="{anchor}"'
        assert report.count(marker) == 1 and f'href="#{anchor}"' in report
        block = report.split(marker, 1)[1].split("</article>", 1)[0]
        assert all(phrase in block for phrase in phrases), (view, key, phrases)
print("TIP_2020_2021_COURT_WAGE_ELECTION_BOTH_VIEWS_OK", folder, flush=True)
