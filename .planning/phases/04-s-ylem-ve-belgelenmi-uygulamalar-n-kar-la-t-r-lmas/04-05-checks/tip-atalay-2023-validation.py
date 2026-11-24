"""Verify both TİP 2023 Atalay comparisons in each reader view."""

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
case = "tip-atalay-2023"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [28, 27, 0]
receipt = harness.main(package, review, case, f"{stem}-walk-event", f"{stem}-walk-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
report = (folder / "index.html").read_text()

expectations = {
    "walk": ("2023-09-20", "2023-10-01", ("20 Eylül", "Hatay Meclis Binası", "28 Ekim", "Anıtpark", "etkisi açık")),
    "court": ("2023-11-07", "2023-11-08", ("2023/53898", "uyulmamasına", "21 Aralık", "3 Ocak 2024", "30 Ocak TBMM")),
}
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for name, (statement_day, event_day, phrases) in expectations.items():
        for suffix in ("statement", "event", "relation", "candidate"):
            table = "practice_" + suffix
            identity = f"{stem}-{name}-{suffix}"
            expected = next(row for row in records[table] if row["id"] == identity)
            actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (identity,)).fetchone()
            assert expected in export[table] and dict(actual) == expected, identity
            if suffix == "statement":
                assert actual["statement_at"] == statement_day
            if suffix == "event":
                assert actual["event_at"] == event_day
        for view in ("party", "comparison"):
            anchor = f"{view}-practice-{stem}-{name}-relation"
            marker = f'id="{anchor}"'
            assert report.count(marker) == 1 and f'href="#{anchor}"' in report
            card = report.split(marker, 1)[1].split("</article>", 1)[0]
            assert all(phrase in card for phrase in phrases), (view, name)
    ruling = db.execute("SELECT pdf_page_index,exact FROM passage WHERE id=?", (f"{stem}-yargitay-ruling-p",)).fetchone()
    assert tuple(ruling) == (21, "Anayasa Mahkemesi'nin anılan kararına UYULMAMASINA,")
    authority = db.execute("SELECT publisher,public_url FROM source_attribution WHERE version_id=?",
                           (f"{stem}-yargitay-v1",)).fetchone()
    assert authority["publisher"] == "Yargıtay 3. Ceza Dairesi" and "im.haberturk.com/" in authority["public_url"]
print("TIP_ATALAY_2023_BOTH_VIEWS_OK", folder, flush=True)
