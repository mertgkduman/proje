"""Check the three 2018 source records in both reader views."""

import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import sys

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', checks.parent / '04-04-checks' / 'samsun-reply-validation.py'
)
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'emep'
case = 'emep-2018-disk-adana'
stage = Path(os.environ['GSD0410_DISK_ADANA_CANDIDATE']).resolve()
package,review = (stage/f'{case}{suffix}-draft.json' for suffix in ('','-review'))
assert [harness.sha(path) for path in (package, review)] == sys.argv[1:]
prefix = '0410-emep-2018-disk-adana'
receipt = harness.main(package,review,case,f'{prefix}-disk-event','0410-emep-istanbul-sozlesmesi-relation',
                       None,expected_party='emep',namespace='gsd-0410')
folder=Path(receipt['preview'])
rows=json.loads(package.read_bytes())['practice_records']
export=json.loads((folder/'records.json').read_bytes())
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
    db.row_factory=sqlite3.Row
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not db.execute('PRAGMA foreign_key_check').fetchall()
    for table,n in (('practice_event',91),('practice_relation',82),('practice_closure',0)):
        assert len(rows[table])==n
        assert all(row in export[table] for row in rows[table])
    candidates = db.execute(
        'SELECT c.id,c.state,c.relation_id,v.event_at FROM practice_candidate c '
        'JOIN practice_event v ON c.event_id=v.id WHERE c.id LIKE ?', (prefix+'%',),
    )
    days={'disk':'2018-10-09','adana':'2018-10-19','decision':'2018-12-05'}
    assert {tuple(r) for r in candidates} == {(f'{prefix}-{key}-unmatched','unmatched',None,date) for key,date in days.items()}
    for table in ('practice_event','practice_candidate'):
        for row in rows[table]:
            if row['id'].startswith(prefix):
                assert row in export[table]
                assert row==dict(db.execute(f'SELECT * FROM {table} WHERE id=?',(row['id'],)).fetchone())
html=(folder/'index.html').read_text()
for key, phrases in {
    'disk':('9 Ekim','DİSK','görev dağılımı'),
    'adana':('19 Ekim','beş','6362/107(2)'),
    'decision':('5 Aralık','yayım günü','imzalı takipsizlik'),
}.items():
    for view in ('party','comparison'):
        anchor=f'{view}-unmatched-{prefix}-{key}-unmatched'
        marker=f'id="{anchor}"'
        assert html.count(marker)==1 and f'href="#{anchor}"' in html,anchor
        card=html.split(marker,1)[1].split('</article>',1)[0].casefold()
        assert all(phrase.casefold() in card for phrase in phrases),(anchor,phrases)
print('EMEP_2018_DISK_ADANA_BOTH_VIEWS_OK',folder,flush=True)
