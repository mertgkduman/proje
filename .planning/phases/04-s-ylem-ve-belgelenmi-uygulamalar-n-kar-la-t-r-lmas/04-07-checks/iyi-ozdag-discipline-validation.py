"""Validate the two dated İYİ Parti disciplinary proceedings."""

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
harness.SOURCE = harness.DATA / "practices" / "sources" / "iyi"
case = "iyi-ozdag-discipline"
prefix = "0407-iyi-ozdag-2020-2021"
package, review = (checks / f"{case}{suffix}-draft.json" for suffix in ("", "-review"))
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [23, 15, 0]
receipt = harness.main(package, review, case, f"{prefix}-board-event", f"{prefix}-board-relation",
                       None, expected_party="iyi", namespace="gsd-0407")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    for table in ("practice_statement", "practice_event", "practice_relation", "practice_candidate", "practice_contribution"):
        for row in records[table]:
            if row["id"].startswith(prefix):
                saved = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(saved), row["id"]
    roles = db.execute("SELECT event_id, contribution_kind FROM practice_contribution WHERE event_id LIKE ?", (prefix + "%",))
    assert {tuple(row) for row in roles} == {
        (f"{prefix}-board-event", "task"),
        (f"{prefix}-court-event", "objection"),
    }
    court_date = db.execute("SELECT event_at FROM practice_event WHERE id=?", (f"{prefix}-court-event",)).fetchone()
    assert court_date[0] == "2021-01-13"
html = (folder / "index.html").read_text()
for key, phrases in {
    "board": ("Müşterek Disiplin Kurulu", "Ümit Özdağ", "16 Kasım", "oybirliği", "Kurucular Kurulu"),
    "court": ("Asliye Hukuk Mahkemesi", "13 Ocak", "20 Ocak", "14 Ocak", "dosya numarası"),
}.items():
    for view in ("party", "comparison"):
        anchor = f"{view}-practice-{prefix}-{key}-relation"
        marker = f'id="{anchor}"'
        assert html.count(marker) == 1 and f'href="#{anchor}"' in html, anchor
        card = html.split(marker, 1)[1].split("</article>", 1)[0].casefold()
        assert all(phrase.casefold() in card for phrase in phrases), (anchor, phrases)
print("IYI_OZDAG_DISCIPLINE_BOTH_VIEWS_OK", folder, flush=True)
