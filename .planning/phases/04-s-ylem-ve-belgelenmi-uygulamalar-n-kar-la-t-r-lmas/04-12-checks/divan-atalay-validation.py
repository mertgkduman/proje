"""Verify a party notice and four separately documented Can Atalay proceedings."""

from html import escape
import importlib.util
import json
from pathlib import Path
import sqlite3

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "practice_validation", checks.parent / "04-04-checks" / "samsun-reply-validation.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / "practices" / "sources" / "demokrat"
case = "divan-atalay"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert harness.sha(package) == "7f8623bd0a4c8f82b26d40853c29092912950e53042902dd3cbfa6efc3fe80dc"
assert harness.sha(review) == "f5de309aee943bb68d9344cbaa1c15f0ce5219c6fe9280ed7f1b0dd70b609dcd"
records = json.loads(package.read_bytes())["practice_records"]
assert (len(records["practice_event"]), len(records["practice_relation"]),
        len(records["practice_closure"])) == (46, 38, 0)
receipt = harness.main(package, review, case, "0412-atalay-judgment-event", "0412-atalay-judgment-relation",
                       None, expected_party="demokrat", namespace="gsd-0412")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
report = (folder / "index.html").read_text()
stems = ("0412-divan-notice", "0412-atalay-chamber", "0412-atalay-judgment",
         "0412-atalay-reading", "0412-atalay-norm")
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identities in (
        ("practice_statement", ("0412-divan-statement", "0412-atalay-statement")),
        ("practice_event", tuple(stem + "-event" for stem in stems)),
        ("practice_relation", tuple(stem + "-relation" for stem in stems if stem != "0412-atalay-chamber")),
        ("practice_candidate", tuple(stem + "-candidate" for stem in stems)),
    ):
        for identity in identities:
            row = next(item for item in records[table] if item["id"] == identity)
            assert row in export[table]
            assert row == dict(db.execute(f"SELECT * FROM {table} WHERE id=?", (identity,)).fetchone())
    assert tuple(db.execute("SELECT state,relation_id FROM practice_candidate WHERE id=?",
                           ("0412-atalay-chamber-candidate",)).fetchone()) == ("unmatched", None)
    assert db.execute("SELECT result_finding_id FROM practice_relation WHERE id=?",
                      ("0412-divan-notice-relation",)).fetchone()[0] is None
    for stem, date in zip(stems, ("2023-07-22", "2023-11-08", "2023-12-21", "2024-01-30", "2024-02-22")):
        assert db.execute("SELECT event_at FROM practice_event WHERE id=?", (stem + "-event",)).fetchone()[0] == date
    for label, date in (("aym", "2023-12-27"), ("norm", "2024-08-01")):
        assert db.execute("SELECT document_date FROM document_version WHERE id=?",
                          ("0412-atalay-" + label + "-v1",)).fetchone()[0] == date
    assert db.execute("SELECT count(*) FROM manual_passage WHERE passage_id LIKE '0412-atalay-%'").fetchone()[0] == 9

cards = (
    ("practice-0412-divan-notice-relation", ("Başkanlık Divanı", "onay", "22 Temmuz")),
    ("unmatched-0412-atalay-chamber-candidate", ("8 Kasım", "Yargıtay", "suç duyurusu")),
    ("practice-0412-atalay-judgment-relation", ("21 Aralık", "2023/99744", "ihlal")),
    ("practice-0412-atalay-reading-relation", ("3/835", "30 Ocak", "okun")),
    ("practice-0412-atalay-norm-relation", ("22 Şubat", "1 Ağustos", "yer olmadığı")),
)
for view in ("party", "comparison"):
    for key, phrases in cards:
        anchor = f"{view}-{key}"
        start = f'id="{anchor}"'
        assert report.count(start) == 1 and f'href="#{anchor}"' in report
        card = report.split(start, 1)[1].split("</article>", 1)[0].casefold()
        for phrase in phrases:
            assert escape(phrase).casefold() in card, (view, key, phrase)
print("DEMOCRAT_DIVAN_ATALAY_BOTH_VIEWS_OK", folder, flush=True)
