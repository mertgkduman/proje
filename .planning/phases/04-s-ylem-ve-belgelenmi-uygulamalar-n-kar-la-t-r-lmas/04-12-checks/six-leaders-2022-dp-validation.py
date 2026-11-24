"""Verify the planned meeting, documented participation, and both report views."""

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
harness.SOURCE = harness.DATA / "practices" / "sources" / "demokrat"
case = "six-leaders-2022-dp"
stem = f"0412-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [80, 51, 0]
receipt = harness.main(package, review, case, f"{stem}-event", f"{stem}-relation",
                       None, expected_party="demokrat", namespace="gsd-0412")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
report = (folder / "index.html").read_text()
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, suffix in (("practice_statement", "statement"), ("practice_event", "event"),
                          ("practice_relation", "relation"), ("practice_candidate", "candidate"),
                          ("practice_contribution", "uysal-contribution")):
        ident = f"{stem}-{suffix}"
        expected = next(row for row in records[table] if row["id"] == ident)
        actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (ident,)).fetchone()
        assert expected in export[table] and expected == dict(actual), ident
    actor = db.execute("SELECT kind,party_id,authorization_passage_id FROM actor WHERE id=?",
                       (f"{stem}-uysal-actor",)).fetchone()
    assert tuple(actor) == ("authorized_representative", "demokrat", f"{stem}-uysal-p")
    publishers = dict(db.execute("SELECT version_id,publisher FROM source_attribution WHERE version_id LIKE ?", (stem + "%",)))
    assert publishers == {f"{stem}-statement-v1": "Demokrat Parti", f"{stem}-meeting-v1": "Independent Türkçe"}
    for view in ("party", "comparison"):
        anchor = f"{view}-practice-{stem}-relation"
        marker = f'id="{anchor}"'
        assert report.count(marker) == 1 and f'href="#{anchor}"' in report
        card = report.split(marker, 1)[1].split("</article>", 1)[0]
        assert all(phrase in card for phrase in (
            "14.00", "14.11", "Gültekin Uysal", "çalışma grubu kurma kararı", "Politikaların uygulanmasına ilişkin sonuç açık")), view
print("DEMOCRAT_SIX_LEADERS_BOTH_VIEWS_OK", folder, flush=True)
