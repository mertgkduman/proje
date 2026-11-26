"""Check the bar law, exam and labour records in both reader views."""

import importlib.util
import json
import os
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
case = "tip-2020-civic-labour"
prefix = "0405-tip-2020-civic"
package, review = (checks / f"{case}{s}-draft.json" for s in ("", "-review"))
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
package_data = json.loads(package.read_bytes())
records = package_data["practice_records"]
assert [len(records[t]) for t in ("practice_event", "practice_relation", "practice_closure")] == [70, 57, 0]
relation = f"{prefix}-bar-relation"
existing_receipt = os.environ.get("GSD0405_CIVIC_PREVIEW_RECEIPT")
if existing_receipt:
    receipt = json.loads(Path(existing_receipt).read_bytes())
    assert receipt["scope"] == case and receipt["relation"] == relation
    assert [receipt["package_sha256"], receipt["review_sha256"]] == sys.argv[1:]
    assert receipt["inventory_sha256"] == harness.sha(harness.INVENTORY)
    assert receipt["canonical"] == harness.canonical_identity()
else:
    receipt = harness.main(
        package, review, case, f"{prefix}-bar-event", relation, None,
        expected_party="tip", namespace="gsd-0405",
    )
folder = Path(receipt["preview"])
assert harness.sha(folder / "manifest.json") == receipt["preview_manifest_sha256"]
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
assert all(harness.sha(folder / name) == digest for name, digest in manifest["files"].items())
report = (folder / "index.html").read_text()
export = json.loads((folder / "records.json").read_bytes())
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert not db.execute("PRAGMA foreign_key_check").fetchall()
    for table in ("practice_event", "practice_relation", "practice_candidate", "practice_contribution"):
        for row in records[table]:
            if row["id"].startswith(prefix):
                result = db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone()
                assert row in export[table] and row == dict(result), row["id"]
    support = db.execute(
        "SELECT contribution_kind FROM practice_contribution WHERE event_id LIKE ?",
        (prefix + "%",),
    ).fetchall()
    assert [tuple(row) for row in support] == [("support",)]
    assert {
        (row["id"].removeprefix(prefix + "-").removesuffix("-candidate"), row["state"])
        for row in export["practice_candidate"] if row["id"].startswith(prefix)
    } == {("bar", "eligible"), ("yks", "unmatched"), ("may", "unmatched"),
          ("tempo-august", "unmatched"), ("tempo-report", "unmatched")}

markers = {
    f"practice-{relation}": ("2/2999", "11 Temmuz", "15 Temmuz", "şahsı adına"),
    f"unmatched-{prefix}-yks-candidate": ("20–21 Haziran", "27–28 Haziran", "ÖSYM"),
    f"unmatched-{prefix}-may-candidate": ("DİSK", "1 Mayıs", "15 gözaltı"),
    f"unmatched-{prefix}-tempo-august-candidate": ("12 Ağustos", "Şişli", "25 Ağustos"),
    f"unmatched-{prefix}-tempo-report-candidate": ("21 Eylül", "geçmiş alacakların fiilî ödemesi açık", "Evrensel"),
}
for tail, words in markers.items():
    for view in ("party", "comparison"):
        anchor = f"{view}-{tail}"
        tag = f'id="{anchor}"'
        assert report.count(tag) == 1 and f'href="#{anchor}"' in report, anchor
        card = report.split(tag, 1)[1].split("</article>", 1)[0].casefold()
        assert all(word.casefold() in card for word in words), (anchor, words)
tempo_passage = next(
    entry["values"] for entry in package_data["entries"]
    if entry["kind"] == "passage" and entry["values"]["id"] == f"{prefix}-tempo-report"
)
tempo_version = next(
    entry["values"] for entry in package_data["entries"]
    if entry["kind"] == "document_version" and entry["values"]["id"] == tempo_passage["version_id"]
)
assert tempo_passage["exact"] == "19 işçi, geçmişe dönük hakları da ödenmek üzere"
for key in ("original_path", "readable_path"):
    path = tempo_version[key]
    artifact = folder.parents[1] / path
    assert harness.sha(artifact) == manifest["asset_files"][path]
    assert tempo_passage["exact"] in artifact.read_text(encoding="utf-8")
print("TIP_2020_CIVIC_LABOUR_BOTH_VIEWS_OK", folder, flush=True)
