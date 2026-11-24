"""Verify the 2023 constitutional ruling and public debt rule in both views."""

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
harness.SOURCE = harness.DATA / "practices" / "sources" / "tip"
case = "tip-july-october-2023"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [30, 29, 0]
receipt = harness.main(package, review, case, f"{stem}-court-event", f"{stem}-court-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
phrases = {
    "court": ("25 Ağustos", "25 Ekim", "iki hak ihlali", "Fiilî tahliye ayrı", "8 Kasım Yargıtay"),
    "debt": ("7 Temmuz", "14 Temmuz", "7456/11", "üç kat", "Fiilî borç tutarı", "KDV ve telefon harcı ayrı"),
}
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for label, expected_phrases in phrases.items():
        for suffix in ("statement", "event", "relation", "candidate"):
            table = "practice_" + suffix
            ident = f"{stem}-{label}-{suffix}"
            expected = next(row for row in records[table] if row["id"] == ident)
            actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (ident,)).fetchone()
            assert expected in export[table] and expected == dict(actual), ident
        for view in ("party", "comparison"):
            anchor = f"{view}-practice-{stem}-{label}-relation"
            marker = f'id="{anchor}"'
            assert report.count(marker) == 1 and f'href="#{anchor}"' in report
            card = report.split(marker, 1)[1].split("</article>", 1)[0]
            assert all(phrase in card for phrase in expected_phrases), (view, label)
    order = db.execute("SELECT version_id,pdf_page_index,printed_page FROM passage WHERE id=?",
                       (f"{stem}-court-order-p",)).fetchone()
    assert tuple(order) == ("0405-tip-atalay-2023-aym-first-v1", 850, "1602")
    debt = db.execute("SELECT exact FROM passage WHERE id=?", (f"{stem}-debt-text-p",)).fetchone()
    assert debt["exact"] == "borç kullanım tutarının üç katı olarak uygulanır."
print("TIP_JULY_OCTOBER_2023_BOTH_VIEWS_OK", folder, flush=True)
