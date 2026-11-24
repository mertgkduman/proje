"""Check TİP's 7242 comparison and the two individual voting rows."""

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
case = "tip-7242"
base = f"0405-{case}"
package = checks / f"{case}-draft.json"
review = checks / f"{case}-review-draft.json"
assert [harness.sha(path) for path in (package,review)] == sys.argv[1:]
records = json.loads(package.read_bytes())["practice_records"]
assert [len(records[k]) for k in ("practice_event","practice_relation","practice_closure")] == [22,21,0]
receipt = harness.main(package,review,case,f"{base}-event",f"{base}-relation",
                       None,expected_party="tip",namespace="gsd-0405")
folder = Path(receipt["preview"])
manifest = json.loads((folder / "manifest.json").read_bytes())
assert manifest["preview"] and manifest["renderer_version"] == 31
export = json.loads((folder / "records.json").read_bytes())
with sqlite3.connect((folder / "records.sqlite3").as_uri()+"?mode=ro",uri=True) as db:
    db.row_factory=sqlite3.Row
    for table,suffix in (("practice_statement","statement"),("practice_event","event"),
                         ("practice_relation","relation"),("practice_candidate","candidate")):
        ident = f"{base}-{suffix}"
        expected = next(row for row in records[table] if row["id"]==ident)
        actual = db.execute(f"SELECT * FROM {table} WHERE id=?",(ident,)).fetchone()
        assert expected in export[table] and expected==dict(actual),ident
    points=dict(db.execute("SELECT passage_id,supported_point FROM practice_event_evidence WHERE event_id=?",(f"{base}-event",)))
    assert "Barış Atay Mengüllüoğlu için Katılmadı" in points[f"{base}-roll-atay-p"]
    assert "Erkan Baş için Katılmadı" in points[f"{base}-roll-bas-p"]
    assert "00.09, 279 kabul, 51 ret" in points[f"{base}-roll-count-p"]
report=(folder / "index.html").read_text()
for view in ("party","comparison"):
    anchor=f"{view}-practice-{base}-relation"
    marker=f'id="{anchor}"'
    assert report.count(marker)==1 and f'href="#{anchor}"' in report
    card=report.split(marker,1)[1].split("</article>",1)[0]
    for phrase in ("6 Nisan 2020", "279 kabul ve 51 ret", "Barış Atay Mengüllüoğlu ve Erkan Baş", "Katılmadı", "15 Nisan", "Terörle Mücadele Kanunu"):
        assert phrase in card,(view,phrase)
print("TIP_LAW_7242_BOTH_VIEWS_OK",folder,flush=True)
