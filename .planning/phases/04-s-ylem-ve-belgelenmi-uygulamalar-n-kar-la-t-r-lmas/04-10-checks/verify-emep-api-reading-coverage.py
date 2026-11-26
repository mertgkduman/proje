"""Measure documented EMEP reading by source bytes and character intervals."""

from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys


def digest(body):
    return sha256(body).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def uncovered(start, end, intervals):
    cursor = start
    gaps = []
    for left, right in sorted(intervals):
        if right <= cursor or left >= end:
            continue
        if left > cursor:
            gaps.append([cursor, left])
        cursor = min(end, right)
    if cursor < end:
        gaps.append([cursor, end])
    return gaps


root = Path(__file__).resolve().parent
catalog = read(root / "party-api-catalog.json")
index = {row["id"]: row for row in catalog["posts"]}
assert len(index) == len(catalog["posts"]) == catalog["post_count"]
bodies = {}
for page in catalog["pages"]:
    path = root / "party-api-pages" / Path(page["path"]).name
    raw = path.read_bytes()
    assert digest(raw) == page["sha256"], path
    posts = json.loads(raw)
    assert len(posts) == page["count"], path
    for post in posts:
        identity = post["id"]
        row = index.get(identity)
        if row and Path(row["page"]).name == path.name:
            body = post["content"]["rendered"]
            assert len(body) == row["body_characters"] and digest(body.encode()) == row["body_sha256"], identity
            bodies[identity] = body
assert set(bodies) == set(index)
intervals = defaultdict(list)
unverified = Counter()
receipts = 0
for artifact in sorted(root.glob("party-api-*-reading.json")):
    raw = read(artifact)
    parts = raw.get("parts") or ([raw] if "post_id" in raw else [])
    if not parts:
        unverified["no_intervals"] += 1
        continue
    receipts += 1
    for part in parts:
        identity = part.get("post_id")
        start, end = part.get("start_char"), part.get("end_char")
        entry = index.get(identity)
        if not entry or part.get("body_sha256") != entry["body_sha256"] or not isinstance(start, int) or not isinstance(end, int):
            unverified["incomplete_metadata"] += 1
            continue
        body = bodies[identity]
        if not 0 <= start < end <= len(body):
            unverified["invalid_bounds"] += 1
            continue
        if part.get("slice_sha256") and digest(body[start:end].encode()) != part["slice_sha256"]:
            unverified["slice_mismatch"] += 1
            continue
        if not (part.get("reading_note") or part.get("observation")):
            unverified["missing_reading_note"] += 1
            continue
        intervals[identity].append((start, end))
body_status = Counter()
gaps = []
for row in catalog["posts"]:
    identity = row["id"]
    missing = uncovered(0, row["body_characters"], intervals[identity])
    state = "full" if not missing else "partial" if intervals[identity] else "unverified"
    body_status[state] += 1
    if missing:
        gaps.append(dict(post_id=identity, url=row["url"], page=Path(row["page"]).name,
                         ranges=missing, body_characters=row["body_characters"]))
tranche_status = Counter()
queue = read(root / "party-api-reading-queue.json")
for tranche in queue["tranches"]:
    parts = tranche["parts"]
    checked = [not uncovered(row["start_char"], row["end_char"], intervals[row["post_id"]]) for row in parts]
    state = "full" if all(checked) else "partial" if any(checked) else "unverified"
    tranche_status[tranche["state"], state] += 1
summary = dict(
    cutoff=catalog["cutoff"], source_pages=len(catalog["pages"]), total_posts=len(index),
    receipt_files=receipts, body_status=dict(body_status), excluded_parts=dict(unverified),
    tranche_status=[dict(previous=x, verified=y, count=total)
                    for (x, y), total in sorted(tranche_status.items())],
    next_gaps=gaps[:10],
    note="Sayım özgün API gövdesine ve okuma makbuzlarındaki karakter aralıklarına dayanır. Makbuz eksiği kaynak yokluğu veya kapsam kapanışı değildir.",
)
if len(sys.argv) == 2:
    Path(sys.argv[1]).write_text(json.dumps(gaps,ensure_ascii=False,indent=2)+"\n")
print(json.dumps(summary,ensure_ascii=False,indent=2))
