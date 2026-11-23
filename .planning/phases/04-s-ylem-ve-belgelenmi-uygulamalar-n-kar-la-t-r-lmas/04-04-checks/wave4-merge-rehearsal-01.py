"""Reproduce the isolated structural merge from committed working pairs."""

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess

from uygulama_birlestirme import _json, merge_packages

here = Path(__file__).resolve().parent
number = os.environ.get('GSD0404_REHEARSAL_NUMBER', '01')
assert number in {'01', '02'}
receipt = json.loads((here / f'wave4-merge-rehearsal-{number}.json').read_bytes())
decision_bytes = (here / f'wave4-merge-rehearsal-{number}-decisions.json').read_bytes()
data = Path('data')
inventory = json.loads((data/'practices/04-inventory.json').read_bytes())
base = json.loads((data/'releases'/inventory['base_release']/'records.json').read_bytes())


def digest(raw):
    return sha256(raw).hexdigest()


def committed(path):
    return subprocess.check_output(['git','show',f"{receipt['git_commit']}:{path}"])


inputs = []
for party, expected in receipt['original_packages'].items():
    path = data/'practices'/f'04-{party}.json'
    package_raw = committed(path)
    review_raw = committed(path.with_name(f'04-{party}-review.json'))
    assert digest(package_raw) == expected['package_sha256']
    assert digest(review_raw) == expected['companion_review_sha256']
    package = json.loads(package_raw)
    assert package['stage'] == receipt['original_stages'][party]
    package['stage'] = receipt['isolated_stage']
    records = package['practice_records']
    for row in records['practice_contract']:
        row['stage'] = receipt['isolated_stage']
    records['practice_source_review'] = json.loads(review_raw)['practice_source_review']
    records['practice_source_review_contract'] = [{'version':1}]
    raw = _json(package).encode()
    assert digest(raw) == receipt['isolated_envelope_sha256'][party]
    inputs.append(dict(identity=party,raw=raw))

first = merge_packages(inventory,inputs,decision_bytes,decisions_sha256=receipt['decisions_sha256'],base_records=base)
second = merge_packages(inventory,inputs[::-1],decision_bytes,decisions_sha256=receipt['decisions_sha256'],base_records=base)
assert first == second
assert digest(_json(first).encode()) == receipt['output_sha256']
records = first['payload']['practice_records']
assert len(records['practice_event']) == receipt['merged_events']
assert len(records['practice_relation']) == receipt['merged_relations']
assert len(records['practice_closure']) == receipt['closure_count'] == 0
assert len(first['aliases']) == receipt['event_aliases']
assert len(first['review_origins']) == receipt['review_origins']
print('STRUCTURAL_REHEARSAL_REPRODUCED',receipt['output_sha256'])
