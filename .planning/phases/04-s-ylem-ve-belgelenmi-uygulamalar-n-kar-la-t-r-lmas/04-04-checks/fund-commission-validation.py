"""Verify the 14 October committee result in both views and persisted records."""

import importlib.util
import json
from pathlib import Path
import sqlite3

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('practice_validation',here/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
stem = '0404-fon-komisyon-1014'
package = here/'fund-commission-draft.json'
review = here/'fund-commission-review-draft.json'
assert harness.sha(package) == 'dddcd536d93ff226804b8287cefaba3911f9f2497e8f4f26d907af8834187ee3'
assert harness.sha(review) == 'ef2c83011427e40f8cedd2c2c3817f9e98b45829d150588e6f20adf8b9d27794'
draft = json.loads(package.read_bytes())['practice_records']
assert len(draft['practice_event']) == 140 and len(draft['practice_relation']) == 141
assert not draft['practice_closure']
receipt = harness.main(package,review,'fund-commission',stem+'-event',stem+'-relation',None)
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event','practice_relation','practice_candidate'):
        for row in draft[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
    result = db.execute("SELECT passage_id FROM practice_event_evidence WHERE event_id=? AND stage='result'",
                        (stem+'-event',)).fetchall()
    assert {row[0] for row in result} == {'0404-fund-commission-5472-'+tail for tail in (
        'merge-result','subcommission','result')}
    assert not db.execute("SELECT 1 FROM practice_event_evidence WHERE event_id=? AND stage='result'",
                          ('0404-tbmm-erken-7-51538-event',)).fetchone()
page = (folder/'index.html').read_text()
for view in ('party','comparison'):
    anchor=f'{view}-practice-{stem}-relation'
    tag=f'id="{anchor}"'
    assert page.count(tag)==1 and f'href="#{anchor}"' in page
    card=page.split(tag,1)[1].split('</article>',1)[0]
    assert all(term in card for term in ('2/3895','2/3939','alt komisyon','bağımsız denetim','reddetti'))
print('YENI_PARTI_FUND_COMMITTEE_DB_JSON_BOTH_VIEWS_OK',folder,flush=True)
