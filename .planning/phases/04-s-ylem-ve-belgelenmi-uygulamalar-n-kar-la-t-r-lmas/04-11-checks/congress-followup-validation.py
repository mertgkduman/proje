"""Validate accepted-byte candidates adding distinct congress proceedings."""

import importlib.util
import json
from pathlib import Path
import sqlite3
import sys

phase = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'practice_validation', phase/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
cases = {
    'saadet': ('11','0411-saadet-2024-haziran-olaganustu','0411-saadet-2024-haziran-olaganustu-relation',
               '3805e36c9eb643d1978a0a1306a65064f54168c53a51230a5209c89af3bc0ff1',
               'cee5aa56d52c7659a8f23216056b0ce38bd1d4964dd8c1db259abc78e6615907'),
    'demokrat': ('12','0412-demokrat-2024-merkez-kurul-secimi','0412-demokrat-2024-merkez-kurul-secimi-gik-relation',
                 'be44a4e34558c7da52365b501622e0d79a4ef3a8efd779ac129b2fa3178c888b',
                 'fa239f2e4cf050c3da8b909b3a2f0acb4434121037bafedaa39814b543b510a5'),
}
party=sys.argv[1]
plan,stem,relation,package_hash,review_hash=cases[party]
here=phase/f'04-{plan}-checks'
harness.HERE=here
harness.SOURCE=harness.DATA/'practices'/'sources'/party
sample='congress-followup-v2' if party=='demokrat' else 'congress-followup'
package=here/f'{sample}-draft.json'
review=here/f'{sample}-review-draft.json'
assert (harness.sha(package),harness.sha(review))==(package_hash,review_hash)
receipt=harness.main(package,review,'congress-followup',stem+'-event',relation,None,
                     expected_party=party,namespace=f'gsd-04{plan}')
folder=Path(receipt['preview'])
manifest=json.loads((folder/'manifest.json').read_text())
assert manifest['preview'] and manifest['renderer_version']==30
draft=json.loads(package.read_text())['practice_records']
saved=json.loads((folder/'records.json').read_text())
assert len(draft['practice_event'])==2 and not draft['practice_closure']
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for table in ('practice_event','practice_relation','practice_statement','practice_dispute'):
        for row in draft[table]:
            assert row in saved[table] and row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
html=(folder/'index.html').read_text()
for row in draft['practice_relation']:
    for view in ('party','comparison'):
        anchor=f'{view}-practice-{row["id"]}'
        assert html.count(f'id="{anchor}"')==1 and f'href="#{anchor}"' in html
for row in draft['practice_dispute']:
    assert html.count(f'data-finding-id="{row["summary_finding_id"]}"')==2
print('CONGRESS_FOLLOWUP_DB_JSON_BOTH_VIEWS_OK',party,folder,flush=True)
