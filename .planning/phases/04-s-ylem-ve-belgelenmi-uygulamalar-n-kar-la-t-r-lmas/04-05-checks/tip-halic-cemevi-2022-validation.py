"""Verify the Haliç and cemevi evidence in both reader views."""

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
case = "tip-halic-cemevi-2022"
stem = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [37, 35, 0]
receipt = harness.main(package, review, case, f"{stem}-cemevi-event", f"{stem}-cemevi-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
report = (folder / "index.html").read_text()
markers = {
    f"practice-{stem}-cemevi-relation": ("10 Ekim", "16 Kasım", "26 Kasım", "aydınlatma", "ödeneğe"),
    f"practice-{stem}-halic-relation": ("25 Ağustos", "Haliç", "25 Eylül", "Erkan Baş"),
}
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ("practice_event", "practice_relation", "practice_contribution", "practice_candidate"):
        for row in records[table]:
            if row["id"].startswith(stem):
                actual = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(actual), row["id"]
    education = db.execute("SELECT scope_context FROM practice_event WHERE id=?",
                           ("0405-tip-earthquake-2023-education-event",)).fetchone()
    assert education[0] == "30 Mart 2023 YÖK kararıyla bahar döneminde uzaktan öğretimin yanında yüz yüze eğitim seçeneği."
    assert "14 Şubat TİP Bilim Kurulu fizikî açılış çağrısı" in report
    roles = db.execute("SELECT a.kind, p.name FROM practice_contribution AS c "
                       "JOIN actor AS a ON a.id=c.actor_id LEFT JOIN person AS p ON p.id=a.person_id "
                       "WHERE c.event_id=? ORDER BY a.kind", (f"{stem}-halic-event",)).fetchall()
    assert [tuple(row) for row in roles] == [("authorized_representative", "Erkan Baş"), ("institution", None)]
    assert db.execute("SELECT COUNT(*) FROM practice_relation WHERE event_id=?", (f"{stem}-halic-event",)).fetchone()[0] == 1
    proof = db.execute("SELECT v.sha256 FROM passage p JOIN document_version v ON p.version_id=v.id WHERE p.id=?",
                       (f"{stem}-halic-held-p",)).fetchone()
    assert proof[0] == "a086de25cf9ac44d84a409f658b25d16a6e9f33b801089d56e066806fd10625e"
for anchor, phrases in markers.items():
    for view in ("party", "comparison"):
        marker = f'id="{view}-{anchor}"'
        assert report.count(marker) == 1 and f'href="#{view}-{anchor}"' in report
        block = report.split(marker, 1)[1].split("</article>", 1)[0]
        assert all(phrase in block for phrase in phrases), (view, anchor, phrases)
print("TIP_HALIC_CEMEVI_2022_BOTH_VIEWS_OK", folder, flush=True)
