"""Check three Istanbul Convention proceedings through both archive views."""

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
case = "tip-istanbul-sozlesmesi"
prefix = "0405-tip-istanbul-sozlesmesi"
package, review = (checks / f"{case}{suffix}-draft.json" for suffix in ("", "-review"))
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [78, 60, 0]
receipt = harness.main(package, review, case, f"{prefix}-withdrawal-event", f"{prefix}-withdrawal-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    for table in ("practice_statement", "practice_event", "practice_candidate", "practice_relation", "practice_contribution"):
        for row in records[table]:
            if row["id"].startswith(prefix):
                saved = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(saved), row["id"]
    roles = db.execute(
        "SELECT event_id, contribution_kind FROM practice_contribution WHERE event_id LIKE ?",
        (prefix + "%",),
    )
    assert {tuple(row) for row in roles} == {
        (f"{prefix}-court-first-event", "objection"),
        (f"{prefix}-court-final-event", "objection"),
    }
    statement = db.execute("SELECT statement_at,date_precision FROM practice_statement WHERE id=?",
                           (f"{prefix}-stance-statement",)).fetchone()
    assert tuple(statement) == (None, "unknown")
html = (folder / "index.html").read_text()
for key, phrases in {
    "withdrawal": ("3718", "20 Mart", "3928", "1 Temmuz", "6284"),
    "court-first": ("14 Haziran", "E.2021/1514", "K.2022/3217", "Onuncu Daire", "davacı"),
    "court-final": ("19 Aralık", "E.2022/3473", "K.2022/3752", "ehliyetini", "kesin", "AYM"),
}.items():
    for view in ("party", "comparison"):
        anchor = f"{view}-practice-{prefix}-{key}-relation"
        marker = f'id="{anchor}"'
        assert html.count(marker) == 1 and f'href="#{anchor}"' in html, anchor
        card = html.split(marker, 1)[1].split("</article>", 1)[0].casefold()
        assert all(phrase.casefold() in card for phrase in phrases), (anchor, phrases)
print("TIP_ISTANBUL_SOZLESMESI_BOTH_VIEWS_OK", folder, flush=True)
