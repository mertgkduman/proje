"""Verify whether both 2020 policy comparisons retain their dates and limits."""

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
case = "tip-2020-policy"
prefix = f"0405-{case}"
package, review = (checks / f"{case}{suffix}-draft.json" for suffix in ("", "-review"))
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [65, 56, 0]
receipt = harness.main(
    package, review, case, f"{prefix}-idlib-event", f"{prefix}-idlib-relation",
    None, expected_party="tip", namespace="gsd-0405",
)
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ("practice_event", "practice_relation", "practice_candidate", "practice_statement"):
        for row in records[table]:
            if row["id"].startswith(prefix):
                actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(actual), row["id"]
    for suffix, stage in (
        ("idlib-signature", "action"), ("idlib-start", "result"), ("idlib-patrol", "result"),
        ("idlib-transmission", "result"), ("izin-accept", "action"), ("izin-protection", "result"),
        ("izin-unpaid", "result"), ("izin-support", "result"), ("izin-effective", "result"),
    ):
        actual = db.execute("SELECT stage FROM practice_event_evidence WHERE passage_id=?",
                            (f"{prefix}-{suffix}",)).fetchone()
        assert tuple(actual) == (stage,), suffix
    assert not db.execute("SELECT 1 FROM practice_contribution WHERE event_id LIKE ?", (prefix + "%",)).fetchall()
report = (folder / "index.html").read_text()
for key, phrases in {
    "idlib": ("3 Şubat", "5 Mart", "6 Mart", "00.01", "Suriye’den çekilme", "devriye"),
    "izin": ("12 Mart", "16 Nisan", "17 Nisan", "iki hafta ücretli", "ücretsiz izin", "Nakdi ücret desteği"),
}.items():
    for view in ("party", "comparison"):
        anchor = f"{view}-practice-{prefix}-{key}-relation"
        marker = f'id="{anchor}"'
        assert report.count(marker) == 1 and f'href="#{anchor}"' in report, anchor
        block = report.split(marker, 1)[1].split("</article>", 1)[0]
        assert all(phrase.casefold() in block.casefold() for phrase in phrases), (view, key, phrases)
print("TIP_2020_POLICY_BOTH_VIEWS_OK", folder, flush=True)
