"""Verify the original evidence when adding DBP to the Haliç event."""

from datetime import datetime, timezone
from pathlib import Path
from sys import argv
import json

audit = json.loads(Path(argv[1]).read_bytes())
groups = {row["candidate_key"]: row for row in audit["common_event_candidates"]}
cases = {
    "halic-emek-ozgurluk-2022-09-24": (
        {"tip", "dem", "emep", "dbp"}, "0405-tip-halic-cemevi-2022-halic-event",
        "a086de25cf9ac44d84a409f658b25d16a6e9f33b801089d56e066806fd10625e",
        "DBP, aynı Bianet haberinin özdeş özgün baytlarında eş genel başkanı Keskin Bayındır’ın katılımını belgeliyor. Önceki üç çalışmanın olay kimlikleri, kaynakları ve katkıları korunuyor. DBP katkısı salonda bulunma ile sınırlı.",
    ),
}
result = []
reviewed = datetime.now(timezone.utc).isoformat()
for key, (parties, canonical, digest, reason) in cases.items():
    group = groups[key]
    assert group["differing_fields"] == []
    assert digest in group["common_evidence_sha256"]
    assert {row["party"] for row in group["party_records"]} == parties
    assert canonical in {row["event"]["id"] for row in group["party_records"]}
    members = {}
    for row in group["party_records"]:
        evidence = [dict(passage_id=p["passage_id"], sha256=digest, source=p["source"],
                         section=p["section"], claim=p["claim"])
                    for p in row["evidence"] if p["source_sha256"] == digest]
        assert evidence
        members[row["party"]] = dict(event=row["event"], passages=evidence)
    result.append(dict(candidate_key=key, differing_fields=[], canonical_event_id=canonical, decision="same",
                       common_source_sha256=[digest], overlap_reason=reason, reviewer_kind="agent",
                       reviewed_at=reviewed, members=members))
with Path(argv[2]).open("x") as stream:
    stream.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print("REHEARSAL_15_SHARED_ORIGINALS_OK", *(row["candidate_key"] for row in result), flush=True)
