"""Verify the Yeni Yol debate, vote rows, and report references."""

from collections import Counter
from html import unescape
import importlib.util
import json
from pathlib import Path
import re
import sqlite3

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', here.parent/'04-04-checks'/'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = here
harness.SOURCE = harness.DATA/'practices'/'sources'/'yeni-yol'
stem = '0408-yeni-yol-2026-mekke'
package = here/'mekke-draft.json'
review = here/'mekke-review-draft.json'
assert harness.sha(package) == '4a2c9554f27325cd8acbfc043aea42aaea178a37eb2ffe872bf7faee23d6d3a2'
assert harness.sha(review) == 'f926e4dc049de8be49023985004e8992a153fdcaf5df88145cd8a98d674c3dc7'
draft = json.loads(package.read_bytes())
records = draft['practice_records']
assert len(records['practice_event']) == 6 and len(records['practice_relation']) == 3
assert not records['practice_closure']
receipt = harness.main(package, review, 'mekke', stem+'-event', stem+'-relation', None,
                       expected_party='yeni-yol', namespace='gsd-0408')
folder = Path(receipt['preview'])
manifest = json.loads((folder/'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
saved = json.loads((folder/'records.json').read_bytes())
source = json.loads((here/'mekke-source-records.json').read_bytes())
version = next(e['values'] for e in source['entries'] if e['kind']=='document_version'
               and e['values']['id']=='0408-mekke-ballot-v1')
raw = harness.SOURCE/version['original_path']
assert harness.sha(raw) == version['sha256']
assert (harness.DATA/'practices'/'sources'/'saadet'/version['original_path']).read_bytes() == raw.read_bytes()
ballot = raw.read_bytes().decode('windows-1254')
votes = source['vote_rows']
assert len(votes)==20 and Counter(row[-3] for row in votes)=={'RET':15,'KABUL':1,'KATILMADI':4}
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table in ('practice_event', 'practice_relation', 'practice_candidate', 'practice_contribution'):
        for row in records[table]:
            assert row in saved[table]
            assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (row['id'],)).fetchone())
    for passage_id, province, surname, name, electronic, paper, result, day, clock in votes:
        row = dict(db.execute('SELECT * FROM passage WHERE id=?',(passage_id,)).fetchone())
        assert row in saved['passage'] and row['exact'] in ballot
        cells = [unescape(re.sub(r'<[^>]+>', '', cell)).strip()
                 for cell in re.findall(r'<td[^>]*>(.*?)</td>', row['exact'], re.S|re.I)]
        assert cells == [province, surname, name, 'Yeni Yol Partisi', electronic, paper, result, day, clock]
page = (folder/'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert page.count(tag) == 1 and f'href="#{anchor}"' in page
    card = page.split(tag, 1)[1].split('</article>', 1)[0]
    assert all(text in card for text in ('15 ret, 1 kabul ve 4 katılmadı', '277 kabul ve 118 ret', 'Ertuğrul Kaya'))
assert page.count(f'data-finding-id="{stem}-group-speech"') == 2
print('YENI_YOL_MEKKE_DB_JSON_BOTH_VIEWS_OK', folder, flush=True)
