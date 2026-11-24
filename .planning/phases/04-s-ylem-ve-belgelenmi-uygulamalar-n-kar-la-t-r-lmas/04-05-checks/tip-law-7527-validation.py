"""Verify the TİP 7527 comparison and the two official vote counts."""

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

case = "tip-law-7527"
prefix = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[k]) for k in ("practice_event", "practice_relation", "practice_closure")] == [26, 25, 0]
receipt = harness.main(package, review, case, f"{prefix}-event", f"{prefix}-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())

with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, suffix in (
        ("practice_statement", "statement"), ("practice_event", "event"),
        ("practice_relation", "relation"), ("practice_candidate", "candidate"),
    ):
        identity = f"{prefix}-{suffix}"
        expected = next(row for row in records[table] if row["id"] == identity)
        actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (identity,)).fetchone()
        assert dict(actual) == expected and expected in export[table], identity

    sources = {
        "floor-count": ("floor", 213, "388", "Kullanılan oy sayısı : 500"),
        "roll-count": ("floor", 214, "389", "Kabul Edenler : 273"),
        "roll-duplicates": ("floor", 214, "389", "Mükerrer Oylar : 2"),
        "roll-bas": ("floor", 219, "394", "İstanbul Baş Erkan TİP Ret"),
        "roll-kadigil": ("floor", 220, "395", "İstanbul Kadıgil Saliha Sera TİP Ret"),
        "roll-sik": ("floor", 221, "396", "İstanbul Şık Ahmet TİP Ret"),
        "correction": ("correction", 70, "491", "Oyumun rengi “kabul” şeklindedir"),
    }
    for suffix, (version, index, printed, quote) in sources.items():
        row = db.execute('SELECT version_id,pdf_page_index,printed_page,exact FROM passage WHERE id=?',
                         (f"{prefix}-{suffix}-p",)).fetchone()
        assert tuple(row) == (f"{prefix}-{version}-v1", index, printed, quote), suffix

report = (folder / "index.html").read_text()
for view in ("party", "comparison"):
    anchor = f"{view}-practice-{prefix}-relation"
    marker = f'id="{anchor}"'
    assert report.count(marker) == 1 and f'href="#{anchor}"' in report
    card = report.split(marker, 1)[1].split("</article>", 1)[0]
    for phrase in ("275 kabul", "273 kabul", "2 mükerrer", "Aydoğdu", "Erkan Baş",
                   "Saliha Sera Kadıgil", "Ahmet Şık", "Yerel uygulama sonuçları açık"):
        assert phrase in card, (view, phrase)
print("TIP_LAW_7527_BOTH_VIEWS_OK", folder, flush=True)
