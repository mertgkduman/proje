"""Run all gates and independently inspect both November events and views."""
import importlib.util, json, sqlite3, sys
from pathlib import Path

checks=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('practice_validation',checks.parent/'04-04-checks'/'samsun-reply-validation.py')
h=importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
h.HERE=checks; h.SOURCE=h.DATA/'practices/sources/demokrat'
case='six-leaders-november-dp-v2'; stem='0412-six-leaders-2022-11-28'
package=checks/f'{case}-draft.json'; review=checks/f'{case}-review-draft.json'
assert [h.sha(p) for p in (package,review)]==sys.argv[1:]
records=json.loads(package.read_bytes())['practice_records']
assert [len(records[k]) for k in ('practice_event','practice_relation','practice_closure')]==[83,54,0]
receipt=h.main(package,review,case,f'{stem}-meeting-event',f'{stem}-meeting-relation',None,expected_party='demokrat',namespace='gsd-0412')
folder=Path(receipt['preview']); data=json.loads((folder/'records.json').read_bytes()); report=(folder/'index.html').read_text()
with sqlite3.connect((folder/'records.sqlite3').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 for name in ('meeting','presentation'):
  for table,suffix in (('practice_statement','statement'),('practice_event','event'),('practice_relation','relation'),('practice_candidate','candidate'),('practice_contribution','uysal-contribution')):
   ident=f'{stem}-{name}-{suffix}'; expected=next(r for r in records[table] if r['id']==ident)
   actual=db.execute(f'SELECT * FROM {table} WHERE id=?',(ident,)).fetchone()
   assert expected in data[table] and actual is not None and expected==dict(actual),ident
  for view in ('party','comparison'):
   anchor=f'{view}-practice-{stem}-{name}-relation'; marker=f'id="{anchor}"'
   assert report.count(marker)==1 and f'href="#{anchor}"' in report
   assert 'Uysal' in report.split(marker,1)[1].split('</article>',1)[0],anchor
assert h.canonical_identity()==receipt['canonical']
print('DEMOCRAT_NOVEMBER_BOTH_EVENTS_BOTH_VIEWS_OK',folder,flush=True)
