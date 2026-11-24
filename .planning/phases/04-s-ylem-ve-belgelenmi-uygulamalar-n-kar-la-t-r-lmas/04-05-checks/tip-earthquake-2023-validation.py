"""Verify the 2023 housing law and education comparisons in both reader views."""

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
case = "tip-earthquake-2023"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [35, 33, 0]
receipt = harness.main(package, review, case, f"{stem}-housing-event", f"{stem}-housing-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
phrases = {
    "housing": ("9 Mart", "5 Nisan", "10 Nisan", "plan ve parselasyon", "konut teslimini"),
    "education": ("14 Şubat", "17 Şubat", "30 Mart", "3 Nisan", "üniversite kurulları"),
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
    selected = db.execute("SELECT pdf_page_index, exact FROM passage WHERE id=?",
                          (f"{stem}-education-choice-p",)).fetchone()
    assert selected[0] == 6 and "yüz yüze eğitim verilebilmesine" in selected[1]
    expected = db.execute("SELECT exact FROM passage WHERE id=?", (f"{stem}-housing-exception-p",)).fetchone()
    assert expected[0] == "askı, ilan, itirazlara ilişkin hükümleri uygulanmaz."
print("TIP_EARTHQUAKE_2023_BOTH_VIEWS_OK", folder, flush=True)
