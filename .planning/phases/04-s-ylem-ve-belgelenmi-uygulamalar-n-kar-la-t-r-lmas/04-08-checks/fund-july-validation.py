"""Verify 10/4343 and the later fund debate in the two reader views."""

import importlib.util
import json
from pathlib import Path
import sqlite3

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation',here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = here
harness.SOURCE = harness.DATA/'practices/sources/yeni-yol'
july = '0408-yeni-yol-2026-4343'
october = '0408-yeni-yol-2026-fund-1007'
package = here/'fund-july-draft.json'
review = here/'fund-july-review-draft.json'
assert harness.sha(package)=='e6aa7c1eb76d7c759588c17f191c6eae92cd7935adeda037e2f730f5b3994ae6'
assert harness.sha(review)=='0eb705e8360f659f7c3e73c459fd7d9da17fbed9439033818ed55996f2930d08'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event'])==11 and len(draft['practice_relation'])==7
assert not draft['practice_closure']
receipt = harness.main(package,review,'fund-july',july+'-event',july+'-relation',None,
                       expected_party='yeni-yol',namespace='gsd-0408')
folder = Path(receipt['preview'])
assert json.loads((folder/'manifest.json').read_bytes())['renderer_version']==31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_candidate','practice_relation','practice_statement','practice_contribution'):
        for row in draft[table]:
            assert row in saved[table]
            assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    assert not db.execute("SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'",
                          (october+'-event',)).fetchone()
    for passage in ('quorum1','quorum2','decision'):
        assert db.execute("SELECT event_id FROM practice_event_evidence WHERE passage_id=?",
                          ('0408-fund-july-floor-'+passage,)).fetchone()[0]==july+'-event'
report = (folder/'index.html').read_text()
for view in ('party','comparison'):
    for stem,terms in ((july,('10/4343','karar yeter sayısı','üçüncü elektronik')),
                       (october,('Bülent Kaya','araştırma komisyonu','7 Ekim'))):
        tag=f'id="{view}-practice-{stem}-relation"'
        assert report.count(tag)==1
        card=report.split(tag,1)[1].split('</article>',1)[0]
        assert all(term in card for term in terms),(view,stem)
print('YENI_YOL_4343_AND_FUND_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
