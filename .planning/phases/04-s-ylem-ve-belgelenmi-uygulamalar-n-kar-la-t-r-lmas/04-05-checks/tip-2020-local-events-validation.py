"""Check the five local events and their links across SQLite, JSON and both reader views."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("practice_validation", checks.parent / "04-04-checks" / "samsun-reply-validation.py")
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / "practices" / "sources" / "tip"
name = "tip-2020-local-events"
package, review = [checks / f"{name}{suffix}-draft.json" for suffix in ("", "-review")]
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[key]) for key in ("practice_event", "practice_relation", "practice_closure")] == [63, 54, 0]
prefix = "0405-tip-2020-local"
receipt = harness.main(package, review, name, f"{prefix}-zincir-event", "0405-tip-bakirkoy-2019-relation",
                       None, expected_party="tip", namespace="gsd-0405")
folder = Path(receipt["preview"])
export = json.loads((folder / "records.json").read_bytes())
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
markers = {
    "zincir": ("Küçükçekmece Gölü", "12 Ocak", "Bianet"),
    "grev": ("Trelleborg", "22 Ocak", "33. günü"),
    "yemek": ("yemekhane", "6 Ocak", "rektörlük"),
    "tarife": ("Şubat 2020", "10 Şubat", "UKOME"),
    "gezi": ("18 Şubat", "beraat", "tutuklama"),
}
with sqlite3.connect((folder / "records.sqlite3").as_uri() + "?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ("practice_event", "practice_candidate", "practice_contribution"):
        for row in records[table]:
            if row["id"].startswith(f"{prefix}-"):
                assert row in export[table] and row == dict(db.execute(f"SELECT * FROM {table} WHERE id=?", (row["id"],)).fetchone())
    assert all(row["relation_id"] is None and row["state"] == "unmatched" for row in export["practice_candidate"]
               if row["id"].startswith(f"{prefix}-"))
html = (folder / "index.html").read_text()
for key, words in markers.items():
    for view in ("party", "comparison"):
        anchor = f"{view}-unmatched-{prefix}-{key}-unmatched"
        marker = f'id="{anchor}"'
        assert html.count(marker) == 1 and f'href="#{anchor}"' in html, anchor
        card = html.split(marker, 1)[1].split("</article>", 1)[0].casefold()
        assert all(word.casefold() in card for word in words), (anchor, words)
print("TIP_2020_LOCAL_EVENTS_BOTH_VIEWS_OK", folder, flush=True)
