"""Check the nine reviewed packages against the previous common-event decisions."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from uygulama_birlestirme import _json, merge_packages
from uygulamalar import _digest

checks=Path(sys.argv[1])
source_commit=sys.argv[2]
data=Path("data")
audit=json.loads(Path(sys.argv[3]).read_bytes())
baseline = json.loads(Path(sys.argv[6]).read_bytes()) if len(sys.argv) > 6 else {}
if baseline:
    before = json.loads(subprocess.check_output([sys.executable, str(checks/"wave4-common-event-audit.py"), baseline["git_commit"]]))
    assert before["packages"] == baseline["original_packages"]
else:
    before=json.loads((checks/"wave4-common-event-audit-10.json").read_bytes())
groups = {row["candidate_key"]:row for row in audit["common_event_candidates"]}
prior_keys = {row["candidate_key"] for row in before["common_event_candidates"]}
overlap = json.loads(Path(sys.argv[5]).read_bytes()) if len(sys.argv) > 5 else None
added_keys = {overlap["candidate_key"]} if overlap else set()
assert set(groups) == prior_keys | added_keys and not prior_keys & added_keys
assert before["common_event_candidates"] == [row for row in audit["common_event_candidates"]
                                             if row["candidate_key"] in prior_keys]
preceding_decisions = Path(sys.argv[6]).stem+"-decisions.json" if baseline else "wave4-merge-rehearsal-06-decisions.json"
previous=json.loads((checks/preceding_decisions).read_bytes())
inventory=json.loads((data/"practices/04-inventory.json").read_bytes())
base=json.loads((data/"releases"/inventory["base_release"]/"records.json").read_bytes())
assert audit["base_release"]==before["base_release"]==inventory["base_release"]

def digest(raw):
    return sha256(raw).hexdigest()

def committed(path):
    return subprocess.check_output(["git","show",f"{source_commit}:{path}"])

inputs=[]
envelopes={}
stages={}
for party, row in audit["packages"].items():
    package_raw=committed(f"data/practices/04-{party}.json")
    review_raw=committed(f"data/practices/04-{party}-review.json")
    assert digest(package_raw)==row["package_sha256"]
    assert digest(review_raw)==row["companion_review_sha256"]
    package=json.loads(package_raw)
    stages[party]=package["stage"]
    package["stage"]="partial"
    records=package["practice_records"]
    for contract in records["practice_contract"]:
        contract["stage"]="partial"
    records["practice_source_review"]=json.loads(review_raw)["practice_source_review"]
    records["practice_source_review_contract"]=[{"version":1}]
    raw=_json(package).encode()
    envelopes[party]=digest(raw)
    inputs.append(dict(identity=party,raw=raw))

members={event["event"]["id"]:event["party"] for group in audit["common_event_candidates"] for event in group["party_records"]}
decisions=[]
for record in previous["decisions"]:
    refs=[dict(event_id=ref["event_id"],input_package_sha256=envelopes[members[ref["event_id"]]])
          for ref in record["event_refs"]]
    decisions.append(dict(record,event_refs=refs))
if overlap:
    key = overlap["candidate_key"]
    group = groups[key]
    assert group["differing_fields"] == overlap["differing_fields"]
    refs, evidence = [], []
    for member in group["party_records"]:
        party, event = member["party"], member["event"]
        read = overlap["members"][party]
        assert read["event"] == event
        actual = {row["passage_id"]:row["source_sha256"] for row in member["evidence"]}
        assert all(actual[row["passage_id"]] == row["sha256"] for row in read["passages"])
        refs.append(dict(event_id=event["id"],input_package_sha256=envelopes[party]))
        evidence.extend(row["passage_id"] for row in read["passages"])
    assert len(refs) == len(overlap["members"])
    canonical = overlap.get("canonical_event_id")
    if overlap["decision"] == "same":
        assert not group["differing_fields"] and canonical in {ref["event_id"] for ref in refs}
        assert set(overlap["common_source_sha256"]) <= set(group["common_evidence_sha256"])
        assert overlap["common_source_sha256"]
    else:
        assert overlap["decision"] == "unresolved" and canonical is None
    decisions.append(dict(id=key,candidate_keys=[key],event_refs=refs,
        decision=overlap["decision"],canonical_event_id=canonical,overlap_reason=overlap["overlap_reason"],
        source_passage_ids=sorted(evidence),reviewed_at=overlap["reviewed_at"],reviewer_kind=overlap["reviewer_kind"]))
decision_bytes=(_json(dict(decisions=decisions,input_digests=envelopes,
                           inventory_digest=_digest(inventory),version=1))+"\n").encode()
decisions_hash=digest(decision_bytes)
merged=merge_packages(inventory,inputs,decision_bytes,decisions_sha256=decisions_hash,base_records=base)
reversed_merge=merge_packages(inventory,list(reversed(inputs)),decision_bytes,decisions_sha256=decisions_hash,base_records=base)
assert merged==reversed_merge
records=merged["payload"]["practice_records"]
counts={k:len(records[k]) for k in ("practice_event","practice_relation","practice_closure")}
expected_events=sum(row["events"] for row in audit["packages"].values())-sum(
    len(row["event_refs"])-1 for row in decisions if row["decision"]=="same")
assert counts==dict(practice_event=expected_events,practice_relation=sum(row["relations"] for row in audit["packages"].values()),
                    practice_closure=0), counts
receipt=dict(git_commit=source_commit,base_release=inventory["base_release"],kind="isolated_merge_preflight",
             original_packages=audit["packages"],isolated_envelopes=envelopes,
             preceding_decisions=preceding_decisions,
             unchanged_candidate_sources=True, decisions_sha256=decisions_hash,
             output_sha256=digest(_json(merged).encode()), forward_reverse_equal=True,
             same_candidates=sum(r["decision"]=="same" for r in decisions),
             unresolved_candidates=sum(r["decision"]=="unresolved" for r in decisions),
             counts=counts, aliases=len(merged["aliases"]), review_origins=len(merged["review_origins"]),
             canonical_pointer_sha256=digest((data/"current.json").read_bytes()))
assert receipt["canonical_pointer_sha256"]=="5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7"
output = Path(sys.argv[4]) if len(sys.argv) > 4 else checks / "wave4-merge-rehearsal-07-preflight.json"
if overlap:
    receipt.update(original_stages=stages,isolated_stage="partial",isolated_envelope_sha256=envelopes,
        merged_events=counts["practice_event"],merged_relations=counts["practice_relation"],
        closure_count=counts["practice_closure"],event_aliases=receipt["aliases"],added_reviewed_candidates=sorted(added_keys))
    with output.with_name(output.stem+"-decisions.json").open("xb") as stream:
        stream.write(decision_bytes)
with output.open("x") as stream:
    stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
print("REHEARSAL_INPUTS_AND_ORDER_OK",counts,receipt["output_sha256"],flush=True)
