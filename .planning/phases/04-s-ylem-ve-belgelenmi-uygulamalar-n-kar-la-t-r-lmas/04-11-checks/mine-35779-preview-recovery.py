"""Rebuild the 7/35779 preview on local storage using the verified input pair."""

from hashlib import file_digest
import json
import os
from pathlib import Path
from shutil import copytree
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory

checks = Path(__file__).resolve().parent
root = checks.parents[3]
archive = Path("/work/mg551/gsd0411-2020-miners")
package = archive / "candidate-draft.json"
review = archive / "candidate-review-draft.json"
inventory = root / "data/practices/04-inventory.json"
pointer = root / "data/current.json"
prior = archive / "candidate-verify-62258890"
job = os.environ["SLURM_JOB_ID"]
output = archive / f"candidate-preview-recovery-{job}"
output.mkdir()

def sha(path):
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()

def read(path):
    return json.loads(path.read_bytes())

assert sha(package) == "2bca7d9a895c282df74d9a09c36e817be5ce6394cba738cd3b7e528c65ab2783"
assert sha(review) == "a305484f46ec4bd7cae6eae1201e3bc509ba71c06c90e1d30192d81116a85e36"
assert sha(inventory) == "58e75b83e3a3634e33ef8dc519302c709ea923dac6074b276b487991c83cb5d7"
expected_pointer = "5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7"
assert sha(pointer) == expected_pointer
prior_logs = {}
for gate, marker in (("input", "PRACTICE_INPUT_OK"), ("source", "PRACTICE_SOURCE_REVIEW_OK")):
    log = prior / f"{gate}-retry.log"
    assert (prior / f"{gate}-retry.exit").read_text().strip() == "0"
    assert log.read_text().strip() == marker
    prior_logs[gate] = sha(log)
old_root = root / "data/practices/sources/saadet"
new_root = archive / "source-root"
entries = read(package)["entries"]
new_versions = [
    entry["values"] for entry in entries
    if entry["kind"] == "document_version" and entry["values"]["id"].startswith("0411-mine-inquiry-")
]
assert {row["id"] for row in new_versions} == {
    "0411-mine-inquiry-identity-v1", "0411-mine-inquiry-filing-v1", "0411-mine-inquiry-answer-v1",
}
for row in new_versions:
    assert sha(new_root / row["original_path"]) == row["sha256"]
with TemporaryDirectory(prefix="gsd-0411-35779-preview-", dir="/tmp") as folder:
    scratch = Path(folder)
    source = scratch / "party-sources"
    copytree(old_root, source)
    for src in sorted(path for path in new_root.rglob("*") if path.is_file()):
        dst = source / src.relative_to(new_root)
        if dst.exists():
            assert sha(dst) == sha(src), dst
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
    out = scratch / "preview"
    log = output / "preview.log"
    command = [
        sys.executable, "src/arsiv.py", "practice-preview", "--input", str(package),
        "--inventory", str(inventory), "--out", str(out), "--source-root", str(source),
    ]
    with log.open("x") as stream:
        status = subprocess.call(command, cwd=root, env={**os.environ,"TMPDIR":"/tmp"},
                                 stdout=stream, stderr=subprocess.STDOUT)
    (output/"preview.exit").write_text(f"{status}\n")
    assert status == 0 and log.read_text().startswith("PRACTICE_PREVIEW_OK")
    local_release, = (out/"releases").iterdir()
    preview = output / "preview"
    copytree(out, preview)
release = preview / "releases" / local_release.name
manifest = read(release/"manifest.json")
assert manifest["preview"] and manifest["renderer_version"] == 31
assert all(sha(release/name) == digest for name,digest in manifest["files"].items())
assert sha(pointer) == expected_pointer and not (root/"data/.write.lock").exists()
records = read(package)["practice_records"]
rendered = read(release/"records.json")
counts = {}
stem = "0411-saadet-mine-inquiry-35779"
with sqlite3.connect((release/"records.sqlite3").resolve().as_uri()+"?mode=ro", uri=True) as db:
    db.row_factory = sqlite3.Row
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    for table in ("practice_event","practice_relation","practice_contribution","practice_closure"):
        expected = {row["id"]:row for row in records[table]}
        actual = {row["id"]:row for row in rendered[table] if row["id"] in expected}
        sql_rows = {row["id"]:dict(row) for row in db.execute(f"SELECT * FROM {table}") if row["id"] in expected}
        assert expected == actual == sql_rows
        counts[table] = len(expected)
    assert (counts["practice_event"],counts["practice_relation"],counts["practice_closure"]) == (41,37,0)
report = (release/"index.html").read_text()
for view in ("party","comparison"):
    anchor = f"{view}-practice-{stem}-relation"
    target = f'id="{anchor}"'
    assert report.count(target) == 1 and f'href="#{anchor}"' in report
    card = report.split(target,1)[1].split("</article>",1)[0]
    for word in ("2020","2021","kıdem","Bakanlık"):
        assert word.casefold() in card.casefold(), (view,word)
result = {
    "job":job, "input_source_allocation":"62258890", "prior_logs":prior_logs,
    "package_sha256":sha(package), "review_sha256":sha(review), "inventory_sha256":sha(inventory),
    "preview":str(release), "manifest_sha256":sha(release/"manifest.json"),
    "counts":counts, "canonical_pointer_sha256":expected_pointer,
}
(output/"receipt.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
print("SAADET_35779_PREVIEW_RECOVERY_BOTH_VIEWS_OK", release, flush=True)
