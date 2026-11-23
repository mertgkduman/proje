"""Verify the July group position and the retained October match history."""

import importlib.util
import json
from pathlib import Path
import sqlite3

here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('practice_validation',
    here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness=importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE=here
harness.SOURCE=harness.DATA/'practices/sources/iyi'
july='0407-iyi-2026-4343'
october='0407-iyi-2026-fund-1007'
package=here/'fund-july-draft.json'
review=here/'fund-july-review-draft.json'
assert harness.sha(package)=='aa72e5eda7c2dc6faabd8a4ab74cf8d21d761dc61097717ce336c4fcb78a97ab'
assert harness.sha(review)=='d3c223c1d0d4bda8376b87f508407c2ce5990fcf6a91ccf5bbe79e90aa3ee163'
draft=json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event'])==10 and len(draft['practice_relation'])==8
assert not draft['practice_closure']
receipt=harness.main(package,review,'fund-july',october+'-event',october+'-relation',None,
    expected_party='iyi',namespace='gsd-0407')
folder=Path(receipt['preview'])
assert json.loads((folder/'manifest.json').read_bytes())['renderer_version']==31
saved=json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    for table in ('practice_event','practice_candidate','practice_candidate_revision','practice_relation','practice_statement','practice_contribution'):
        for row in draft[table]:
            assert row in saved[table]
            assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    assert db.execute('SELECT state FROM practice_candidate WHERE id=?',(october+'-unmatched',)).fetchone()[0]=='unmatched'
    rev=db.execute('SELECT state,candidate_id,relation_id FROM practice_candidate_revision WHERE id=?',
        (october+'-reviewed-match',)).fetchone()
    assert tuple(rev)==('eligible',october+'-unmatched',october+'-relation')
    assert db.execute('SELECT result_finding_id FROM practice_relation WHERE id=?',(october+'-relation',)).fetchone()[0] is None
page=(folder/'index.html').read_text()
for view in ('party','comparison'):
    tag=f'id="{view}-practice-{october}-relation"'
    assert page.count(tag)==1
    card=page.split(tag,1)[1].split('</article>',1)[0]
    assert all(term in card for term in ('10/4343','1 Temmuz','7 Ekim','araştırma komisyonu'))
    assert f'id="{view}-unmatched-{july}-unmatched"' in page
    assert f'id="{view}-unmatched-{october}-unmatched"' not in page
print('IYI_4343_AND_OCTOBER_REVIEWED_MATCH_OK',folder,flush=True)
