"""Verify the five evidence-based civic records in both reader views."""

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
case = "tip-2020-autumn-civic"
prefix = "0405-tip-2020-autumn"
package, review = (checks / f"{case}{suffix}-draft.json" for suffix in ("", "-review"))
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [75, 57, 0]
receipt = harness.main(package, review, case, f"{prefix}-atay-event", "0405-tip-2020-civic-bar-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    for table in ("practice_event", "practice_candidate", "practice_contribution"):
        for row in records[table]:
            if row["id"].startswith(prefix):
                saved = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(saved), row["id"]
    roles = db.execute(
        "SELECT event_id, contribution_kind FROM practice_contribution WHERE event_id LIKE ?",
        (prefix + "%",),
    )
    assert {tuple(row) for row in roles} == {
        (f"{prefix}-izmir-event", "support"),
        (f"{prefix}-yogurtcu-event", "task"),
    }
    assert db.execute(
        "SELECT COUNT(DISTINCT event_id) FROM practice_candidate WHERE id LIKE ? AND state='unmatched' AND relation_id IS NULL",
        (prefix + "%",),
    ).fetchone()[0] == 5
html = (folder / "index.html").read_text()
for key, phrases in {
    "atay": ("31 Ağustos", "ilk derece", "kesinleşme"),
    "yogurtcu": ("1 Eylül", "Yoğurtçu Parkı", "imzalı açıklaması"),
    "izmir": ("30 Ekim", "çadır, battaniye ve gıda", "yararlanıcı"),
    "women": ("25 Kasım", "Platformu", "10 şehirde"),
    "ermenek": ("25 Kasım", "12 Ekim", "gözaltıları"),
}.items():
    for view in ("party", "comparison"):
        anchor = f"{view}-unmatched-{prefix}-{key}-unmatched"
        marker = f'id="{anchor}"'
        assert html.count(marker) == 1 and f'href="#{anchor}"' in html, anchor
        card = html.split(marker, 1)[1].split("</article>", 1)[0].casefold()
        assert all(phrase.casefold() in card for phrase in phrases), (anchor, phrases)
print("TIP_2020_AUTUMN_CIVIC_BOTH_VIEWS_OK", folder, flush=True)
