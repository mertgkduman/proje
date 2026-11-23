"""İki benzer sonuç cümlesinin doğru gündem önerisine bağlandığını sınar."""
import json
from pathlib import Path
from arsiv import html_source_text
c = Path(__file__).resolve().parent
root = c.parents[3]
source = root/'data/practices/sources/dem/objects/43f76c014493808d974aed00ce23152667132f1862f387bde6f788524a17357b/original.html.bin'
text = html_source_text(source.read_bytes())
def passages(name, prefix):
    records = json.loads((c/name).read_text())['entries']
    return {e['values']['id'].removeprefix(prefix):e['values']['exact'] for e in records if e['kind']=='passage'}
a = passages('nov03-dem-source-records.json', '0406-nov03-genelgorusme-')
b = passages('nov03-4961-dem-source-records.json', '0406-nov03-4961-')
first_call = text.index(a['floor-call'])
first_role = text.index(a['floor-dem-role'], first_call)
first_vote = text.index(a['floor-vote'], first_role)
second_call = text.index(b['floor-call'], first_vote)
second_role = text.index(b['floor-dem-role'], second_call)
second_vote = text.index(b['floor-vote'], second_role)
assert first_call < first_role < first_vote < second_call < second_role < second_vote
assert text.index(a['floor-vote'], first_call) == first_vote
assert text.index(b['floor-vote'], second_call) == second_vote
print('TWO_SEPARATE_AGENDA_ORDERS_OK', first_call, first_role, first_vote, second_call, second_role, second_vote)
