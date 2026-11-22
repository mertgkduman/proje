"""Verify the two additional parliamentary records for a party."""

import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys

phase = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'practice_validation', phase/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
cases = {
    'yeni-yol': ('08','0408-yeni-yol-2025-2-3406-istihdam',2,
        'bb0454e596b75bdb355dfc963a347b163ff3c83f5fd06ee0e72f88a03d1b1891',
        '76a251035631cc836031fdc6fe29fdcab387f3026ede7b20862a5e7242b1b675'),
    'demokrat': ('12','0412-demokrat-2023-7-5577-petrol',6,
        '598bd72c66632a073947de1d996599bbdbb1b681f9891b8f42c767a6d86bdedc',
        'fb5fdc96f6f95ed3062667143b3d73842ec7d1691a2f1b73d7bc409a9a4fed59'),
}
party = sys.argv[1]
plan, stem, expected_relations, package_hash, review_hash = cases[party]
here = phase/f'04-{plan}-checks'
harness.HERE = here
code_root = os.environ.get('GSD04_RENDERER_CHECKOUT')
if code_root:
    harness.ROOT = Path(code_root)
    harness.DATA = harness.ROOT/'data'
    harness.INVENTORY = harness.DATA/'practices'/'04-inventory.json'
harness.SOURCE = harness.DATA/'practices'/'sources'/party
package = here/'policy-followup-draft.json'
review = here/'policy-followup-review-draft.json'
assert (harness.sha(package), harness.sha(review)) == (package_hash, review_hash)
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 5 and len(draft['practice_relation']) == expected_relations
assert not draft['practice_closure']
if len(sys.argv) == 4 and sys.argv[2] == '--receipt':
    receipt_path = Path(sys.argv[3])
    receipt = json.loads(receipt_path.read_bytes())
    assert receipt_path.stem == f'policy-followup-{receipt["job"]}'
    assert receipt['canonical'] == harness.canonical_identity()
    assert receipt['inventory_sha256'] == harness.sha(harness.INVENTORY)
    assert receipt['package_sha256'] == package_hash and receipt['review_sha256'] == review_hash
    for mode in ('input', 'source', 'preview'):
        assert receipt_path.with_name(f'{receipt_path.stem}-{mode}.exit').read_text().strip() == '0'
else:
    assert len(sys.argv) == 2
    receipt = harness.main(package, review, 'policy-followup', stem+'-event', stem+'-relation', None,
                           expected_party=party, namespace=f'gsd-04{plan}')
folder = Path(receipt['preview'])
manifest_path = folder/'manifest.json'
manifest = json.loads(manifest_path.read_bytes())
assert harness.sha(manifest_path) == receipt['preview_manifest_sha256']
assert all(harness.sha(folder/name) == digest for name, digest in manifest['files'].items())
assert manifest['preview'] and manifest['renderer_version'] == (31 if party == 'yeni-yol' else 30)
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate','practice_contribution'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    proposal = ('0408-yeni-yol-2025-2-3406-istihdam' if party == 'yeni-yol'
                else '0412-demokrat-2024-2-2172-engellilik')
    assert not db.execute(
        "SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'",
        (proposal+'-event',)).fetchone()
page = (folder/'index.html').read_text()
for row in draft['practice_relation']:
    for view in ('party','comparison'):
        anchor = f'{view}-practice-{row["id"]}'
        assert page.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in page
if party == 'yeni-yol':
    candidate = '0408-yeni-yol-2025-10-3464-destek-candidate'
    for view in ('party','comparison'):
        anchor = f'{view}-unmatched-{candidate}'
        tag = f'id="{anchor}"'
        assert page.count(tag) == 1 and f'href="#{anchor}"' in page
        card = page.split(tag,1)[1].split('</article>',1)[0]
        assert all(term in card for term in ('10/3464', 'Elif Esen', 'destek', 'oylama yapılmadı'))
        assert 'data-finding-id="0408-yeni-yol-2025-10-3464-destek-support-finding"' in card
else:
    for term in ('11528','6 rafinerici','36 dağıtıcı'):
        assert term in page
print('POLICY_FOLLOWUP_DB_JSON_BOTH_VIEWS_OK',party,folder,flush=True)
