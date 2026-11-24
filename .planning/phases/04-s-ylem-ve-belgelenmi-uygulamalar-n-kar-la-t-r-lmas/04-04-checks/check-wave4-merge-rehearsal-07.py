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
before=json.loads((checks/"wave4-common-event-audit-10.json").read_bytes())
assert before["common_event_candidates"]==audit["common_event_candidates"]
previous=json.loads((checks/"wave4-merge-rehearsal-06-decisions.json").read_bytes())
inventory=json.loads((data/"practices/04-inventory.json").read_bytes())
base=json.loads((data/"releases"/inventory["base_release"]/"records.json").read_bytes())
assert audit["base_release"]==before["base_release"]==inventory["base_release"]

def digest(raw):
    return sha256(raw).hexdigest()

def committed(path):
    return subprocess.check_output(["git","show",f"{source_commit}:{path}"])

inputs=[]
envelopes={}
for party, row in audit["packages"].items():
    package_raw=committed(f"data/practices/04-{party}.json")
    review_raw=committed(f"data/practices/04-{party}-review.json")
    assert digest(package_raw)==row["package_sha256"]
    assert digest(review_raw)==row["companion_review_sha256"]
    package=json.loads(package_raw)
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
             preceding_decisions="wave4-merge-rehearsal-06-decisions.json",
             unchanged_candidate_sources=True, decisions_sha256=decisions_hash,
             output_sha256=digest(_json(merged).encode()), forward_reverse_equal=True,
             same_candidates=sum(r["decision"]=="same" for r in decisions),
             unresolved_candidates=sum(r["decision"]=="unresolved" for r in decisions),
             counts=counts, aliases=len(merged["aliases"]), review_origins=len(merged["review_origins"]),
             canonical_pointer_sha256=digest((data/"current.json").read_bytes()))
assert receipt["canonical_pointer_sha256"]=="5a20d69e24d6623361b067c30d2af018bdfc8fc51874d065111065c1a98b0ad7"
output = Path(sys.argv[4]) if len(sys.argv) > 4 else checks / "wave4-merge-rehearsal-07-preflight.json"
with output.open("x") as stream:
    stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n")
print("REHEARSAL_INPUTS_AND_ORDER_OK",counts,receipt["output_sha256"],flush=True)
