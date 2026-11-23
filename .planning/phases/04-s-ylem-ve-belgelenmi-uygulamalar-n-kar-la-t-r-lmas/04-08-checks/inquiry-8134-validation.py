"""Verify the dated 8/134 filing and its distinction from later decisions."""

import importlib.util
import json
from pathlib import Path
import sqlite3

checks = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'practice_validation', checks.parent / '04-04-checks' / 'samsun-reply-validation.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)
harness.HERE = checks
harness.SOURCE = harness.DATA / 'practices' / 'sources' / 'yeni-yol'
case = 'inquiry-8134'
stem = '0408-inquiry-8134'
package = checks / f'{case}-draft.json'
review = checks / f'{case}-review-draft.json'
assert harness.sha(package) == '9c735ddaa70da3d4fdc9e77fa4091b3c503943754ef3cc5350ddc66f50c41390'
assert harness.sha(review) == 'c85a375414a050c4192bb81be0829f7270926ce501ba2fb089d815b6da10e441'
records = json.loads(package.read_bytes())['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (20, 12, 0)
receipt = harness.main(package, review, case, stem + '-event', stem + '-relation',
                       None, expected_party='yeni-yol', namespace='gsd-0408')
folder = Path(receipt['preview'])
manifest = json.loads((folder / 'manifest.json').read_bytes())
assert manifest['preview'] and manifest['renderer_version'] == 31
export = json.loads((folder / 'records.json').read_bytes())
with sqlite3.connect((folder / 'records.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
    db.row_factory = sqlite3.Row
    for table, identity in (
        ('practice_statement', '0408-yeni-yol-2026-7573-statement'),
        ('practice_event', stem + '-event'),
        ('practice_relation', stem + '-relation'),
    ):
        row = next(row for row in records[table] if row['id'] == identity)
        assert row in export[table]
        assert row == dict(db.execute(f'SELECT * FROM {table} WHERE id=?', (identity,)).fetchone())
    page = db.execute('SELECT pdf_page_index,printed_page FROM passage WHERE id=?', (stem + '-appendix-listed',)).fetchone()
    assert tuple(page) == (32, '931')
    manual = db.execute('SELECT count(*) FROM manual_passage WHERE passage_id LIKE ?', (stem + '-signed-%',)).fetchone()
    assert manual[0] == 4
report = (folder / 'index.html').read_text()
for view in ('party', 'comparison'):
    anchor = f'{view}-practice-{stem}-relation'
    tag = f'id="{anchor}"'
    assert report.count(tag) == 1 and f'href="#{anchor}"' in report, tag
    card = report.split(tag, 1)[1].split('</article>', 1)[0]
    for term in ('17 Haziran', '1 Temmuz', '931. sayfası', 'Gündemde', 'asgari ücret alt sınırı', 'intibak'):
        assert term.casefold() in card.casefold(), (view, term)
    for suffix in ('-signed-lower-bound', '-appendix-listed', '-register-day'):
        assert f'href="#source-{stem}{suffix}"' in card, (view, suffix)
print('YENI_YOL_INQUIRY_8134_BOTH_VIEWS_OK', folder, flush=True)
