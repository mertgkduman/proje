"""Check the original newspaper evidence for the 18 May 2020 statement."""

from datetime import datetime, timezone
from pathlib import Path
from sys import argv
import json

audit = json.loads(Path(argv[1]).read_bytes())
groups = {row["candidate_key"]: row for row in audit["common_event_candidates"]}
cases = {
    "yerel-yonetimler-2020-05-18-ortak-bildiri": (
        {"tip", "dem", "emep", "dbp"}, "0406-yesilsol-2020-event",
        "ff2a7d6312825665a6e74c54f5b1164045c0cc0324eef5237400bb9507085d22",
        "19 Mayıs 2020 BirGün basılı sayısının 8. sayfası, 18 Mayıs ortak bildirisini ve dört partinin imzasını gösteriyor. "
        "TİP ve HDP özgün metinlerinin yayıncıları ve tarihsel imzacılar kendi kaynaklarında korunuyor. "
        "Bildiri yayımlanması ile belediye işlemleri ayrı.",
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
print("REHEARSAL_16_SHARED_ORIGINALS_OK", *(row["candidate_key"] for row in result), flush=True)
