"""Check the source stages and reader anchors for three TİP comparisons."""

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
case = "tip-school-montro-paris"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [42, 40, 0]
receipt = harness.main(
    package, review, case, f"{stem}-school-event", f"{stem}-school-relation",
    None, expected_party="tip", namespace="gsd-0405",
)
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
markers = {
    "school": ("10 Ağustos", "19 Ağustos", "6 Eylül", "derslik"),
    "montro": ("24 Şubat", "2 Mart", "19. madde", "limana dönüş"),
    "paris": ("5 Ağustos", "6 Ekim", "11 Ekim", "10 Kasım"),
}
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ("practice_event", "practice_relation", "practice_candidate", "practice_statement"):
        for row in records[table]:
            if row["id"].startswith(stem):
                actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(actual), row["id"]
    for suffix, stage in (
        ("school-announcement", "initiative"),
        ("school-start", "action"),
        ("school-guidance", "result"),
        ("montro-art19", "action"),
        ("montro-application", "result"),
        ("paris-law-adopted", "initiative"),
        ("paris-deposit", "action"),
        ("paris-effective", "result"),
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
print("TIP_SCHOOL_MONTRO_PARIS_BOTH_VIEWS_OK", folder, flush=True)
