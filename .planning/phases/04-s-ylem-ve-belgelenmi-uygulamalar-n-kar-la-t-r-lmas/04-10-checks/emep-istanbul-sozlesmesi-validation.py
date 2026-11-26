"""Validate EMEP’s separate relation to the shared Istanbul Convention decision."""

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
harness.SOURCE = harness.DATA / "practices" / "sources" / "emep"
case = "emep-istanbul-sozlesmesi"
prefix = "0410-emep-istanbul-sozlesmesi"
tip_prefix = "0405-tip-istanbul-sozlesmesi"
package, review = (checks / f"{case}{suffix}-draft.json" for suffix in ("", "-review"))
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
emep = json.loads(package.read_bytes())
records = emep["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [88, 82, 0]
tip_path = checks.parent / "04-05-checks" / "tip-istanbul-sozlesmesi-draft.json"
assert harness.sha(tip_path) == "ea387982aa36335f24dd001e020065a699b843526039dcbcb6bf9a6420e06893"
tip = json.loads(tip_path.read_bytes())
event = next(row for row in records["practice_event"] if row["id"] == f"{prefix}-event")
tip_event = next(row for row in tip["practice_records"]["practice_event"]
                 if row["id"] == f"{tip_prefix}-withdrawal-event")
assert {key: value for key, value in event.items() if key != "id"} == {
    key: value for key, value in tip_event.items() if key != "id"
}

def get_entry(package, kind, identity):
    return next(entry["values"] for entry in package["entries"]
                if entry["kind"] == kind and entry["values"]["id"] == identity)

for key in ("withdrawal-id", "withdrawal-publication", "effect-id", "effect-publication"):
    left = get_entry(emep, "passage", f"{prefix}-{key}")
    right = get_entry(tip, "passage", f"{tip_prefix}-{key}")
    assert (left["exact"], left["pdf_page_index"]) == (right["exact"], right["pdf_page_index"])
    left_version = get_entry(emep, "document_version", left["version_id"])
    right_version = get_entry(tip, "document_version", right["version_id"])
    assert (left_version["original_url"], left_version["sha256"]) == (right_version["original_url"], right_version["sha256"])
receipt = harness.main(package, review, case, f"{prefix}-event", f"{prefix}-relation",
                       None, expected_party="emep", namespace="gsd-0410")
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
    roles = db.execute("SELECT contribution_kind FROM practice_contribution WHERE event_id=?", (f"{prefix}-event",))
    assert [tuple(row) for row in roles] == [("objection",)]
html = (folder / "index.html").read_text()
for view in ("party", "comparison"):
    anchor = f"{view}-practice-{prefix}-relation"
    marker = f'id="{anchor}"'
    assert html.count(marker) == 1 and f'href="#{anchor}"' in html
    card = html.split(marker, 1)[1].split("</article>", 1)[0]
    for phrase in ("Şükran Doğan", "28 Ağustos", "3718", "3928", "1 Temmuz", "Selma Gürkan"):
        assert phrase in card, (view, phrase)
print("EMEP_ISTANBUL_SOZLESMESI_BOTH_VIEWS_OK", folder, flush=True)
